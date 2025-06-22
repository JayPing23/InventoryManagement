"""
A modern inventory management application built with Python and the Tkinter library.

This application provides a graphical user interface (GUI) for users to manage
an inventory of items. It allows for adding, editing, deleting, searching, and
filtering items. The inventory can be saved to and loaded from a JSON file,
making it persistent across sessions.

The UI is designed to be sleek and modern, using a tabbed interface to keep
controls organized and compact, while maximizing space for the inventory table.
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from datetime import datetime

# Import modular components
from models import Product
from managers.inventory_manager import InventoryManager
from utils.file_utils import FileUtils
from utils.ui_utils import UIUtils

# --- Color Scheme ---
# A centralized dictionary for a modern and consistent color palette.
COLORS = {
    'primary': '#2563eb', 'primary_dark': '#1d4ed8',      # Blue tones
    'secondary': '#64748b', 'secondary_dark': '#475569',  # Slate tones
    'success': '#059669', 'success_dark': '#047857',      # Green tones
    'warning': '#d97706', 'warning_dark': '#b45309',      # Orange tones
    'danger': '#dc2626', 'danger_dark': '#b91c1c',       # Red tones
    'light': '#f1f5f9',                                   # Light background
    'dark': '#1e293b',                                    # Dark text
    'white': '#ffffff',                                   # Card background
    'border': '#e2e8f0'                                   # Border for cards
}

class ModernButton(ttk.Button):
    """A custom ttk.Button that uses a pre-defined modern style."""
    def __init__(self, parent, **kwargs):
        # The specific style (e.g., 'Success.TButton') is passed in kwargs.
        super().__init__(parent, **kwargs)

class EditItemDialog:
    """
    A modal dialog window for editing the details of an existing inventory item.
    
    This dialog is created when a user double-clicks an item or uses the 'Edit'
    button. It comes pre-filled with the item's current data and provides
    fields to modify the name, quantity, and category.
    """
    def __init__(self, parent, item_data, categories):
        """
        Initializes the EditItemDialog.

        Args:
            parent: The parent widget (the main application window).
            item_data (dict): A dictionary containing the data of the item to be edited.
            categories (list): A list of available categories for the dropdown.
        """
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Edit Item")
        self.dialog.geometry("450x300")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)  # Keeps the dialog on top of the parent.
        self.dialog.grab_set()         # Makes the dialog modal.
        self.dialog.configure(bg=UIUtils.COLORS['white'])
        
        # Center the dialog relative to the parent window.
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.item_data = item_data
        self.categories = categories
        self.result = None  # Stores the edited data if the user saves.
        
        self.create_widgets()

    def create_widgets(self):
        """Creates and arranges all widgets within the dialog."""
        main_frame = ttk.Frame(self.dialog, padding="30", style='TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True)

        title_label = UIUtils.create_styled_label(main_frame, "✏️ Edit Item", 'title')
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 25))

        # --- Input Fields ---
        # Name
        UIUtils.create_styled_label(main_frame, "Name:").grid(row=1, column=0, sticky=tk.W, pady=8)
        self.name_entry = UIUtils.create_styled_entry(main_frame, width=35)
        self.name_entry.grid(row=1, column=1, padx=(15, 0), pady=8, sticky=tk.W)
        self.name_entry.insert(0, self.item_data['name']) # Pre-fill with existing data.

        # Quantity
        UIUtils.create_styled_label(main_frame, "Quantity:").grid(row=2, column=0, sticky=tk.W, pady=8)
        self.quantity_entry = UIUtils.create_styled_entry(main_frame, width=15)
        self.quantity_entry.grid(row=2, column=1, padx=(15, 0), pady=8, sticky=tk.W)
        self.quantity_entry.insert(0, str(self.item_data['quantity'])) # Pre-fill

        # Category
        UIUtils.create_styled_label(main_frame, "Category:").grid(row=3, column=0, sticky=tk.W, pady=8)
        self.category_combo = ttk.Combobox(main_frame, values=self.categories, width=32, state="readonly", font=("Segoe UI", 10))
        self.category_combo.grid(row=3, column=1, padx=(15, 0), pady=8, sticky=tk.W)
        self.category_combo.set(self.item_data['category']) # Pre-fill

        # Description
        description_label = ttk.Label(main_frame, text="Description:")
        description_label.grid(row=4, column=0, sticky=tk.W, pady=8)
        self.description_entry = ttk.Entry(main_frame, width=35)
        self.description_entry.grid(row=4, column=1, padx=(15, 0), pady=8, sticky=tk.W)
        self.description_entry.insert(0, self.item_data.get('description', ''))

        # --- Action Buttons ---
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=(30, 0))

        save_button = UIUtils.create_styled_button(button_frame, "💾 Save Changes", self.save_changes, 'success')
        save_button.pack(side=tk.LEFT, padx=(0, 15))
        cancel_button = UIUtils.create_styled_button(button_frame, "❌ Cancel", self.cancel, 'secondary')
        cancel_button.pack(side=tk.LEFT)

        # --- Bindings and Focus ---
        self.dialog.bind('<Return>', lambda e: self.save_changes()) # Enter key to save.
        self.dialog.bind('<Escape>', lambda e: self.cancel())       # Escape key to cancel.
        self.name_entry.focus_set() # Set initial focus to the name field.

    def save_changes(self):
        """Validates the input data and, if valid, stores it and closes the dialog."""
        # Retrieve and strip whitespace from inputs.
        name = self.name_entry.get().strip()
        quantity_str = self.quantity_entry.get().strip()
        category = self.category_combo.get()
        description = self.description_entry.get().strip()
        
        # Basic validation.
        if not name or not quantity_str or not category:
            UIUtils.show_message("Error", "All fields are required.", 'error')
            return
            
        # Quantity validation.
        try:
            quantity = int(quantity_str)
            if quantity < 0: raise ValueError("Quantity cannot be negative")
        except ValueError:
            UIUtils.show_message("Error", "Quantity must be a positive integer.", 'error')
            return
            
        # If validation passes, store the result.
        self.result = {'name': name, 'quantity': quantity, 'category': category, 'description': description}
        self.dialog.destroy() # Close the dialog.
        
    def cancel(self):
        """Closes the dialog without saving any changes."""
        self.dialog.destroy()

class InventoryApp:
    """
    The main class for the Inventory Management application.
    
    This class sets up the main window, defines all the UI styles and widgets,
    and contains all the logic for inventory operations like adding, editing,
    deleting, saving, and loading items.
    """
    def __init__(self, root):
        """
        Initializes the main application.

        Args:
            root: The root Tkinter window.
        """
        self.root = root
        self.root.title("📦 Sleek Inventory Manager")
        self.root.geometry("900x650")
        self.root.configure(bg=UIUtils.COLORS['light'])
        
        # Initialize inventory manager and file utilities
        self.inventory_manager = InventoryManager()
        self.file_utils = FileUtils()
        
        # Initialize styles, inventory list, and widgets.
        self.setup_styles()
        self.current_file = None # To track the path of the currently loaded file.
        
        # A comprehensive list of categories for consistency.
        self.categories = [
            "Electronics", "Clothing & Apparel", "Books & Media", "Home & Garden", 
            "Sports & Recreation", "Automotive", "Health & Beauty", "Food & Beverages", 
            "Office Supplies", "Tools & Hardware", "Toys & Games", "Jewelry & Accessories", 
            "Pet Supplies", "Baby & Kids", "Art & Crafts", "Musical Instruments", 
            "Outdoor & Camping", "Kitchen & Dining", "Bathroom & Personal Care", "Bedroom & Furniture", 
            "Lighting & Electrical", "Plumbing & Fixtures", "Building Materials", "Garden & Landscaping", 
            "Cleaning Supplies", "Medical & First Aid", "Safety Equipment", "Storage & Organization", 
            "Seasonal Items", "Collectibles", "Antiques", "Vintage Items", "Handmade Items", 
            "Digital Products", "Services", "Other"
        ]
        self.create_widgets()

    def setup_styles(self):
        """Configures all the custom ttk styles for the application's modern look."""
        style = ttk.Style(self.root)
        # 'clam' theme is used because it's more customizable than the default theme.
        style.theme_use('clam')

        # General styles for frames and labels.
        style.configure('TFrame', background=UIUtils.COLORS['white'])
        style.configure('TLabel', background=UIUtils.COLORS['white'], foreground=UIUtils.COLORS['dark'], font=('Segoe UI', 9))
        style.configure('Card.TFrame', background=UIUtils.COLORS['white'], relief='solid', borderwidth=1, bordercolor=UIUtils.COLORS['gray'])
        style.configure('light.TFrame', background=UIUtils.COLORS['light']) # For the main background.

        # --- Button Styling ---
        # Defines a base style for all buttons and maps colors for different states.
        button_font = ('Segoe UI', 9, 'bold')
        button_padding = (10, 6)
        style.configure('TButton', font=button_font, padding=button_padding, borderwidth=0)
        # Ensures button text is always white.
        style.map('TButton', foreground=[('!active', UIUtils.COLORS['white'])])

        # Style for each button type (Primary, Success, etc.)
        style.configure('Primary.TButton', background=UIUtils.COLORS['primary'])
        style.map('Primary.TButton', background=[('active', UIUtils.lighten_color(UIUtils.COLORS['primary'], 0.1))])
        
        style.configure('Success.TButton', background=UIUtils.COLORS['success'])
        style.map('Success.TButton', background=[('active', UIUtils.lighten_color(UIUtils.COLORS['success'], 0.1))])
        
        style.configure('Warning.TButton', background=UIUtils.COLORS['warning'])
        style.map('Warning.TButton', background=[('active', UIUtils.lighten_color(UIUtils.COLORS['warning'], 0.1))])
        
        style.configure('Danger.TButton', background=UIUtils.COLORS['danger'])
        style.map('Danger.TButton', background=[('active', UIUtils.lighten_color(UIUtils.COLORS['danger'], 0.1))])
        
        style.configure('Secondary.TButton', background=UIUtils.COLORS['secondary'])
        style.map('Secondary.TButton', background=[('active', UIUtils.lighten_color(UIUtils.COLORS['secondary'], 0.1))])

        # --- Entry Styling ---
        style.configure('TEntry', fieldbackground=UIUtils.COLORS['white'], borderwidth=1, relief='solid')
        style.map('TEntry', bordercolor=[('focus', UIUtils.COLORS['accent'])])

        # --- Combobox Styling ---
        style.configure('TCombobox', fieldbackground=UIUtils.COLORS['white'], borderwidth=1, relief='solid')
        style.map('TCombobox', bordercolor=[('focus', UIUtils.COLORS['accent'])])

        # --- Treeview Styling ---
        style.configure('Treeview', 
                       background=UIUtils.COLORS['light'],
                       foreground=UIUtils.COLORS['dark'],
                       rowheight=25,
                       fieldbackground=UIUtils.COLORS['light'])
        style.configure('Treeview.Heading', 
                       background=UIUtils.COLORS['primary'],
                       foreground=UIUtils.COLORS['white'],
                       font=('Segoe UI', 9, 'bold'))

    def create_widgets(self):
        # Main vertical layout
        main_frame = ttk.Frame(self.root, style='light.TFrame', padding=5)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Compact summary label at the top ---
        self.summary_label = ttk.Label(main_frame, text="", style='TLabel', font=("Segoe UI", 9))
        self.summary_label.pack(fill=tk.X, padx=5, pady=(0, 2))

        # --- Notebook for tabs ---
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        self.create_add_tab(self.notebook)
        self.create_search_tab(self.notebook)
        self.create_actions_tab(self.notebook)

        # --- Inventory Table (main content, below tabs) ---
        table_frame = ttk.Frame(main_frame, style='Card.TFrame')
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(2, 0))
        columns = ("ID", "Name", "Category", "Quantity", "Price", "Description")
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=18)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100 if col != "Description" else 180, anchor='center')
        self.tree.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        self.tree.bind('<Double-1>', self.on_double_click)
        self.update_table()

    def create_add_tab(self, notebook):
        add_frame = ttk.Frame(notebook, style='Card.TFrame', padding=5)
        notebook.add(add_frame, text="➕ Add Item")
        input_frame = ttk.Frame(add_frame)
        input_frame.pack(pady=5)
        UIUtils.create_styled_label(input_frame, "Name:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.name_entry = UIUtils.create_styled_entry(input_frame, placeholder="Enter item name", width=20)
        self.name_entry.grid(row=0, column=1, padx=(5, 0), pady=2, sticky=tk.W)
        UIUtils.create_styled_label(input_frame, "Quantity:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.quantity_entry = UIUtils.create_styled_entry(input_frame, placeholder="Enter quantity", width=10)
        self.quantity_entry.grid(row=1, column=1, padx=(5, 0), pady=2, sticky=tk.W)
        UIUtils.create_styled_label(input_frame, "Price:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.price_entry = UIUtils.create_styled_entry(input_frame, placeholder="Enter price", width=10)
        self.price_entry.grid(row=2, column=1, padx=(5, 0), pady=2, sticky=tk.W)
        UIUtils.create_styled_label(input_frame, "Category:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.category_combo = ttk.Combobox(input_frame, values=self.categories, width=18, state="readonly", font=("Segoe UI", 9))
        self.category_combo.grid(row=3, column=1, padx=(5, 0), pady=2, sticky=tk.W)
        # Add description label and entry
        description_label = ttk.Label(input_frame, text="Description:")
        description_label.grid(row=4, column=0, padx=5, pady=5, sticky='e')
        self.description_entry = ttk.Entry(input_frame)
        self.description_entry.grid(row=4, column=1, padx=5, pady=5, sticky='w')
        add_button = UIUtils.create_styled_button(add_frame, "Add Item", self.add_item, 'success')
        add_button.pack(pady=5)

    def create_search_tab(self, notebook):
        search_frame = ttk.Frame(notebook, style='Card.TFrame', padding=5)
        notebook.add(search_frame, text="🔍 Search & Filter")
        search_controls = ttk.Frame(search_frame)
        search_controls.pack(pady=5)
        UIUtils.create_styled_label(search_controls, "Search:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.search_entry = UIUtils.create_styled_entry(search_controls, placeholder="Search items...", width=18)
        self.search_entry.grid(row=0, column=1, padx=(5, 5), pady=2, sticky=tk.W)
        self.search_entry.bind('<KeyRelease>', self.filter_items)
        UIUtils.create_styled_label(search_controls, "Category:").grid(row=0, column=2, sticky=tk.W, pady=2)
        self.filter_category = ttk.Combobox(search_controls, values=['All'] + self.categories, width=15, state="readonly", font=("Segoe UI", 9))
        self.filter_category.grid(row=0, column=3, padx=(5, 0), pady=2, sticky=tk.W)
        self.filter_category.set('All')
        self.filter_category.bind('<<ComboboxSelected>>', self.filter_items)
        clear_button = UIUtils.create_styled_button(search_frame, "Clear Filters", self.clear_filters, 'secondary')
        clear_button.pack(pady=5)

    def create_actions_tab(self, notebook):
        actions_frame = ttk.Frame(notebook, style='Card.TFrame', padding=5)
        notebook.add(actions_frame, text="⚙️ Actions")
        file_frame = ttk.Frame(actions_frame)
        file_frame.pack(pady=5)
        save_button = UIUtils.create_styled_button(file_frame, "Save", self.save_inventory, 'primary')
        save_button.pack(side=tk.LEFT, padx=2, pady=2)
        load_button = UIUtils.create_styled_button(file_frame, "Load", self.load_inventory, 'secondary')
        load_button.pack(side=tk.LEFT, padx=2, pady=2)
        export_button = UIUtils.create_styled_button(file_frame, "Export for POS", self.export_for_pos, 'primary')
        export_button.pack(side=tk.LEFT, padx=2, pady=2)
        item_frame = ttk.Frame(actions_frame)
        item_frame.pack(pady=5)
        edit_button = UIUtils.create_styled_button(item_frame, "Edit Selected", self.edit_selected_item, 'primary')
        edit_button.pack(side=tk.LEFT, padx=2, pady=2)
        delete_button = UIUtils.create_styled_button(item_frame, "Delete Selected", self.delete_item, 'danger')
        delete_button.pack(side=tk.LEFT, padx=2, pady=2)
        clear_button = UIUtils.create_styled_button(item_frame, "Clear All", self.clear_entries, 'secondary')
        clear_button.pack(side=tk.LEFT, padx=2, pady=2)

    def add_item(self):
        """Adds a new item to the inventory."""
        name = self.name_entry.get().strip()
        quantity_str = self.quantity_entry.get().strip()
        price_str = self.price_entry.get().strip()
        category = self.category_combo.get()
        description = self.description_entry.get().strip()

        # Validation
        if not name or not quantity_str or not price_str or not category:
            UIUtils.show_message("Error", "All fields are required.", 'error')
            return

        try:
            quantity = int(quantity_str)
            price = float(price_str)
            if quantity < 0 or price < 0:
                raise ValueError("Values cannot be negative")
        except ValueError:
            UIUtils.show_message("Error", "Quantity and price must be valid positive numbers.", 'error')
            return

        # Create product using the model
        product = Product(
            name=name,
            category=category,
            price=price,
            quantity=quantity,
            description=description
        )

        # Add to inventory manager
        success = self.inventory_manager.add_product(product)
        if success:
            self.update_table()
            self.clear_entries()
            UIUtils.show_message("Success", f"Item '{name}' added successfully!", 'info')
        else:
            UIUtils.show_message("Error", "Failed to add item. Please try again.", 'error')

    def update_table(self):
        """Updates the inventory table with current data."""
        self.tree.delete(*self.tree.get_children())
        total_items = 0
        total_value = 0.0
        for p in self.inventory_manager.get_all_products():
            total_items += 1
            total_value += (p.price or 0.0) * (p.quantity or 0)
            self.tree.insert('', 'end', values=(p.product_id, p.name, p.category, p.quantity, p.price, p.description))
        self.summary_label.config(text=f"Total Items: {total_items} | Total Value: ${total_value:.2f}")

    def filter_items(self, event=None):
        """Filters the inventory table based on search criteria."""
        search_term = self.search_entry.get().lower()
        category_filter = self.filter_category.get()

        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Get filtered products
        products = self.inventory_manager.get_all_products()
        filtered_products = []

        for product in products:
            # Check search term
            if search_term and search_term not in product.name.lower():
                continue
            
            # Check category filter
            if category_filter != 'All' and product.category != category_filter:
                continue
            
            filtered_products.append(product)

        # Add filtered items to table
        for product in filtered_products:
            total_value = product.price * product.quantity
            self.tree.insert('', 'end', values=(
                product.product_id,
                product.name,
                product.category,
                product.quantity,
                UIUtils.format_currency(product.price),
                UIUtils.format_currency(total_value),
                UIUtils.format_date(getattr(product, 'last_updated', ''))
            ))

    def clear_filters(self):
        """Clears all search and filter criteria."""
        self.search_entry.delete(0, tk.END)
        self.filter_category.set('All')
        self.update_table()

    def clear_entries(self):
        """Clears all input fields in the add tab."""
        self.name_entry.delete(0, tk.END)
        self.quantity_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)
        self.category_combo.set('')
        self.description_entry.delete(0, tk.END)

    def save_inventory(self):
        """Saves the current inventory to the current file."""
        if self.current_file:
            success = self.inventory_manager.save_to_file(self.current_file)
            if success:
                UIUtils.show_message("Success", "Inventory saved successfully!", 'info')
            else:
                UIUtils.show_message("Error", "Failed to save inventory.", 'error')
        else:
            self.save_inventory_as()

    def save_inventory_as(self):
        """Saves the inventory to a new file."""
        filename = self.file_utils.get_save_filename(
            "Save Inventory",
            [("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            success = self.inventory_manager.save_to_file(filename)
            if success:
                self.current_file = filename
                UIUtils.show_message("Success", "Inventory saved successfully!", 'info')
            else:
                UIUtils.show_message("Error", "Failed to save inventory.", 'error')

    def load_inventory(self):
        """Loads inventory from a file."""
        filename = self.file_utils.get_open_filename(
            "Load Inventory",
            [("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            success = self.inventory_manager.load_from_file(filename)
            if success:
                self.current_file = filename
                self.update_table()
                UIUtils.show_message("Success", "Inventory loaded successfully!", 'info')
            else:
                UIUtils.show_message("Error", "Failed to load inventory.", 'error')

    def get_selected_item_data(self):
        """Gets the data of the currently selected item."""
        selection = self.tree.selection()
        if not selection:
            UIUtils.show_message("Warning", "Please select an item first.", 'warning')
            return None
        
        item_id = self.tree.item(selection[0])['values'][0]
        product = self.inventory_manager.get_product_by_id(item_id)
        
        if product:
            return {
                'id': product.product_id,
                'name': product.name,
                'category': product.category,
                'quantity': product.quantity,
                'price': product.price
            }
        return None

    def edit_selected_item(self):
        """Opens the edit dialog for the selected item."""
        item_data = self.get_selected_item_data()
        if item_data:
            self.edit_item(item_data, item_data['id'])

    def edit_item(self, item_data, item_id):
        """Opens the edit dialog and handles the editing process."""
        dialog = EditItemDialog(self.root, item_data, self.categories)
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            # Update the product
            product = Product(
                product_id=item_id,
                name=dialog.result['name'],
                category=dialog.result['category'],
                price=item_data['price'],
                quantity=dialog.result['quantity'],
                description=dialog.result.get('description', '')
            )
            
            success = self.inventory_manager.update_product(product)
            if success:
                self.update_table()
                UIUtils.show_message("Success", "Item updated successfully!", 'info')
            else:
                UIUtils.show_message("Error", "Failed to update item.", 'error')

    def delete_item(self):
        """Deletes the selected item from the inventory."""
        item_data = self.get_selected_item_data()
        if item_data:
            confirm = UIUtils.show_message(
                "Confirm Delete",
                f"Are you sure you want to delete '{item_data['name']}'?",
                'question'
            )
            
            if confirm:
                success = self.inventory_manager.delete_product(item_data['id'])
                if success:
                    self.update_table()
                    UIUtils.show_message("Success", "Item deleted successfully!", 'info')
                else:
                    UIUtils.show_message("Error", "Failed to delete item.", 'error')

    def on_double_click(self, event):
        """Handles double-click events on the inventory table."""
        self.edit_selected_item()

    def export_for_pos(self):
        file_path = filedialog.asksaveasfilename(
            title="Export for POS",
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt")],
            initialdir="datas/"
        )
        if not file_path:
            return
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                for p in self.inventory_manager.get_all_products():
                    # Use product_id or generate one if missing
                    pid = p.product_id or f"prod_{hash(p.name) % 10000}"
                    name = p.name or "Unknown"
                    price = p.price if hasattr(p, 'price') else 0.0
                    stock = p.quantity if hasattr(p, 'quantity') else 0
                    f.write(f"{pid}|{name}|{price}|{stock}\n")
            messagebox.showinfo("Export Complete", f"Exported products for POS import to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export: {e}")


def main():
    """Main function to run the application."""
    root = tk.Tk()
    app = InventoryApp(root)
    root.mainloop()


if __name__ == "__main__":
    main() 