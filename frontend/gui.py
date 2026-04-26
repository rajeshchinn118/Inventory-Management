import tkinter as tk
from tkinter import ttk
from api import fetch_products, fetch_skus, fetch_orders

class AppGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Inventory manager")
        self.master.geometry("800x600")
        self.menu_bar = tk.Menu(self.master)
        self.master.config(menu=self.menu_bar)

        # Create View dropdown menu
        self.view_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="View", menu=self.view_menu)
        self.view_menu.add_command(label="Products", command=self.show_products)
        self.view_menu.add_command(label="SKUs", command=self.show_skus)
        self.view_menu.add_command(label="Orders", command=self.show_orders)

        self.content_frame = tk.Frame(self.master)
        self.content_frame.pack(fill=tk.BOTH, expand=True)

        self.loading_label = tk.Label(self.content_frame, text="Loading...", font=("Arial", 12))
        self.no_data_label = tk.Label(self.content_frame, text="No data exists", font=("Arial", 12), fg="red")
        self.loading_visible = False

    def setup(self):
        pass  # Add any setup logic here

    
    def display_response(self, response):
        text_box = tk.Text(self.content_frame, wrap="word")
        text_box.insert("1.0", response)
        text_box.pack(fill=tk.BOTH, expand=True)

    def show_products(self):
        self.clear_content_frame()
        self.no_data_label.pack_forget()  # Hide the "No data exists" label if it's visible

        try:
            response = fetch_products()  # Fetch products
            console.log(response)
            if not response:  # If response is empty
                self.no_data_label.config(text="No products available yet", fg="red")
                self.no_data_label.pack()
            else:
                columns = ["id", "sku_id", "name", "price", "quantity", "supplier_id"]  # Specified column names
                tree = ttk.Treeview(self.content_frame, columns=columns, show="headings")

                # Set column headings
                for col in columns:
                    tree.heading(col, text=col)

                # Insert data into the treeview
                for product in response:
                    tree.insert("", "end", values=list(product.values()))

                tree.pack(fill=tk.BOTH, expand=True)

        except Exception as e:
            print("Error fetching products:", e)



    def show_skus(self):
        self.clear_content_frame()
        self.no_data_label.pack_forget()  # Hide the "No data exists" label if it's visible

        try:
            response = fetch_skus()
            if not response:  # If response is empty
                self.no_data_label.config(text="No SKUs available yet", fg="red")
                self.no_data_label.pack()
            else:
                self.display_response(response)
        except Exception as e:
            print("Error fetching SKUs:", e)

    def show_orders(self):
        self.clear_content_frame()
        orders = fetch_orders()
        self.display_table(orders)

    def display_table(self, data):
        tree = ttk.Treeview(self.content_frame)
        tree["columns"] = tuple(data[0].keys())

        for col in tree["columns"]:
            tree.heading(col, text=col)

        for item in data:
            values = [str(item[col]) for col in tree["columns"]]
            tree.insert("", "end", values=values)

        tree.pack(fill=tk.BOTH, expand=True)

    def clear_content_frame(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
