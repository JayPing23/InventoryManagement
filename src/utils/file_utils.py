"""
File utility functions for Inventory Management System.
"""
import json
import csv
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox


class FileUtils:
    """Utility class for file operations and data management."""
    
    @staticmethod
    def save_to_json(data: Dict[str, Any], filename: str) -> bool:
        """
        Save data to JSON file with error handling.
        
        Args:
            data: Data to save
            filename: Target filename
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving to JSON: {e}")
            return False
    
    @staticmethod
    def load_from_json(filename: str) -> Optional[Dict[str, Any]]:
        """
        Load data from JSON file with error handling.
        
        Args:
            filename: Source filename
            
        Returns:
            Dict or None: Loaded data or None if error
        """
        try:
            if not os.path.exists(filename):
                return {}
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading from JSON: {e}")
            return None
    
    @staticmethod
    def export_to_csv(data: List[Dict[str, Any]], filename: str, fieldnames: List[str]) -> bool:
        """
        Export data to CSV file.
        
        Args:
            data: List of dictionaries to export
            filename: Target filename
            fieldnames: Column headers
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            return True
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False
    
    @staticmethod
    def get_save_filename(title: str, filetypes: List[tuple]) -> Optional[str]:
        """
        Open file dialog for saving files.
        
        Args:
            title: Dialog title
            filetypes: List of (description, extension) tuples
            
        Returns:
            str or None: Selected filename or None if cancelled
        """
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        filename = filedialog.asksaveasfilename(
            title=title,
            filetypes=filetypes,
            defaultextension=filetypes[0][1] if filetypes else ""
        )
        root.destroy()
        return filename if filename else None
    
    @staticmethod
    def get_open_filename(title: str, filetypes: List[tuple]) -> Optional[str]:
        """
        Open file dialog for opening files.
        
        Args:
            title: Dialog title
            filetypes: List of (description, extension) tuples
            
        Returns:
            str or None: Selected filename or None if cancelled
        """
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        filename = filedialog.askopenfilename(
            title=title,
            filetypes=filetypes
        )
        root.destroy()
        return filename if filename else None
    
    @staticmethod
    def backup_data(data: Dict[str, Any], backup_dir: str = "backups") -> bool:
        """
        Create a backup of data with timestamp.
        
        Args:
            data: Data to backup
            backup_dir: Backup directory name
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = os.path.join(backup_dir, f"backup_{timestamp}.json")
            
            return FileUtils.save_to_json(data, backup_filename)
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False
    
    @staticmethod
    def validate_product_data(product: Dict[str, Any]) -> List[str]:
        """
        Validate product data and return list of errors.
        
        Args:
            product: Product data to validate
            
        Returns:
            List[str]: List of validation errors
        """
        errors = []
        
        # Required fields
        required_fields = ['name', 'category', 'price', 'quantity']
        for field in required_fields:
            if field not in product or not product[field]:
                errors.append(f"Missing required field: {field}")
        
        # Data type validation
        if 'price' in product:
            try:
                float(product['price'])
            except (ValueError, TypeError):
                errors.append("Price must be a valid number")
        
        if 'quantity' in product:
            try:
                int(product['quantity'])
            except (ValueError, TypeError):
                errors.append("Quantity must be a valid integer")
        
        if 'min_stock' in product and product['min_stock']:
            try:
                int(product['min_stock'])
            except (ValueError, TypeError):
                errors.append("Minimum stock must be a valid integer")
        
        return errors 