# src/player_state.py
class PlayerState:
    def __init__(self):
        self.points = 0.0
        self.click_power = 1.0
        self.global_multiplier = 1.0
        # track purchased upgrades (ids)
        self.purchased_upgrades = []

    def ToDict(self):
        return {
            "points": self.points,
            "click_power": self.click_power,
            "global_multiplier": self.global_multiplier,
            "purchased_upgrades": self.purchased_upgrades,
        }

    @classmethod
    def FromDict(cls, d):
        p = cls()
        p.points = d.get("points", 0.0)
        p.click_power = d.get("click_power", 1.0)
        p.global_multiplier = d.get("global_multiplier", 1.0)
        p.purchased_upgrades = d.get("purchased_upgrades", [])
        return p
