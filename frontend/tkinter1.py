# main.py
import tkinter as tk
from tkinter import ttk, messagebox
import requests
from tkinter.simpledialog import askstring
import matplotlib.pyplot as plt

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
BASE_URL = "http://localhost:8000"

class TableView(tk.Frame):
    def __init__(self, parent, columns):
        super().__init__(parent)
        
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
        self.tree.pack(side="left", fill="y")
        
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

    def clear(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def insert(self, data):
        self.tree.insert("", "end", values=data)

from tkinter import simpledialog

class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory Management System")
        self.root.geometry("800x600")
        root.option_add('*Font', 'Roboto 12')

        self.main_tab = ttk.Notebook(self.root)
        self.main_tab.pack(expand=1, fill="both")

      
        self.create_view_tab()

        # Create the "Analytics" tab
        self.analytics_tab = ttk.Frame(self.main_tab)
        self.main_tab.add(self.analytics_tab, text="Analytics")

        # Add a button to fetch and display sales and capacity analytics data
        generate_button = ttk.Button(self.analytics_tab, text="Generate Analytics", command=self.generate_analytics)
        generate_button.pack()

        # # Text widget to display the JSON result
        # self.result_text = tk.Text(self.analytics_tab, height=20, width=80)
        # self.result_text.pack()

        # Create placeholders for Matplotlib plots
        self.sales_fig, self.sales_ax = plt.subplots()
        self.capacity_fig, self.capacity_ax = plt.subplots()

        # Canvas to display Matplotlib plots
        self.sales_canvas = FigureCanvasTkAgg(self.sales_fig, master=self.analytics_tab)
        self.sales_canvas.draw()
        self.sales_canvas.get_tk_widget().pack(expand=1, fill="both")

        self.capacity_canvas = FigureCanvasTkAgg(self.capacity_fig, master=self.analytics_tab)
        self.capacity_canvas.draw()
        self.capacity_canvas.get_tk_widget().pack(expand=1, fill="both")   
    def generate_analytics(self):
        # Make GET requests to fetch sales and capacity analytics data
        sales_url = "http://localhost:8000/sales-analytics"
        capacity_url = "http://localhost:8000/capacity-analytics"


        try:
            # Fetch sales analytics data
            sales_response = requests.get(sales_url)
            sales_data = sales_response.json()

            # Fetch capacity analytics data
            capacity_response = requests.get(capacity_url)
            capacity_data = capacity_response.json()

            # # Display the JSON results in the text widget
            # self.result_text.delete(1.0, tk.END)
            # self.result_text.insert(tk.END, "Sales Analytics:\n")
            # self.result_text.insert(tk.END, str(sales_data) + "\n\n")

            # self.result_text.insert(tk.END, "Capacity Analytics:\n")
            # self.result_text.insert(tk.END, str(capacity_data) + "\n")

            # Visualize sales analytics data
            self.plot_sales_analytics(sales_data)

            # Visualize capacity analytics data
            self.plot_capacity_analytics(capacity_data)

        except requests.exceptions.RequestException as e:
            # Handle any errors that occur during the request
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "Error fetching data: " + str(e))

    def plot_sales_analytics(self, data):
        self.sales_ax.clear()

        products = [item[0] for item in data]
        items_sold = [item[1] for item in data]

        self.sales_ax.bar(products, items_sold, color='skyblue')
        self.sales_ax.set_xlabel('Product')
        self.sales_ax.set_ylabel('Items Sold')
        self.sales_ax.set_title('Sales Analytics')
        self.sales_ax.tick_params(axis='x', rotation=45)

        self.sales_canvas.draw()

    def plot_capacity_analytics(self, data):
        self.capacity_ax.clear()

        sku_names = [item[1] for item in data]
        total_capacity = [item[2] for item in data]
        remaining_capacity = [item[3] for item in data]

        x = range(len(sku_names))
        width = 0.35

        self.capacity_ax.bar(x, total_capacity, width, label='Total Capacity', color='skyblue')
        self.capacity_ax.bar([i + width for i in x], remaining_capacity, width, label='Remaining Capacity', color='orange')
        self.capacity_ax.set_xticks([i + width/2 for i in x])
        self.capacity_ax.set_xticklabels(sku_names, rotation=45)
        self.capacity_ax.set_xlabel('SKU')
        self.capacity_ax.set_ylabel('Capacity')
        self.capacity_ax.set_title('Capacity Analytics')
        self.capacity_ax.legend()

        self.capacity_canvas.draw()
    def create_view_tab(self):
        view_tab = tk.Frame(self.main_tab)
        self.main_tab.add(view_tab, text="View")

        # Create a frame to contain the buttons in a row
        button_row_frame = tk.Frame(view_tab)
        button_row_frame.pack(pady=10)  # Padding for the button row frame

        # Function to switch to the selected view
        def switch_to(option):
            self.switch_view(option)

        # Create buttons for each view option
        view_options = ["Products", "Orders", "SKUs", "Suppliers"]
        for option in view_options:
            button = tk.Button(button_row_frame, text=option, command=lambda v=option: switch_to(v))
            button.pack(side="left", padx=10)  

        # Sub-tabs for different views
        self.sub_tabs = {}
        for option in view_options:
            self.sub_tabs[option] = ttk.Notebook(view_tab)
            self.sub_tabs[option].pack(expand=1, fill="both")

        # Initially select the first option
        self.switch_view(view_options[0])

    def switch_view(self, selected_view):
        selected_tab = self.sub_tabs[selected_view]

        # Hide all sub-tabs except the selected one
        for option, tab in self.sub_tabs.items():
            if tab == selected_tab:
                tab.pack(expand=1, fill="both")
            else:
                tab.pack_forget()

        # Create the selected tab if it doesn't exist yet
        if selected_view == "Products" and not selected_tab.winfo_children():
            self.create_product_tab(selected_tab)
        elif selected_view == "Orders" and not selected_tab.winfo_children():
            self.create_order_tab(selected_tab)
        elif selected_view == "SKUs" and not selected_tab.winfo_children():
            self.create_sku_tab(selected_tab)
        elif selected_view == "Suppliers" and not selected_tab.winfo_children():
            self.create_supplier_tab(selected_tab)

    def create_product_tab(self,parent):
        product_tab = tk.Frame(parent)
        parent.add(product_tab, text="Products")

        
        self.product_table = TableView(product_tab, columns=["ID", "SKU ID", "Name", "Price", "Quantity", "Supplier ID"])
        self.product_table.pack(expand=True, fill="both")
        
        self.refresh_product_table_button = tk.Button(product_tab, text="Refresh Products", command=self.refresh_product_table)
        self.refresh_product_table_button.pack(side="right", padx=5)
        
        self.delete_product_button = tk.Button(product_tab, text="Delete Product", command=self.delete_product)
        self.delete_product_button.pack(side="right", padx=5)
        
        self.update_product_button = tk.Button(product_tab, text="Update Product", command=self.update_product)
        self.update_product_button.pack(side="right", padx=5)
        
        self.add_product_button = tk.Button(product_tab, text="Add Product", command=self.add_product)
        self.add_product_button.pack(side="right", padx=5)

    def create_sku_tab(self,parent):
        sku_tab = tk.Frame(parent)
        parent.add(sku_tab, text="SKUs")
        
        self.sku_table = TableView(sku_tab, columns=["ID", "Name", "Location", "Capacity"])
        self.sku_table.pack(expand=True, fill="both")
        
        self.refresh_sku_table_button = tk.Button(sku_tab, text="Refresh SKUs", command=self.refresh_sku_table)
        self.refresh_sku_table_button.pack(side="right", padx=5)
        
        self.delete_sku_button = tk.Button(sku_tab, text="Delete SKU", command=self.delete_sku)
        self.delete_sku_button.pack(side="right", padx=5)
        
        self.update_sku_button = tk.Button(sku_tab, text="Update SKU", command=self.update_sku)
        self.update_sku_button.pack(side="right", padx=5)
        
        self.add_sku_button = tk.Button(sku_tab, text="Add SKU", command=self.add_sku)
        self.add_sku_button.pack(side="right", padx=5)

    def create_order_tab(self, parent):
        order_tab = tk.Frame(parent)
        parent.add(order_tab, text="Orders")
        
        self.order_table = TableView(order_tab, columns=["ID", "Product ID", "Quantity", "Customer Name", "Customer Email"])
        self.order_table.pack(expand=True, fill="both")
        
        self.refresh_order_table_button = tk.Button(order_tab, text="Refresh Orders", command=self.refresh_order_table)
        self.refresh_order_table_button.pack(side="right", padx=5)
        
        self.delete_order_button = tk.Button(order_tab, text="Delete Order", command=self.delete_order)
        self.delete_order_button.pack(side="right", padx=5)
        
        self.update_order_button = tk.Button(order_tab, text="Update Order", command=self.update_order)
        self.update_order_button.pack(side="right", padx=5)
        
        self.add_order_button = tk.Button(order_tab, text="Add Order", command=self.add_order)
        self.add_order_button.pack(side="right", padx=5)

    def create_supplier_tab(self, parent):
        supplier_tab = tk.Frame(parent)
        parent.add(supplier_tab, text="Suppliers")
        
        self.supplier_table = TableView(supplier_tab, columns=["ID", "Name", "Email"])
        self.supplier_table.pack(expand=True, fill="both")
        
        self.refresh_supplier_table_button = tk.Button(supplier_tab, text="Refresh Suppliers", command=self.refresh_supplier_table)
        self.refresh_supplier_table_button.pack(side="right", padx=5)
        
        self.delete_supplier_button = tk.Button(supplier_tab, text="Delete Supplier", command=self.delete_supplier)
        self.delete_supplier_button.pack(side="right", padx=5)
        
        self.update_supplier_button = tk.Button(supplier_tab, text="Update Supplier", command=self.update_supplier)
        self.update_supplier_button.pack(side="right", padx=5)
        
        self.add_supplier_button = tk.Button(supplier_tab, text="Add Supplier", command=self.add_supplier)
        self.add_supplier_button.pack(side="right", padx=5)

    def refresh_product_table(self):
        self.product_table.clear()
        products = self.get_data("/products")
        for product in products:
            self.product_table.insert(product)

    def refresh_sku_table(self):
        self.sku_table.clear()
        skus = self.get_data("/skus")
        for sku in skus:
            self.sku_table.insert(sku)

    def refresh_order_table(self):
        self.order_table.clear()
        orders = self.get_data("/orders")
        for order in orders:
            self.order_table.insert(order)

    def refresh_supplier_table(self):
        self.supplier_table.clear()
        suppliers = self.get_data("/suppliers")
        for supplier in suppliers:
            self.supplier_table.insert(supplier)

    def get_data(self, endpoint):
        response = requests.get(BASE_URL + endpoint)
        if response.status_code == 200:
            return response.json()
        else:
            messagebox.showerror("Error", "Failed to fetch data from the server.")
            return []

    def delete_product(self):
        selected_item = self.product_table.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a product to delete.")
            return
        
        confirm = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this product?")
        if confirm:
            product_id = self.product_table.tree.item(selected_item)['values'][0]
            response = requests.delete(f"{BASE_URL}/products/{product_id}")
            if response.status_code == 200:
                messagebox.showinfo("Success", "Product deleted successfully.")
                self.refresh_product_table()
            else:
                messagebox.showerror("Error", "Failed to delete product.")

    def delete_sku(self):
        selected_item = self.sku_table.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a SKU to delete.")
            return
        
        confirm = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this SKU?")
        if confirm:
            sku_id = self.sku_table.tree.item(selected_item)['values'][0]
            response = requests.delete(f"{BASE_URL}/skus/{sku_id}")
            if response.status_code == 200:
                messagebox.showinfo("Success", "SKU deleted successfully.")
                self.refresh_sku_table()
            else:
                messagebox.showerror("Error", "Failed to delete SKU.")

    def delete_order(self):
        selected_item = self.order_table.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select an order to delete.")
            return
        
        confirm = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this order?")
        if confirm:
            order_id = self.order_table.tree.item(selected_item)['values'][0]
            response = requests.delete(f"{BASE_URL}/orders/{order_id}")
            if response.status_code == 200:
                messagebox.showinfo("Success", "Order deleted successfully.")
                self.refresh_order_table()
            else:
                messagebox.showerror("Error", "Failed to delete order.")

    def delete_supplier(self):
        selected_item = self.supplier_table.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a supplier to delete.")
            return
        
        confirm = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this supplier?")
        if confirm:
            supplier_id = self.supplier_table.tree.item(selected_item)['values'][0]
            response = requests.delete(f"{BASE_URL}/suppliers/{supplier_id}")
            if response.status_code == 200:
                messagebox.showinfo("Success", "Supplier deleted successfully.")
                self.refresh_supplier_table()
            else:
                messagebox.showerror("Error", "Failed to delete supplier.")
                
    def update_product(self):
        # Create a dialog window
        dialog = tk.Toplevel(self.root)
        dialog.title("Update Product")

        # Create a frame to contain input fields
        frame = tk.Frame(dialog)
        frame.pack(padx=10, pady=10)

        # Input fields for each parameter
        input_fields = {}
        parameters = ["ID", "SKU ID", "Name", "Price", "Quantity", "Supplier ID"]
        for index, param in enumerate(parameters):
            label = tk.Label(frame, text=f"{param}:")
            label.grid(row=index, column=0, sticky="w")
            input_fields[param] = tk.Entry(frame)
            input_fields[param].grid(row=index, column=1, padx=5, pady=5)

        # Add a Submit button
        submit_button = tk.Button(frame, text="Submit", command=lambda: self.submit_updated_product(dialog, input_fields))
        submit_button.grid(row=len(parameters), columnspan=2, pady=10)

        # Add a Cancel button
        cancel_button = tk.Button(frame, text="Cancel", command=dialog.destroy)
        cancel_button.grid(row=len(parameters) + 1, columnspan=2, pady=10)

    def submit_updated_product(self, dialog, input_fields):
        # Retrieve values from input fields and update naming
        updated_data = {
            "id": int(input_fields["ID"].get()),
            "sku_id": int(input_fields["SKU ID"].get()),
            "name": input_fields["Name"].get(),
            "price": float(input_fields["Price"].get()),
            "quantity": int(input_fields["Quantity"].get()),
            "supplier_id": int(input_fields["Supplier ID"].get())
        }

        response = requests.put(f"{BASE_URL}/products/{updated_data['id']}", json=updated_data)
        if response.status_code == 200:
            messagebox.showinfo("Success", "Product updated successfully.")
            self.refresh_product_table()
            dialog.destroy()  # Close the dialog window after successful submission
        else:
            messagebox.showerror("Error", "Failed to update product.")

    def _prompt_for_data(self, existing_data=None):
        # Create a dialog box
        dialog = simpledialog.Dialog(self.root, title="Enter Data")
        
        # Create a frame to contain input fields
        frame = tk.Frame(dialog)
        frame.pack(padx=10, pady=10)
        
        # Use existing data as default values for the prompt
        # If no existing data, create empty dictionary
        existing_data = existing_data or {}

        # Create input fields for each key in existing_data
        input_fields = {}
        for key, value in existing_data.items():
            label = tk.Label(frame, text=f"{key}:")
            label.grid(row=len(input_fields), column=0, sticky="w")
            input_fields[key] = tk.Entry(frame)
            input_fields[key].insert(0, value)  # Set default value
            input_fields[key].grid(row=len(input_fields), column=1, padx=5, pady=5)
        
        # Add a button to submit data
        submit_button = tk.Button(frame, text="Submit", command=lambda: dialog.ok())
        submit_button.grid(row=len(input_fields), columnspan=2, pady=10)
        
        # Wait for dialog to close
        dialog.mainloop()
        
        # Retrieve values from input fields
        new_data = {key: input_field.get() for key, input_field in input_fields.items()}
        
        return new_data




    def add_sku(self):
        # Create a dialog window
        dialog = tk.Toplevel(self.root)
        dialog.title("Add SKU")

        # Create a frame to contain input fields
        frame = tk.Frame(dialog)
        frame.pack(padx=10, pady=10)

        # Input fields for each parameter
        input_fields = {}
        parameters = ["Name", "Location", "Capacity"]
        for index, param in enumerate(parameters):
            label = tk.Label(frame, text=f"{param}:")
            label.grid(row=index, column=0, sticky="w")
            input_fields[param] = tk.Entry(frame)
            input_fields[param].grid(row=index, column=1, padx=5, pady=5)

        # Add a Submit button
        submit_button = tk.Button(frame, text="Submit", command=lambda: self.submit_added_sku(dialog, input_fields))
        submit_button.grid(row=len(parameters), columnspan=2, pady=10)

        # Add a Cancel button
        cancel_button = tk.Button(frame, text="Cancel", command=dialog.destroy)
        cancel_button.grid(row=len(parameters) + 1, columnspan=2, pady=10)

    def submit_added_sku(self, dialog, input_fields):
        # Retrieve values from input fields
        new_data = {
            "name": input_fields["Name"].get(),
            "location": input_fields["Location"].get(),
            "capacity": int(input_fields["Capacity"].get())
        }

        response = requests.post(f"{BASE_URL}/skus/", json=new_data)
        if response.status_code == 200:
            messagebox.showinfo("Success", "SKU added successfully.")
            self.refresh_sku_table()
            dialog.destroy()  # Close the dialog window after successful submission
        else:
            messagebox.showerror("Error", "Failed to add SKU.")

    def update_order(self):
        # Create a dialog window
        dialog = tk.Toplevel(self.root)
        dialog.title("Update Order")

        # Create a frame to contain input fields
        frame = tk.Frame(dialog)
        frame.pack(padx=10, pady=10)

        # Input fields for each parameter
        input_fields = {}
        parameters = ["ID", "Product ID", "Quantity", "Customer Name", "Customer Email"]
        for index, param in enumerate(parameters):
            label = tk.Label(frame, text=f"{param}:")
            label.grid(row=index, column=0, sticky="w")
            input_fields[param] = tk.Entry(frame)
            input_fields[param].grid(row=index, column=1, padx=5, pady=5)

        # Add a Submit button
        submit_button = tk.Button(frame, text="Submit", command=lambda: self.submit_updated_order(dialog, input_fields))
        submit_button.grid(row=len(parameters), columnspan=2, pady=10)

        # Add a Cancel button
        cancel_button = tk.Button(frame, text="Cancel", command=dialog.destroy)
        cancel_button.grid(row=len(parameters) + 1, columnspan=2, pady=10)

    def submit_updated_order(self, dialog, input_fields):
        # Retrieve values from input fields and update order
        updated_data = {
            "id": int(input_fields["ID"].get()),
            "product_id": int(input_fields["Product ID"].get()),
            "quantity": int(input_fields["Quantity"].get()),
            "customer_name": input_fields["Customer Name"].get(),
            "customer_email": input_fields["Customer Email"].get()
        }

        response = requests.put(f"{BASE_URL}/orders/{updated_data['id']}", json=updated_data)
        if response.status_code == 200:
            messagebox.showinfo("Success", "Order updated successfully.")
            self.refresh_order_table()
            dialog.destroy()  # Close the dialog window after successful submission
        else:
            messagebox.showerror("Error", "Failed to update order.")


    def update_supplier(self):
        selected_item = self.supplier_table.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a supplier to update.")
            return

        supplier_id = self.supplier_table.tree.item(selected_item)['values'][0]
        response = requests.get(f"{BASE_URL}/suppliers/{supplier_id}")
        if response.status_code == 200:
            supplier_data = response.json()
            
            # Create a dialog window for updating supplier details
            dialog = tk.Toplevel(self.root)
            dialog.title("Update Supplier")

            # Create a frame to contain input fields
            frame = tk.Frame(dialog)
            frame.pack(padx=10, pady=10)

            # Input fields for ID, email, and name
            id_label = tk.Label(frame, text="ID:")
            id_label.grid(row=0, column=0, sticky="w")
            id_entry = tk.Entry(frame)
            id_entry.insert(0, supplier_data['id'])
            id_entry.grid(row=0, column=1, padx=5, pady=5)

            email_label = tk.Label(frame, text="Email:")
            email_label.grid(row=1, column=0, sticky="w")
            email_entry = tk.Entry(frame)
            email_entry.insert(0, supplier_data['email'])
            email_entry.grid(row=1, column=1, padx=5, pady=5)

            name_label = tk.Label(frame, text="Name:")
            name_label.grid(row=2, column=0, sticky="w")
            name_entry = tk.Entry(frame)
            name_entry.insert(0, supplier_data['name'])
            name_entry.grid(row=2, column=1, padx=5, pady=5)

            # Function to submit updated supplier data
            def submit_update():
                updated_data = {
                    "id": int(id_entry.get()),
                    "email": email_entry.get(),
                    "name": name_entry.get()
                }
                response = requests.put(f"{BASE_URL}/suppliers/{supplier_id}", json=updated_data)
                if response.status_code == 200:
                    messagebox.showinfo("Success", "Supplier updated successfully.")
                    self.refresh_supplier_table()
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", "Failed to update supplier.")

            # Submit button
            submit_button = tk.Button(frame, text="Submit", command=submit_update)
            submit_button.grid(row=3, columnspan=2, pady=10)

        else:
            messagebox.showerror("Error", "Failed to fetch supplier data.")

    def add_supplier(self):
        new_data = self._prompt_for_data()
        if new_data:
            response = requests.post(f"{BASE_URL}/suppliers/", json=new_data)
            if response.status_code == 200:
                messagebox.showinfo("Success", "Supplier added successfully.")
                self.refresh_supplier_table()
            else:
                messagebox.showerror("Error", "Failed to add supplier.")


    def _prompt_for_data(self, existing_data=None):
        # Create a dialog box
        dialog = simpledialog.Dialog(self.root, title="Enter Data")
        
        # Create a frame to contain input fields
        frame = tk.Frame(dialog)
        frame.pack(padx=10, pady=10)
        
        # Use existing data as default values for the prompt
        # If no existing data, create empty dictionary
        existing_data = existing_data or {}

        # Create input fields for each key in existing_data
        input_fields = {}
        for key, value in existing_data.items():
            label = tk.Label(frame, text=f"{key}:")
            label.grid(row=len(input_fields), column=0, sticky="w")
            input_fields[key] = tk.Entry(frame)
            input_fields[key].insert(0, value)  # Set default value
            input_fields[key].grid(row=len(input_fields), column=1, padx=5, pady=5)
        
        # Add a button to submit data
        submit_button = tk.Button(frame, text="Submit", command=lambda: dialog.ok())
        submit_button.grid(row=len(input_fields), columnspan=2, pady=10)
        
        # Wait for dialog to close
        dialog.mainloop()
        
        # Retrieve values from input fields
        new_data = {key: input_field.get() for key, input_field in input_fields.items()}
        
        return new_data
    def add_product(self):
        # Create a dialog window
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Product")

        # Create a frame to contain input fields
        frame = tk.Frame(dialog)
        frame.pack(padx=10, pady=10)

        # Input fields for each parameter
        input_fields = {}
        parameters = ["SKU ID", "Name", "Price", "Quantity", "Supplier ID"]
        for index, param in enumerate(parameters):
            label = tk.Label(frame, text=f"{param}:")
            label.grid(row=index, column=0, sticky="w")
            input_fields[param] = tk.Entry(frame)
            input_fields[param].grid(row=index, column=1, padx=5, pady=5)

        # Add a Submit button
        submit_button = tk.Button(frame, text="Submit", command=lambda: self.submit_product(dialog, input_fields))
        submit_button.grid(row=len(parameters), columnspan=2, pady=10)

        # Add a Cancel button
        cancel_button = tk.Button(frame, text="Cancel", command=dialog.destroy)
        cancel_button.grid(row=len(parameters) + 1, columnspan=2, pady=10)

    def submit_product(self, dialog, input_fields):
        # Retrieve values from input fields and update naming
        new_data = {
            "sku_id": int(input_fields["SKU ID"].get()),
            "name": input_fields["Name"].get(),
            "price": float(input_fields["Price"].get()),
            "quantity": int(input_fields["Quantity"].get()),
            "supplier_id": int(input_fields["Supplier ID"].get())
        }
        
        response = requests.post(f"{BASE_URL}/products/", json=new_data)
        if response.status_code == 200:
            messagebox.showinfo("Success", "Product added successfully.")
            self.refresh_product_table()
            dialog.destroy()  # Close the dialog window after successful submission
        else:
            messagebox.showerror("Error", "Failed to add product.")
    def update_sku(self):
        # Create a dialog window
        dialog = tk.Toplevel(self.root)
        dialog.title("Update Product")

        # Create a frame to contain input fields
        frame = tk.Frame(dialog)
        frame.pack(padx=10, pady=10)

        # Input fields for each parameter
        input_fields = {}
        parameters = ["ID", "Name", "Location", "Capacity"]
        for index, param in enumerate(parameters):
            label = tk.Label(frame, text=f"{param}:")
            label.grid(row=index, column=0, sticky="w")
            input_fields[param] = tk.Entry(frame)
            input_fields[param].grid(row=index, column=1, padx=5, pady=5)
        print(input_fields)
        # Add a Submit button
        submit_button = tk.Button(frame, text="Submit", command=lambda: self.submit_updated_sku(dialog, input_fields))
        submit_button.grid(row=len(parameters), columnspan=2, pady=10)

        # Add a Cancel button
        cancel_button = tk.Button(frame, text="Cancel", command=dialog.destroy)
        cancel_button.grid(row=len(parameters) + 1, columnspan=2, pady=10)

    def submit_updated_sku(self, dialog, input_fields):
        # Retrieve values from input fields and update naming
        updated_data = {
            "id": int(input_fields["ID"].get()),
            "name": input_fields["Name"].get(),
            "location": input_fields["Location"].get(),
            "capacity": int(input_fields["Capacity"].get())
        }

        response = requests.put(f"{BASE_URL}/skus/{updated_data['id']}", json=updated_data)
        if response.status_code == 200:
            messagebox.showinfo("Success", "Product updated successfully.")
            self.refresh_product_table()
            dialog.destroy()  # Close the dialog window after successful submission
        else:
            messagebox.showerror("Error", "Failed to update product.")
    def add_order(self):
        # Fetch all products
        response = requests.get(f"{BASE_URL}/products")
        if response.status_code == 200:
            products = response.json()
            
            # Convert the response format to the desired structure
            mapped_products = []
            for product in products:
                mapped_product = {
                    "ID": product[0],
                    "SKU ID": product[1],
                    "Name": product[2],
                    "Price": product[3],
                    "Quantity": product[4],
                    "Supplier ID": product[5]
                }
                mapped_products.append(mapped_product)

            # Create a dialog window
            dialog = tk.Toplevel(self.root)
            dialog.title("Add Order")

            # Create a frame to contain input fields
            frame = tk.Frame(dialog)
            frame.pack(padx=10, pady=10)

            # Dropdown menu for selecting the product
            product_label = tk.Label(frame, text="Select Product:")
            product_label.grid(row=0, column=0, sticky="w")
            product_var = tk.StringVar(dialog)
            product_var.set(mapped_products[0]["Name"])  # Default to the first product
            product_dropdown = tk.OptionMenu(frame, product_var, *[product["Name"] for product in mapped_products])
            product_dropdown.grid(row=0, column=1, padx=5, pady=5)

            # Input field for quantity
            quantity_label = tk.Label(frame, text="Quantity:")
            quantity_label.grid(row=1, column=0, sticky="w")
            quantity_entry = tk.Entry(frame)
            quantity_entry.grid(row=1, column=1, padx=5, pady=5)

            # Input field for customer name
            name_label = tk.Label(frame, text="Customer Name:")
            name_label.grid(row=2, column=0, sticky="w")
            name_entry = tk.Entry(frame)
            name_entry.grid(row=2, column=1, padx=5, pady=5)

            # Input field for customer email
            email_label = tk.Label(frame, text="Customer Email:")
            email_label.grid(row=3, column=0, sticky="w")
            email_entry = tk.Entry(frame)
            email_entry.grid(row=3, column=1, padx=5, pady=5)

            # Add a Submit button
            submit_button = tk.Button(frame, text="Submit", command=lambda: self.submit_order(dialog, mapped_products, product_var.get(), quantity_entry.get(), name_entry.get(), email_entry.get()))
            submit_button.grid(row=4, columnspan=2, pady=10)

            # Add a Cancel button
            cancel_button = tk.Button(frame, text="Cancel", command=dialog.destroy)
            cancel_button.grid(row=5, columnspan=2, pady=10)
        else:
            messagebox.showerror("Error", "Failed to fetch products.")

    def submit_order(self, dialog, products, selected_product_name, quantity, customer_name, customer_email):
        # Find the selected product ID
        selected_product_id = None
        for product in products:
            if product["Name"] == selected_product_name:
                selected_product_id = product["ID"]
                break
        
        # Validate quantity, customer name, and customer email (you can add more validation if needed)
        if not quantity.isdigit():
            messagebox.showerror("Error", "Quantity must be a positive integer.")
            return
        if not customer_name:
            messagebox.showerror("Error", "Please enter customer name.")
            return
        if not customer_email:
            messagebox.showerror("Error", "Please enter customer email.")
            return

        # Prepare the data for the POST request
        new_order_data = {
            "product_id": selected_product_id,
            "quantity": int(quantity),
            "customer_name": customer_name,
            "customer_email": customer_email
        }

        print("New order data:", new_order_data)  # Debugging print statement

        # Send the POST request to add the new order
        response = requests.post(f"{BASE_URL}/orders/", json=new_order_data)
        if response.status_code == 200:
            messagebox.showinfo("Success", "Order added successfully.")
            self.refresh_order_table()
            dialog.destroy()  # Close the dialog window after successful submission
        else:
            messagebox.showerror("Error", "Failed to add order.")

if __name__ == "__main__":
    root = tk.Tk()
    app = InventoryApp(root)
    root.mainloop()
