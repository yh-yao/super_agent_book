import random
from typing import Dict


class Improver:
    """Improves summarization parameters based on scores."""
    
    def __init__(self, lr: float = 0.2):
        self.lr = lr

    def step(self, params: Dict, score: Dict[str, float]) -> Dict[str, float]:
        """Update parameters based on current scores."""
        new_params = params.copy()
        
        # Adjust target words based on length fitness
        target = params.get("target_words", 150)
        if score["length_fit"] < 0.8:
            delta = int((random.random() - 0.5) * 20)
            target = max(60, min(400, target + delta))
        new_params["target_words"] = target

        # Adjust bullet preference based on structure score
        prefer_bullets = params.get("prefer_bullets", False)
        if score["structure"] < 0.8 and random.random() < 0.6:
            prefer_bullets = not prefer_bullets
        new_params["prefer_bullets"] = prefer_bullets

        # Adjust bullet probability
        bp = float(params.get("bullet_prob", 0.55))
        bp = min(0.9, max(0.1, bp + self.lr * (random.random() - 0.5)))
        new_params["bullet_prob"] = bp

        return new_params
