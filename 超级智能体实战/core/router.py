
import yaml

class ModelRouter:
    def __init__(self, cfg="configs/models.yaml"):
        with open(cfg,"r",encoding="utf-8") as f:
            self.cfg = yaml.safe_load(f)

    def pick_llm(self, task):
        has_image = task.get("multimodal", {}).get("has_image", False)
        ctx = task.get("ctx_tokens", 2000)
        if has_image:
            return self.cfg["llm"]["vision"]
        if ctx < 4000:
            return self.cfg["llm"]["small"]
        return self.cfg["llm"]["large"]

    def pick_embed(self):
        return self.cfg["embed"]["default"]
