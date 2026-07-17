# auto_repair_management_system_qt.py

import sys
import os
from datetime import datetime, date
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import mysql.connector
from mysql.connector import Error 
from fpdf import FPDF
import csv
from decimal import Decimal


class DatabaseManager:
    """Singleton Database Manager"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance.connection = None
            cls._instance.cursor = None
        return cls._instance
    
    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host='localhost',
                user='root',  # Change this
                password='5757',  # Change this
                database='auto_repair_shop',
                autocommit=False
            )
            self.cursor = self.connection.cursor(dictionary=True)
            return True
        except Error as e:
            QMessageBox.critical(None, "Database Error", 
                               f"Failed to connect to database:\n{str(e)}")
            return False
    
    def execute_query(self, query, params=None):
        try:
            self.cursor.execute(query, params or ())
            return self.cursor
        except Error as e:
            QMessageBox.critical(None, "Query Error", str(e))
            return None
    
    def commit(self):
        try:
            self.connection.commit()
            return True
        except Error as e:
            QMessageBox.critical(None, "Commit Error", str(e))
            return False
    
    def rollback(self):
        self.connection.rollback()
    
    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()


class CurrencyDelegate(QStyledItemDelegate):
    """Custom delegate to display currency in Cedi format"""
    def displayText(self, value, locale):
        try:
            amount = float(value)
            return f"GH₵ {amount:,.2f}"
        except (ValueError, TypeError):
            return str(value)


class ModernButton(QPushButton):
    """Custom styled button"""
    def __init__(self, text, color="#3498db", parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self._lighten_color(color)};
            }}
            QPushButton:pressed {{
                background-color: {color};
            }}
        """)
        self.setCursor(Qt.PointingHandCursor)
    
    def _lighten_color(self, color):
        """Lighten the color slightly"""
        c = QColor(color)
        h, s, l, a = c.getHsl()
        return QColor.fromHsl(h, s, min(255, l + 20), a).name()


class DashboardWidget(QWidget):
    """Dashboard/Home page widget"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = DatabaseManager()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Welcome section
        welcome_label = QLabel("E.AMOAKO ENGINEERING SERVICES")
        welcome_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #2c3e50;
            padding: 10px;
        """)
        welcome_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(welcome_label)
        
        subtitle = QLabel("Comprehensive management solution for your auto repair business")
        subtitle.setStyleSheet("font-size: 14px; color: #7f8c8d;")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        # Statistics cards
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        stats = [
            ("Total Customers", "SELECT COUNT(*) as count FROM customer", "#e74c3c", "👥"),
            ("Active Services", "SELECT COUNT(*) as count FROM service_record WHERE status='In Progress'", "#3498db", "🔧"),
            ("Pending Payments", "SELECT COUNT(*) as count FROM payment WHERE payment_status='Pending'", "#f39c12", "💳"),
            ("Active Mechanics", "SELECT COUNT(*) as count FROM mechanic WHERE status='Active'", "#27ae60", "👨‍🔧")
        ]
        
        for title, query, color, icon in stats:
            card = self.create_stat_card(title, query, color, icon)
            stats_layout.addWidget(card)
        
        layout.addLayout(stats_layout)
        
        # Quick actions
        actions_label = QLabel("Quick Actions")
        actions_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(actions_label)
        
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(15)
        
        actions = [
            ("New Service Record", None),
            ("Add Customer", None),
            ("Process Payment", None),
            ("Generate Report", None)
        ]
        
        for text, _ in actions:
            btn = ModernButton(text, "#2ecc71")
            actions_layout.addWidget(btn)
        
        layout.addLayout(actions_layout)
        layout.addStretch()
    
    def create_stat_card(self, title, query, color, icon):
        """Create a statistics card widget"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 2px solid {color};
                border-radius: 10px;
                padding: 15px;
            }}
        """)
        card.setMinimumHeight(150)
        
        layout = QVBoxLayout(card)
        
        # Icon
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 36px;")
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        
        # Count
        try:
            cursor = self.db.execute_query(query)
            result = cursor.fetchone()
            count = result['count'] if result else 0
        except:
            count = 0
        
        count_label = QLabel(str(count))
        count_label.setStyleSheet(f"""
            font-size: 32px;
            font-weight: bold;
            color: {color};
        """)
        count_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(count_label)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 11px; color: #7f8c8d;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        return card


class TableViewWidget(QWidget):
    """Generic table view widget for entities"""
    def __init__(self, entity_name, columns, table_name, parent=None):
        super().__init__(parent)
        self.entity_name = entity_name
        self.columns = columns
        self.table_name = table_name
        self.db = DatabaseManager()
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        header = QLabel(f"Manage {self.entity_name.replace('_', ' ').title()}")
        header.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #2c3e50;
            padding: 10px;
            background-color: #ecf0f1;
            border-radius: 5px;
        """)
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Search bar
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search records...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        self.search_input.textChanged.connect(self.filter_data)
        search_layout.addWidget(self.search_input)
        
        refresh_btn = ModernButton("🔄 Refresh", "#3498db")
        refresh_btn.clicked.connect(self.load_data)
        search_layout.addWidget(refresh_btn)
        
        layout.addLayout(search_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(len(self.columns))
        self.table.setHorizontalHeaderLabels([col.replace('_', ' ').title() for col in self.columns])
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setSortingEnabled(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Style the table
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                gridline-color: #ecf0f1;
                background-color: white;
                alternate-background-color: #f8f9fa;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(self.table)
        
        # Action buttons
        btn_layout = QHBoxLayout()
        
        add_btn = ModernButton("➕ Add New", "#27ae60")
        add_btn.clicked.connect(self.add_record)
        btn_layout.addWidget(add_btn)
        
        edit_btn = ModernButton("✏️ Edit", "#f39c12")
        edit_btn.clicked.connect(self.edit_record)
        btn_layout.addWidget(edit_btn)
        
        delete_btn = ModernButton("🗑️ Delete", "#e74c3c")
        delete_btn.clicked.connect(self.delete_record)
        btn_layout.addWidget(delete_btn)
        
        export_btn = ModernButton("📥 Export CSV", "#9b59b6")
        export_btn.clicked.connect(self.export_to_csv)
        btn_layout.addWidget(export_btn)
        
        layout.addLayout(btn_layout)
        
        # Status bar
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #7f8c8d; padding: 5px;")
        layout.addWidget(self.status_label)
    
    def load_data(self):
        """Load data from database into table"""
        try:
            query = f"SELECT * FROM {self.table_name}"
            cursor = self.db.execute_query(query)
            
            if cursor:
                records = cursor.fetchall()
                self.table.setRowCount(len(records))
                
                for row, record in enumerate(records):
                    for col, key in enumerate(self.columns):
                        value = record.get(key, '')
                        
                        # Format currency fields
                        if any(currency_field in key.lower() for currency_field in 
                              ['amount', 'price', 'rate', 'total', 'discount', 'tax']):
                            item = QTableWidgetItem(f"GH₵ {float(value):,.2f}" if value else "GH₵ 0.00")
                        else:
                            item = QTableWidgetItem(str(value) if value is not None else '')
                        
                        item.setData(Qt.UserRole, record)  # Store full record
                        self.table.setItem(row, col, item)
                
                self.status_label.setText(f"Loaded {len(records)} records")
            else:
                self.status_label.setText("Failed to load data")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load data: {str(e)}")
            self.status_label.setText("Error loading data")
    
    def filter_data(self):
        """Filter table based on search input"""
        search_text = self.search_input.text().lower()
        
        for row in range(self.table.rowCount()):
            show_row = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and search_text in item.text().lower():
                    show_row = True
                    break
            self.table.setRowHidden(row, not show_row)
    
    def get_selected_record(self):
        """Get the currently selected record"""
        selected_rows = self.table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Warning", "Please select a record first")
            return None
        
        row = selected_rows[0].row()
        item = self.table.item(row, 0)
        return item.data(Qt.UserRole)
    
    def add_record(self):
        """Add new record dialog"""
        dialog = RecordDialog(self.entity_name, self.table_name, self.columns, self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_data()
    
    def edit_record(self):
        """Edit selected record"""
        record = self.get_selected_record()
        if record:
            dialog = RecordDialog(self.entity_name, self.table_name, self.columns, self, record)
            if dialog.exec_() == QDialog.Accepted:
                self.load_data()
    
    def delete_record(self):
        """Delete selected record"""
        record = self.get_selected_record()
        if not record:
            return
        
        # Get the ID field name
        id_field = f"{self.entity_name}_id" if not self.entity_name.endswith('s') else f"{self.entity_name[:-1]}_id"
        
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete this {self.entity_name.replace('_', ' ')} record?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                query = f"DELETE FROM {self.table_name} WHERE {id_field} = %s"
                self.db.execute_query(query, (record[id_field],))
                self.db.commit()
                self.load_data()
                self.status_label.setText("Record deleted successfully")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete record: {str(e)}")
    
    def export_to_csv(self):
        """Export table data to CSV"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export to CSV",
            f"{self.entity_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    
                    # Write headers
                    headers = [self.table.horizontalHeaderItem(i).text() 
                             for i in range(self.table.columnCount())]
                    writer.writerow(headers)
                    
                    # Write data
                    for row in range(self.table.rowCount()):
                        if not self.table.isRowHidden(row):
                            row_data = []
                            for col in range(self.table.columnCount()):
                                item = self.table.item(row, col)
                                row_data.append(item.text() if item else '')
                            writer.writerow(row_data)
                
                QMessageBox.information(self, "Success", f"Data exported to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export: {str(e)}")


class RecordDialog(QDialog):
    """Dialog for adding/editing records"""
    def __init__(self, entity_name, table_name, columns, parent=None, record=None):
        super().__init__(parent)
        self.entity_name = entity_name
        self.table_name = table_name
        self.columns = columns
        self.record = record
        self.db = DatabaseManager()
        self.fields = {}
        self.setup_ui()
        
        if record:
            self.load_record_data()
    
    def setup_ui(self):
        mode = "Edit" if self.record else "Add New"
        self.setWindowTitle(f"{mode} {self.entity_name.replace('_', ' ').title()}")
        self.setModal(True)
        self.resize(500, 600)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel(f"{mode} {self.entity_name.replace('_', ' ').title()}")
        title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
            padding: 10px;
            background-color: #ecf0f1;
            border-radius: 5px;
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Scroll area for form fields
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setSpacing(10)
        
        # Create fields based on entity
        field_definitions = self.get_field_definitions()
        
        for field_name, field_label, field_type, options in field_definitions:
            if field_name == f"{self.entity_name}_id" or field_name == 'registration_date':
                continue  # Skip auto-increment and auto-generated fields
                
            if field_type == 'text':
                widget = QTextEdit()
                widget.setMaximumHeight(100)
                self.fields[field_name] = widget
                form_layout.addRow(f"{field_label}:", widget)
                
            elif field_type == 'combo':
                widget = QComboBox()
                widget.addItems(options)
                self.fields[field_name] = widget
                form_layout.addRow(f"{field_label}:", widget)
                
            elif field_type == 'date':
                widget = QDateEdit()
                widget.setCalendarPopup(True)
                widget.setDate(QDate.currentDate())
                widget.setDisplayFormat("yyyy-MM-dd")
                self.fields[field_name] = widget
                form_layout.addRow(f"{field_label}:", widget)
                
            else:  # Default to line edit
                widget = QLineEdit()
                if 'phone' in field_name:
                    widget.setPlaceholderText("XXX-XXX-XXXX")
                elif 'email' in field_name:
                    widget.setPlaceholderText("email@example.com")
                elif any(curr in field_name for curr in ['amount', 'price', 'rate', 'total']):
                    widget.setPlaceholderText("0.00")
                self.fields[field_name] = widget
                form_layout.addRow(f"{field_label}:", widget)
        
        scroll.setWidget(form_widget)
        layout.addWidget(scroll)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = ModernButton("💾 Save", "#27ae60")
        save_btn.clicked.connect(self.save_record)
        button_layout.addWidget(save_btn)
        
        cancel_btn = ModernButton("❌ Cancel", "#e74c3c")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def get_field_definitions(self):
        """Get field definitions for each entity"""
        definitions = {
            'customer': [
                ('first_name', 'First Name', 'entry', None),
                ('last_name', 'Last Name', 'entry', None),
                ('phone', 'Phone', 'entry', None),
                ('email', 'Email', 'entry', None),
                ('address', 'Address', 'text', None),
                ('city', 'City', 'entry', None),
                ('state', 'State', 'entry', None),
                ('zip_code', 'ZIP Code', 'entry', None),
            ],
            'workshop': [
                ('workshop_name', 'Workshop Name', 'entry', None),
                ('location', 'Location', 'text', None),
                ('contact_number', 'Contact Number', 'entry', None),
                ('manager_name', 'Manager Name', 'entry', None),
                ('capacity', 'Capacity', 'entry', None),
                ('opening_hours', 'Opening Hours', 'entry', None),
                ('status', 'Status', 'combo', ['Active', 'Inactive', 'Maintenance']),
            ],
            'vehicle': [
                ('customer_id', 'Customer ID', 'entry', None),
                ('workshop_id', 'Workshop ID', 'entry', None),
                ('make', 'Make', 'entry', None),
                ('model', 'Model', 'entry', None),
                ('year', 'Year', 'entry', None),
                ('license_plate', 'License Plate', 'entry', None),
                ('vin', 'VIN', 'entry', None),
                ('color', 'Color', 'entry', None),
                ('mileage', 'Mileage', 'entry', None),
                ('vehicle_type', 'Vehicle Type', 'entry', None),
            ],
            'mechanic': [
                ('workshop_id', 'Workshop ID', 'entry', None),
                ('first_name', 'First Name', 'entry', None),
                ('last_name', 'Last Name', 'entry', None),
                ('specialization', 'Specialization', 'entry', None),
                ('certification_level', 'Certification', 'entry', None),
                ('phone', 'Phone', 'entry', None),
                ('email', 'Email', 'entry', None),
                ('hire_date', 'Hire Date', 'date', None),
                ('hourly_rate', 'Hourly Rate (GH₵)', 'entry', None),
                ('status', 'Status', 'combo', ['Active', 'On Leave', 'Terminated']),
            ],
            'service_record': [
                ('vehicle_id', 'Vehicle ID', 'entry', None),
                ('mechanic_id', 'Mechanic ID', 'entry', None),
                ('service_date', 'Service Date', 'date', None),
                ('service_type', 'Service Type', 'entry', None),
                ('description', 'Description', 'text', None),
                ('labor_hours', 'Labor Hours', 'entry', None),
                ('labor_rate', 'Labor Rate (GH₵/hr)', 'entry', None),
                ('status', 'Status', 'combo', ['Pending', 'In Progress', 'Completed', 'Cancelled']),
                ('priority', 'Priority', 'combo', ['Low', 'Medium', 'High', 'Urgent']),
            ],
            'part': [
                ('service_id', 'Service ID', 'entry', None),
                ('part_name', 'Part Name', 'entry', None),
                ('manufacturer', 'Manufacturer', 'entry', None),
                ('part_number', 'Part Number', 'entry', None),
                ('quantity', 'Quantity', 'entry', None),
                ('unit_price', 'Unit Price (GH₵)', 'entry', None),
                ('supplier', 'Supplier', 'entry', None),
                ('warranty_period', 'Warranty Period', 'entry', None),
            ],
            'payment': [
                ('service_id', 'Service ID', 'entry', None),
                ('customer_id', 'Customer ID', 'entry', None),
                ('amount', 'Amount (GH₵)', 'entry', None),
                ('payment_date', 'Payment Date', 'date', None),
                ('payment_method', 'Payment Method', 'combo', 
                 ['Cash', 'Credit Card', 'Debit Card', 'Mobile Money', 'Bank Transfer']),
                ('payment_status', 'Payment Status', 'combo', 
                 ['Paid', 'Pending', 'Partial', 'Refunded']),
                ('transaction_id', 'Transaction ID', 'entry', None),
                ('due_date', 'Due Date', 'date', None),
                ('discount', 'Discount (GH₵)', 'entry', None),
                ('tax', 'Tax (GH₵)', 'entry', None),
            ],
        }
        
        return definitions.get(self.entity_name, [])
    
    def load_record_data(self):
        """Load existing record data into form fields"""
        for field_name, widget in self.fields.items():
            if field_name in self.record:
                value = self.record[field_name]
                
                if isinstance(widget, QLineEdit):
                    widget.setText(str(value) if value else '')
                elif isinstance(widget, QTextEdit):
                    widget.setText(str(value) if value else '')
                elif isinstance(widget, QComboBox):
                    index = widget.findText(str(value))
                    if index >= 0:
                        widget.setCurrentIndex(index)
                elif isinstance(widget, QDateEdit):
                    if value:
                        widget.setDate(QDate.fromString(str(value), "yyyy-MM-dd"))
    
    def save_record(self):
        """Save record to database"""
        # Validate required fields
        data = {}
        for field_name, widget in self.fields.items():
            if isinstance(widget, QLineEdit):
                data[field_name] = widget.text().strip()
            elif isinstance(widget, QTextEdit):
                data[field_name] = widget.toPlainText().strip()
            elif isinstance(widget, QComboBox):
                data[field_name] = widget.currentText()
            elif isinstance(widget, QDateEdit):
                data[field_name] = widget.date().toString("yyyy-MM-dd")
        
        try:
            if self.record:  # Update
                id_field = f"{self.entity_name}_id"
                set_clause = ', '.join([f"{key} = %s" for key in data.keys()])
                query = f"UPDATE {self.table_name} SET {set_clause} WHERE {id_field} = %s"
                params = tuple(data.values()) + (self.record[id_field],)
            else:  # Insert
                columns = ', '.join(data.keys())
                placeholders = ', '.join(['%s'] * len(data))
                query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
                params = tuple(data.values())
            
            self.db.execute_query(query, params)
            self.db.commit()
            QMessageBox.information(self, "Success", "Record saved successfully!")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save record: {str(e)}")
            self.db.rollback()


class ReportsWidget(QWidget):
    """Reports dashboard widget"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = DatabaseManager()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("📊 Reports Dashboard")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            padding: 15px;
            background-color: #ecf0f1;
            border-radius: 5px;
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Reports grid
        grid = QGridLayout()
        grid.setSpacing(15)
        
        reports = [
            ("Customer Service History", "📋", "#3498db", self.report_customer_service),
            ("Mechanic Performance", "👨‍🔧", "#2ecc71", self.report_mechanic_performance),
            ("Revenue by Service Type", "💰", "#f39c12", self.report_revenue_service),
            ("Parts Inventory Usage", "⚙️", "#9b59b6", self.report_parts_usage),
            ("Payment Status Summary", "💳", "#e74c3c", self.report_payment_status),
            ("Workshop Capacity", "🏭", "#1abc9c", self.report_workshop_capacity),
            ("Vehicle Service Schedule", "🚗", "#e67e22", self.report_vehicle_schedule),
            ("Monthly Revenue Report", "📈", "#34495e", self.report_monthly_revenue),
        ]
        
        for i, (title, icon, color, handler) in enumerate(reports):
            card = self.create_report_card(title, icon, color, handler)
            grid.addWidget(card, i // 2, i % 2)
        
        layout.addLayout(grid)
    
    def create_report_card(self, title, icon, color, handler):
        """Create a clickable report card"""
        card = QPushButton()
        card.setStyleSheet(f"""
            QPushButton {{
                background-color: white;
                border: 2px solid {color};
                border-radius: 10px;
                padding: 20px;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: {color};
                color: white;
            }}
        """)
        card.setCursor(Qt.PointingHandCursor)
        card.setMinimumHeight(120)
        card.clicked.connect(handler)
        
        layout = QHBoxLayout(card)
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 36px;")
        layout.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {color};")
        title_label.setWordWrap(True)
        layout.addWidget(title_label)
        
        layout.addStretch()
        
        return card
    
    def show_report(self, title, query, currency_columns=None):
        """Display report in a new window"""
        report_window = QDialog(self)
        report_window.setWindowTitle(title)
        report_window.resize(1000, 600)
        
        layout = QVBoxLayout(report_window)
        
        # Header
        header = QLabel(title)
        header.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
            padding: 10px;
        """)
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        date_label = QLabel(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        date_label.setStyleSheet("color: #7f8c8d;")
        date_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(date_label)
        
        # Execute query
        cursor = self.db.execute_query(query)
        if not cursor:
            return
        
        results = cursor.fetchall()
        if not results:
            QMessageBox.information(report_window, "No Data", "No records found for this report")
            return
        
        # Create table
        table = QTableWidget()
        columns = list(results[0].keys())
        table.setColumnCount(len(columns))
        table.setHorizontalHeaderLabels([col.replace('_', ' ').title() for col in columns])
        table.setRowCount(len(results))
        table.setAlternatingRowColors(True)
        
        for row, record in enumerate(results):
            for col, key in enumerate(columns):
                value = record[key]
                
                # Format currency fields
                if currency_columns and key in currency_columns:
                    text = f"GH₵ {float(value):,.2f}" if value else "GH₵ 0.00"
                elif isinstance(value, (Decimal, float)):
                    text = f"{value:,.2f}"
                else:
                    text = str(value) if value is not None else ''
                
                item = QTableWidgetItem(text)
                table.setItem(row, col, item)
        
        table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #bdc3c7;
                gridline-color: #ecf0f1;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 8px;
                font-weight: bold;
            }
        """)
        table.horizontalHeader().setStretchLastSection(True)
        
        layout.addWidget(table)
        
        # Summary
        summary = QLabel(f"Total Records: {len(results)}")
        summary.setStyleSheet("""
            font-size: 12px;
            font-weight: bold;
            color: #2c3e50;
            padding: 10px;
            background-color: #ecf0f1;
            border-radius: 5px;
        """)
        layout.addWidget(summary)
        
        # Export button
        export_btn = ModernButton("📥 Export to CSV", "#27ae60")
        export_btn.clicked.connect(lambda: self.export_report(title, results, columns))
        layout.addWidget(export_btn)
        
        report_window.exec_()
    
    def export_report(self, title, data, columns):
        """Export report to CSV"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Report",
            f"{title.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv",
            "CSV Files (*.csv)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.DictWriter(file, fieldnames=columns)
                    writer.writeheader()
                    writer.writerows(data)
                QMessageBox.information(self, "Success", f"Report exported to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Export failed: {str(e)}")
    
    # Report query methods
    def report_customer_service(self):
        query = """
            SELECT 
                c.first_name, c.last_name, v.make, v.model,
                v.license_plate, sr.service_type, sr.service_date,
                sr.status, p.total_amount
            FROM customer c
            JOIN vehicle v ON c.customer_id = v.customer_id
            JOIN service_record sr ON v.vehicle_id = sr.vehicle_id
            LEFT JOIN payment p ON sr.service_id = p.service_id
            ORDER BY sr.service_date DESC
        """
        self.show_report("Customer Service History", query, ['total_amount'])
    
    def report_mechanic_performance(self):
        query = """
            SELECT 
                m.first_name, m.last_name, m.specialization,
                COUNT(sr.service_id) as total_services,
                COALESCE(SUM(sr.labor_hours), 0) as total_hours,
                COALESCE(AVG(p.total_amount), 0) as avg_service_value
            FROM mechanic m
            LEFT JOIN service_record sr ON m.mechanic_id = sr.mechanic_id
            LEFT JOIN payment p ON sr.service_id = p.service_id
            WHERE sr.status = 'Completed' OR sr.status IS NULL
            GROUP BY m.mechanic_id
            ORDER BY total_services DESC
        """
        self.show_report("Mechanic Performance", query, ['avg_service_value'])
    
    def report_revenue_service(self):
        query = """
            SELECT 
                sr.service_type,
                COUNT(*) as service_count,
                COALESCE(SUM(p.total_amount), 0) as total_revenue,
                COALESCE(AVG(p.total_amount), 0) as avg_revenue,
                COALESCE(MIN(p.total_amount), 0) as min_revenue,
                COALESCE(MAX(p.total_amount), 0) as max_revenue
            FROM service_record sr
            JOIN payment p ON sr.service_id = p.service_id
            WHERE p.payment_status = 'Paid'
            GROUP BY sr.service_type
            ORDER BY total_revenue DESC
        """
        self.show_report("Revenue by Service Type", query, 
                        ['total_revenue', 'avg_revenue', 'min_revenue', 'max_revenue'])
    
    def report_parts_usage(self):
        query = """
            SELECT 
                p.part_name, p.manufacturer,
                SUM(p.quantity) as total_used,
                SUM(p.quantity * p.unit_price) as total_cost,
                p.supplier,
                COUNT(DISTINCT p.service_id) as times_used
            FROM part p
            GROUP BY p.part_name, p.manufacturer, p.supplier
            ORDER BY total_cost DESC
        """
        self.show_report("Parts Inventory Usage", query, ['total_cost'])
    
    def report_payment_status(self):
        query = """
            SELECT 
                payment_status,
                COUNT(*) as count,
                COALESCE(SUM(total_amount), 0) as total_amount,
                COALESCE(AVG(total_amount), 0) as avg_amount,
                COALESCE(SUM(discount), 0) as total_discounts,
                COALESCE(SUM(tax), 0) as total_tax
            FROM payment
            GROUP BY payment_status
            ORDER BY total_amount DESC
        """
        self.show_report("Payment Status Summary", query, 
                        ['total_amount', 'avg_amount', 'total_discounts', 'total_tax'])
    
    def report_workshop_capacity(self):
        query = """
            SELECT 
                w.workshop_name, w.location, w.capacity,
                (SELECT COUNT(*) FROM mechanic m WHERE m.workshop_id = w.workshop_id AND m.status = 'Active') as active_mechanics,
                (SELECT COUNT(*) FROM vehicle v WHERE v.workshop_id = w.workshop_id) as assigned_vehicles,
                w.status
            FROM workshop w
            ORDER BY w.capacity DESC
        """
        self.show_report("Workshop Capacity", query)
    
    def report_vehicle_schedule(self):
        query = """
            SELECT 
                v.make, v.model, v.license_plate,
                c.first_name, c.last_name,
                sr.service_type, sr.service_date, sr.status,
                CONCAT(m.first_name, ' ', m.last_name) as mechanic_name
            FROM vehicle v
            JOIN customer c ON v.customer_id = c.customer_id
            JOIN service_record sr ON v.vehicle_id = sr.vehicle_id
            LEFT JOIN mechanic m ON sr.mechanic_id = m.mechanic_id
            WHERE sr.status IN ('Pending', 'In Progress')
            ORDER BY sr.service_date
        """
        self.show_report("Vehicle Service Schedule", query)
    
    def report_monthly_revenue(self):
        query = """
            SELECT 
                DATE_FORMAT(payment_date, '%Y-%m') as month,
                COUNT(*) as transactions,
                COALESCE(SUM(total_amount), 0) as total_revenue,
                COALESCE(SUM(discount), 0) as total_discounts,
                COALESCE(SUM(tax), 0) as total_tax,
                COALESCE(SUM(total_amount) + SUM(tax) - SUM(discount), 0) as net_revenue
            FROM payment
            WHERE payment_status = 'Paid'
            GROUP BY DATE_FORMAT(payment_date, '%Y-%m')
            ORDER BY month DESC
            LIMIT 12
        """
        self.show_report("Monthly Revenue Report", query,
                        ['total_revenue', 'total_discounts', 'total_tax', 'net_revenue'])


class MainWindow(QMainWindow):
    """Main application window"""
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        if not self.db.connect():
            sys.exit(1)
        
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Auto Repair Shop Management System")
        self.setGeometry(100, 100, 1400, 800)
        
        # Set application icon
        self.setWindowIcon(QIcon.fromTheme("applications-engineering"))
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                padding: 15px;
            }
        """)
        header.setFixedHeight(80)
        
        header_layout = QHBoxLayout(header)
        
        title = QLabel("🔧 Auto Repair Shop Management System")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: white;
        """)
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Clock
        self.clock_label = QLabel()
        self.clock_label.setStyleSheet("color: white; font-size: 14px;")
        self.update_clock()
        header_layout.addWidget(self.clock_label)
        
        main_layout.addWidget(header)
        
        # Navigation sidebar and content area
        content_layout = QHBoxLayout()
        content_layout.setSpacing(0)
        
        # Sidebar
        sidebar = QFrame()
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #34495e;
                min-width: 200px;
                max-width: 200px;
            }
        """)
        
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setSpacing(5)
        sidebar_layout.setContentsMargins(10, 10, 10, 10)
        
        # Navigation buttons
        nav_buttons = [
            ("🏠 Dashboard", self.show_dashboard, "#2ecc71"),
            ("👥 Customers", self.show_customers, "#3498db"),
            ("🏭 Workshops", self.show_workshops, "#e74c3c"),
            ("🚗 Vehicles", self.show_vehicles, "#f39c12"),
            ("👨‍🔧 Mechanics", self.show_mechanics, "#9b59b6"),
            ("🔧 Services", self.show_services, "#1abc9c"),
            ("⚙️ Parts", self.show_parts, "#e67e22"),
            ("💳 Payments", self.show_payments, "#c0392b"),
            ("📊 Reports", self.show_reports, "#27ae60"),
        ]
        
        for text, handler, color in nav_buttons:
            btn = QPushButton(text)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    padding: 12px;
                    border-radius: 5px;
                    font-size: 12px;
                    font-weight: bold;
                    text-align: left;
                }}
                QPushButton:hover {{
                    background-color: {self._lighten_color(color)};
                }}
                QPushButton:pressed {{
                    background-color: {color};
                }}
            """)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(handler)
            sidebar_layout.addWidget(btn)
        
        sidebar_layout.addStretch()
        
        # Logout button
        logout_btn = QPushButton("🚪 Exit")
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #c0392b;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 5px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e74c3c;
            }
        """)
        logout_btn.clicked.connect(self.close)
        sidebar_layout.addWidget(logout_btn)
        
        content_layout.addWidget(sidebar)
        
        # Content area
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("background-color: #ecf0f1;")
        content_layout.addWidget(self.content_stack)
        
        main_layout.addLayout(content_layout)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #34495e;
                color: white;
                padding: 5px;
            }
        """)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready | Database Connected")
        
        # Add pages to stack
        self.dashboard_page = DashboardWidget()
        self.content_stack.addWidget(self.dashboard_page)
        
        # Initialize other pages as None, create them when needed
        self.pages = {
            'customers': None,
            'workshops': None,
            'vehicles': None,
            'mechanics': None,
            'services': None,
            'parts': None,
            'payments': None,
            'reports': None,
        }
        
        # Timer for clock
        timer = QTimer(self)
        timer.timeout.connect(self.update_clock)
        timer.start(1000)
    
    def _lighten_color(self, color):
        """Lighten a color"""
        c = QColor(color)
        h, s, l, a = c.getHsl()
        return QColor.fromHsl(h, s, min(255, l + 30), a).name()
    
    def update_clock(self):
        """Update clock display"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.clock_label.setText(current_time)
    
    def get_or_create_page(self, key, entity_name, columns, table_name):
        """Get existing page or create new one"""
        if self.pages[key] is None:
            self.pages[key] = TableViewWidget(entity_name, columns, table_name)
            self.content_stack.addWidget(self.pages[key])
        return self.pages[key]
    
    def show_dashboard(self):
        self.content_stack.setCurrentWidget(self.dashboard_page)
        self.status_bar.showMessage("Dashboard")
    
    def show_customers(self):
        page = self.get_or_create_page(
            'customers', 'customer',
            ['customer_id', 'first_name', 'last_name', 'phone', 'email', 
             'address', 'city', 'state', 'zip_code', 'registration_date'],
            'customer'
        )
        self.content_stack.setCurrentWidget(page)
        self.status_bar.showMessage("Managing Customers")
    
    def show_workshops(self):
        page = self.get_or_create_page(
            'workshops', 'workshop',
            ['workshop_id', 'workshop_name', 'location', 'contact_number',
             'manager_name', 'capacity', 'opening_hours', 'status'],
            'workshop'
        )
        self.content_stack.setCurrentWidget(page)
        self.status_bar.showMessage("Managing Workshops")
    
    def show_vehicles(self):
        page = self.get_or_create_page(
            'vehicles', 'vehicle',
            ['vehicle_id', 'customer_id', 'workshop_id', 'make', 'model',
             'year', 'license_plate', 'vin', 'color', 'mileage',
             'vehicle_type', 'registration_date'],
            'vehicle'
        )
        self.content_stack.setCurrentWidget(page)
        self.status_bar.showMessage("Managing Vehicles")
    
    def show_mechanics(self):
        page = self.get_or_create_page(
            'mechanics', 'mechanic',
            ['mechanic_id', 'workshop_id', 'first_name', 'last_name',
             'specialization', 'certification_level', 'phone', 'email',
             'hire_date', 'hourly_rate', 'status'],
            'mechanic'
        )
        self.content_stack.setCurrentWidget(page)
        self.status_bar.showMessage("Managing Mechanics")
    
    def show_services(self):
        page = self.get_or_create_page(
            'services', 'service_record',
            ['service_id', 'vehicle_id', 'mechanic_id', 'service_date',
             'service_type', 'description', 'labor_hours', 'labor_rate',
             'status', 'priority', 'notes', 'completion_date'],
            'service_record'
        )
        self.content_stack.setCurrentWidget(page)
        self.status_bar.showMessage("Managing Service Records")
    
    def show_parts(self):
        page = self.get_or_create_page(
            'parts', 'part',
            ['part_id', 'service_id', 'part_name', 'manufacturer',
             'part_number', 'quantity', 'unit_price', 'supplier',
             'warranty_period', 'installation_date'],
            'part'
        )
        self.content_stack.setCurrentWidget(page)
        self.status_bar.showMessage("Managing Parts")
    
    def show_payments(self):
        page = self.get_or_create_page(
            'payments', 'payment',
            ['payment_id', 'service_id', 'customer_id', 'amount',
             'payment_date', 'payment_method', 'payment_status',
             'transaction_id', 'due_date', 'discount', 'tax', 'total_amount', 'notes'],
            'payment'
        )
        self.content_stack.setCurrentWidget(page)
        self.status_bar.showMessage("Managing Payments")
    
    def show_reports(self):
        if self.pages['reports'] is None:
            self.pages['reports'] = ReportsWidget()
            self.content_stack.addWidget(self.pages['reports'])
        self.content_stack.setCurrentWidget(self.pages['reports'])
        self.status_bar.showMessage("Reports Dashboard")
    
    def closeEvent(self, event):
        """Handle application close"""
        reply = QMessageBox.question(
            self,
            "Confirm Exit",
            "Are you sure you want to exit the application?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.db.close()
            event.accept()
        else:
            event.ignore()


def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Set dark palette
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(236, 240, 241))
    palette.setColor(QPalette.WindowText, QColor(44, 62, 80))
    app.setPalette(palette)
    
    # Set application font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()