import math
from collections import Counter
from typing import Dict, List


def _tokens(text: str) -> List[str]:
    """将文本分割为小写标记，支持中文。"""
    import re
    # 对中文文本，统计字符数而不是词数
    # 移除标点和空格，统计实际内容字符
    chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
    english_words = re.findall(r'[a-zA-Z]+', text.lower())
    # 中文字符 + 英文词汇
    return chinese_chars + english_words


def _ngram_counts(tokens: List[str], n: int = 2) -> Counter:
    """计算标记列表中的n-gram。"""
    return Counter(
        tuple(tokens[i:i+n]) for i in range(len(tokens) - n + 1)
    )


def redundancy_score(text: str) -> float:
    """基于重复的二元组计算冗余分数。"""
    toks = _tokens(text)
    if len(toks) < 10:
        return 1.0
    
    bigrams = _ngram_counts(toks, 2)
    total = max(1, sum(bigrams.values()))
    repeats = sum(c for c in bigrams.values() if c > 1)
    return max(0.0, 1.0 - repeats / total)


def relevance_score(prompt: str, report: str) -> float:
    """计算报告与提示词的相关性分数。"""
    prompt_tokens = set(_tokens(prompt))
    report_tokens = set(_tokens(report))
    if not prompt_tokens:
        return 1.0
    
    overlap = len(prompt_tokens & report_tokens) / len(prompt_tokens)
    return min(1.0, 0.3 + 0.7 * overlap)


def completeness_score(report: str) -> float:
    """评估报告的完整性（是否包含多个部分）。"""
    lines = report.splitlines()
    sections = sum(1 for line in lines if line.strip().startswith("##"))
    
    # 商业报告应该有多个部分
    if sections >= 4:
        return 1.0
    elif sections >= 2:
        return 0.7
    elif sections >= 1:
        return 0.4
    else:
        return 0.2


def length_fit_score(report: str, target_words: int) -> float:
    """计算长度适合度分数，对中文更友好。"""
    tokens = _tokens(report)
    actual_count = len(tokens)
    if actual_count == 0:
        return 0.0
    
    ratio = actual_count / max(1, target_words)
    # 使用更宽松的评分标准，允许 50%-150% 的范围都有较好分数
    if 0.5 <= ratio <= 1.5:
        # 在理想范围内，使用平滑的评分曲线
        return 1.0 - abs(ratio - 1.0) * 0.5
    elif ratio < 0.5:
        # 太短，线性衰减
        return ratio * 2.0 * 0.75  # 最低 0，在 50% 时为 0.75
    else:
        # 太长，较温和的衰减
        return max(0.1, 1.0 / (ratio * 0.8))  # 不会完全为0


def structure_score(report: str, prefer_bullets: bool) -> float:
    """基于格式偏好计算结构分数。"""
    lines = report.splitlines()
    has_bullets = any(
        line.strip().startswith(("-", "*")) for line in lines
    )
    has_paragraphs = any(
        len(line.strip()) > 0 and not line.strip().startswith(("-", "*", "#"))
        for line in lines
    )
    has_headers = any(
        line.strip().startswith("#") for line in lines
    )
    
    # 商业报告应该有标题结构
    base_score = 0.8 if has_headers else 0.3
    
    if prefer_bullets:
        return base_score + (0.2 if has_bullets else 0.0)
    else:
        return base_score + (0.2 if has_paragraphs else 0.0)


def overall_score(
    source: str, summary: str, target_words: int, prefer_bullets: bool
) -> Dict[str, float]:
    """计算带权重组件的总体分数。"""
    r = redundancy_score(summary)
    rel = relevance_score(source, summary)  # 使用相关性而不是覆盖率
    comp = completeness_score(summary)  # 新增完整性评分
    l = length_fit_score(summary, target_words)
    s = structure_score(summary, prefer_bullets)
    
    # 重新调整权重，更适合商业报告生成
    total = 0.2 * r + 0.3 * rel + 0.25 * comp + 0.15 * l + 0.1 * s
    
    return {
        "redundancy": r,
        "relevance": rel,
        "completeness": comp,
        "length_fit": l,
        "structure": s,
        "total": total
    }
