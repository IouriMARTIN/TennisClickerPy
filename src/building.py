# building.py
from dataclasses import dataclass

@dataclass
class Building:
    id: int
    name: str
    base_price: int
    count: int
    production_per_second: float

    def price_next(self):
        return int(self.base_price * (1.15 ** self.count))

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "base_price": self.base_price,
            "count": self.count,
            "production_per_second": self.production_per_second
        }

    @classmethod
    def from_dict(cls, d):
        # ensure id becomes int if possible
        bid = d.get("id", None)
        try:
            bid = int(bid)
        except Exception:
            pass
        return cls(
            id=bid,
            name=d.get("name", bid),
            base_price=d.get("base_price", 1),
            count=d.get("count", 0),
            production_per_second=d.get("production_per_second", 0.0)
        )
