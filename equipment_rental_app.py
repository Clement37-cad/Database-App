# equipment_rental_app.py
import sys
import os
from datetime import datetime, date
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import mysql.connector
from mysql.connector import Error
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import subprocess

class DatabaseConnection:
    def __init__(self):
        self.connection = None
        self.connect()
    
    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host='localhost',
                database='equipment_rental',
                user='root',
                password='5757'  
            )
            if self.connection.is_connected():
                print("Connected to MySQL database")
        except Error as e:
            QMessageBox.critical(None, "Database Error", f"Error connecting to database: {e}")
    
    def execute_query(self, query, params=None):
        try:
            cursor = self.connection.cursor(dictionary=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if query.strip().upper().startswith('SELECT'):
                result = cursor.fetchall()
                cursor.close()
                return result
            else:
                self.connection.commit()
                cursor.close()
                return cursor.lastrowid
        except Error as e:
            QMessageBox.critical(None, "Query Error", f"Error executing query: {e}")
            return None
    
    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()

class StyledButton(QPushButton):
    def __init__(self, text, color, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                padding: 12px 25px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
                min-width: 200px;
            }}
            QPushButton:hover {{
                background-color: {self.darken_color(color)};
                margin-top: -2px;
                margin-bottom: 2px;
            }}
            QPushButton:pressed {{
                background-color: {color};
                margin-top: 0px;
                margin-bottom: 0px;
            }}
        """)
    
    def darken_color(self, color):
        # Simple darkening by reducing values
        color = color.lstrip('#')
        r, g, b = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
        r = max(0, r - 30)
        g = max(0, g - 30)
        b = max(0, b - 30)
        return f'#{r:02x}{g:02x}{b:02x}'

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DatabaseConnection()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Equipment Rental Management System")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("background-color: #f5f6fa;")
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(50, 30, 50, 30)
        
        # Header
        header_widget = QWidget()
        header_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 15px;
                padding: 20px;
            }
        """)
        header_layout = QVBoxLayout(header_widget)
        
        title_label = QLabel("Equipment Rental Management System")
        title_label.setStyleSheet("color: white; font-size: 32px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Complete Equipment & Rental Management Solution")
        subtitle_label.setStyleSheet("color: #e0e0e0; font-size: 16px;")
        subtitle_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(subtitle_label)
        
        main_layout.addWidget(header_widget)
        
        # Menu buttons grid
        menu_widget = QWidget()
        menu_widget.setStyleSheet("background-color: white; border-radius: 15px; padding: 20px;")
        menu_layout = QGridLayout(menu_widget)
        menu_layout.setSpacing(15)
        
        buttons = [
            ("👥 Customers", "#4CAF50", self.open_customer_interface),
            ("🔧 Equipment", "#2196F3", self.open_equipment_interface),
            ("👨‍💼 Staff", "#FF9800", self.open_staff_interface),
            ("📋 Rentals", "#9C27B0", self.open_rental_interface),
            ("💰 Payments", "#00BCD4", self.open_payment_interface),
            ("🔨 Maintenance", "#F44336", self.open_maintenance_interface),
            ("📊 Reports", "#607D8B", self.open_reports),
        ]
        
        row, col = 0, 0
        for text, color, command in buttons:
            btn = QPushButton(text)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    padding: 20px;
                    font-size: 16px;
                    font-weight: bold;
                    border-radius: 10px;
                    min-height: 80px;
                }}
                QPushButton:hover {{
                    background-color: {self.darken_color(color)};
                    transform: scale(1.02);
                }}
                QPushButton:pressed {{
                    background-color: {color};
                }}
            """)
            btn.clicked.connect(command)
            btn.setCursor(Qt.PointingHandCursor)
            menu_layout.addWidget(btn, row, col)
            
            col += 1
            if col > 2:
                col = 0
                row += 1
        
        main_layout.addWidget(menu_widget)
        
        # Footer
        footer_label = QLabel("© 2024 Equipment Rental Management System | Version 2.0")
        footer_label.setStyleSheet("color: #666; font-size: 11px;")
        footer_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(footer_label)
    
    def darken_color(self, color):
        color = color.lstrip('#')
        r, g, b = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
        r = max(0, r - 30)
        g = max(0, g - 30)
        b = max(0, b - 30)
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def create_entity_window(self, title, table_name, columns):
        window = QMainWindow(self)
        window.setWindowTitle(title)
        window.setGeometry(150, 150, 1300, 800)
        
        central_widget = QWidget()
        window.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Header
        header = QWidget()
        header.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2c3e50, stop:1 #3498db);
                border-radius: 10px;
                padding: 15px;
            }
        """)
        header_layout = QHBoxLayout(header)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        header_layout.addWidget(title_label)
        
        back_btn = QPushButton("← Back to Menu")
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        back_btn.clicked.connect(window.close)
        back_btn.setCursor(Qt.PointingHandCursor)
        header_layout.addWidget(back_btn, alignment=Qt.AlignRight)
        
        main_layout.addWidget(header)
        
        # Content area
        content = QWidget()
        content_layout = QHBoxLayout(content)
        
        # Left panel - Form
        form_widget = QWidget()
        form_widget.setMaximumWidth(350)
        form_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #ddd;
            }
        """)
        form_layout = QVBoxLayout(form_widget)
        
        form_title = QLabel("Add / Edit Record")
        form_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; padding: 10px;")
        form_layout.addWidget(form_title)
        
        # Scroll area for form
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        
        scroll_widget = QWidget()
        self.form_layout = QVBoxLayout(scroll_widget)
        
        self.entries = {}
        for col in columns[1:]:  # Skip ID
            label = QLabel(col.replace('_', ' ').title() + ':')
            label.setStyleSheet("font-size: 12px; color: #555; margin-top: 5px;")
            self.form_layout.addWidget(label)
            
            entry = QLineEdit()
            entry.setStyleSheet("""
                QLineEdit {
                    padding: 8px;
                    border: 2px solid #ddd;
                    border-radius: 5px;
                    font-size: 12px;
                }
                QLineEdit:focus {
                    border-color: #3498db;
                }
            """)
            self.form_layout.addWidget(entry)
            self.entries[col] = entry
        
        self.form_layout.addStretch()
        scroll.setWidget(scroll_widget)
        form_layout.addWidget(scroll)
        
        # Buttons
        btn_widget = QWidget()
        btn_layout = QHBoxLayout(btn_widget)
        
        add_btn = QPushButton("➕ Add")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #219a52; }
        """)
        add_btn.clicked.connect(lambda: self.add_record(table_name, columns))
        add_btn.setCursor(Qt.PointingHandCursor)
        btn_layout.addWidget(add_btn)
        
        update_btn = QPushButton("✏️ Update")
        update_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                padding: 10px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #d68910; }
        """)
        update_btn.clicked.connect(lambda: self.update_record(table_name, columns))
        update_btn.setCursor(Qt.PointingHandCursor)
        btn_layout.addWidget(update_btn)
        
        btn_widget2 = QWidget()
        btn_layout2 = QHBoxLayout(btn_widget2)
        
        delete_btn = QPushButton("🗑️ Delete")
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 10px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #c0392b; }
        """)
        delete_btn.clicked.connect(lambda: self.delete_record(table_name, columns[0]))
        delete_btn.setCursor(Qt.PointingHandCursor)
        btn_layout2.addWidget(delete_btn)
        
        clear_btn = QPushButton("🔄 Clear")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 10px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #7f8c8d; }
        """)
        clear_btn.clicked.connect(lambda: self.clear_form())
        clear_btn.setCursor(Qt.PointingHandCursor)
        btn_layout2.addWidget(clear_btn)
        
        form_layout.addWidget(btn_widget)
        form_layout.addWidget(btn_widget2)
        
        content_layout.addWidget(form_widget)
        
        # Right panel - Table
        table_widget = QWidget()
        table_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #ddd;
            }
        """)
        table_layout = QVBoxLayout(table_widget)
        
        # Search bar
        search_widget = QWidget()
        search_layout = QHBoxLayout(search_widget)
        
        self.search_entry = QLineEdit()
        self.search_entry.setPlaceholderText("Search records...")
        self.search_entry.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #ddd;
                border-radius: 5px;
                font-size: 13px;
            }
            QLineEdit:focus { border-color: #3498db; }
        """)
        search_layout.addWidget(self.search_entry)
        
        search_btn = QPushButton("🔍 Search")
        search_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #2980b9; }
        """)
        search_btn.clicked.connect(lambda: self.search_records(table_name, columns))
        search_btn.setCursor(Qt.PointingHandCursor)
        search_layout.addWidget(search_btn)
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                padding: 10px 20px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #27ae60; }
        """)
        refresh_btn.clicked.connect(lambda: self.refresh_table(table_name, columns))
        refresh_btn.setCursor(Qt.PointingHandCursor)
        search_layout.addWidget(refresh_btn)
        
        table_layout.addWidget(search_widget)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels([col.replace('_', ' ').title() for col in columns])
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                gridline-color: #f0f0f0;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 8px;
                font-weight: bold;
                border: none;
            }
        """)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.clicked.connect(lambda: self.on_table_select(columns))
        
        table_layout.addWidget(self.table)
        content_layout.addWidget(table_widget)
        
        main_layout.addWidget(content)
        
        # Store references
        self.current_table_name = table_name
        self.current_columns = columns
        self.current_window = window
        
        # Load data
        self.refresh_table(table_name, columns)
        
        window.show()
    
    def refresh_table(self, table_name, columns):
        query = f"SELECT * FROM {table_name}"
        results = self.db.execute_query(query)
        
        self.table.setRowCount(0)
        if results:
            for row_idx, row in enumerate(results):
                self.table.insertRow(row_idx)
                for col_idx, col in enumerate(columns):
                    value = row[col] if row[col] is not None else ''
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
    
    def on_table_select(self, columns):
        current_row = self.table.currentRow()
        if current_row >= 0:
            self.clear_form()
            for i, col in enumerate(columns[1:]):
                item = self.table.item(current_row, i + 1)
                if item and col in self.entries:
                    self.entries[col].setText(item.text())
    
    def clear_form(self):
        for entry in self.entries.values():
            entry.clear()
    
    def add_record(self, table_name, columns):
        values = []
        for col in columns[1:]:
            value = self.entries[col].text()
            values.append(value if value else None)
        
        placeholders = ', '.join(['%s'] * len(columns[1:]))
        columns_str = ', '.join(columns[1:])
        query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
        
        result = self.db.execute_query(query, values)
        if result:
            QMessageBox.information(self, "Success", "Record added successfully!")
            self.refresh_table(table_name, columns)
            self.clear_form()
    
    def update_record(self, table_name, columns):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a record to update")
            return
        
        record_id = self.table.item(current_row, 0).text()
        
        set_clause = []
        values = []
        for col in columns[1:]:
            value = self.entries[col].text()
            if value:
                set_clause.append(f"{col} = %s")
                values.append(value)
        
        if not set_clause:
            QMessageBox.warning(self, "Warning", "No values to update")
            return
        
        set_clause_str = ', '.join(set_clause)
        values.append(record_id)
        query = f"UPDATE {table_name} SET {set_clause_str} WHERE {columns[0]} = %s"
        
        result = self.db.execute_query(query, values)
        if result is not None:
            QMessageBox.information(self, "Success", "Record updated successfully!")
            self.refresh_table(table_name, columns)
    
    def delete_record(self, table_name, id_column):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a record to delete")
            return
        
        reply = QMessageBox.question(self, "Confirm", "Are you sure you want to delete this record?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.No:
            return
        
        record_id = self.table.item(current_row, 0).text()
        query = f"DELETE FROM {table_name} WHERE {id_column} = %s"
        
        result = self.db.execute_query(query, (record_id,))
        if result is not None:
            QMessageBox.information(self, "Success", "Record deleted successfully!")
            self.refresh_table(table_name, self.current_columns)
            self.clear_form()
    
    def search_records(self, table_name, columns):
        search_term = self.search_entry.text()
        if not search_term:
            self.refresh_table(table_name, columns)
            return
        
        search_conditions = []
        for col in columns:
            search_conditions.append(f"{col} LIKE %s")
        
        query = f"SELECT * FROM {table_name} WHERE {' OR '.join(search_conditions)}"
        params = [f"%{search_term}%"] * len(columns)
        
        results = self.db.execute_query(query, params)
        
        self.table.setRowCount(0)
        if results:
            for row_idx, row in enumerate(results):
                self.table.insertRow(row_idx)
                for col_idx, col in enumerate(columns):
                    value = row[col] if row[col] is not None else ''
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
    
    # Entity interface methods
    def open_customer_interface(self):
        self.create_entity_window("Customer Management", "customers", 
                                 ['customer_id', 'first_name', 'last_name', 'email', 'phone', 'address', 'registration_date'])
    
    def open_equipment_interface(self):
        self.create_entity_window("Equipment Management", "equipment",
                                 ['equipment_id', 'name', 'category', 'description', 'daily_rate', 'status', 'purchase_date', 'last_maintenance_date'])
    
    def open_staff_interface(self):
        self.create_entity_window("Staff Management", "staff",
                                 ['staff_id', 'first_name', 'last_name', 'email', 'phone', 'position', 'hire_date', 'salary'])
    
    def open_rental_interface(self):
        self.create_entity_window("Rental Management", "rentals",
                                 ['rental_id', 'customer_id', 'equipment_id', 'staff_id', 'rental_date', 'return_date', 'total_amount', 'status'])
    
    def open_payment_interface(self):
        self.create_entity_window("Payment Management", "payments",
                                 ['payment_id', 'rental_id', 'amount', 'payment_date', 'payment_method', 'status'])
    
    def open_maintenance_interface(self):
        self.create_entity_window("Maintenance Management", "maintenance",
                                 ['maintenance_id', 'equipment_id', 'staff_id', 'maintenance_date', 'description', 'cost', 'next_maintenance_date', 'status'])
    
    def open_reports(self):
        dialog = ReportsDialog(self.db, self)
        dialog.exec_()

class ReportsDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Generate Reports")
        self.setGeometry(300, 300, 600, 500)
        self.setStyleSheet("background-color: white;")
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        title = QLabel("Report Generation")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; padding: 20px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        reports = [
            ("👥 Customer Report", "#4CAF50", self.generate_customer_report),
            ("🔧 Equipment Report", "#2196F3", self.generate_equipment_report),
            ("📋 Rental Activity Report", "#9C27B0", self.generate_rental_report),
            ("💰 Payment Summary Report", "#00BCD4", self.generate_payment_report),
            ("🔨 Maintenance Report", "#F44336", self.generate_maintenance_report),
            ("👨‍💼 Staff Performance Report", "#FF9800", self.generate_staff_report),
        ]
        
        for text, color, command in reports:
            btn = QPushButton(text)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    padding: 15px;
                    font-size: 14px;
                    font-weight: bold;
                    border-radius: 8px;
                    margin: 5px 20px;
                }}
                QPushButton:hover {{
                    background-color: {self.darken_color(color)};
                }}
            """)
            btn.clicked.connect(command)
            btn.setCursor(Qt.PointingHandCursor)
            layout.addWidget(btn)
        
        layout.addStretch()
    
    def darken_color(self, color):
        color = color.lstrip('#')
        r, g, b = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
        r = max(0, r - 30)
        g = max(0, g - 30)
        b = max(0, b - 30)
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def generate_customer_report(self):
        query = """
        SELECT c.customer_id, c.first_name, c.last_name, c.email, c.phone,
               COUNT(r.rental_id) as total_rentals,
               SUM(COALESCE(p.amount, 0)) as total_payments
        FROM customers c
        LEFT JOIN rentals r ON c.customer_id = r.customer_id
        LEFT JOIN payments p ON r.rental_id = p.rental_id
        GROUP BY c.customer_id
        ORDER BY total_payments DESC
        """
        results = self.db.execute_query(query)
        if results:
            self.create_pdf_report("Customer_Report", 
                                 ["ID", "First Name", "Last Name", "Email", "Phone", "Total Rentals", "Total Payments"],
                                 results)
    
    def generate_equipment_report(self):
        query = """
        SELECT e.equipment_id, e.name, e.category, e.status, e.daily_rate,
               COUNT(r.rental_id) as times_rented,
               COUNT(m.maintenance_id) as maintenance_count
        FROM equipment e
        LEFT JOIN rentals r ON e.equipment_id = r.equipment_id
        LEFT JOIN maintenance m ON e.equipment_id = m.equipment_id
        GROUP BY e.equipment_id
        ORDER BY times_rented DESC
        """
        results = self.db.execute_query(query)
        if results:
            self.create_pdf_report("Equipment_Report",
                                 ["ID", "Name", "Category", "Status", "Daily Rate", "Times Rented", "Maintenance Count"],
                                 results)
    
    def generate_rental_report(self):
        query = """
        SELECT r.rental_id, CONCAT(c.first_name, ' ', c.last_name) as customer,
               e.name as equipment, CONCAT(s.first_name, ' ', s.last_name) as staff,
               r.rental_date, r.return_date, r.total_amount, r.status
        FROM rentals r
        JOIN customers c ON r.customer_id = c.customer_id
        JOIN equipment e ON r.equipment_id = e.equipment_id
        JOIN staff s ON r.staff_id = s.staff_id
        ORDER BY r.rental_date DESC
        """
        results = self.db.execute_query(query)
        if results:
            self.create_pdf_report("Rental_Activity_Report",
                                 ["Rental ID", "Customer", "Equipment", "Staff", "Rental Date", "Return Date", "Amount", "Status"],
                                 results)
    
    def generate_payment_report(self):
        query = """
        SELECT p.payment_id, r.rental_id, 
               CONCAT(c.first_name, ' ', c.last_name) as customer,
               p.amount, p.payment_date, p.payment_method, p.status
        FROM payments p
        JOIN rentals r ON p.rental_id = r.rental_id
        JOIN customers c ON r.customer_id = c.customer_id
        ORDER BY p.payment_date DESC
        """
        results = self.db.execute_query(query)
        if results:
            self.create_pdf_report("Payment_Summary_Report",
                                 ["Payment ID", "Rental ID", "Customer", "Amount", "Date", "Method", "Status"],
                                 results)
    
    def generate_maintenance_report(self):
        query = """
        SELECT m.maintenance_id, e.name as equipment,
               CONCAT(s.first_name, ' ', s.last_name) as staff,
               m.maintenance_date, m.description, m.cost, m.status, m.next_maintenance_date
        FROM maintenance m
        JOIN equipment e ON m.equipment_id = e.equipment_id
        JOIN staff s ON m.staff_id = s.staff_id
        ORDER BY m.maintenance_date DESC
        """
        results = self.db.execute_query(query)
        if results:
            self.create_pdf_report("Maintenance_Report",
                                 ["ID", "Equipment", "Staff", "Date", "Description", "Cost", "Status", "Next Maintenance"],
                                 results)
    
    def generate_staff_report(self):
        query = """
        SELECT s.staff_id, CONCAT(s.first_name, ' ', s.last_name) as staff_name,
               s.position, s.hire_date,
               COUNT(r.rental_id) as rentals_handled,
               COUNT(m.maintenance_id) as maintenance_performed,
               SUM(COALESCE(p.amount, 0)) as revenue_generated
        FROM staff s
        LEFT JOIN rentals r ON s.staff_id = r.staff_id
        LEFT JOIN payments p ON r.rental_id = p.rental_id
        LEFT JOIN maintenance m ON s.staff_id = m.staff_id
        GROUP BY s.staff_id
        ORDER BY revenue_generated DESC
        """
        results = self.db.execute_query(query)
        if results:
            self.create_pdf_report("Staff_Performance_Report",
                                 ["ID", "Staff Name", "Position", "Hire Date", "Rentals Handled", "Maintenance Done", "Revenue Generated"],
                                 results)
    
    def create_pdf_report(self, filename, headers, data):
        try:
            if not os.path.exists('reports'):
                os.makedirs('reports')
            
            filepath = f"reports/{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            doc = SimpleDocTemplate(filepath, pagesize=letter)
            elements = []
            
            styles = getSampleStyleSheet()
            title_style = styles['Heading1']
            title = Paragraph(f"<u>{filename.replace('_', ' ')}</u>", title_style)
            elements.append(title)
            elements.append(Spacer(1, 20))
            
            timestamp = Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                                styles['Normal'])
            elements.append(timestamp)
            elements.append(Spacer(1, 20))
            
            table_data = [headers]
            for row in data:
                table_data.append([str(val) if val is not None else '' for val in row.values()])
            
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
            ]))
            
            elements.append(table)
            doc.build(elements)
            
            QMessageBox.information(self, "Success", f"Report generated successfully!\nSaved to: {filepath}")
            
            if os.name == 'nt':
                os.startfile(filepath)
            elif os.name == 'posix':
                subprocess.call(['open', filepath])
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error generating report: {e}")

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Set application-wide style
    app.setStyleSheet("""
        * {
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        QMainWindow {
            background-color: #f5f6fa;
        }
    """)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()