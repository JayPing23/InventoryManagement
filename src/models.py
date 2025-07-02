import uuid
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class Batch:
    """Represents a batch/lot of products."""
    batch_id: str
    product_id: str
    quantity: int
    manufacturing_date: str
    expiration_date: Optional[str] = None
    lot_number: str = ""
    supplier_id: str = ""
    cost_per_unit: float = 0.0
    location: str = ""
    notes: str = ""
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = self.created_at

class Product:
    """
    Represents a product in the inventory system.
    All fields are optional and default to empty or zero values for flexibility.
    Includes batch/lot tracking capabilities.
    """
    def __init__(self, product_id: str = None, name: str = "", category: str = "", 
                 quantity: int = 0, price: float = 0.0, description: str = "",
                 requires_batch_tracking: bool = False, min_quantity: int = 0,
                 reorder_point: int = 0, preferred_supplier_id: str = ""):
        """
        :param product_id: Unique product ID (auto-generated if None)
        :param name: Product name
        :param category: Product category
        :param quantity: Total quantity in stock (sum of all batches if batch-tracked)
        :param price: Price per unit
        :param description: Product description
        :param requires_batch_tracking: Whether this product requires batch/lot tracking
        :param min_quantity: Minimum quantity threshold
        :param reorder_point: Quantity at which to reorder
        :param preferred_supplier_id: ID of the preferred supplier
        """
        self.product_id = product_id if product_id else self.generate_id()
        self.name = name
        self.category = category
        self.quantity = quantity
        self.price = price
        self.description = description
        self.requires_batch_tracking = requires_batch_tracking
        self.min_quantity = min_quantity
        self.reorder_point = reorder_point
        self.preferred_supplier_id = preferred_supplier_id
        self.batches: Dict[str, Batch] = {}
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at

    @staticmethod
    def generate_id() -> str:
        """Generate a random, uniform, barcode-like product ID."""
        # Example: PRD-XXXXXXXX (8 uppercase hex digits)
        return f"PRD-{uuid.uuid4().hex[:8].upper()}"

    def add_batch(self, quantity: int, manufacturing_date: str,
                 expiration_date: Optional[str] = None, lot_number: str = "",
                 supplier_id: str = "", cost_per_unit: float = 0.0,
                 location: str = "", notes: str = "") -> str:
        """
        Add a new batch of the product.
        
        Returns:
            str: Batch ID
        """
        if not self.requires_batch_tracking:
            raise ValueError("This product does not require batch tracking")

        batch_id = f"BAT-{uuid.uuid4().hex[:8].upper()}"
        batch = Batch(
            batch_id=batch_id,
            product_id=self.product_id,
            quantity=quantity,
            manufacturing_date=manufacturing_date,
            expiration_date=expiration_date,
            lot_number=lot_number,
            supplier_id=supplier_id,
            cost_per_unit=cost_per_unit,
            location=location,
            notes=notes
        )
        
        self.batches[batch_id] = batch
        self._update_total_quantity()
        self.updated_at = datetime.now().isoformat()
        return batch_id

    def update_batch_quantity(self, batch_id: str, quantity_change: int) -> bool:
        """
        Update the quantity of a specific batch.
        
        Args:
            batch_id: Batch ID
            quantity_change: Change in quantity (positive for addition, negative for reduction)
            
        Returns:
            bool: True if successful, False if batch not found or invalid quantity
        """
        if not self.requires_batch_tracking or batch_id not in self.batches:
            return False

        batch = self.batches[batch_id]
        new_quantity = batch.quantity + quantity_change
        if new_quantity < 0:
            return False

        batch.quantity = new_quantity
        batch.updated_at = datetime.now().isoformat()
        self._update_total_quantity()
        self.updated_at = datetime.now().isoformat()
        return True

    def remove_batch(self, batch_id: str) -> bool:
        """Remove a batch from the product."""
        if batch_id in self.batches:
            del self.batches[batch_id]
            self._update_total_quantity()
            self.updated_at = datetime.now().isoformat()
            return True
        return False

    def get_expiring_batches(self, days_threshold: int = 30) -> List[Batch]:
        """Get batches that will expire within the specified number of days."""
        if not self.requires_batch_tracking:
            return []

        threshold_date = datetime.now()
        expiring = []

        for batch in self.batches.values():
            if batch.expiration_date:
                expiry = datetime.fromisoformat(batch.expiration_date)
                days_until_expiry = (expiry - threshold_date).days
                if 0 <= days_until_expiry <= days_threshold:
                    expiring.append(batch)

        return expiring

    def get_expired_batches(self) -> List[Batch]:
        """Get batches that have already expired."""
        if not self.requires_batch_tracking:
            return []

        current_date = datetime.now()
        return [
            batch for batch in self.batches.values()
            if batch.expiration_date and datetime.fromisoformat(batch.expiration_date) < current_date
        ]

    def _update_total_quantity(self) -> None:
        """Update the total quantity based on batch quantities."""
        if self.requires_batch_tracking:
            self.quantity = sum(batch.quantity for batch in self.batches.values())

    def to_dict(self) -> dict:
        """Convert the product to a dictionary for serialization."""
        return {
            "product_id": self.product_id,
            "name": self.name,
            "category": self.category,
            "quantity": self.quantity,
            "price": self.price,
            "description": self.description,
            "requires_batch_tracking": self.requires_batch_tracking,
            "min_quantity": self.min_quantity,
            "reorder_point": self.reorder_point,
            "preferred_supplier_id": self.preferred_supplier_id,
            "batches": {bid: vars(batch) for bid, batch in self.batches.items()},
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @staticmethod
    def from_dict(data: dict):
        """Create a Product instance from a dictionary, allowing missing fields."""
        product = Product(
            product_id=data.get("product_id"),
            name=data.get("name", ""),
            category=data.get("category", ""),
            quantity=int(data.get("quantity", 0)),
            price=float(data.get("price", 0.0)),
            description=data.get("description", ""),
            requires_batch_tracking=data.get("requires_batch_tracking", False),
            min_quantity=int(data.get("min_quantity", 0)),
            reorder_point=int(data.get("reorder_point", 0)),
            preferred_supplier_id=data.get("preferred_supplier_id", "")
        )
        
        # Restore batches if present
        batches_data = data.get("batches", {})
        for batch_data in batches_data.values():
            product.batches[batch_data["batch_id"]] = Batch(**batch_data)
        
        # Restore timestamps
        product.created_at = data.get("created_at", product.created_at)
        product.updated_at = data.get("updated_at", product.updated_at)
        
        return product 