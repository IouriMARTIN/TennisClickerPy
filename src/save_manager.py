import json
from pathlib import Path

class SaveManager:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def save(self, player_state, shop):
        data = {
            "player": player_state.to_dict(),
            "shop": shop.to_dict(),
            # optionally time stamp
        }
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load(self):
        if not self.path.exists():
            return None
        with open(self.path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
