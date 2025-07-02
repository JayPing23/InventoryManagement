"""
Supplier Management System

This module provides comprehensive supplier management capabilities including:
- Supplier information tracking
- Purchase order management
- Supplier performance metrics
- Order history tracking
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict
import json
import os
from pathlib import Path

@dataclass
class Supplier:
    """Data structure for supplier information."""
    id: str
    name: str
    contact_person: str
    email: str
    phone: str
    address: str
    payment_terms: str = "30 days"
    rating: float = 5.0
    active: bool = True
    notes: str = ""
    created_at: str = ""
    updated_at: str = ""

@dataclass
class PurchaseOrder:
    """Data structure for purchase orders."""
    id: str
    supplier_id: str
    order_date: str
    expected_delivery: str
    items: List[Dict[str, Any]]
    status: str = "pending"  # pending, confirmed, shipped, delivered, cancelled
    total_amount: float = 0.0
    payment_status: str = "unpaid"  # unpaid, partial, paid
    notes: str = ""
    created_at: str = ""
    updated_at: str = ""

class SupplierManager:
    """Manages supplier relationships and purchase orders."""
    
    def __init__(self, data_path: str = "data"):
        """Initialize the supplier manager."""
        self.data_path = Path(data_path)
        self.data_path.mkdir(exist_ok=True)
        self.suppliers: Dict[str, Supplier] = {}
        self.purchase_orders: Dict[str, PurchaseOrder] = {}
        self.load_data()
    
    def load_data(self) -> None:
        """Load supplier and purchase order data from storage."""
        try:
            # Load suppliers
            supplier_file = self.data_path / "suppliers.json"
            if supplier_file.exists():
                with open(supplier_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for sup_id, sup_data in data.items():
                        self.suppliers[sup_id] = Supplier(**sup_data)
            
            # Load purchase orders
            po_file = self.data_path / "purchase_orders.json"
            if po_file.exists():
                with open(po_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for po_id, po_data in data.items():
                        self.purchase_orders[po_id] = PurchaseOrder(**po_data)
        
        except Exception as e:
            print(f"Error loading supplier data: {e}")
    
    def save_data(self) -> None:
        """Save supplier and purchase order data to storage."""
        try:
            # Save suppliers
            supplier_data = {sid: asdict(sup) for sid, sup in self.suppliers.items()}
            with open(self.data_path / "suppliers.json", 'w', encoding='utf-8') as f:
                json.dump(supplier_data, f, indent=2)
            
            # Save purchase orders
            po_data = {pid: asdict(po) for pid, po in self.purchase_orders.items()}
            with open(self.data_path / "purchase_orders.json", 'w', encoding='utf-8') as f:
                json.dump(po_data, f, indent=2)
        
        except Exception as e:
            print(f"Error saving supplier data: {e}")
    
    def add_supplier(self, name: str, contact_person: str, email: str, phone: str,
                    address: str, payment_terms: str = "30 days") -> str:
        """Add a new supplier."""
        supplier_id = f"SUP{len(self.suppliers) + 1:04d}"
        now = datetime.now().isoformat()
        
        supplier = Supplier(
            id=supplier_id,
            name=name,
            contact_person=contact_person,
            email=email,
            phone=phone,
            address=address,
            payment_terms=payment_terms,
            created_at=now,
            updated_at=now
        )
        
        self.suppliers[supplier_id] = supplier
        self.save_data()
        return supplier_id
    
    def update_supplier(self, supplier_id: str, **kwargs) -> bool:
        """Update supplier information."""
        if supplier_id not in self.suppliers:
            return False
        
        supplier = self.suppliers[supplier_id]
        for key, value in kwargs.items():
            if hasattr(supplier, key):
                setattr(supplier, key, value)
        
        supplier.updated_at = datetime.now().isoformat()
        self.save_data()
        return True
    
    def create_purchase_order(self, supplier_id: str, items: List[Dict[str, Any]],
                            expected_delivery: str) -> str:
        """Create a new purchase order."""
        if supplier_id not in self.suppliers:
            raise ValueError("Invalid supplier ID")
        
        po_id = f"PO{len(self.purchase_orders) + 1:06d}"
        now = datetime.now().isoformat()
        
        # Calculate total amount
        total_amount = sum(item.get('quantity', 0) * item.get('unit_price', 0) for item in items)
        
        po = PurchaseOrder(
            id=po_id,
            supplier_id=supplier_id,
            order_date=now,
            expected_delivery=expected_delivery,
            items=items,
            total_amount=total_amount,
            created_at=now,
            updated_at=now
        )
        
        self.purchase_orders[po_id] = po
        self.save_data()
        return po_id
    
    def update_po_status(self, po_id: str, status: str, notes: str = "") -> bool:
        """Update purchase order status."""
        if po_id not in self.purchase_orders:
            return False
        
        valid_statuses = {'pending', 'confirmed', 'shipped', 'delivered', 'cancelled'}
        if status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")
        
        po = self.purchase_orders[po_id]
        po.status = status
        if notes:
            po.notes = notes
        po.updated_at = datetime.now().isoformat()
        
        self.save_data()
        return True
    
    def get_supplier_performance(self, supplier_id: str) -> Dict[str, Any]:
        """Calculate supplier performance metrics."""
        if supplier_id not in self.suppliers:
            raise ValueError("Invalid supplier ID")
        
        # Get all POs for this supplier
        supplier_pos = [po for po in self.purchase_orders.values() if po.supplier_id == supplier_id]
        
        total_orders = len(supplier_pos)
        if total_orders == 0:
            return {
                'supplier_id': supplier_id,
                'total_orders': 0,
                'total_value': 0,
                'on_time_delivery_rate': 0,
                'average_delay_days': 0,
                'cancelled_orders': 0
            }
        
        # Calculate metrics
        total_value = sum(po.total_amount for po in supplier_pos)
        cancelled = sum(1 for po in supplier_pos if po.status == 'cancelled')
        
        # Calculate delivery performance
        delivered_pos = [po for po in supplier_pos if po.status == 'delivered']
        on_time = 0
        total_delay_days = 0
        
        for po in delivered_pos:
            expected = datetime.fromisoformat(po.expected_delivery)
            actual = datetime.fromisoformat(po.updated_at)
            delay_days = (actual - expected).days
            
            if delay_days <= 0:
                on_time += 1
            else:
                total_delay_days += delay_days
        
        delivered_count = len(delivered_pos)
        on_time_rate = (on_time / delivered_count * 100) if delivered_count > 0 else 0
        avg_delay = (total_delay_days / delivered_count) if delivered_count > 0 else 0
        
        return {
            'supplier_id': supplier_id,
            'total_orders': total_orders,
            'total_value': total_value,
            'on_time_delivery_rate': on_time_rate,
            'average_delay_days': avg_delay,
            'cancelled_orders': cancelled
        }
    
    def get_pending_orders(self) -> List[PurchaseOrder]:
        """Get all pending purchase orders."""
        return [po for po in self.purchase_orders.values() if po.status == 'pending']
    
    def get_supplier_order_history(self, supplier_id: str) -> List[PurchaseOrder]:
        """Get order history for a specific supplier."""
        return [po for po in self.purchase_orders.values() if po.supplier_id == supplier_id]
    
    def search_suppliers(self, query: str) -> List[Supplier]:
        """Search suppliers by name or contact person."""
        query = query.lower()
        return [
            supplier for supplier in self.suppliers.values()
            if query in supplier.name.lower() or query in supplier.contact_person.lower()
        ] 