from dataclasses import dataclass

@dataclass
class Upgrade:
    id: str
    name: str
    description: str
    price: int
    bought: bool = False

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "bought": self.bought
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            id=d["id"],
            name=d.get("name", d["id"]),
            description=d.get("description",""),
            price=d.get("price", 0),
            bought=d.get("bought", False)
        )