"""
Unified Inventory Management System

This module provides a centralized inventory management system that can handle
both Point of Sale (POS) products and general inventory items. It supports
different data structures for different types of inventory while maintaining
a consistent interface.

Features:
- Support for POS products (with price, stock, ID)
- Support for general inventory items (with quantity, category)
- JSON-based data storage
- Automatic data validation
- Search and filtering capabilities
- Export/import functionality
"""

import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, asdict
from enum import Enum

class InventoryType(Enum):
    """Types of inventory items supported by the system."""
    POS_PRODUCT = "pos_product"
    GENERAL_ITEM = "general_item"

@dataclass
class POSProduct:
    """Data structure for Point of Sale products."""
    id: str
    name: str
    price: float
    stock: int
    category: str = "General"
    description: str = ""
    created_at: str = ""
    updated_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = datetime.now().isoformat()

@dataclass
class GeneralItem:
    """Data structure for general inventory items."""
    id: str
    name: str
    quantity: int
    category: str
    description: str = ""
    unit: str = "pcs"
    min_quantity: int = 0
    location: str = ""
    created_at: str = ""
    updated_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = datetime.now().isoformat()

class InventoryManager:
    """
    Centralized inventory management system that handles both POS products
    and general inventory items.
    """
    
    def __init__(self, data_file: str = "unified_inventory.json"):
        """
        Initialize the inventory manager.
        
        Args:
            data_file: Path to the JSON file for storing inventory data
        """
        self.data_file = data_file
        self.pos_products: Dict[str, POSProduct] = {}
        self.general_items: Dict[str, GeneralItem] = {}
        self.load_data()
    
    def load_data(self) -> None:
        """Load inventory data from the JSON file."""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # Load POS products
                pos_data = data.get('pos_products', {})
                for product_id, product_data in pos_data.items():
                    self.pos_products[product_id] = POSProduct(**product_data)
                
                # Load general items
                general_data = data.get('general_items', {})
                for item_id, item_data in general_data.items():
                    self.general_items[item_id] = GeneralItem(**item_data)
                    
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            print(f"Error loading inventory data: {e}")
            # Initialize with empty data if file is corrupted
            self.pos_products = {}
            self.general_items = {}
    
    def save_data(self) -> bool:
        """Save inventory data to the JSON file."""
        try:
            data = {
                'pos_products': {pid: asdict(product) for pid, product in self.pos_products.items()},
                'general_items': {iid: asdict(item) for iid, item in self.general_items.items()},
                'last_updated': datetime.now().isoformat(),
                'version': '1.0'
            }
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return True
            
        except Exception as e:
            print(f"Error saving inventory data: {e}")
            return False
    
    # POS Product Methods
    def add_pos_product(self, name: str, price: float, stock: int, 
                       category: str = "General", description: str = "") -> str:
        """
        Add a new POS product to the inventory.
        
        Args:
            name: Product name
            price: Product price
            stock: Initial stock quantity
            category: Product category
            description: Product description
            
        Returns:
            Product ID
        """
        product_id = f"prod_{uuid.uuid4().hex[:8]}"
        product = POSProduct(
            id=product_id,
            name=name,
            price=price,
            stock=stock,
            category=category,
            description=description
        )
        self.pos_products[product_id] = product
        self.save_data()
        return product_id
    
    def update_pos_product(self, product_id: str, **kwargs) -> bool:
        """
        Update an existing POS product.
        
        Args:
            product_id: ID of the product to update
            **kwargs: Fields to update
            
        Returns:
            True if successful, False otherwise
        """
        if product_id not in self.pos_products:
            return False
        
        product = self.pos_products[product_id]
        for key, value in kwargs.items():
            if hasattr(product, key):
                setattr(product, key, value)
        
        product.updated_at = datetime.now().isoformat()
        self.save_data()
        return True
    
    def get_pos_product(self, product_id: str) -> Optional[POSProduct]:
        """Get a POS product by ID."""
        return self.pos_products.get(product_id)
    
    def get_all_pos_products(self) -> List[POSProduct]:
        """Get all POS products."""
        return list(self.pos_products.values())
    
    def delete_pos_product(self, product_id: str) -> bool:
        """Delete a POS product."""
        if product_id in self.pos_products:
            del self.pos_products[product_id]
            self.save_data()
            return True
        return False
    
    def update_pos_stock(self, product_id: str, quantity_change: int) -> bool:
        """
        Update stock quantity for a POS product.
        
        Args:
            product_id: Product ID
            quantity_change: Change in quantity (positive for addition, negative for reduction)
            
        Returns:
            True if successful, False otherwise
        """
        if product_id not in self.pos_products:
            return False
        
        product = self.pos_products[product_id]
        new_stock = product.stock + quantity_change
        if new_stock < 0:
            return False
        
        product.stock = new_stock
        product.updated_at = datetime.now().isoformat()
        self.save_data()
        return True
    
    # General Item Methods
    def add_general_item(self, name: str, quantity: int, category: str,
                        description: str = "", unit: str = "pcs", 
                        min_quantity: int = 0, location: str = "") -> str:
        """
        Add a new general inventory item.
        
        Args:
            name: Item name
            quantity: Initial quantity
            category: Item category
            description: Item description
            unit: Unit of measurement
            min_quantity: Minimum quantity threshold
            location: Storage location
            
        Returns:
            Item ID
        """
        item_id = f"item_{uuid.uuid4().hex[:8]}"
        item = GeneralItem(
            id=item_id,
            name=name,
            quantity=quantity,
            category=category,
            description=description,
            unit=unit,
            min_quantity=min_quantity,
            location=location
        )
        self.general_items[item_id] = item
        self.save_data()
        return item_id
    
    def update_general_item(self, item_id: str, **kwargs) -> bool:
        """
        Update an existing general inventory item.
        
        Args:
            item_id: ID of the item to update
            **kwargs: Fields to update
            
        Returns:
            True if successful, False otherwise
        """
        if item_id not in self.general_items:
            return False
        
        item = self.general_items[item_id]
        for key, value in kwargs.items():
            if hasattr(item, key):
                setattr(item, key, value)
        
        item.updated_at = datetime.now().isoformat()
        self.save_data()
        return True
    
    def get_general_item(self, item_id: str) -> Optional[GeneralItem]:
        """Get a general item by ID."""
        return self.general_items.get(item_id)
    
    def get_all_general_items(self) -> List[GeneralItem]:
        """Get all general inventory items."""
        return list(self.general_items.values())
    
    def delete_general_item(self, item_id: str) -> bool:
        """Delete a general inventory item."""
        if item_id in self.general_items:
            del self.general_items[item_id]
            self.save_data()
            return True
        return False
    
    def update_general_quantity(self, item_id: str, quantity_change: int) -> bool:
        """
        Update quantity for a general inventory item.
        
        Args:
            item_id: Item ID
            quantity_change: Change in quantity
            
        Returns:
            True if successful, False otherwise
        """
        if item_id not in self.general_items:
            return False
        
        item = self.general_items[item_id]
        new_quantity = item.quantity + quantity_change
        if new_quantity < 0:
            return False
        
        item.quantity = new_quantity
        item.updated_at = datetime.now().isoformat()
        self.save_data()
        return True
    
    # Search and Filter Methods
    def search_pos_products(self, query: str, field: str = "name") -> List[POSProduct]:
        """
        Search POS products by field.
        
        Args:
            query: Search query
            field: Field to search in (name, category, description)
            
        Returns:
            List of matching products
        """
        query = query.lower()
        results = []
        
        for product in self.pos_products.values():
            if hasattr(product, field):
                field_value = getattr(product, field, "").lower()
                if query in field_value:
                    results.append(product)
        
        return results
    
    def search_general_items(self, query: str, field: str = "name") -> List[GeneralItem]:
        """
        Search general items by field.
        
        Args:
            query: Search query
            field: Field to search in (name, category, description, location)
            
        Returns:
            List of matching items
        """
        query = query.lower()
        results = []
        
        for item in self.general_items.values():
            if hasattr(item, field):
                field_value = getattr(item, field, "").lower()
                if query in field_value:
                    results.append(item)
        
        return results
    
    def filter_by_category(self, category: str, inventory_type: InventoryType) -> List[Union[POSProduct, GeneralItem]]:
        """
        Filter items by category.
        
        Args:
            category: Category to filter by
            inventory_type: Type of inventory to filter
            
        Returns:
            List of items in the specified category
        """
        if inventory_type == InventoryType.POS_PRODUCT:
            return [p for p in self.pos_products.values() if p.category.lower() == category.lower()]
        else:
            return [i for i in self.general_items.values() if i.category.lower() == category.lower()]
    
    def get_low_stock_items(self, threshold: int = 5) -> Dict[str, List]:
        """
        Get items with low stock.
        
        Args:
            threshold: Stock threshold for low stock alert
            
        Returns:
            Dictionary with low stock POS products and general items
        """
        low_stock_pos = [p for p in self.pos_products.values() if p.stock <= threshold]
        low_stock_general = [i for i in self.general_items.values() if i.quantity <= i.min_quantity]
        
        return {
            'pos_products': low_stock_pos,
            'general_items': low_stock_general
        }
    
    # Import/Export Methods
    def export_to_json(self, filepath: str) -> bool:
        """Export all inventory data to a JSON file."""
        try:
            data = {
                'pos_products': {pid: asdict(product) for pid, product in self.pos_products.items()},
                'general_items': {iid: asdict(item) for iid, item in self.general_items.items()},
                'export_date': datetime.now().isoformat(),
                'version': '1.0'
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return True
            
        except Exception as e:
            print(f"Error exporting data: {e}")
            return False
    
    def import_from_json(self, filepath: str, merge: bool = True) -> bool:
        """
        Import inventory data from a JSON file.
        
        Args:
            filepath: Path to the JSON file
            merge: If True, merge with existing data. If False, replace all data.
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not merge:
                self.pos_products.clear()
                self.general_items.clear()
            
            # Import POS products
            pos_data = data.get('pos_products', {})
            for product_id, product_data in pos_data.items():
                self.pos_products[product_id] = POSProduct(**product_data)
            
            # Import general items
            general_data = data.get('general_items', {})
            for item_id, item_data in general_data.items():
                self.general_items[item_id] = GeneralItem(**item_data)
            
            self.save_data()
            return True
            
        except Exception as e:
            print(f"Error importing data: {e}")
            return False
    
    # Statistics and Reports
    def get_inventory_stats(self) -> Dict[str, Any]:
        """Get comprehensive inventory statistics."""
        total_pos_products = len(self.pos_products)
        total_general_items = len(self.general_items)
        
        total_pos_value = sum(p.price * p.stock for p in self.pos_products.values())
        total_pos_stock = sum(p.stock for p in self.pos_products.values())
        total_general_quantity = sum(i.quantity for i in self.general_items.values())
        
        pos_categories = set(p.category for p in self.pos_products.values())
        general_categories = set(i.category for i in self.general_items.values())
        
        low_stock = self.get_low_stock_items()
        
        return {
            'total_pos_products': total_pos_products,
            'total_general_items': total_general_items,
            'total_pos_value': total_pos_value,
            'total_pos_stock': total_pos_stock,
            'total_general_quantity': total_general_quantity,
            'pos_categories': len(pos_categories),
            'general_categories': len(general_categories),
            'low_stock_pos': len(low_stock['pos_products']),
            'low_stock_general': len(low_stock['general_items']),
            'last_updated': datetime.now().isoformat()
        }
    
    def migrate_from_old_format(self, pos_file: str, general_file: str) -> bool:
        """
        Migrate data from old format files to the unified format.
        
        Args:
            pos_file: Path to old POS products file
            general_file: Path to old general inventory file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Migrate POS products from pipe-delimited format
            if os.path.exists(pos_file):
                with open(pos_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and '|' in line:
                            parts = line.split('|')
                            if len(parts) >= 4:
                                product_id, name, price, stock = parts[:4]
                                try:
                                    self.add_pos_product(
                                        name=name,
                                        price=float(price),
                                        stock=int(stock),
                                        category="General"
                                    )
                                except (ValueError, TypeError):
                                    continue
            
            # Migrate general items from JSON format
            if os.path.exists(general_file):
                with open(general_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item_data in data:
                        try:
                            self.add_general_item(
                                name=item_data['name'],
                                quantity=item_data['quantity'],
                                category=item_data['category']
                            )
                        except (KeyError, TypeError):
                            continue
            
            return True
            
        except Exception as e:
            print(f"Error migrating data: {e}")
            return False 