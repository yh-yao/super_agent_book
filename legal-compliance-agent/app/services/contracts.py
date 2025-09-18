import os, re, json, uuid, pdfplumber
from typing import Tuple
from docx import Document

BASELINE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "standard_clauses")
REPORT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "reports")

def _read_text_from_file(path: str) -> str:
    if path.lower().endswith(".pdf"):
        text = ""
        with pdfplumber.open(path) as pdf:
            for p in pdf.pages:
                text += p.extract_text() or ""
        return text
    elif path.lower().endswith(".docx"):
        doc = Document(path)
        return "\n".join([p.text for p in doc.paragraphs])
    else:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

def _load_baseline() -> str:
    fp = os.path.join(BASELINE_DIR, "baseline_dpa.txt")
    if os.path.exists(fp):
        with open(fp, "r", encoding="utf-8") as f:
            return f.read()
    return ""

CLAUSE_PATTERNS = {
    "governing_law": re.compile(r"(?i)governing law[:\s].*"),
    "breach_notification": re.compile(r"(?i)(breach|personal data breach).*(\d+\s*hours|without undue delay)"),
    "subprocessors": re.compile(r"(?i)subprocessors?.*(consent|authorization|approve)"),
    "liability_cap": re.compile(r"(?i)(liability|aggregate).*(USD|\$|EUR|€|amount)"),
    "tom": re.compile(r"(?i)(technical and organizational measures|TOMs?)")
}

def extract_clauses(text: str) -> dict:
    res = {}
    for name, pat in CLAUSE_PATTERNS.items():
        m = pat.search(text)
        if m:
            res[name] = m.group(0)
    return res

def compare_to_baseline(extracted: dict, baseline_text: str) -> list:
    risks = []
    # Toy comparisons
    if "breach_notification" in extracted and ("72" in extracted["breach_notification"] or "undue delay" in extracted["breach_notification"].lower()):
        pass
    else:
        risks.append({"clause":"breach_notification","severity":"high","note":"Missing 72h or undue delay wording."})

    if "subprocessors" not in extracted:
        risks.append({"clause":"subprocessors","severity":"medium","note":"No explicit subprocessor approval."})

    if "liability_cap" in extracted and any(x in extracted["liability_cap"] for x in ["100,000","100000"]):
        risks.append({"clause":"liability_cap","severity":"medium","note":"Liability cap may be low."})
    return risks

def review_contract_file(tmp_path: str) -> Tuple[dict, list, str]:
    text = _read_text_from_file(tmp_path)
    extracted = extract_clauses(text)
    baseline = _load_baseline()
    risks = compare_to_baseline(extracted, baseline)
    rep_id = str(uuid.uuid4())[:8]
    report_path = os.path.join(REPORT_DIR, f"contract_report_{rep_id}.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump({"extracted":extracted,"risks":risks}, f, ensure_ascii=False, indent=2)
    return extracted, risks, report_path
