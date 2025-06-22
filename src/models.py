import uuid

class Product:
    """
    Represents a product in the inventory system.
    All fields are optional and default to empty or zero values for flexibility.
    """
    def __init__(self, product_id: str = None, name: str = "", category: str = "", quantity: int = 0, price: float = 0.0, description: str = ""):
        """
        :param product_id: Unique product ID (auto-generated if None)
        :param name: Product name
        :param category: Product category
        :param quantity: Quantity in stock
        :param price: Price per unit
        :param description: Product description (required)
        """
        self.product_id = product_id if product_id else self.generate_id()
        self.name = name
        self.category = category
        self.quantity = quantity
        self.price = price
        self.description = description

    @staticmethod
    def generate_id() -> str:
        """Generate a random, uniform, barcode-like product ID."""
        # Example: PRD-XXXXXXXX (8 uppercase hex digits)
        return f"PRD-{uuid.uuid4().hex[:8].upper()}"

    def to_dict(self) -> dict:
        """Convert the product to a dictionary for serialization."""
        return {
            "product_id": self.product_id,
            "name": self.name,
            "category": self.category,
            "quantity": self.quantity,
            "price": self.price,
            "description": self.description
        }

    @staticmethod
    def from_dict(data: dict):
        """Create a Product instance from a dictionary, allowing missing fields."""
        return Product(
            product_id=data.get("product_id"),
            name=data.get("name", ""),
            category=data.get("category", ""),
            quantity=int(data.get("quantity", 0)),
            price=float(data.get("price", 0.0)),
            description=data.get("description", "")
        ) 