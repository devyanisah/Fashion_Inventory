import unittest
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
import sqlite3
import os
from Fashion_V1 import InventoryManagementSystem, LoginDialog, CreateUserDialog, User

class TestFashionInventoryManagementSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication(sys.argv)
        # Use a test database
        cls.db_name = 'test_inventory.db'
        cls.conn = sqlite3.connect(cls.db_name)
        cls.cursor = cls.conn.cursor()

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()
        os.remove(cls.db_name)

    def setUp(self):
        self.window = InventoryManagementSystem()
        self.window.conn = self.conn
        self.window.cursor = self.cursor
        self.window.setup_database()

    def tearDown(self):
        self.window.close()

    def test_login_dialog(self):
        dialog = LoginDialog()
        dialog.username.setText("testuser")
        dialog.password.setText("testpass")
        self.assertEqual(dialog.username.text(), "testuser")
        self.assertEqual(dialog.password.text(), "testpass")

    def test_create_user_dialog(self):
        dialog = CreateUserDialog()
        dialog.username.setText("newuser")
        dialog.password.setText("newpass")
        dialog.role.setCurrentText("manager")
        dialog.passkey.setText("managerpass")
        self.assertEqual(dialog.username.text(), "newuser")
        self.assertEqual(dialog.password.text(), "newpass")
        self.assertEqual(dialog.role.currentText(), "manager")
        self.assertEqual(dialog.passkey.text(), "managerpass")

    def test_user_creation(self):
        self.window.current_user = User("manager", "manager")
        self.window.create_new_user()
        dialog = self.window.findChild(CreateUserDialog)
        self.assertIsNotNone(dialog)
        dialog.username.setText("testuser")
        dialog.password.setText("testpass")
        dialog.role.setCurrentText("sales_staff")
        dialog.passkey.setText("managerpass")
        QTest.mouseClick(dialog.findChild(type(dialog.findChild(type(dialog.buttonBox))), "QDialogButtonBox").button(dialog.buttonBox.Ok), Qt.LeftButton)
        
        # Verify user was created
        self.cursor.execute("SELECT username, role FROM users WHERE username = ?", ("testuser",))
        user = self.cursor.fetchone()
        self.assertIsNotNone(user)
        self.assertEqual(user[0], "testuser")
        self.assertEqual(user[1], "sales_staff")

    def test_add_brand(self):
        self.window.add_brand("Test Brand")
        self.cursor.execute("SELECT name FROM brands WHERE name = ?", ("Test Brand",))
        brand = self.cursor.fetchone()
        self.assertIsNotNone(brand)
        self.assertEqual(brand[0], "Test Brand")

    def test_add_product(self):
        # First, add a brand
        self.window.add_brand("Test Brand")
        self.cursor.execute("SELECT id FROM brands WHERE name = ?", ("Test Brand",))
        brand_id = self.cursor.fetchone()[0]

        # Now add a product
        self.window.add_product("Test Product", "Test Brand", brand_id, "Tops", "M", "Red", "10", "29.99", "5")
        
        self.cursor.execute("SELECT name, brand_id, category, size, color, quantity, price, low_stock_threshold FROM products WHERE name = ?", ("Test Product",))
        product = self.cursor.fetchone()
        self.assertIsNotNone(product)
        self.assertEqual(product[0], "Test Product")
        self.assertEqual(product[1], brand_id)
        self.assertEqual(product[2], "Tops")
        self.assertEqual(product[3], "M")
        self.assertEqual(product[4], "Red")
        self.assertEqual(product[5], 10)
        self.assertEqual(product[6], 29.99)
        self.assertEqual(product[7], 5)

    def test_process_sale(self):
        # First, add a product
        self.window.add_brand("Test Brand")
        self.cursor.execute("SELECT id FROM brands WHERE name = ?", ("Test Brand",))
        brand_id = self.cursor.fetchone()[0]
        self.window.add_product("Test Product", "Test Brand", brand_id, "Tops", "M", "Red", "10", "29.99", "5")

        # Now process a sale
        self.window.process_sale()
        dialog = self.window.findChild(type(self.window.findChild(type(self.window.central_widget))))
        self.assertIsNotNone(dialog)
        
        # Simulate adding an item to the sale
        search_input = dialog.findChild(type(dialog.findChild(type(dialog.layout))))
        search_input.setText("Test Product")
        search_button = dialog.findChild(type(dialog.findChild(type(dialog.layout))), "QPushButton")
        QTest.mouseClick(search_button, Qt.LeftButton)
        
        results_list = dialog.findChild(type(dialog.findChild(type(dialog.layout))), "QListWidget")
        results_list.setCurrentRow(0)
        
        add_button = dialog.findChild(type(dialog.findChild(type(dialog.layout))), "QPushButton", "Add to Bill")
        QTest.mouseClick(add_button, Qt.LeftButton)
        
        # Process the sale
        process_button = dialog.findChild(type(dialog.findChild(type(dialog.layout))), "QPushButton", "Process Sale")
        QTest.mouseClick(process_button, Qt.LeftButton)
        
        # Verify the sale was processed
        self.cursor.execute("SELECT quantity FROM products WHERE name = ?", ("Test Product",))
        new_quantity = self.cursor.fetchone()[0]
        self.assertEqual(new_quantity, 9)  # Original quantity was 10, should now be 9
        
        self.cursor.execute("SELECT COUNT(*) FROM sales")
        sale_count = self.cursor.fetchone()[0]
        self.assertEqual(sale_count, 1)

    def test_generate_report(self):
        # Add some test data
        self.window.add_brand("Test Brand")
        self.cursor.execute("SELECT id FROM brands WHERE name = ?", ("Test Brand",))
        brand_id = self.cursor.fetchone()[0]
        self.window.add_product("Test Product", "Test Brand", brand_id, "Tops", "M", "Red", "10", "29.99", "5")
        
        # Process a sale
        self.window.process_sale()
        dialog = self.window.findChild(type(self.window.findChild(type(self.window.central_widget))))
        search_input = dialog.findChild(type(dialog.findChild(type(dialog.layout))))
        search_input.setText("Test Product")
        search_button = dialog.findChild(type(dialog.findChild(type(dialog.layout))), "QPushButton")
        QTest.mouseClick(search_button, Qt.LeftButton)
        results_list = dialog.findChild(type(dialog.findChild(type(dialog.layout))), "QListWidget")
        results_list.setCurrentRow(0)
        add_button = dialog.findChild(type(dialog.findChild(type(dialog.layout))), "QPushButton", "Add to Bill")
        QTest.mouseClick(add_button, Qt.LeftButton)
        process_button = dialog.findChild(type(dialog.findChild(type(dialog.layout))), "QPushButton", "Process Sale")
        QTest.mouseClick(process_button, Qt.LeftButton)

        # Generate a sales report
        self.window.view_reports()
        report_dialog = self.window.findChild(type(self.window.findChild(type(self.window.central_widget))))
        report_type = report_dialog.findChild(type(report_dialog.findChild(type(report_dialog.layout))), "QComboBox")
        report_type.setCurrentText("Sales Report")
        generate_button = report_dialog.findChild(type(report_dialog.findChild(type(report_dialog.layout))), "QPushButton", "Generate Report")
        QTest.mouseClick(generate_button, Qt.LeftButton)
        
        # Verify the report was generated
        report_table = report_dialog.findChild(type(report_dialog.findChild(type(report_dialog.layout))), "QTableWidget")
        self.assertGreater(report_table.rowCount(), 0)

if __name__ == '__main__':
    unittest.main()