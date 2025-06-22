import json
import csv
from typing import List, Optional
from ..models import Product
import os

class InventoryManager:
    """
    Manages inventory operations: add, edit, delete, search, save/load, and export.
    """
    def __init__(self):
        self.products: List[Product] = []

    def add_product(self, product: Product) -> None:
        self.products.append(product)

    def edit_product(self, product_id: str, **kwargs) -> bool:
        for product in self.products:
            if product.product_id == product_id:
                for key, value in kwargs.items():
                    if hasattr(product, key):
                        setattr(product, key, value)
                return True
        return False

    def delete_product(self, product_id: str) -> bool:
        for i, product in enumerate(self.products):
            if product.product_id == product_id:
                del self.products[i]
                return True
        return False

    def search_products(self, query: str) -> List[Product]:
        query = query.lower()
        return [p for p in self.products if query in p.name.lower() or query in p.category.lower()]

    def save_to_json(self, filepath: str) -> bool:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump([p.to_dict() for p in self.products], f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving to JSON: {e}")
            return False

    def load_from_json(self, filepath: str) -> bool:
        try:
            if not os.path.exists(filepath):
                return False
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.products = [Product.from_dict(item) for item in data]
            return True
        except Exception as e:
            print(f"Error loading from JSON: {e}")
            return False

    def save_to_txt(self, filepath: str) -> bool:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                for p in self.products:
                    line = f"{p.product_id}|{p.name}|{p.category}|{p.quantity}|{p.price}|{p.description}\n"
                    f.write(line)
            return True
        except Exception as e:
            print(f"Error saving to TXT: {e}")
            return False

    def load_from_txt(self, filepath: str) -> bool:
        try:
            if not os.path.exists(filepath):
                return False
            with open(filepath, 'r', encoding='utf-8') as f:
                self.products = []
                for line in f:
                    parts = line.strip().split('|')
                    if len(parts) >= 6:
                        self.products.append(Product(
                            product_id=parts[0],
                            name=parts[1],
                            category=parts[2],
                            quantity=int(parts[3]),
                            price=float(parts[4]),
                            description=parts[5]
                        ))
            return True
        except Exception as e:
            print(f"Error loading from TXT: {e}")
            return False

    def export_to_csv(self, filepath: str) -> bool:
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Product ID", "Name", "Category", "Quantity", "Price", "Description"])
                for p in self.products:
                    writer.writerow([p.product_id, p.name, p.category, p.quantity, p.price, p.description])
            return True
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False 