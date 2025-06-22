"""
Sales Analytics and Business Intelligence System

This module provides comprehensive sales analytics, reporting, and visualization
capabilities for the POS and inventory management system. It includes:

Features:
- Sales history tracking and analysis
- Product performance analytics
- Revenue and profit analysis
- Customer behavior insights
- Visual charts and graphs
- Export capabilities for reports
- Real-time dashboard data
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
import tkinter as tk
from tkinter import ttk, messagebox
import calendar
from dataclasses import dataclass
from pathlib import Path

# Set style for better-looking charts
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

@dataclass
class SalesRecord:
    """Data structure for sales records."""
    id: str
    timestamp: datetime
    items: List[Dict[str, Any]]
    subtotal: float
    tax: float
    total: float
    tendered: float
    change: float
    payment_method: str = "cash"
    customer_id: str = ""
    salesperson_id: str = ""

class SalesAnalytics:
    """
    Comprehensive sales analytics and reporting system.
    """
    
    def __init__(self, data_path: str = "sales_history"):
        """
        Initialize the sales analytics system.
        
        Args:
            data_path: Path to sales history data
        """
        self.data_path = Path(data_path)
        self.data_path.mkdir(exist_ok=True)
        self.sales_records: List[SalesRecord] = []
        self.load_sales_data()
    
    def load_sales_data(self):
        """Load sales data from storage."""
        try:
            sales_file = self.data_path / "sales_history.json"
            if sales_file.exists():
                with open(sales_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.sales_records = []
                for record_data in data.get('sales', []):
                    # Convert timestamp string back to datetime
                    record_data['timestamp'] = datetime.fromisoformat(record_data['timestamp'])
                    self.sales_records.append(SalesRecord(**record_data))
        except Exception as e:
            print(f"Error loading sales data: {e}")
            self.sales_records = []
    
    def save_sales_data(self):
        """Save sales data to storage."""
        try:
            sales_file = self.data_path / "sales_history.json"
            data = {
                'sales': [
                    {
                        'id': record.id,
                        'timestamp': record.timestamp.isoformat(),
                        'items': record.items,
                        'subtotal': record.subtotal,
                        'tax': record.tax,
                        'total': record.total,
                        'tendered': record.tendered,
                        'change': record.change,
                        'payment_method': record.payment_method,
                        'customer_id': record.customer_id,
                        'salesperson_id': record.salesperson_id
                    }
                    for record in self.sales_records
                ],
                'last_updated': datetime.now().isoformat()
            }
            
            with open(sales_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving sales data: {e}")
    
    def add_sale(self, sale_record: SalesRecord):
        """Add a new sale record."""
        self.sales_records.append(sale_record)
        self.save_sales_data()
    
    def get_sales_summary(self, start_date: datetime = None, end_date: datetime = None) -> Dict[str, Any]:
        """
        Get comprehensive sales summary for a date range.
        
        Args:
            start_date: Start date for analysis
            end_date: End date for analysis
            
        Returns:
            Dictionary with sales summary statistics
        """
        if start_date is None:
            start_date = datetime.now() - timedelta(days=30)
        if end_date is None:
            end_date = datetime.now()
        
        # Filter sales by date range
        filtered_sales = [
            sale for sale in self.sales_records
            if start_date <= sale.timestamp <= end_date
        ]
        
        if not filtered_sales:
            return {
                'total_sales': 0,
                'total_revenue': 0.0,
                'total_tax': 0.0,
                'average_sale': 0.0,
                'total_transactions': 0,
                'date_range': f"{start_date.date()} to {end_date.date()}"
            }
        
        total_revenue = sum(sale.total for sale in filtered_sales)
        total_tax = sum(sale.tax for sale in filtered_sales)
        total_transactions = len(filtered_sales)
        average_sale = total_revenue / total_transactions
        
        return {
            'total_sales': total_revenue,
            'total_revenue': total_revenue,
            'total_tax': total_tax,
            'average_sale': average_sale,
            'total_transactions': total_transactions,
            'date_range': f"{start_date.date()} to {end_date.date()}"
        }
    
    def get_product_performance(self, start_date: datetime = None, end_date: datetime = None) -> Dict[str, Any]:
        """
        Analyze product performance and sales.
        
        Args:
            start_date: Start date for analysis
            end_date: End date for analysis
            
        Returns:
            Dictionary with product performance data
        """
        if start_date is None:
            start_date = datetime.now() - timedelta(days=30)
        if end_date is None:
            end_date = datetime.now()
        
        # Filter sales by date range
        filtered_sales = [
            sale for sale in self.sales_records
            if start_date <= sale.timestamp <= end_date
        ]
        
        # Collect product data
        product_stats = defaultdict(lambda: {
            'quantity_sold': 0,
            'revenue': 0.0,
            'transactions': 0
        })
        
        for sale in filtered_sales:
            for item in sale.items:
                product_id = item.get('id', 'unknown')
                product_name = item.get('name', 'Unknown Product')
                quantity = item.get('quantity', 0)
                price = item.get('price', 0.0)
                
                product_stats[product_name]['quantity_sold'] += quantity
                product_stats[product_name]['revenue'] += quantity * price
                product_stats[product_name]['transactions'] += 1
        
        # Convert to list and sort by revenue
        product_list = [
            {
                'name': name,
                'quantity_sold': stats['quantity_sold'],
                'revenue': stats['revenue'],
                'transactions': stats['transactions'],
                'average_price': stats['revenue'] / stats['quantity_sold'] if stats['quantity_sold'] > 0 else 0
            }
            for name, stats in product_stats.items()
        ]
        
        product_list.sort(key=lambda x: x['revenue'], reverse=True)
        
        return {
            'products': product_list,
            'top_sellers': product_list[:10],
            'worst_sellers': product_list[-10:],
            'total_products': len(product_list)
        }
    
    def get_daily_sales_trend(self, days: int = 30) -> Dict[str, Any]:
        """
        Get daily sales trend data.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dictionary with daily sales data
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Create date range
        date_range = []
        current_date = start_date
        while current_date <= end_date:
            date_range.append(current_date.date())
            current_date += timedelta(days=1)
        
        # Group sales by date
        daily_sales = defaultdict(lambda: {
            'revenue': 0.0,
            'transactions': 0,
            'items_sold': 0
        })
        
        for sale in self.sales_records:
            if start_date <= sale.timestamp <= end_date:
                date_key = sale.timestamp.date()
                daily_sales[date_key]['revenue'] += sale.total
                daily_sales[date_key]['transactions'] += 1
                daily_sales[date_key]['items_sold'] += sum(item.get('quantity', 0) for item in sale.items)
        
        # Create complete data for all dates
        trend_data = []
        for date in date_range:
            sales_data = daily_sales[date]
            trend_data.append({
                'date': date,
                'revenue': sales_data['revenue'],
                'transactions': sales_data['transactions'],
                'items_sold': sales_data['items_sold']
            })
        
        return {
            'daily_data': trend_data,
            'total_revenue': sum(day['revenue'] for day in trend_data),
            'total_transactions': sum(day['transactions'] for day in trend_data),
            'average_daily_revenue': sum(day['revenue'] for day in trend_data) / len(trend_data)
        }
    
    def get_hourly_sales_pattern(self, days: int = 7) -> Dict[str, Any]:
        """
        Analyze hourly sales patterns.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dictionary with hourly sales data
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Filter sales by date range
        filtered_sales = [
            sale for sale in self.sales_records
            if start_date <= sale.timestamp <= end_date
        ]
        
        # Group sales by hour
        hourly_sales = defaultdict(lambda: {
            'revenue': 0.0,
            'transactions': 0
        })
        
        for sale in filtered_sales:
            hour = sale.timestamp.hour
            hourly_sales[hour]['revenue'] += sale.total
            hourly_sales[hour]['transactions'] += 1
        
        # Create complete hourly data
        hourly_data = []
        for hour in range(24):
            sales_data = hourly_sales[hour]
            hourly_data.append({
                'hour': hour,
                'revenue': sales_data['revenue'],
                'transactions': sales_data['transactions'],
                'average_transaction': sales_data['revenue'] / sales_data['transactions'] if sales_data['transactions'] > 0 else 0
            })
        
        return {
            'hourly_data': hourly_data,
            'peak_hour': max(hourly_data, key=lambda x: x['revenue']),
            'quiet_hour': min(hourly_data, key=lambda x: x['revenue'])
        }
    
    def get_category_performance(self, start_date: datetime = None, end_date: datetime = None) -> Dict[str, Any]:
        """
        Analyze sales performance by category.
        
        Args:
            start_date: Start date for analysis
            end_date: End date for analysis
            
        Returns:
            Dictionary with category performance data
        """
        if start_date is None:
            start_date = datetime.now() - timedelta(days=30)
        if end_date is None:
            end_date = datetime.now()
        
        # Filter sales by date range
        filtered_sales = [
            sale for sale in self.sales_records
            if start_date <= sale.timestamp <= end_date
        ]
        
        # Collect category data
        category_stats = defaultdict(lambda: {
            'revenue': 0.0,
            'quantity_sold': 0,
            'transactions': 0,
            'products': set()
        })
        
        for sale in filtered_sales:
            for item in sale.items:
                category = item.get('category', 'Uncategorized')
                quantity = item.get('quantity', 0)
                price = item.get('price', 0.0)
                product_name = item.get('name', 'Unknown')
                
                category_stats[category]['revenue'] += quantity * price
                category_stats[category]['quantity_sold'] += quantity
                category_stats[category]['transactions'] += 1
                category_stats[category]['products'].add(product_name)
        
        # Convert to list
        category_list = [
            {
                'category': category,
                'revenue': stats['revenue'],
                'quantity_sold': stats['quantity_sold'],
                'transactions': stats['transactions'],
                'product_count': len(stats['products']),
                'average_transaction': stats['revenue'] / stats['transactions'] if stats['transactions'] > 0 else 0
            }
            for category, stats in category_stats.items()
        ]
        
        category_list.sort(key=lambda x: x['revenue'], reverse=True)
        
        return {
            'categories': category_list,
            'top_category': category_list[0] if category_list else None,
            'total_categories': len(category_list)
        }
    
    def generate_sales_report(self, report_type: str = "comprehensive", 
                            start_date: datetime = None, end_date: datetime = None) -> Dict[str, Any]:
        """
        Generate comprehensive sales report.
        
        Args:
            report_type: Type of report (comprehensive, summary, product, category)
            start_date: Start date for report
            end_date: End date for report
            
        Returns:
            Dictionary with report data
        """
        if start_date is None:
            start_date = datetime.now() - timedelta(days=30)
        if end_date is None:
            end_date = datetime.now()
        
        report = {
            'report_type': report_type,
            'generated_at': datetime.now().isoformat(),
            'date_range': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'summary': self.get_sales_summary(start_date, end_date)
        }
        
        if report_type in ['comprehensive', 'product']:
            report['product_performance'] = self.get_product_performance(start_date, end_date)
        
        if report_type in ['comprehensive', 'category']:
            report['category_performance'] = self.get_category_performance(start_date, end_date)
        
        if report_type == 'comprehensive':
            report['daily_trend'] = self.get_daily_sales_trend((end_date - start_date).days)
            report['hourly_pattern'] = self.get_hourly_sales_pattern((end_date - start_date).days)
        
        return report
    
    def export_report(self, report_data: Dict[str, Any], format: str = "json", filename: str = None) -> bool:
        """
        Export report to various formats.
        
        Args:
            report_data: Report data to export
            format: Export format (json, csv, txt)
            filename: Output filename
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"sales_report_{timestamp}.{format}"
            
            filepath = self.data_path / filename
            
            if format == "json":
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(report_data, f, indent=4, ensure_ascii=False)
            
            elif format == "csv":
                # Flatten the report data for CSV export
                flattened_data = self._flatten_report_data(report_data)
                df = pd.DataFrame(flattened_data)
                df.to_csv(filepath, index=False)
            
            elif format == "txt":
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(self._format_report_as_text(report_data))
            
            return True
            
        except Exception as e:
            print(f"Error exporting report: {e}")
            return False
    
    def _flatten_report_data(self, report_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Flatten report data for CSV export."""
        flattened = []
        
        # Add summary data
        summary = report_data.get('summary', {})
        flattened.append({
            'section': 'summary',
            'metric': 'total_revenue',
            'value': summary.get('total_revenue', 0)
        })
        flattened.append({
            'section': 'summary',
            'metric': 'total_transactions',
            'value': summary.get('total_transactions', 0)
        })
        
        # Add product performance data
        product_perf = report_data.get('product_performance', {})
        for product in product_perf.get('products', []):
            flattened.append({
                'section': 'product_performance',
                'product_name': product['name'],
                'quantity_sold': product['quantity_sold'],
                'revenue': product['revenue'],
                'transactions': product['transactions']
            })
        
        return flattened
    
    def _format_report_as_text(self, report_data: Dict[str, Any]) -> str:
        """Format report data as readable text."""
        text = []
        text.append("=" * 60)
        text.append("SALES ANALYTICS REPORT")
        text.append("=" * 60)
        text.append(f"Generated: {report_data.get('generated_at', 'Unknown')}")
        text.append(f"Date Range: {report_data.get('date_range', {}).get('start', 'Unknown')} to {report_data.get('date_range', {}).get('end', 'Unknown')}")
        text.append("")
        
        # Summary
        summary = report_data.get('summary', {})
        text.append("SUMMARY")
        text.append("-" * 20)
        text.append(f"Total Revenue: ${summary.get('total_revenue', 0):.2f}")
        text.append(f"Total Transactions: {summary.get('total_transactions', 0)}")
        text.append(f"Average Sale: ${summary.get('average_sale', 0):.2f}")
        text.append("")
        
        # Top Products
        product_perf = report_data.get('product_performance', {})
        if product_perf.get('top_sellers'):
            text.append("TOP SELLING PRODUCTS")
            text.append("-" * 25)
            for i, product in enumerate(product_perf['top_sellers'][:5], 1):
                text.append(f"{i}. {product['name']} - ${product['revenue']:.2f} ({product['quantity_sold']} units)")
            text.append("")
        
        return "\n".join(text)

class SalesVisualization:
    """
    Sales data visualization using matplotlib and seaborn.
    """
    
    def __init__(self, analytics: SalesAnalytics):
        """
        Initialize the visualization system.
        
        Args:
            analytics: SalesAnalytics instance
        """
        self.analytics = analytics
    
    def create_daily_sales_chart(self, days: int = 30) -> Figure:
        """Create daily sales trend chart."""
        trend_data = self.analytics.get_daily_sales_trend(days)
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        dates = [day['date'] for day in trend_data['daily_data']]
        revenues = [day['revenue'] for day in trend_data['daily_data']]
        transactions = [day['transactions'] for day in trend_data['daily_data']]
        
        # Revenue chart
        ax1.plot(dates, revenues, marker='o', linewidth=2, markersize=6)
        ax1.set_title('Daily Sales Revenue', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Revenue ($)', fontsize=12)
        ax1.grid(True, alpha=0.3)
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        ax1.xaxis.set_major_locator(mdates.DayLocator(interval=7))
        
        # Transactions chart
        ax2.bar(dates, transactions, alpha=0.7, color='skyblue')
        ax2.set_title('Daily Transactions', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Number of Transactions', fontsize=12)
        ax2.set_xlabel('Date', fontsize=12)
        ax2.grid(True, alpha=0.3)
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        ax2.xaxis.set_major_locator(mdates.DayLocator(interval=7))
        
        plt.tight_layout()
        return fig
    
    def create_product_performance_chart(self, days: int = 30) -> Figure:
        """Create product performance chart."""
        product_data = self.analytics.get_product_performance(
            datetime.now() - timedelta(days=days),
            datetime.now()
        )
        
        # Get top 10 products
        top_products = product_data['top_sellers'][:10]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 8))
        
        # Revenue by product
        product_names = [p['name'][:20] + '...' if len(p['name']) > 20 else p['name'] for p in top_products]
        revenues = [p['revenue'] for p in top_products]
        
        bars1 = ax1.barh(product_names, revenues, color='lightcoral')
        ax1.set_title('Top Products by Revenue', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Revenue ($)', fontsize=12)
        ax1.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for bar, revenue in zip(bars1, revenues):
            ax1.text(bar.get_width() + max(revenues) * 0.01, bar.get_y() + bar.get_height()/2,
                    f'${revenue:.0f}', va='center', fontsize=10)
        
        # Quantity sold by product
        quantities = [p['quantity_sold'] for p in top_products]
        
        bars2 = ax2.barh(product_names, quantities, color='lightblue')
        ax2.set_title('Top Products by Quantity Sold', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Quantity Sold', fontsize=12)
        ax2.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for bar, quantity in zip(bars2, quantities):
            ax2.text(bar.get_width() + max(quantities) * 0.01, bar.get_y() + bar.get_height()/2,
                    f'{quantity}', va='center', fontsize=10)
        
        plt.tight_layout()
        return fig
    
    def create_hourly_pattern_chart(self, days: int = 7) -> Figure:
        """Create hourly sales pattern chart."""
        hourly_data = self.analytics.get_hourly_sales_pattern(days)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        hours = [data['hour'] for data in hourly_data['hourly_data']]
        revenues = [data['revenue'] for data in hourly_data['hourly_data']]
        transactions = [data['transactions'] for data in hourly_data['hourly_data']]
        
        # Revenue by hour
        ax1.bar(hours, revenues, alpha=0.7, color='gold')
        ax1.set_title('Hourly Sales Revenue', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Hour of Day', fontsize=12)
        ax1.set_ylabel('Revenue ($)', fontsize=12)
        ax1.set_xticks(range(0, 24, 2))
        ax1.grid(True, alpha=0.3)
        
        # Transactions by hour
        ax2.bar(hours, transactions, alpha=0.7, color='lightgreen')
        ax2.set_title('Hourly Transactions', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Hour of Day', fontsize=12)
        ax2.set_ylabel('Number of Transactions', fontsize=12)
        ax2.set_xticks(range(0, 24, 2))
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def create_category_performance_chart(self, days: int = 30) -> Figure:
        """Create category performance chart."""
        category_data = self.analytics.get_category_performance(
            datetime.now() - timedelta(days=days),
            datetime.now()
        )
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 8))
        
        categories = [cat['category'] for cat in category_data['categories']]
        revenues = [cat['revenue'] for cat in category_data['categories']]
        quantities = [cat['quantity_sold'] for cat in category_data['categories']]
        
        # Revenue by category (pie chart)
        ax1.pie(revenues, labels=categories, autopct='%1.1f%%', startangle=90)
        ax1.set_title('Revenue by Category', fontsize=14, fontweight='bold')
        
        # Quantity by category (bar chart)
        bars = ax2.bar(categories, quantities, alpha=0.7, color='lightcoral')
        ax2.set_title('Quantity Sold by Category', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Category', fontsize=12)
        ax2.set_ylabel('Quantity Sold', fontsize=12)
        ax2.tick_params(axis='x', rotation=45)
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig

class SalesDashboard(tk.Toplevel):
    """
    Interactive sales dashboard with charts and analytics.
    """
    
    def __init__(self, parent, analytics: SalesAnalytics):
        super().__init__(parent)
        self.analytics = analytics
        self.visualization = SalesVisualization(analytics)
        
        self.title("Sales Analytics Dashboard")
        self.geometry("1400x900")
        self.configure(bg='#f0f0f0')
        
        self.create_widgets()
        self.refresh_dashboard()
    
    def create_widgets(self):
        """Create the dashboard widgets."""
        # Main frame
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(header_frame, text="Sales Analytics Dashboard", 
                 font=('Segoe UI', 20, 'bold')).pack(side=tk.LEFT)
        
        # Control panel
        control_frame = ttk.Frame(header_frame)
        control_frame.pack(side=tk.RIGHT)
        
        ttk.Label(control_frame, text="Time Period:").pack(side=tk.LEFT)
        self.period_var = tk.StringVar(value="30")
        period_combo = ttk.Combobox(control_frame, textvariable=self.period_var, 
                                   values=["7", "30", "90", "365"], width=10)
        period_combo.pack(side=tk.LEFT, padx=(5, 10))
        period_combo.bind('<<ComboboxSelected>>', lambda e: self.refresh_dashboard())
        
        ttk.Button(control_frame, text="Refresh", 
                  command=self.refresh_dashboard).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(control_frame, text="Export Report", 
                  command=self.export_report).pack(side=tk.LEFT)
        
        # Create notebook for different views
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Summary tab
        self.summary_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.summary_frame, text="Summary")
        
        # Charts tab
        self.charts_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.charts_frame, text="Charts")
        
        # Products tab
        self.products_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.products_frame, text="Products")
        
        # Categories tab
        self.categories_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.categories_frame, text="Categories")
    
    def refresh_dashboard(self):
        """Refresh all dashboard data and charts."""
        try:
            days = int(self.period_var.get())
            
            # Update summary
            self.update_summary(days)
            
            # Update charts
            self.update_charts(days)
            
            # Update product analysis
            self.update_product_analysis(days)
            
            # Update category analysis
            self.update_category_analysis(days)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error refreshing dashboard: {e}")
    
    def update_summary(self, days: int):
        """Update summary statistics."""
        # Clear existing widgets
        for widget in self.summary_frame.winfo_children():
            widget.destroy()
        
        # Get summary data
        summary = self.analytics.get_sales_summary(
            datetime.now() - timedelta(days=days),
            datetime.now()
        )
        
        # Create summary cards
        cards_frame = ttk.Frame(self.summary_frame)
        cards_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Configure grid
        for i in range(4):
            cards_frame.columnconfigure(i, weight=1)
        
        # Total Revenue Card
        revenue_frame = ttk.Frame(cards_frame, relief='solid', borderwidth=2)
        revenue_frame.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
        ttk.Label(revenue_frame, text="Total Revenue", font=('Segoe UI', 12, 'bold')).pack(pady=10)
        ttk.Label(revenue_frame, text=f"${summary['total_revenue']:,.2f}", 
                 font=('Segoe UI', 20, 'bold'), foreground='green').pack(pady=10)
        
        # Total Transactions Card
        transactions_frame = ttk.Frame(cards_frame, relief='solid', borderwidth=2)
        transactions_frame.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')
        ttk.Label(transactions_frame, text="Total Transactions", font=('Segoe UI', 12, 'bold')).pack(pady=10)
        ttk.Label(transactions_frame, text=f"{summary['total_transactions']:,}", 
                 font=('Segoe UI', 20, 'bold'), foreground='blue').pack(pady=10)
        
        # Average Sale Card
        avg_frame = ttk.Frame(cards_frame, relief='solid', borderwidth=2)
        avg_frame.grid(row=0, column=2, padx=10, pady=10, sticky='nsew')
        ttk.Label(avg_frame, text="Average Sale", font=('Segoe UI', 12, 'bold')).pack(pady=10)
        ttk.Label(avg_frame, text=f"${summary['average_sale']:.2f}", 
                 font=('Segoe UI', 20, 'bold'), foreground='orange').pack(pady=10)
        
        # Date Range Card
        date_frame = ttk.Frame(cards_frame, relief='solid', borderwidth=2)
        date_frame.grid(row=0, column=3, padx=10, pady=10, sticky='nsew')
        ttk.Label(date_frame, text="Date Range", font=('Segoe UI', 12, 'bold')).pack(pady=10)
        ttk.Label(date_frame, text=summary['date_range'], 
                 font=('Segoe UI', 12), wraplength=150).pack(pady=10)
    
    def update_charts(self, days: int):
        """Update charts tab."""
        # Clear existing widgets
        for widget in self.charts_frame.winfo_children():
            widget.destroy()
        
        # Create charts
        try:
            # Daily sales chart
            daily_fig = self.visualization.create_daily_sales_chart(days)
            daily_canvas = FigureCanvasTkAgg(daily_fig, self.charts_frame)
            daily_canvas.draw()
            daily_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
        except Exception as e:
            ttk.Label(self.charts_frame, text=f"Error creating charts: {e}").pack(pady=20)
    
    def update_product_analysis(self, days: int):
        """Update product analysis tab."""
        # Clear existing widgets
        for widget in self.products_frame.winfo_children():
            widget.destroy()
        
        try:
            # Get product data
            product_data = self.analytics.get_product_performance(
                datetime.now() - timedelta(days=days),
                datetime.now()
            )
            
            # Create product chart
            product_fig = self.visualization.create_product_performance_chart(days)
            product_canvas = FigureCanvasTkAgg(product_fig, self.products_frame)
            product_canvas.draw()
            product_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
        except Exception as e:
            ttk.Label(self.products_frame, text=f"Error creating product analysis: {e}").pack(pady=20)
    
    def update_category_analysis(self, days: int):
        """Update category analysis tab."""
        # Clear existing widgets
        for widget in self.categories_frame.winfo_children():
            widget.destroy()
        
        try:
            # Create category chart
            category_fig = self.visualization.create_category_performance_chart(days)
            category_canvas = FigureCanvasTkAgg(category_fig, self.categories_frame)
            category_canvas.draw()
            category_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
        except Exception as e:
            ttk.Label(self.categories_frame, text=f"Error creating category analysis: {e}").pack(pady=20)
    
    def export_report(self):
        """Export current report."""
        try:
            days = int(self.period_var.get())
            report_data = self.analytics.generate_sales_report(
                "comprehensive",
                datetime.now() - timedelta(days=days),
                datetime.now()
            )
            
            # Ask user for format
            format_var = tk.StringVar(value="json")
            dialog = tk.Toplevel(self)
            dialog.title("Export Report")
            dialog.geometry("300x150")
            dialog.transient(self)
            dialog.grab_set()
            
            ttk.Label(dialog, text="Export Format:").pack(pady=10)
            format_combo = ttk.Combobox(dialog, textvariable=format_var, 
                                      values=["json", "csv", "txt"], state="readonly")
            format_combo.pack(pady=10)
            
            def do_export():
                format_type = format_var.get()
                success = self.analytics.export_report(report_data, format_type)
                if success:
                    messagebox.showinfo("Success", f"Report exported successfully as {format_type}")
                else:
                    messagebox.showerror("Error", "Failed to export report")
                dialog.destroy()
            
            ttk.Button(dialog, text="Export", command=do_export).pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error exporting report: {e}") 