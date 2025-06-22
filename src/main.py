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
        self.dialog.configure(bg=COLORS['white'])
        
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

        title_label = ttk.Label(main_frame, text="✏️ Edit Item", font=("Segoe UI", 16, "bold"), foreground=COLORS['dark'])
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 25))

        # --- Input Fields ---
        # Name
        ttk.Label(main_frame, text="Name:", font=("Segoe UI", 10, "bold")).grid(row=1, column=0, sticky=tk.W, pady=8)
        self.name_entry = ttk.Entry(main_frame, width=35, font=("Segoe UI", 10))
        self.name_entry.grid(row=1, column=1, padx=(15, 0), pady=8, sticky=tk.W)
        self.name_entry.insert(0, self.item_data['name']) # Pre-fill with existing data.

        # Quantity
        ttk.Label(main_frame, text="Quantity:", font=("Segoe UI", 10, "bold")).grid(row=2, column=0, sticky=tk.W, pady=8)
        self.quantity_entry = ttk.Entry(main_frame, width=15, font=("Segoe UI", 10))
        self.quantity_entry.grid(row=2, column=1, padx=(15, 0), pady=8, sticky=tk.W)
        self.quantity_entry.insert(0, str(self.item_data['quantity'])) # Pre-fill

        # Category
        ttk.Label(main_frame, text="Category:", font=("Segoe UI", 10, "bold")).grid(row=3, column=0, sticky=tk.W, pady=8)
        self.category_combo = ttk.Combobox(main_frame, values=self.categories, width=32, state="readonly", font=("Segoe UI", 10))
        self.category_combo.grid(row=3, column=1, padx=(15, 0), pady=8, sticky=tk.W)
        self.category_combo.set(self.item_data['category']) # Pre-fill

        # --- Action Buttons ---
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(30, 0))

        save_button = ModernButton(button_frame, text="💾 Save Changes", command=self.save_changes, style='Success.TButton')
        save_button.pack(side=tk.LEFT, padx=(0, 15))
        cancel_button = ModernButton(button_frame, text="❌ Cancel", command=self.cancel, style='Secondary.TButton')
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
        
        # Basic validation.
        if not name or not quantity_str or not category:
            messagebox.showerror("Error", "All fields are required.", parent=self.dialog)
            return
            
        # Quantity validation.
        try:
            quantity = int(quantity_str)
            if quantity < 0: raise ValueError("Quantity cannot be negative")
        except ValueError:
            messagebox.showerror("Error", f"Quantity must be a positive integer.", parent=self.dialog)
            return
            
        # If validation passes, store the result.
        self.result = {'name': name, 'quantity': quantity, 'category': category}
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
        self.root.configure(bg=COLORS['light'])
        
        # Initialize styles, inventory list, and widgets.
        self.setup_styles()
        self.inventory = []
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
        style.configure('TFrame', background=COLORS['white'])
        style.configure('TLabel', background=COLORS['white'], foreground=COLORS['dark'], font=('Segoe UI', 9))
        style.configure('Card.TFrame', background=COLORS['white'], relief='solid', borderwidth=1, bordercolor=COLORS['border'])
        style.configure('light.TFrame', background=COLORS['light']) # For the main background.

        # --- Button Styling ---
        # Defines a base style for all buttons and maps colors for different states.
        button_font = ('Segoe UI', 9, 'bold')
        button_padding = (10, 6)
        style.configure('TButton', font=button_font, padding=button_padding, borderwidth=0)
        # Ensures button text is always white.
        style.map('TButton', foreground=[('!active', COLORS['white'])])

        # Style for each button type (Primary, Success, etc.)
        style.configure('Primary.TButton', background=COLORS['primary'])
        style.map('Primary.TButton', background=[('active', COLORS['primary_dark'])]) # Darker on click/hover.
        
        style.configure('Success.TButton', background=COLORS['success'])
        style.map('Success.TButton', background=[('active', COLORS['success_dark'])])
        
        style.configure('Secondary.TButton', background=COLORS['secondary'])
        style.map('Secondary.TButton', background=[('active', COLORS['secondary_dark'])])

        style.configure('Warning.TButton', background=COLORS['warning'])
        style.map('Warning.TButton', background=[('active', COLORS['warning_dark'])])

        style.configure('Danger.TButton', background=COLORS['danger'])
        style.map('Danger.TButton', background=[('active', COLORS['danger_dark'])])

        # --- Treeview (Inventory Table) Styling ---
        style.configure('Treeview', font=('Segoe UI', 9), rowheight=28, background=COLORS['white'], fieldbackground=COLORS['white'], borderwidth=0)
        style.configure('Treeview.Heading', font=('Segoe UI', 10, 'bold'), padding=(10, 8), background=COLORS['light'], borderwidth=0)
        style.map('Treeview.Heading', background=[('active', COLORS['border'])]) # Slight color change on hover.

        # --- Notebook (Tabs) Styling ---
        style.configure('TNotebook', background=COLORS['light'], borderwidth=0)
        style.configure('TNotebook.Tab', font=('Segoe UI', 10, 'bold'), padding=[12, 6], background=COLORS['light'], borderwidth=0)
        # The selected tab should have a white background to match the card style.
        style.map('TNotebook.Tab', background=[('selected', COLORS['white'])], expand=[("selected", (0,0,0,0))])

    def create_widgets(self):
        """Creates the main layout and all UI components of the application."""
        # The main container uses a grid layout to prioritize the table's vertical space.
        main_container = ttk.Frame(self.root, padding=15)
        main_container.pack(fill=tk.BOTH, expand=True)
        main_container.grid_rowconfigure(1, weight=1)    # Row 1 (table) will expand.
        main_container.grid_columnconfigure(0, weight=1) # Column 0 will expand.
        main_container.configure(style='light.TFrame')

        # --- Controls Panel ---
        # A Notebook widget provides a compact, tabbed interface for all controls.
        controls_notebook = ttk.Notebook(main_container)
        controls_notebook.grid(row=0, column=0, sticky='ew', pady=(0, 15))
        
        # Create each tab.
        self.create_add_tab(controls_notebook)
        self.create_search_tab(controls_notebook)
        self.create_actions_tab(controls_notebook)

        # --- Inventory Table Section ---
        table_frame = ttk.Frame(main_container, padding=15, style='Card.TFrame')
        table_frame.grid(row=1, column=0, sticky='nsew')
        table_frame.grid_rowconfigure(0, weight=1)    # Ensures the Treeview inside expands.
        table_frame.grid_columnconfigure(0, weight=1)

        # The Treeview widget acts as our main inventory display table.
        columns = ('Name', 'Quantity', 'Category')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings')
        self.tree.heading('Name', text='📝 Name')
        self.tree.heading('Quantity', text='🔢 Quantity')
        self.tree.heading('Category', text='🏷️ Category')
        self.tree.column('Name', width=400, anchor=tk.W)
        self.tree.column('Quantity', width=120, anchor=tk.CENTER)
        self.tree.column('Category', width=250, anchor=tk.W)
        
        # Add scrollbars to the table.
        tree_scroll_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        tree_scroll_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
        
        # Place the Treeview and scrollbars in the grid.
        self.tree.grid(row=0, column=0, sticky='nsew')
        tree_scroll_y.grid(row=0, column=1, sticky='ns')
        tree_scroll_x.grid(row=1, column=0, sticky='ew')
        
        # Bind double-click event to the edit function for quick editing.
        self.tree.bind('<Double-1>', self.on_double_click)

    def create_add_tab(self, notebook):
        """Creates the 'Add Item' tab with its widgets."""
        add_frame = ttk.Frame(notebook, padding=20, style='Card.TFrame')
        notebook.add(add_frame, text='➕ Add Item')
        
        ttk.Label(add_frame, text="Name:", font=("Segoe UI", 9, 'bold')).grid(row=0, column=0, sticky=tk.W, padx=(0,10), pady=5)
        self.name_entry = ttk.Entry(add_frame, width=40, font=("Segoe UI", 9))
        self.name_entry.grid(row=0, column=1, padx=(0, 20), pady=5)

        ttk.Label(add_frame, text="Quantity:", font=("Segoe UI", 9, 'bold')).grid(row=0, column=2, sticky=tk.W, padx=(0,10), pady=5)
        self.quantity_entry = ttk.Entry(add_frame, width=15, font=("Segoe UI", 9))
        self.quantity_entry.grid(row=0, column=3, padx=(0, 20), pady=5)

        ttk.Label(add_frame, text="Category:", font=("Segoe UI", 9, 'bold')).grid(row=1, column=0, sticky=tk.W, padx=(0,10), pady=5)
        self.category_combo = ttk.Combobox(add_frame, values=self.categories, width=37, state="readonly", font=("Segoe UI", 9))
        self.category_combo.grid(row=1, column=1, pady=5)
        self.category_combo.set("Select Category")

        self.add_button = ModernButton(add_frame, text="Add Item", command=self.add_item, style='Success.TButton')
        self.add_button.grid(row=1, column=3, pady=5)

    def create_search_tab(self, notebook):
        """Creates the 'Search & Filter' tab with its widgets."""
        search_frame = ttk.Frame(notebook, padding=20, style='Card.TFrame')
        notebook.add(search_frame, text='🔍 Search & Filter')
        
        ttk.Label(search_frame, text="Search by Name:", font=("Segoe UI", 9, 'bold')).grid(row=0, column=0, sticky=tk.W, padx=(0,10), pady=5)
        self.search_entry = ttk.Entry(search_frame, width=40, font=("Segoe UI", 9))
        self.search_entry.grid(row=0, column=1, padx=(0, 20), pady=5)
        # Bind the KeyRelease event to filter items as the user types.
        self.search_entry.bind('<KeyRelease>', self.filter_items)
        
        ttk.Label(search_frame, text="Filter by Category:", font=("Segoe UI", 9, 'bold')).grid(row=0, column=2, sticky=tk.W, padx=(0,10), pady=5)
        self.filter_combo = ttk.Combobox(search_frame, values=["All Categories"] + self.categories, width=25, state="readonly", font=("Segoe UI", 9))
        self.filter_combo.grid(row=0, column=3, padx=(0, 20), pady=5)
        self.filter_combo.set("All Categories")
        # Bind the ComboboxSelected event to filter items when a category is chosen.
        self.filter_combo.bind('<<ComboboxSelected>>', self.filter_items)
        
        self.clear_filter_button = ModernButton(search_frame, text="Clear", command=self.clear_filters, style='Secondary.TButton')
        self.clear_filter_button.grid(row=0, column=4, pady=5)
        
    def create_actions_tab(self, notebook):
        """Creates the 'File & Edit Actions' tab with its buttons."""
        actions_frame = ttk.Frame(notebook, padding=20, style='Card.TFrame')
        notebook.add(actions_frame, text='⚙️ File & Edit Actions')
        
        # A series of buttons for core file and item operations.
        self.load_button = ModernButton(actions_frame, text="📂 Load", command=self.load_inventory, style='Primary.TButton')
        self.load_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.save_button = ModernButton(actions_frame, text="💾 Save", command=self.save_inventory, style='Success.TButton')
        self.save_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.save_as_button = ModernButton(actions_frame, text="💾 Save As...", command=self.save_inventory_as, style='Secondary.TButton')
        self.save_as_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.edit_button = ModernButton(actions_frame, text="✏️ Edit", command=self.edit_selected_item, style='Warning.TButton')
        self.edit_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.delete_button = ModernButton(actions_frame, text="🗑️ Delete", command=self.delete_item, style='Danger.TButton')
        self.delete_button.pack(side=tk.LEFT, padx=(0, 10))
        
    # --- LOGIC METHODS ---
    def add_item(self):
        """Adds a new item to the inventory based on the input fields."""
        name = self.name_entry.get()
        quantity_str = self.quantity_entry.get()
        category = self.category_combo.get()
        if not name or not quantity_str or category == "Select Category":
            messagebox.showerror("Error", "All fields are required and category must be selected.")
            return
        try:
            quantity = int(quantity_str)
        except ValueError:
            messagebox.showerror("Error", "Quantity must be an integer.")
            return
        item = {"name": name, "quantity": quantity, "category": category}
        self.inventory.append(item)
        self.update_table()
        self.clear_entries()

    def update_table(self):
        """Clears and repopulates the inventory table from the self.inventory list."""
        # It's more efficient to delete all children at once than one by one.
        for item in self.tree.get_children(): self.tree.delete(item)
        # Re-insert all items.
        for item in self.inventory: self.tree.insert('', tk.END, values=(item['name'], item['quantity'], item['category']))

    def filter_items(self, event=None):
        """Filters the items displayed in the table based on search and category filters."""
        search_term = self.search_entry.get().lower()
        selected_category = self.filter_combo.get()
        
        # Clear the table before showing filtered results.
        for item in self.tree.get_children(): self.tree.delete(item)
        
        # Loop through the master inventory list and add matching items to the table.
        for item in self.inventory:
            name_match = search_term in item['name'].lower()
            category_match = selected_category == "All Categories" or item['category'] == selected_category
            if name_match and category_match:
                self.tree.insert('', tk.END, values=(item['name'], item['quantity'], item['category']))

    def clear_filters(self):
        """Resets the search and category filters and updates the table."""
        self.search_entry.delete(0, tk.END)
        self.filter_combo.set("All Categories")
        self.update_table()

    def clear_entries(self):
        """Clears the input fields in the 'Add Item' tab."""
        self.name_entry.delete(0, tk.END)
        self.quantity_entry.delete(0, tk.END)
        self.category_combo.set("Select Category")

    def save_inventory(self):
        """Saves the current inventory to the currently loaded file, or prompts 'Save As' if no file is loaded."""
        if self.current_file:
            try:
                with open(self.current_file, "w") as f: json.dump(self.inventory, f, indent=4)
                messagebox.showinfo("Success", f"Inventory saved to {self.current_file}")
            except Exception as e: messagebox.showerror("Error", f"Failed to save: {e}")
        else:
            # If there's no current file, treat it as a 'Save As' operation.
            self.save_inventory_as()

    def save_inventory_as(self):
        """Opens a file dialog to save the current inventory to a new file."""
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json"), ("Text files", "*.txt"), ("All files", "*.*")], title="Save Inventory As")
        if file_path:
            try:
                with open(file_path, "w") as f: json.dump(self.inventory, f, indent=4)
                self.current_file = file_path # Set the new file as the current file.
                messagebox.showinfo("Success", f"Inventory saved to {file_path}")
            except Exception as e: messagebox.showerror("Error", f"Failed to save: {e}")

    def load_inventory(self):
        """Opens a file dialog to load an inventory from a JSON file."""
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json"), ("Text files", "*.txt"), ("All files", "*.*")], title="Load Inventory File")
        if file_path:
            try:
                with open(file_path, "r") as f: self.inventory = json.load(f)
                self.current_file = file_path
                self.update_table()
                messagebox.showinfo("Success", f"Loaded from {file_path}")
            except Exception as e: messagebox.showerror("Error", f"Failed to load: {e}")

    def get_selected_item_data(self):
        """
        Finds the selected item in the Treeview and returns its corresponding
        data dictionary from the main inventory list and its Treeview ID.
        """
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showerror("Error", "No item selected.")
            return None
        
        item_id = selected_items[0]
        # The values from the treeview are strings, so we need to find the matching item in our inventory list.
        item_values = self.tree.item(item_id)['values']
        
        # Search the inventory list for the item that matches the selected row's values.
        for item in self.inventory:
            # Quantity needs to be cast to string for comparison.
            if item['name'] == item_values[0] and str(item['quantity']) == str(item_values[1]) and item['category'] == item_values[2]:
                return item, item_id
        return None

    def edit_selected_item(self):
        """Initiates the editing process for the currently selected item."""
        result = self.get_selected_item_data()
        if result: self.edit_item(result[0], result[1])

    def edit_item(self, item_data, item_id):
        """
        Opens the EditItemDialog and updates the inventory if changes are saved.

        Args:
            item_data (dict): The original data of the item being edited.
            item_id: The ID of the item in the Treeview.
        """
        dialog = EditItemDialog(self.root, item_data, self.categories)
        self.root.wait_window(dialog.dialog) # Wait for the dialog to be closed.
        
        # If the dialog's result is not None, it means the user saved changes.
        if dialog.result:
            # Find the original item in the inventory and replace it with the new data.
            for i, item in enumerate(self.inventory):
                if item == item_data:
                    self.inventory[i] = dialog.result
                    break
            self.update_table()
            messagebox.showinfo("Success", "Item updated successfully!")

    def delete_item(self):
        """Deletes the selected item(s) from the inventory after confirmation."""
        if not self.tree.selection():
            messagebox.showerror("Error", "No item selected for deletion.")
            return
            
        # Confirmation dialog is crucial for destructive actions.
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected item(s)?"):
            items_to_delete = self.tree.selection()
            # It's safer to iterate over a copy when removing items.
            inventory_copy = list(self.inventory)
            for item_id in items_to_delete:
                item_values = self.tree.item(item_id)['values']
                for inv_item in inventory_copy:
                    if str(inv_item['name']) == str(item_values[0]) and str(inv_item['quantity']) == str(item_values[1]) and str(inv_item['category']) == str(item_values[2]):
                        self.inventory.remove(inv_item)
                        break
            self.update_table()

    def on_double_click(self, event):
        """Handles the double-click event on the Treeview to edit an item."""
        result = self.get_selected_item_data()
        if result: self.edit_item(result[0], result[1])

if __name__ == "__main__":
    root = tk.Tk()
    app = InventoryApp(root)
    root.mainloop() 