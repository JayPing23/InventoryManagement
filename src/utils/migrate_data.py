#!/usr/bin/env python3
"""
Data Migration Script

This script migrates existing POS and inventory data to the unified
inventory management system. It reads from the old format files and
converts them to the new unified JSON format.
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path to import inventory_manager
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.managers.inventory_manager import InventoryManager

def migrate_data():
    """Migrate data from old format files to the unified system."""
    
    # Initialize the unified inventory manager
    inventory_manager = InventoryManager("unified_inventory.json")
    
    # Paths to old data files
    pos_file = "../PointOfSales/products.txt"
    general_file = "inventory.txt"
    
    print("🔄 Starting data migration...")
    print(f"📁 POS Products file: {pos_file}")
    print(f"📁 General Inventory file: {general_file}")
    
    # Check if files exist
    if not os.path.exists(pos_file):
        print(f"⚠️  POS products file not found: {pos_file}")
    else:
        print(f"✅ Found POS products file: {pos_file}")
    
    if not os.path.exists(general_file):
        print(f"⚠️  General inventory file not found: {general_file}")
    else:
        print(f"✅ Found general inventory file: {general_file}")
    
    # Perform migration
    success = inventory_manager.migrate_from_old_format(pos_file, general_file)
    
    if success:
        print("✅ Data migration completed successfully!")
        
        # Get statistics
        stats = inventory_manager.get_inventory_stats()
        print("\n📊 Migration Statistics:")
        print(f"   POS Products: {stats['total_pos_products']}")
        print(f"   General Items: {stats['total_general_items']}")
        print(f"   Total POS Value: ${stats['total_pos_value']:.2f}")
        print(f"   Total POS Stock: {stats['total_pos_stock']}")
        print(f"   Total General Quantity: {stats['total_general_quantity']}")
        
        # Show some sample data
        print("\n📋 Sample POS Products:")
        pos_products = inventory_manager.get_all_pos_products()
        for i, product in enumerate(pos_products[:5]):  # Show first 5
            print(f"   {i+1}. {product.name} - ${product.price:.2f} (Stock: {product.stock})")
        
        print("\n📋 Sample General Items:")
        general_items = inventory_manager.get_all_general_items()
        for i, item in enumerate(general_items[:5]):  # Show first 5
            print(f"   {i+1}. {item.name} - {item.quantity} {item.unit} ({item.category})")
        
        print(f"\n💾 Unified data saved to: {inventory_manager.data_file}")
        
    else:
        print("❌ Data migration failed!")
        return False
    
    return True

def create_backup():
    """Create backup of original files before migration."""
    backup_dir = "backup"
    os.makedirs(backup_dir, exist_ok=True)
    
    files_to_backup = [
        ("../PointOfSales/products.txt", "pos_products_backup.txt"),
        ("inventory.txt", "general_inventory_backup.txt")
    ]
    
    print("💾 Creating backups...")
    
    for source, backup_name in files_to_backup:
        if os.path.exists(source):
            import shutil
            backup_path = os.path.join(backup_dir, backup_name)
            shutil.copy2(source, backup_path)
            print(f"   ✅ Backed up {source} to {backup_path}")
        else:
            print(f"   ⚠️  Source file not found: {source}")
    
    print(f"📁 Backups saved in: {backup_dir}/")

def main():
    """Main function to run the migration."""
    print("🚀 Unified Inventory Management - Data Migration Tool")
    print("=" * 60)
    
    # Check if unified data already exists
    if os.path.exists("unified_inventory.json"):
        response = input("⚠️  Unified inventory file already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("❌ Migration cancelled.")
            return
    
    # Create backups
    create_backup()
    
    # Perform migration
    if migrate_data():
        print("\n🎉 Migration completed successfully!")
        print("\n📝 Next steps:")
        print("   1. Update your POS system to use the unified inventory manager")
        print("   2. Update your inventory management system to use the unified format")
        print("   3. Test both systems to ensure they work correctly")
        print("   4. Keep the backup files for safety")
    else:
        print("\n❌ Migration failed. Check the error messages above.")

if __name__ == "__main__":
    main() 