import sys
import csv
import hashlib
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QLineEdit, QTableWidget, QTableWidgetItem, 
                             QComboBox, QMessageBox, QDialog, QDialogButtonBox, QFormLayout,
                             QFileDialog, QTextEdit, QDateEdit, QStackedWidget, QTabWidget,
                             QListWidget, QCalendarWidget, QInputDialog)
from PyQt5.QtCore import Qt, QTimer, QDate
from PyQt5.QtGui import QColor, QPalette
import sqlite3
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtCore import Qt, QTimer, QDate
from datetime import datetime, timedelta

class User:
    def __init__(self, username, role):
        self.username = username
        self.role = role

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Login")
        self.layout = QFormLayout(self)
        self.username = QLineEdit(self)
        self.password = QLineEdit(self)
        self.password.setEchoMode(QLineEdit.Password)
        self.layout.addRow("Username:", self.username)
        self.layout.addRow("Password:", self.password)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.layout.addRow(buttons)

class CreateUserDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New User")
        self.layout = QFormLayout(self)
        self.username = QLineEdit(self)
        self.password = QLineEdit(self)
        self.password.setEchoMode(QLineEdit.Password)
        self.role = QComboBox(self)
        self.role.addItems(["manager", "inventory_manager", "sales_staff"])
        self.passkey = QLineEdit(self)
        self.passkey.setEchoMode(QLineEdit.Password)
        self.layout.addRow("Username:", self.username)
        self.layout.addRow("Password:", self.password)
        self.layout.addRow("Role:", self.role)
        self.layout.addRow("Your Passkey:", self.passkey)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.layout.addRow(buttons)

class InventoryManagementSystem(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fashion Inventory Management System")
        self.setGeometry(100, 100, 1200, 800)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.current_user = None
        self.setup_database()
        self.add_test_users()
        self.login()

        self.alert_timer = QTimer(self)
        self.alert_timer.timeout.connect(self.check_low_stock)
        self.alert_timer.start(60000)  # Check every minute

        self.set_color_scheme()

    def set_color_scheme(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(240, 240, 240))
        palette.setColor(QPalette.WindowText, QColor(0, 0, 0))
        palette.setColor(QPalette.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.AlternateBase, QColor(245, 245, 245))
        palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 220))
        palette.setColor(QPalette.ToolTipText, QColor(0, 0, 0))
        palette.setColor(QPalette.Text, QColor(0, 0, 0))
        palette.setColor(QPalette.Button, QColor(220, 220, 220))
        palette.setColor(QPalette.ButtonText, QColor(0, 0, 0))
        palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        self.setPalette(palette)

    def setup_database(self):
        self.conn = sqlite3.connect('inventory.db')
        self.cursor = self.conn.cursor()
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS brands
                            (id INTEGER PRIMARY KEY, name TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS products
                            (id TEXT PRIMARY KEY, name TEXT, brand_id INTEGER, category TEXT, 
                             size TEXT, color TEXT, quantity INTEGER, price REAL, low_stock_threshold INTEGER)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS sales
                            (id INTEGER PRIMARY KEY, product_id TEXT, quantity INTEGER, 
                             total_price REAL, date TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users
                            (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, role TEXT)''')
        self.conn.commit()

    def add_test_users(self):
        test_users = [
            ('admin', 'admin123', 'manager'),
            ('inventory', 'inventory123', 'inventory_manager'),
            ('sales', 'sales123', 'sales_staff')
        ]
        for username, password, role in test_users:
            hashed_password = self.hash_password(password)
            self.cursor.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)", 
                                (username, hashed_password, role))
            print(f"Added user: {username}, role: {role}")  # Add this line
        self.conn.commit()
        print("Test users added successfully")  # Add this line
        
    def authenticate(self, username, password):
        hashed_password = self.hash_password(password)
        self.cursor.execute("SELECT role FROM users WHERE username = ? AND password = ?", (username, hashed_password))
        result = self.cursor.fetchone()
        print(f"Login attempt: username={username}, result={result}")  # Add this line
        return result[0] if result else None
    
    def print_all_users(self):
        self.cursor.execute("SELECT username, password, role FROM users")
        users = self.cursor.fetchall()
        print("All users in database:")
        for user in users:
            print(f"Username: {user[0]}, Password: {user[1]}, Role: {user[2]}")

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def login(self):
        dialog = LoginDialog(self)
        if dialog.exec_():
            username = dialog.username.text()
            password = dialog.password.text()
            role = self.authenticate(username, password)
            if role:
                self.current_user = User(username, role)
                self.setup_ui()
            else:
                QMessageBox.warning(self, "Login Failed", "Invalid username or password")
                self.close()

    def authenticate(self, username, password):
        hashed_password = self.hash_password(password)
        self.cursor.execute("SELECT role FROM users WHERE username = ? AND password = ?", (username, hashed_password))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def setup_ui(self):
        for i in reversed(range(self.layout.count())): 
            self.layout.itemAt(i).widget().setParent(None)

        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)

        inventory_tab = QWidget()
        inventory_layout = QVBoxLayout(inventory_tab)
        self.inventory_table = QTableWidget()
        inventory_layout.addWidget(self.inventory_table)
        self.tab_widget.addTab(inventory_tab, "Inventory")

        if self.current_user.role in ['manager', 'inventory_manager']:
            management_tab = QWidget()
            management_layout = QVBoxLayout(management_tab)
            management_layout.addWidget(self.create_button("Manage Brands", self.manage_brands))
            management_layout.addWidget(self.create_button("Manage Products", self.manage_products))
            self.tab_widget.addTab(management_tab, "Management")

        if self.current_user.role in ['manager', 'sales_staff']:
            sales_tab = QWidget()
            sales_layout = QVBoxLayout(sales_tab)
            sales_layout.addWidget(self.create_button("Process Sale", self.process_sale))
            sales_layout.addWidget(self.create_button("Generate Bill", self.generate_bill))
            self.tab_widget.addTab(sales_tab, "Sales")

        if self.current_user.role == 'manager':
            reports_tab = QWidget()
            reports_layout = QVBoxLayout(reports_tab)
            reports_layout.addWidget(self.create_button("Sales Analysis", self.sales_analysis))
            reports_layout.addWidget(self.create_button("Inventory Analysis", self.inventory_analysis))
            reports_layout.addWidget(self.create_button("Export Data", self.export_data))
            self.tab_widget.addTab(reports_tab, "Reports")

        if self.current_user.role == 'manager':
            admin_tab = QWidget()
            admin_layout = QVBoxLayout(admin_tab)
            admin_layout.addWidget(self.create_button("Create New User", self.create_new_user))
            self.tab_widget.addTab(admin_tab, "Admin")
            
        self.update_inventory_table()
    
    def create_button(self, text, function):
        button = QPushButton(text)
        button.clicked.connect(function)
        return button

    def update_inventory_table(self):
        self.cursor.execute('''SELECT p.id, p.name, b.name, p.category, p.size, p.color, p.quantity, p.price 
                               FROM products p JOIN brands b ON p.brand_id = b.id''')
        data = self.cursor.fetchall()
        self.inventory_table.setColumnCount(8)
        self.inventory_table.setHorizontalHeaderLabels(["ID", "Name", "Brand", "Category", "Size", "Color", "Quantity", "Price"])
        self.inventory_table.setRowCount(len(data))
        for row, item in enumerate(data):
            for col, value in enumerate(item):
                self.inventory_table.setItem(row, col, QTableWidgetItem(str(value)))
        self.inventory_table.resizeColumnsToContents()

    def manage_brands(self):
        # Implement brand management functionalit
        dialog = QDialog(self)
        dialog.setWindowTitle("Manage Brands")
        layout = QVBoxLayout(dialog)

        brand_name = QLineEdit(dialog)
        add_button = QPushButton("Add Brand", dialog)
        add_button.clicked.connect(lambda: self.add_brand(brand_name.text()))

        layout.addWidget(QLabel("Brand Name:"))
        layout.addWidget(brand_name)
        layout.addWidget(add_button)

        brand_list = QTableWidget(dialog)
        brand_list.setColumnCount(2)
        brand_list.setHorizontalHeaderLabels(["ID", "Name"])
        layout.addWidget(brand_list)

        self.update_brand_list(brand_list)

        dialog.exec_()
        
    def add_brand(self, name):
        self.cursor.execute("INSERT INTO brands (name) VALUES (?)", (name,))
        self.conn.commit()
        QMessageBox.information(self, "Success", f"Brand '{name}' added successfully")

    def update_brand_list(self, table):
        self.cursor.execute("SELECT * FROM brands")
        brands = self.cursor.fetchall()
        table.setRowCount(len(brands))
        for row, brand in enumerate(brands):
            table.setItem(row, 0, QTableWidgetItem(str(brand[0])))
            table.setItem(row, 1, QTableWidgetItem(brand[1]))

    def manage_products(self):
        # Implement product management functionality
        dialog = QDialog(self)
        dialog.setWindowTitle("Manage Products")
        layout = QVBoxLayout(dialog)

        form_layout = QFormLayout()
        product_name = QLineEdit(dialog)
        brand_combo = QComboBox(dialog)
        category_combo = QComboBox(dialog)
        size = QLineEdit(dialog)
        color = QLineEdit(dialog)
        quantity = QLineEdit(dialog)
        price = QLineEdit(dialog)
        low_stock_threshold = QLineEdit(dialog)

        self.cursor.execute("SELECT id, name FROM brands")
        brands = self.cursor.fetchall()
        for brand in brands:
            brand_combo.addItem(brand[1], brand[0])

        category_combo.addItems(["Tops", "Bottoms", "Dresses", "Accessories", "Footwear"])

        form_layout.addRow("Name:", product_name)
        form_layout.addRow("Brand:", brand_combo)
        form_layout.addRow("Category:", category_combo)
        form_layout.addRow("Size:", size)
        form_layout.addRow("Color:", color)
        form_layout.addRow("Quantity:", quantity)
        form_layout.addRow("Price:", price)
        form_layout.addRow("Low Stock Threshold:", low_stock_threshold)

        layout.addLayout(form_layout)

        add_button = QPushButton("Add Product", dialog)
        add_button.clicked.connect(lambda: self.add_product(
            product_name.text(), brand_combo.currentText(), brand_combo.currentData(),
            category_combo.currentText(), size.text(), color.text(), quantity.text(), price.text(),
            low_stock_threshold.text()
        ))
        layout.addWidget(add_button)

        dialog.exec_()
        
    def add_product(self, name, brand_name, brand_id, category, size, color, quantity, price, low_stock_threshold):
        try:
            # Generate product ID
            product_id = f"{brand_name.upper()}-{name.upper()}-{self.generate_unique_id()}"
            
            self.cursor.execute('''INSERT INTO products 
                                (id, name, brand_id, category, size, color, quantity, price, low_stock_threshold) 
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                                (product_id, name, brand_id, category, size, color, int(quantity), float(price), int(low_stock_threshold)))
            self.conn.commit()
            QMessageBox.information(self, "Success", f"Product '{name}' added successfully with ID: {product_id}")
            self.update_inventory_table()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "Product ID conflict. Please try again.")
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid quantity, price, or low stock threshold")

    def generate_unique_id(self):
        self.cursor.execute("SELECT MAX(CAST(SUBSTR(id, -3) AS INTEGER)) FROM products")
        max_id = self.cursor.fetchone()[0]
        return f"{(max_id or 0) + 1:03d}"

    def view_reports(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("View Reports")
        layout = QVBoxLayout(dialog)

        report_type = QComboBox(dialog)
        report_type.addItems(["Sales Report", "Inventory Report", "Top Selling Items", "Inventory Turnover"])
        
        date_range = QComboBox(dialog)
        date_range.addItems(["Daily", "Weekly", "Monthly"])
        
        date_select = QDateEdit(dialog)
        date_select.setDate(QDate.currentDate())
        
        generate_button = QPushButton("Generate Report", dialog)
        generate_button.clicked.connect(lambda: self.generate_report(report_type.currentText(), date_range.currentText(), date_select.date()))

        layout.addWidget(report_type)
        layout.addWidget(date_range)
        layout.addWidget(date_select)
        layout.addWidget(generate_button)

        self.report_table = QTableWidget(dialog)
        layout.addWidget(self.report_table)

        dialog.exec_()

    def generate_report(self, report_type, date_range, selected_date):
        if report_type == "Sales Report":
            self.generate_sales_report(date_range, selected_date)
        elif report_type == "Inventory Report":
            self.generate_inventory_report()
        elif report_type == "Top Selling Items":
            self.generate_top_selling_items(date_range, selected_date)
        elif report_type == "Inventory Turnover":
            self.generate_inventory_turnover(date_range, selected_date)

    def generate_sales_report(self, date_range, selected_date):
        date_format = "%Y-%m-%d"
        if date_range == "Daily":
            start_date = selected_date.toString(date_format)
            end_date = start_date
        elif date_range == "Weekly":
            start_date = selected_date.addDays(-6).toString(date_format)
            end_date = selected_date.toString(date_format)
        else:  # Monthly
            start_date = selected_date.addDays(-30).toString(date_format)
            end_date = selected_date.toString(date_format)

        self.cursor.execute('''SELECT sales.date, products.name, sales.quantity, sales.total_price 
                               FROM sales JOIN products ON sales.product_id = products.id 
                               WHERE sales.date BETWEEN ? AND ?
                               ORDER BY sales.date DESC''', (start_date, end_date))
        data = self.cursor.fetchall()
        headers = ["Date", "Product", "Quantity", "Total Price"]
        self.populate_report_table(headers, data)

    def generate_inventory_report(self):
        self.cursor.execute('''SELECT products.id, products.name, brands.name, products.category, products.quantity 
                               FROM products JOIN brands ON products.brand_id = brands.id''')
        data = self.cursor.fetchall()
        headers = ["Product ID", "Product Name", "Brand", "Category", "Quantity"]
        self.populate_report_table(headers, data)

    def generate_top_selling_items(self, date_range, selected_date):
        date_format = "%Y-%m-%d"
        if date_range == "Daily":
            start_date = selected_date.toString(date_format)
            end_date = start_date
        elif date_range == "Weekly":
            start_date = selected_date.addDays(-6).toString(date_format)
            end_date = selected_date.toString(date_format)
        else:  # Monthly
            start_date = selected_date.addDays(-30).toString(date_format)
            end_date = selected_date.toString(date_format)

        self.cursor.execute('''SELECT products.name, SUM(sales.quantity) as total_sold 
                               FROM sales JOIN products ON sales.product_id = products.id 
                               WHERE sales.date BETWEEN ? AND ?
                               GROUP BY products.id ORDER BY total_sold DESC LIMIT 10''', (start_date, end_date))
        data = self.cursor.fetchall()
        headers = ["Product Name", "Total Sold"]
        self.populate_report_table(headers, data)

    def generate_inventory_turnover(self, date_range, selected_date):
        date_format = "%Y-%m-%d"
        if date_range == "Daily":
            start_date = selected_date.addDays(-1).toString(date_format)
            end_date = selected_date.toString(date_format)
        elif date_range == "Weekly":
            start_date = selected_date.addDays(-7).toString(date_format)
            end_date = selected_date.toString(date_format)
        else:  # Monthly
            start_date = selected_date.addDays(-30).toString(date_format)
            end_date = selected_date.toString(date_format)

        self.cursor.execute('''SELECT p.name, 
                               SUM(s.quantity) as units_sold,
                               AVG(p.quantity) as avg_inventory,
                               CASE WHEN AVG(p.quantity) > 0 
                                    THEN CAST(SUM(s.quantity) AS FLOAT) / AVG(p.quantity)
                                    ELSE 0 
                               END as turnover_rate
                               FROM products p
                               LEFT JOIN sales s ON p.id = s.product_id AND s.date BETWEEN ? AND ?
                               GROUP BY p.id
                               ORDER BY turnover_rate DESC''', (start_date, end_date))
        data = self.cursor.fetchall()
        headers = ["Product Name", "Units Sold", "Average Inventory", "Turnover Rate"]
        self.populate_report_table(headers, data)

    def populate_report_table(self, headers, data):
        self.report_table.setColumnCount(len(headers))
        self.report_table.setRowCount(len(data))
        self.report_table.setHorizontalHeaderLabels(headers)
        for row, record in enumerate(data):
            for col, value in enumerate(record):
                self.report_table.setItem(row, col, QTableWidgetItem(str(value))) 
                   
    def export_data(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Export Data", "", "CSV Files (*.csv);;All Files (*)", options=options)
        if file_name:
            try:
                with open(file_name, 'w', newline='') as csvfile:
                    csvwriter = csv.writer(csvfile)
                    self.cursor.execute('''SELECT products.id, products.name, brands.name, products.category, 
                                           products.size, products.color, products.quantity, products.price,
                                           products.low_stock_threshold
                                           FROM products JOIN brands ON products.brand_id = brands.id''')
                    rows = self.cursor.fetchall()
                    csvwriter.writerow(["ID", "Name", "Brand", "Category", "Size", "Color", "Quantity", "Price", "Low Stock Threshold"])
                    csvwriter.writerows(rows)
                QMessageBox.information(self, "Success", f"Data exported successfully to {file_name}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to export data: {str(e)}")
                
    def remove_item():
        current_row = selected_items.currentRow()
        if current_row > -1:
            selected_items.removeRow(current_row)
            update_total()

    def process_sale(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Process Sale")
        layout = QVBoxLayout(dialog)

        # Product search
        search_layout = QHBoxLayout()
        search_input = QLineEdit()
        search_button = QPushButton("Search")
        search_layout.addWidget(search_input)
        search_layout.addWidget(search_button)
        layout.addLayout(search_layout)

        # Search results
        results_list = QListWidget()
        layout.addWidget(results_list)

        # Selected items
        selected_items = QTableWidget()
        selected_items.setColumnCount(5)
        selected_items.setHorizontalHeaderLabels(["Product ID", "Product", "Quantity", "Price", "Total"])
        layout.addWidget(selected_items)

        # Total
        total_label = QLabel("Total: $0.00")
        layout.addWidget(total_label)

        # Buttons
        button_layout = QHBoxLayout()
        add_button = QPushButton("Add to Bill")
        remove_button = QPushButton("Remove Item")
        process_button = QPushButton("Process Sale")
        button_layout.addWidget(add_button)
        button_layout.addWidget(remove_button)
        button_layout.addWidget(process_button)
        layout.addLayout(button_layout)

        def search_products():
            query = search_input.text()
            self.cursor.execute('''SELECT p.id, p.name, b.name, p.price, p.quantity 
                                FROM products p JOIN brands b ON p.brand_id = b.id 
                                WHERE p.name LIKE ? OR b.name LIKE ?''', 
                                ('%' + query + '%', '%' + query + '%'))
            results = self.cursor.fetchall()
            results_list.clear()
            for result in results:
                results_list.addItem(f"{result[0]} - {result[1]} ({result[2]}) - ${result[3]:.2f} - Stock: {result[4]}")
                
            
        def update_total():
            total = sum(float(selected_items.item(row, 4).text()[1:]) for row in range(selected_items.rowCount()))
            total_label.setText(f"Total: ${total:.2f}")
                
        
        def add_to_bill():
            selected_item = results_list.currentItem()
            if selected_item:
                product_id = selected_item.text().split(' - ')[0]
                self.cursor.execute("SELECT name, price, quantity FROM products WHERE id = ?", (product_id,))
                product = self.cursor.fetchone()
                available_quantity = product[2]
                quantity, ok = QInputDialog.getInt(dialog, "Quantity", f"Enter quantity (max {available_quantity}):", 1, 1, available_quantity)
                if ok:
                    row = selected_items.rowCount()
                    selected_items.insertRow(row)
                    selected_items.setItem(row, 0, QTableWidgetItem(product_id))
                    selected_items.setItem(row, 1, QTableWidgetItem(product[0]))
                    selected_items.setItem(row, 2, QTableWidgetItem(str(quantity)))
                    selected_items.setItem(row, 3, QTableWidgetItem(f"${product[1]:.2f}"))
                    total = quantity * product[1]
                    selected_items.setItem(row, 4, QTableWidgetItem(f"${total:.2f}"))
                    update_total()

        def process_sale():
            if selected_items.rowCount() == 0:
                QMessageBox.warning(dialog, "No Items", "Please add items to the bill before processing.")
                return

            for row in range(selected_items.rowCount()):
                product_id = selected_items.item(row, 0).text()
                quantity = int(selected_items.item(row, 2).text())
                total_price = float(selected_items.item(row, 4).text()[1:])
                
                # Check if there's enough stock
                self.cursor.execute("SELECT quantity FROM products WHERE id = ?", (product_id,))
                current_stock = self.cursor.fetchone()[0]
                if current_stock < quantity:
                    QMessageBox.warning(dialog, "Insufficient Stock", f"Not enough stock for product {product_id}. Current stock: {current_stock}")
                    return

                # Update stock and add to sales
                self.cursor.execute("UPDATE products SET quantity = quantity - ? WHERE id = ?", (quantity, product_id))
                self.cursor.execute("INSERT INTO sales (product_id, quantity, total_price, date) VALUES (?, ?, ?, ?)",
                                    (product_id, quantity, total_price, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

            self.conn.commit()
            self.update_inventory_table()
            QMessageBox.information(dialog, "Sale Processed", "Sale has been processed successfully!")
            self.generate_bill(selected_items)
            dialog.accept()

        search_button.clicked.connect(search_products)
        add_button.clicked.connect(add_to_bill)
        remove_button.clicked.connect(self.remove_item)
        process_button.clicked.connect(process_sale)

        dialog.exec_()

        
    def generate_bill(self, sale_items):
        dialog = QDialog(self)
        dialog.setWindowTitle("Generated Bill")
        layout = QVBoxLayout(dialog)

        # Bill content
        bill_text = QTextEdit()
        bill_text.setReadOnly(True)
        layout.addWidget(bill_text)

        # Buttons
        button_layout = QHBoxLayout()
        print_button = QPushButton("Print Bill")
        close_button = QPushButton("Close")
        button_layout.addWidget(print_button)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)

        def update_bill():
                bill_content = "Fashion Inventory Management System\n"
                bill_content += "--------------------------------\n\n"
                bill_content += f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                bill_content += "Items:\n"
                bill_content += "--------------------------------\n"
                total = 0
                for row in range(sale_items.rowCount()):
                    product = sale_items.item(row, 1).text()
                    quantity = int(sale_items.item(row, 2).text())
                    price = float(sale_items.item(row, 3).text()[1:])
                    item_total = float(sale_items.item(row, 4).text()[1:])
                    bill_content += f"{product} x{quantity} @ INR{price:.2f}: INR{item_total:.2f}\n"
                    total += item_total
                bill_content += "--------------------------------\n"
                bill_content += f"Total: ${total:.2f}\n"
                bill_text.setPlainText(bill_content)

        def print_bill():
                # In a real application, this would interface with a printer
                QMessageBox.information(dialog, "Print Bill", "Bill sent to printer.")

        update_bill()
        print_button.clicked.connect(print_bill)
        close_button.clicked.connect(dialog.accept)
        dialog.exec_()

    def sales_analysis(self):
            dialog = QDialog(self)
            dialog.setWindowTitle("Sales Analysis")
            layout = QVBoxLayout(dialog)

            # Date range selection
            date_layout = QHBoxLayout()
            start_date = QDateEdit()
            end_date = QDateEdit()
            start_date.setDate(QDate.currentDate().addDays(-30))
            end_date.setDate(QDate.currentDate())
            date_layout.addWidget(QLabel("Start Date:"))
            date_layout.addWidget(start_date)
            date_layout.addWidget(QLabel("End Date:"))
            date_layout.addWidget(end_date)
            layout.addLayout(date_layout)

            # Graph
            figure = plt.figure(figsize=(10, 5))
            canvas = FigureCanvas(figure)
            layout.addWidget(canvas)

            # Analysis text
            analysis_text = QTextEdit()
            analysis_text.setReadOnly(True)
            layout.addWidget(analysis_text)

            def update_analysis():
                start = start_date.date().toString(Qt.ISODate)
                end = end_date.date().addDays(1).toString(Qt.ISODate)  # Include the end date

                # Fetch sales data
                self.cursor.execute('''SELECT date(s.date) as sale_date, SUM(s.total_price) as daily_total,
                                    SUM(s.quantity) as daily_quantity
                                    FROM sales s
                                    WHERE s.date BETWEEN ? AND ?
                                    GROUP BY sale_date
                                    ORDER BY sale_date''', (start, end))
                sales_data = self.cursor.fetchall()

                # Prepare data for plotting
                dates = [datetime.strptime(row[0], '%Y-%m-%d') for row in sales_data]
                totals = [row[1] for row in sales_data]
                quantities = [row[2] for row in sales_data]

                # Plot the graph
                figure.clear()
                ax1 = figure.add_subplot(111)
                ax1.plot(dates, totals, label='Total Sales ($)', color='blue')
                ax1.set_xlabel('Date')
                ax1.set_ylabel('Total Sales ($)', color='blue')
                ax1.tick_params(axis='y', labelcolor='blue')

                ax2 = ax1.twinx()
                ax2.plot(dates, quantities, label='Items Sold', color='red')
                ax2.set_ylabel('Items Sold', color='red')
                ax2.tick_params(axis='y', labelcolor='red')

                ax1.set_title('Daily Sales and Items Sold')
                figure.legend(loc="upper right", bbox_to_anchor=(1,1), bbox_transform=ax1.transAxes)
                figure.autofmt_xdate()
                canvas.draw()

                # Prepare analysis text
                total_sales = sum(totals)
                total_items = sum(quantities)
                num_days = len(sales_data)
                avg_daily_sales = total_sales / num_days if num_days else 0
                avg_daily_items = total_items / num_days if num_days else 0

                analysis = f"Total Sales: ${total_sales:.2f}\n"
                analysis += f"Total Items Sold: {total_items}\n"
                analysis += f"Number of Days: {num_days}\n"
                analysis += f"Average Daily Sales: ${avg_daily_sales:.2f}\n"
                analysis += f"Average Daily Items Sold: {avg_daily_items:.2f}\n"
                if totals:
                    analysis += f"Highest Daily Sales: INR{max(totals):.2f}\n"
                    analysis += f"Lowest Daily Sales: ${min(totals):.2f}\n"
                analysis_text.setPlainText(analysis)

            update_button = QPushButton("Update Analysis")
            update_button.clicked.connect(update_analysis)
            layout.addWidget(update_button)

            update_analysis()  # Initial update
            dialog.exec_()
            
    def add_product(self, name, brand_name, brand_id, category, size, color, quantity, price, low_stock_threshold):
        try:
            # Generate product ID
            product_id = f"{brand_name.upper()}-{name.upper()}-{self.generate_unique_id()}"
            
            self.cursor.execute('''INSERT INTO products 
                                (id, name, brand_id, category, size, color, quantity, price, low_stock_threshold) 
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                                (product_id, name, brand_id, category, size, color, int(quantity), float(price), int(low_stock_threshold)))
            self.conn.commit()
            QMessageBox.information(self, "Success", f"Product '{name}' added successfully with ID: {product_id}")
            self.update_inventory_table()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "Product ID conflict. Please try again.")
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid quantity, price, or low stock threshold")

    def generate_unique_id(self):
        self.cursor.execute("SELECT MAX(CAST(SUBSTR(id, -3) AS INTEGER)) FROM products")
        max_id = self.cursor.fetchone()[0]
        return f"{(max_id or 0) + 1:03d}"

    def view_reports(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("View Reports")
        layout = QVBoxLayout(dialog)

        report_type = QComboBox(dialog)
        report_type.addItems(["Sales Report", "Inventory Report", "Top Selling Items", "Inventory Turnover"])
        
        date_range = QComboBox(dialog)
        date_range.addItems(["Daily", "Weekly", "Monthly"])
        
        date_select = QDateEdit(dialog)
        date_select.setDate(QDate.currentDate())
        
        generate_button = QPushButton("Generate Report", dialog)
        generate_button.clicked.connect(lambda: self.generate_report(report_type.currentText(), date_range.currentText(), date_select.date()))

        layout.addWidget(report_type)
        layout.addWidget(date_range)
        layout.addWidget(date_select)
        layout.addWidget(generate_button)

        self.report_table = QTableWidget(dialog)
        layout.addWidget(self.report_table)

        dialog.exec_()

    def generate_report(self, report_type, date_range, selected_date):
        if report_type == "Sales Report":
            self.generate_sales_report(date_range, selected_date)
        elif report_type == "Inventory Report":
            self.generate_inventory_report()
        elif report_type == "Top Selling Items":
            self.generate_top_selling_items(date_range, selected_date)
        elif report_type == "Inventory Turnover":
            self.generate_inventory_turnover(date_range, selected_date)

    def generate_sales_report(self, date_range, selected_date):
        date_format = "%Y-%m-%d"
        if date_range == "Daily":
            start_date = selected_date.toString(date_format)
            end_date = start_date
        elif date_range == "Weekly":
            start_date = selected_date.addDays(-6).toString(date_format)
            end_date = selected_date.toString(date_format)
        else:  # Monthly
            start_date = selected_date.addDays(-30).toString(date_format)
            end_date = selected_date.toString(date_format)

        self.cursor.execute('''SELECT sales.date, products.name, sales.quantity, sales.total_price 
                               FROM sales JOIN products ON sales.product_id = products.id 
                               WHERE sales.date BETWEEN ? AND ?
                               ORDER BY sales.date DESC''', (start_date, end_date))
        data = self.cursor.fetchall()
        headers = ["Date", "Product", "Quantity", "Total Price"]
        self.populate_report_table(headers, data)

    def generate_inventory_report(self):
        self.cursor.execute('''SELECT products.id, products.name, brands.name, products.category, products.quantity 
                               FROM products JOIN brands ON products.brand_id = brands.id''')
        data = self.cursor.fetchall()
        headers = ["Product ID", "Product Name", "Brand", "Category", "Quantity"]
        self.populate_report_table(headers, data)

    def generate_top_selling_items(self, date_range, selected_date):
        date_format = "%Y-%m-%d"
        if date_range == "Daily":
            start_date = selected_date.toString(date_format)
            end_date = start_date
        elif date_range == "Weekly":
            start_date = selected_date.addDays(-6).toString(date_format)
            end_date = selected_date.toString(date_format)
        else:  # Monthly
            start_date = selected_date.addDays(-30).toString(date_format)
            end_date = selected_date.toString(date_format)

        self.cursor.execute('''SELECT products.name, SUM(sales.quantity) as total_sold 
                               FROM sales JOIN products ON sales.product_id = products.id 
                               WHERE sales.date BETWEEN ? AND ?
                               GROUP BY products.id ORDER BY total_sold DESC LIMIT 10''', (start_date, end_date))
        data = self.cursor.fetchall()
        headers = ["Product Name", "Total Sold"]
        self.populate_report_table(headers, data)

    def generate_inventory_turnover(self, date_range, selected_date):
        date_format = "%Y-%m-%d"
        if date_range == "Daily":
            start_date = selected_date.addDays(-1).toString(date_format)
            end_date = selected_date.toString(date_format)
        elif date_range == "Weekly":
            start_date = selected_date.addDays(-7).toString(date_format)
            end_date = selected_date.toString(date_format)
        else:  # Monthly
            start_date = selected_date.addDays(-30).toString(date_format)
            end_date = selected_date.toString(date_format)

        self.cursor.execute('''SELECT p.name, 
                               SUM(s.quantity) as units_sold,
                               AVG(p.quantity) as avg_inventory,
                               CASE WHEN AVG(p.quantity) > 0 
                                    THEN CAST(SUM(s.quantity) AS FLOAT) / AVG(p.quantity)
                                    ELSE 0 
                               END as turnover_rate
                               FROM products p
                               LEFT JOIN sales s ON p.id = s.product_id AND s.date BETWEEN ? AND ?
                               GROUP BY p.id
                               ORDER BY turnover_rate DESC''', (start_date, end_date))
        data = self.cursor.fetchall()
        headers = ["Product Name", "Units Sold", "Average Inventory", "Turnover Rate"]
        self.populate_report_table(headers, data)

    def populate_report_table(self, headers, data):
        self.report_table.setColumnCount(len(headers))
        self.report_table.setRowCount(len(data))
        self.report_table.setHorizontalHeaderLabels(headers)
        for row, record in enumerate(data):
            for col, value in enumerate(record):
                self.report_table.setItem(row, col, QTableWidgetItem(str(value))) 
                   
    def export_data(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Export Data", "", "CSV Files (*.csv);;All Files (*)", options=options)
        if file_name:
            try:
                with open(file_name, 'w', newline='') as csvfile:
                    csvwriter = csv.writer(csvfile)
                    self.cursor.execute('''SELECT products.id, products.name, brands.name, products.category, 
                                           products.size, products.color, products.quantity, products.price,
                                           products.low_stock_threshold
                                           FROM products JOIN brands ON products.brand_id = brands.id''')
                    rows = self.cursor.fetchall()
                    csvwriter.writerow(["ID", "Name", "Brand", "Category", "Size", "Color", "Quantity", "Price", "Low Stock Threshold"])
                    csvwriter.writerows(rows)
                QMessageBox.information(self, "Success", f"Data exported successfully to {file_name}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to export data: {str(e)}")
        layout.addLayout(date_layout)

        # Graph
        figure = plt.figure(figsize=(10, 5))
        canvas = FigureCanvas(figure)
        layout.addWidget(canvas)

        # Analysis text
        analysis_text = QTextEdit()
        analysis_text.setReadOnly(True)
        layout.addWidget(analysis_text)

        def update_analysis():
            start = start_date.date().toString(Qt.ISODate)
            end = end_date.date().toString(Qt.ISODate)
            
            # Fetch sales data
            self.cursor.execute('''SELECT date(s.date) as sale_date, SUM(s.total_price) as daily_total
                                   FROM sales s
                                   WHERE s.date BETWEEN ? AND ?
                                   GROUP BY sale_date
                                   ORDER BY sale_date''', (start, end))
            sales_data = self.cursor.fetchall()

            # Prepare data for plotting
            dates = [datetime.strptime(row[0], '%Y-%m-%d') for row in sales_data]
            totals = [row[1] for row in sales_data]

            # Plot the graph
            figure.clear()
            ax = figure.add_subplot(111)
            ax.plot(dates, totals)
            ax.set_title('Daily Sales')
            ax.set_xlabel('Date')
            ax.set_ylabel('Total Sales ($)')
            figure.autofmt_xdate()
            canvas.draw()

            # Prepare analysis text
            total_sales = sum(totals)
            avg_daily_sales = total_sales / len(sales_data) if sales_data else 0
            analysis = f"Total Sales: ${total_sales:.2f}\n"
            analysis += f"Average Daily Sales: ${avg_daily_sales:.2f}\n"
            analysis += f"Number of Days: {len(sales_data)}\n"
            if totals:
                analysis += f"Highest Daily Sales: ${max(totals):.2f}\n"
                analysis += f"Lowest Daily Sales: ${min(totals):.2f}\n"
            analysis_text.setPlainText(analysis)

        update_button = QPushButton("Update Analysis")
        update_button.clicked.connect(update_analysis)
        layout.addWidget(update_button)

        update_analysis()  # Initial update
        dialog.exec_()

    def inventory_analysis(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Inventory Analysis")
        layout = QVBoxLayout(dialog)

        # Graph
        figure = plt.figure(figsize=(10, 5))
        canvas = FigureCanvas(figure)
        layout.addWidget(canvas)

        # Analysis text
        analysis_text = QTextEdit()
        analysis_text.setReadOnly(True)
        layout.addWidget(analysis_text)

        def update_analysis():
            # Fetch inventory data
            self.cursor.execute('''SELECT p.category, SUM(p.quantity) as total_quantity, 
                                   SUM(p.quantity * p.price) as total_value
                                   FROM products p
                                   GROUP BY p.category''')
            inventory_data = self.cursor.fetchall()

            # Prepare data for plotting
            categories = [row[0] for row in inventory_data]
            quantities = [row[1] for row in inventory_data]
            values = [row[2] for row in inventory_data]

            # Plot the graphs
            figure.clear()
            ax1 = figure.add_subplot(121)
            ax1.bar(categories, quantities)
            ax1.set_title('Inventory Quantity by Category')
            ax1.set_xlabel('Category')
            ax1.set_ylabel('Quantity')

            ax2 = figure.add_subplot(122)
            ax2.bar(categories, values)
            ax2.set_title('Inventory Value by Category')
            ax2.set_xlabel('Category')
            ax2.set_ylabel('Value ($)')

            figure.tight_layout()
            canvas.draw()

            # Prepare analysis text
            total_quantity = sum(quantities)
            total_value = sum(values)
            analysis = f"Total Inventory Quantity: {total_quantity}\n"
            analysis += f"Total Inventory Value: ${total_value:.2f}\n\n"
            analysis += "Top 5 Categories by Value:\n"
            sorted_categories = sorted(zip(categories, values), key=lambda x: x[1], reverse=True)
            for category, value in sorted_categories[:5]:
                analysis += f"{category}: ${value:.2f}\n"
            analysis_text.setPlainText(analysis)

        update_button = QPushButton("Update Analysis")
        update_button.clicked.connect(update_analysis)
        layout.addWidget(update_button)

        update_analysis()  # Initial update
        dialog.exec_()

    def export_data(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Export Data", "", 
                                                   "CSV Files (*.csv);;All Files (*)", options=options)
        if file_name:
            with open(file_name, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Product ID", "Name", "Brand", "Category", "Size", "Color", "Quantity", "Price"])
                self.cursor.execute('''SELECT p.id, p.name, b.name, p.category, p.size, p.color, p.quantity, p.price 
                                       FROM products p JOIN brands b ON p.brand_id = b.id''')
                for row in self.cursor.fetchall():
                    writer.writerow(row)
            QMessageBox.information(self, "Export Successful", f"Data exported to {file_name}")

    def check_low_stock(self):
        self.cursor.execute('''SELECT p.name, p.quantity, p.low_stock_threshold 
                               FROM products p 
                               WHERE p.quantity <= p.low_stock_threshold''')
        low_stock_items = self.cursor.fetchall()
        if low_stock_items:
            message = "Low stock alert:\n\n"
            for item in low_stock_items:
                message += f"{item[0]}: {item[1]} in stock (Threshold: {item[2]})\n"
            QMessageBox.warning(self, "Low Stock Alert", message)
            
    def create_new_user(self):
        if self.current_user.role != 'manager':
            QMessageBox.warning(self, "Permission Denied", "Only managers can create new users.")
            return

        dialog = CreateUserDialog(self)
        if dialog.exec_():
            username = dialog.username.text()
            password = dialog.password.text()
            role = dialog.role.currentText()

            hashed_password = self.hash_password(password)
            try:
                self.cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                                    (username, hashed_password, role))
                self.conn.commit()
                QMessageBox.information(self, "User Created", f"New user '{username}' with role '{role}' has been created.")
            except sqlite3.IntegrityError:
                QMessageBox.warning(self, "Username Exists", "This username already exists. Please choose a different one.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = InventoryManagementSystem()
    window.show()
    sys.exit(app.exec_())
    

        # Buttons2