import json
import csv
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from src.models import Product
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import numpy as np
from collections import defaultdict

class InventoryManager:
    """
    Manages inventory operations: add, edit, delete, search, save/load, and export.
    Includes advanced analytics and alert systems.
    """
    def __init__(self, email_config: Dict[str, str] = None):
        self.products: List[Product] = []
        self.email_config = email_config or {}
        self.alert_thresholds = {
            'low_stock': 10,
            'critical_stock': 5,
            'reorder_point': 15
        }
        self.sales_history: List[Dict[str, Any]] = []

    def add_product(self, product: Product) -> None:
        """Add a product to inventory. Product must include description."""
        self.products.append(product)

    def edit_product(self, product_id: str, **kwargs) -> bool:
        """Edit a product by ID. Supports updating description."""
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

    def get_all_products(self) -> List[Product]:
        return self.products

    def load_from_csv(self, filepath: str) -> bool:
        try:
            import csv
            if not os.path.exists(filepath):
                return False
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                self.products = []
                for row in reader:
                    self.products.append(Product(
                        product_id=row.get('product_id', ''),
                        name=row.get('name', ''),
                        category=row.get('category', ''),
                        quantity=int(row.get('quantity', 0)),
                        price=float(row.get('price', 0.0)),
                        description=row.get('description', '')
                    ))
            return True
        except Exception as e:
            print(f"Error loading from CSV: {e}")
            return False

    def load_from_yaml(self, filepath: str) -> bool:
        try:
            import yaml
            if not os.path.exists(filepath):
                return False
            with open(filepath, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                self.products = [Product.from_dict(item) for item in data]
            return True
        except Exception as e:
            print(f"Error loading from YAML: {e}")
            return False

    def get_product_by_id(self, product_id: str):
        for product in self.products:
            if product.product_id == product_id:
                return product
        return None

    def configure_alerts(self, thresholds: Dict[str, int]) -> None:
        """Configure alert thresholds for inventory levels."""
        self.alert_thresholds.update(thresholds)

    def check_inventory_alerts(self) -> List[Dict[str, Any]]:
        """Check for products that need attention based on configured thresholds."""
        alerts = []
        for product in self.products:
            if product.quantity <= self.alert_thresholds['critical_stock']:
                alerts.append({
                    'product_id': product.product_id,
                    'name': product.name,
                    'current_stock': product.quantity,
                    'level': 'CRITICAL',
                    'message': f'Critical stock level: Only {product.quantity} units remaining'
                })
            elif product.quantity <= self.alert_thresholds['low_stock']:
                alerts.append({
                    'product_id': product.product_id,
                    'name': product.name,
                    'current_stock': product.quantity,
                    'level': 'LOW',
                    'message': f'Low stock level: {product.quantity} units remaining'
                })
            elif product.quantity <= self.alert_thresholds['reorder_point']:
                alerts.append({
                    'product_id': product.product_id,
                    'name': product.name,
                    'current_stock': product.quantity,
                    'level': 'REORDER',
                    'message': f'Reorder point reached: {product.quantity} units remaining'
                })
        return alerts

    def send_alert_emails(self, alerts: List[Dict[str, Any]]) -> bool:
        """Send email alerts for critical inventory levels."""
        if not self.email_config:
            return False

        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_config['from']
            msg['To'] = self.email_config['to']
            msg['Subject'] = 'Inventory Alert Report'

            body = "Inventory Alert Report\n\n"
            for alert in alerts:
                body += f"{alert['level']}: {alert['name']} - {alert['message']}\n"

            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['username'], self.email_config['password'])
            server.send_message(msg)
            server.quit()
            return True
        except Exception as e:
            print(f"Error sending alert email: {e}")
            return False

    def record_sale(self, product_id: str, quantity: int, sale_price: float) -> bool:
        """Record a sale for analytics purposes."""
        product = self.get_product_by_id(product_id)
        if not product or product.quantity < quantity:
            return False

        sale_record = {
            'product_id': product_id,
            'quantity': quantity,
            'sale_price': sale_price,
            'total': quantity * sale_price,
            'timestamp': datetime.now().isoformat()
        }
        self.sales_history.append(sale_record)
        product.quantity -= quantity
        return True

    def analyze_inventory_turnover(self, days: int = 30) -> Dict[str, Any]:
        """Calculate inventory turnover metrics for the specified period."""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Group sales by product
        product_sales = defaultdict(lambda: {'quantity': 0, 'revenue': 0})
        for sale in self.sales_history:
            sale_date = datetime.fromisoformat(sale['timestamp'])
            if sale_date >= cutoff_date:
                prod_id = sale['product_id']
                product_sales[prod_id]['quantity'] += sale['quantity']
                product_sales[prod_id]['revenue'] += sale['total']

        # Calculate metrics
        turnover_metrics = []
        for product in self.products:
            sales_data = product_sales[product.product_id]
            metrics = {
                'product_id': product.product_id,
                'name': product.name,
                'current_stock': product.quantity,
                'units_sold': sales_data['quantity'],
                'revenue': sales_data['revenue'],
                'turnover_rate': sales_data['quantity'] / (product.quantity + 0.1),  # Avoid division by zero
                'days_to_stockout': product.quantity / (sales_data['quantity'] / days + 0.1)
            }
            turnover_metrics.append(metrics)

        return {
            'period_days': days,
            'metrics': turnover_metrics,
            'total_revenue': sum(m['revenue'] for m in turnover_metrics),
            'total_units_sold': sum(m['units_sold'] for m in turnover_metrics)
        }

    def identify_dead_stock(self, days_threshold: int = 90) -> List[Dict[str, Any]]:
        """Identify products with no sales in the specified period."""
        cutoff_date = datetime.now() - timedelta(days=days_threshold)
        
        # Get products with sales
        active_products = set()
        for sale in self.sales_history:
            sale_date = datetime.fromisoformat(sale['timestamp'])
            if sale_date >= cutoff_date:
                active_products.add(sale['product_id'])

        # Find dead stock
        dead_stock = []
        for product in self.products:
            if product.product_id not in active_products and product.quantity > 0:
                dead_stock.append({
                    'product_id': product.product_id,
                    'name': product.name,
                    'quantity': product.quantity,
                    'value': product.quantity * product.price,
                    'days_inactive': days_threshold
                })

        return dead_stock

    def predict_stock_needs(self, days_forecast: int = 30) -> List[Dict[str, Any]]:
        """Predict future stock needs based on historical sales data."""
        # Calculate daily sales rates
        product_daily_sales = defaultdict(list)
        
        # Group sales by day for each product
        for sale in self.sales_history:
            sale_date = datetime.fromisoformat(sale['timestamp']).date()
            product_daily_sales[sale['product_id']].append({
                'date': sale_date,
                'quantity': sale['quantity']
            })

        predictions = []
        for product in self.products:
            daily_sales = product_daily_sales[product.product_id]
            
            if daily_sales:
                # Calculate average daily sales
                total_sales = sum(sale['quantity'] for sale in daily_sales)
                unique_days = len(set(sale['date'] for sale in daily_sales))
                avg_daily_sales = total_sales / max(unique_days, 1)
                
                # Calculate standard deviation for confidence interval
                daily_quantities = [sale['quantity'] for sale in daily_sales]
                std_dev = np.std(daily_quantities) if len(daily_quantities) > 1 else 0
                
                # Predict future needs
                predicted_need = avg_daily_sales * days_forecast
                safety_stock = std_dev * 2  # 95% confidence interval
                
                predictions.append({
                    'product_id': product.product_id,
                    'name': product.name,
                    'current_stock': product.quantity,
                    'predicted_need': predicted_need,
                    'safety_stock': safety_stock,
                    'recommended_order': max(0, predicted_need + safety_stock - product.quantity),
                    'confidence': 'HIGH' if len(daily_sales) >= 30 else 'MEDIUM' if len(daily_sales) >= 14 else 'LOW'
                })
            else:
                predictions.append({
                    'product_id': product.product_id,
                    'name': product.name,
                    'current_stock': product.quantity,
                    'predicted_need': 0,
                    'safety_stock': 0,
                    'recommended_order': 0,
                    'confidence': 'NO_DATA'
                })

        return predictions 