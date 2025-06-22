"""
Multi-Format Data Manager

This module provides flexible data storage and retrieval capabilities supporting
multiple file formats including TXT, JSON, CSV, and other NoSQL-like formats.
It ensures data consistency across different storage methods and provides
easy migration between formats.

Supported Formats:
- JSON (primary format with full metadata)
- CSV (for spreadsheet compatibility)
- TXT (pipe-delimited for legacy compatibility)
- YAML (for human-readable configuration)
"""

import json
import csv
import yaml
import os
import pickle
import sqlite3
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import pandas as pd

class DataManager:
    """
    Multi-format data manager for flexible storage and retrieval.
    Supports JSON, CSV, TXT, YAML, and SQLite formats.
    """
    
    def __init__(self, base_path: str = "."):
        """
        Initialize the data manager.
        
        Args:
            base_path: Base directory for data files
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
        
        # Create subdirectories for different data types
        (self.base_path / "pos_products").mkdir(exist_ok=True)
        (self.base_path / "general_inventory").mkdir(exist_ok=True)
        (self.base_path / "sales_history").mkdir(exist_ok=True)
        (self.base_path / "analytics").mkdir(exist_ok=True)
        (self.base_path / "backups").mkdir(exist_ok=True)
    
    def save_json(self, data: Dict[str, Any], filename: str) -> bool:
        """Save data to JSON format with metadata."""
        try:
            filepath = self.base_path / filename
            data_with_metadata = {
                'data': data,
                'metadata': {
                    'created_at': datetime.now().isoformat(),
                    'format': 'json',
                    'version': '1.0'
                }
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data_with_metadata, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving JSON: {e}")
            return False
    
    def load_json(self, filename: str) -> Optional[Dict[str, Any]]:
        """Load data from JSON format."""
        try:
            filepath = self.base_path / filename
            if not filepath.exists():
                return None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data_with_metadata = json.load(f)
            
            return data_with_metadata.get('data', {})
        except Exception as e:
            print(f"Error loading JSON: {e}")
            return None
    
    def save_csv(self, data: List[Dict[str, Any]], filename: str) -> bool:
        """Save data to CSV format."""
        try:
            filepath = self.base_path / filename
            if not data:
                return False
            
            # Get all unique keys from all dictionaries
            fieldnames = set()
            for item in data:
                fieldnames.update(item.keys())
            fieldnames = sorted(list(fieldnames))
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            return True
        except Exception as e:
            print(f"Error saving CSV: {e}")
            return False
    
    def load_csv(self, filename: str) -> List[Dict[str, Any]]:
        """Load data from CSV format."""
        try:
            filepath = self.base_path / filename
            if not filepath.exists():
                return []
            
            data = []
            with open(filepath, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Convert string values to appropriate types
                    processed_row = {}
                    for key, value in row.items():
                        if value == '':
                            processed_row[key] = None
                        elif value.lower() in ('true', 'false'):
                            processed_row[key] = value.lower() == 'true'
                        elif value.replace('.', '').replace('-', '').isdigit():
                            if '.' in value:
                                processed_row[key] = float(value)
                            else:
                                processed_row[key] = int(value)
                        else:
                            processed_row[key] = value
                    data.append(processed_row)
            
            return data
        except Exception as e:
            print(f"Error loading CSV: {e}")
            return []
    
    def save_txt(self, data: List[Dict[str, Any]], filename: str, delimiter: str = '|') -> bool:
        """Save data to TXT format (pipe-delimited)."""
        try:
            filepath = self.base_path / filename
            if not data:
                return False
            
            with open(filepath, 'w', encoding='utf-8') as f:
                for item in data:
                    line = delimiter.join(str(value) for value in item.values())
                    f.write(line + '\n')
            return True
        except Exception as e:
            print(f"Error saving TXT: {e}")
            return False
    
    def load_txt(self, filename: str, delimiter: str = '|', headers: List[str] = None) -> List[Dict[str, Any]]:
        """Load data from TXT format (pipe-delimited)."""
        try:
            filepath = self.base_path / filename
            if not filepath.exists():
                return []
            
            data = []
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        values = line.split(delimiter)
                        if headers:
                            item = dict(zip(headers, values))
                        else:
                            item = {f'field_{i}': value for i, value in enumerate(values)}
                        data.append(item)
            
            return data
        except Exception as e:
            print(f"Error loading TXT: {e}")
            return []
    
    def save_yaml(self, data: Dict[str, Any], filename: str) -> bool:
        """Save data to YAML format."""
        try:
            filepath = self.base_path / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
            return True
        except Exception as e:
            print(f"Error saving YAML: {e}")
            return False
    
    def load_yaml(self, filename: str) -> Optional[Dict[str, Any]]:
        """Load data from YAML format."""
        try:
            filepath = self.base_path / filename
            if not filepath.exists():
                return None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading YAML: {e}")
            return None
    
    def save_sqlite(self, data: Dict[str, List[Dict[str, Any]]], db_name: str) -> bool:
        """Save data to SQLite database."""
        try:
            db_path = self.base_path / f"{db_name}.db"
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            for table_name, table_data in data.items():
                if not table_data:
                    continue
                
                # Create table
                columns = list(table_data[0].keys())
                columns_sql = ', '.join([f"{col} TEXT" for col in columns])
                cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_sql})")
                
                # Insert data
                placeholders = ', '.join(['?' for _ in columns])
                insert_sql = f"INSERT OR REPLACE INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
                
                for row in table_data:
                    values = [str(row.get(col, '')) for col in columns]
                    cursor.execute(insert_sql, values)
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving SQLite: {e}")
            return False
    
    def load_sqlite(self, db_name: str) -> Dict[str, List[Dict[str, Any]]]:
        """Load data from SQLite database."""
        try:
            db_path = self.base_path / f"{db_name}.db"
            if not db_path.exists():
                return {}
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            data = {}
            for table in tables:
                cursor.execute(f"SELECT * FROM {table}")
                columns = [description[0] for description in cursor.description]
                rows = cursor.fetchall()
                
                table_data = []
                for row in rows:
                    item = dict(zip(columns, row))
                    table_data.append(item)
                
                data[table] = table_data
            
            conn.close()
            return data
        except Exception as e:
            print(f"Error loading SQLite: {e}")
            return {}
    
    def convert_format(self, source_file: str, source_format: str, 
                      target_file: str, target_format: str) -> bool:
        """
        Convert data from one format to another.
        
        Args:
            source_file: Source filename
            source_format: Source format (json, csv, txt, yaml, sqlite)
            target_file: Target filename
            target_format: Target format (json, csv, txt, yaml, sqlite)
        """
        try:
            # Load data from source format
            if source_format == 'json':
                data = self.load_json(source_file)
            elif source_format == 'csv':
                data = self.load_csv(source_file)
            elif source_format == 'txt':
                data = self.load_txt(source_file)
            elif source_format == 'yaml':
                data = self.load_yaml(source_file)
            elif source_format == 'sqlite':
                data = self.load_sqlite(source_file)
            else:
                print(f"Unsupported source format: {source_format}")
                return False
            
            if data is None:
                print("No data to convert")
                return False
            
            # Save data to target format
            if target_format == 'json':
                return self.save_json(data, target_file)
            elif target_format == 'csv':
                return self.save_csv(data if isinstance(data, list) else [data], target_file)
            elif target_format == 'txt':
                return self.save_txt(data if isinstance(data, list) else [data], target_file)
            elif target_format == 'yaml':
                return self.save_yaml(data, target_file)
            elif target_format == 'sqlite':
                return self.save_sqlite(data if isinstance(data, dict) else {'data': data}, target_file)
            else:
                print(f"Unsupported target format: {target_format}")
                return False
                
        except Exception as e:
            print(f"Error converting format: {e}")
            return False
    
    def create_backup(self, filename: str, backup_suffix: str = None) -> bool:
        """Create a backup of a file."""
        try:
            if backup_suffix is None:
                backup_suffix = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            source_path = self.base_path / filename
            if not source_path.exists():
                return False
            
            backup_path = self.base_path / "backups" / f"{filename}.{backup_suffix}"
            backup_path.parent.mkdir(exist_ok=True)
            
            import shutil
            shutil.copy2(source_path, backup_path)
            return True
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False
    
    def list_files(self, pattern: str = "*") -> List[str]:
        """List all files matching a pattern."""
        try:
            files = []
            for file_path in self.base_path.rglob(pattern):
                if file_path.is_file():
                    files.append(str(file_path.relative_to(self.base_path)))
            return files
        except Exception as e:
            print(f"Error listing files: {e}")
            return []
    
    def get_file_info(self, filename: str) -> Dict[str, Any]:
        """Get information about a file."""
        try:
            file_path = self.base_path / filename
            if not file_path.exists():
                return {}
            
            stat = file_path.stat()
            return {
                'filename': filename,
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'format': file_path.suffix[1:] if file_path.suffix else 'unknown'
            }
        except Exception as e:
            print(f"Error getting file info: {e}")
            return {} 