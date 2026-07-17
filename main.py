# equipment_rental_app.py
import sys
import os
import subprocess
from datetime import datetime
from collections import OrderedDict

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTableWidget, QTableWidgetItem,
    QTabWidget, QGroupBox, QFormLayout, QMessageBox, QHeaderView,
    QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox, QTextEdit,
    QSplitter, QFrame, QToolBar, QAction, QStackedWidget
)
from PyQt5.QtCore import Qt, QDate, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon, QFont, QPalette, QColor

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

import mysql.connector
from mysql.connector import Error


# ============================
# Database Connection
# ============================
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
                password='5757'  # Change to your MySQL password
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


# ============================
# Modern Table Widget
# ============================
class ModernTableWidget(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlternatingRowColors(True)
        self.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                alternate-background-color: #f5f7fa;
                gridline-color: #e1e5eb;
                selection-background-color: #4a90d9;
                selection-color: white;
                font-size: 12px;
                border: none;
            }
            QTableWidget::item {
                padding: 6px;
            }
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 8px;
                font-weight: bold;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #4a90d9;
            }
        """)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.verticalHeader().setVisible(False)
        self.setSelectionBehavior(QTableWidget.SelectRows)


# ============================
# Main Application
# ============================
class EquipmentRentalApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DatabaseConnection()
        self.current_table = None
        self.current_table_name = None
        self.current_columns = []
        self.current_entries = {}
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Equipment Rental Management System")
        self.setGeometry(100, 100, 1400, 800)

        # Set dark title bar style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f2f5;
            }
            QLabel {
                color: #2c3e50;
            }
            QPushButton {
                border-radius: 6px;
                font-weight: bold;
                padding: 8px 16px;
            }
            QPushButton:hover {
                opacity: 0.9;
            }
            QLineEdit, QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox, QTextEdit {
                padding: 8px;
                border: 1px solid #d0d5dd;
                border-radius: 4px;
                background-color: white;
                font-size: 12px;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus {
                border: 1px solid #4a90d9;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #d0d5dd;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 12px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
                color: #2c3e50;
            }
        """)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Top bar
        self.create_top_bar(main_layout)

        # Main content
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #f0f2f5;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)

        # Title
        title_label = QLabel("Equipment Rental Management System")
        title_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #1a2332;
            padding: 10px 0;
        """)
        content_layout.addWidget(title_label)

        # Subtitle
        subtitle_label = QLabel("Select an option below to manage your rental business")
        subtitle_label.setStyleSheet("font-size: 14px; color: #6b7a8a; margin-bottom: 10px;")
        content_layout.addWidget(subtitle_label)

        # Main menu buttons
        self.create_menu_buttons(content_layout)

        main_layout.addWidget(content_widget)

        # Status bar
        self.statusBar().showMessage("Ready")
        self.statusBar().setStyleSheet("""
            QStatusBar {
                background-color: #2c3e50;
                color: white;
                padding: 6px;
            }
        """)

    def create_top_bar(self, layout):
        top_bar = QWidget()
        top_bar.setFixedHeight(60)
        top_bar.setStyleSheet("""
            background-color: #1a2332;
            border-bottom: 2px solid #2c3e50;
        """)
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(20, 0, 20, 0)

        logo_label = QLabel("📦 Equipment Rental")
        logo_label.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        top_layout.addWidget(logo_label)

        top_layout.addStretch()

        # Quick actions
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 6px 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_current_table)
        top_layout.addWidget(refresh_btn)

        about_btn = QPushButton("ℹ️ About")
        about_btn.setStyleSheet("""
            QPushButton {
                background-color: #7f8c8d;
                color: white;
                padding: 6px 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #6c7a7a;
            }
        """)
        about_btn.clicked.connect(self.show_about)
        top_layout.addWidget(about_btn)

        layout.addWidget(top_bar)

    def create_menu_buttons(self, layout):
        button_container = QWidget()
        button_layout = QVBoxLayout(button_container)
        button_layout.setSpacing(12)

        # Row 1
        row1 = QHBoxLayout()
        row1.setSpacing(15)

        buttons = [
            ("👥 Customers", "#4CAF50", self.open_customer_interface),
            ("🔧 Equipment", "#2196F3", self.open_equipment_interface),
            ("👨‍💼 Staff", "#FF9800", self.open_staff_interface),
            ("📋 Rentals", "#9C27B0", self.open_rental_interface),
        ]

        for text, color, callback in buttons:
            btn = QPushButton(text)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    font-size: 16px;
                    padding: 16px 24px;
                    border-radius: 8px;
                }}
                QPushButton:hover {{
                    background-color: {self.darken_color(color)};
                }}
            """)
            btn.clicked.connect(callback)
            btn.setMinimumHeight(60)
            row1.addWidget(btn)

        row1.addStretch()
        button_layout.addLayout(row1)

        # Row 2
        row2 = QHBoxLayout()
        row2.setSpacing(15)

        buttons2 = [
            ("💳 Payments", "#00BCD4", self.open_payment_interface),
            ("🔨 Maintenance", "#F44336", self.open_maintenance_interface),
            ("📊 Reports", "#607D8B", self.open_reports),
        ]

        for text, color, callback in buttons2:
            btn = QPushButton(text)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    font-size: 16px;
                    padding: 16px 24px;
                    border-radius: 8px;
                }}
                QPushButton:hover {{
                    background-color: {self.darken_color(color)};
                }}
            """)
            btn.clicked.connect(callback)
            btn.setMinimumHeight(60)
            row2.addWidget(btn)

        row2.addStretch()
        button_layout.addLayout(row2)

        layout.addWidget(button_container)

    def darken_color(self, color):
        # Simple darken - just return a slightly different shade
        colors_map = {
            "#4CAF50": "#388E3C",
            "#2196F3": "#1976D2",
            "#FF9800": "#F57C00",
            "#9C27B0": "#7B1FA2",
            "#00BCD4": "#0097A7",
            "#F44336": "#D32F2F",
            "#607D8B": "#455A64",
        }
        return colors_map.get(color, "#333333")

    def show_about(self):
        QMessageBox.about(
            self,
            "About Equipment Rental System",
            """
            <h2>Equipment Rental Management System</h2>
            <p>Version 2.0</p>
            <p>A modern desktop application for managing equipment rentals.</p>
            <p><b>Features:</b></p>
            <ul>
                <li>Customer Management</li>
                <li>Equipment Inventory</li>
                <li>Staff Management</li>
                <li>Rental Processing</li>
                <li>Payment Tracking</li>
                <li>Maintenance Scheduling</li>
                <li>Report Generation</li>
            </ul>
            <p>© 2024 Equipment Rental System</p>
            """
        )

    def refresh_current_table(self):
        if self.current_table_name and self.current_columns:
            self.load_table_data(self.current_table_name, self.current_columns)

    # ============================
    # Interface Creation
    # ============================
    def create_interface(self, title, columns, table_name):
        # Create a new window/tab
        interface_widget = QWidget()
        interface_widget.setStyleSheet("background-color: #f0f2f5;")

        layout = QVBoxLayout(interface_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QWidget()
        header.setFixedHeight(70)
        header.setStyleSheet("background-color: #2c3e50;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)

        title_label = QLabel(title)
        title_label.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        back_btn = QPushButton("← Back to Menu")
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 8px 20px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        back_btn.clicked.connect(self.go_back_to_menu)
        header_layout.addWidget(back_btn)

        layout.addWidget(header)

        # Main content
        content = QWidget()
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)

        # Form panel
        form_panel = self.create_form_panel(columns, table_name)
        content_layout.addWidget(form_panel, 1)

        # Table panel
        table_panel = self.create_table_panel(columns, table_name)
        content_layout.addWidget(table_panel, 3)

        layout.addWidget(content)

        # Store references
        self.current_table_name = table_name
        self.current_columns = columns
        self.current_entries = self.entry_widgets
        self.current_table = self.table_widget

        # Load data
        self.load_table_data(table_name, columns)

        # Replace central widget
        self.setCentralWidget(interface_widget)

    def create_form_panel(self, columns, table_name):
        panel = QWidget()
        panel.setStyleSheet("""
            background-color: white;
            border-radius: 8px;
            border: 1px solid #e1e5eb;
        """)
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(20, 20, 20, 20)
        panel_layout.setSpacing(12)

        form_title = QLabel("Add / Edit Record")
        form_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        panel_layout.addWidget(form_title)

        # Form fields
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignRight)

        self.entry_widgets = {}

        for col in columns[1:]:  # Skip ID column
            label_text = col.replace('_', ' ').title()
            entry = QLineEdit()
            entry.setPlaceholderText(f"Enter {label_text.lower()}")

            # Special handling for date fields
            if 'date' in col.lower():
                entry = QDateEdit()
                entry.setDate(QDate.currentDate())
                entry.setCalendarPopup(True)
                entry.setDisplayFormat("yyyy-MM-dd")

            # Special handling for status fields
            if col.lower() == 'status':
                entry = QComboBox()
                entry.addItems(['Active', 'Inactive', 'Pending', 'Completed', 'Maintenance'])

            # Special handling for numeric fields
            if 'rate' in col.lower() or 'amount' in col.lower() or 'salary' in col.lower() or 'cost' in col.lower():
                entry = QDoubleSpinBox()
                entry.setRange(0, 999999)
                entry.setPrefix("GHc")

            self.entry_widgets[col] = entry
            form_layout.addRow(label_text + ":", entry)

        panel_layout.addWidget(form_widget)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        add_btn = QPushButton("➕ Add")
        add_btn.setStyleSheet("background-color: #27ae60; color: white;")
        add_btn.clicked.connect(lambda: self.add_record(table_name, columns[1:], self.entry_widgets))
        btn_layout.addWidget(add_btn)

        update_btn = QPushButton("✏️ Update")
        update_btn.setStyleSheet("background-color: #f39c12; color: white;")
        update_btn.clicked.connect(lambda: self.update_record(table_name, columns, self.entry_widgets))
        btn_layout.addWidget(update_btn)

        delete_btn = QPushButton("🗑️ Delete")
        delete_btn.setStyleSheet("background-color: #e74c3c; color: white;")
        delete_btn.clicked.connect(lambda: self.delete_record(table_name, columns[0]))
        btn_layout.addWidget(delete_btn)

        clear_btn = QPushButton("🔄 Clear")
        clear_btn.setStyleSheet("background-color: #95a5a6; color: white;")
        clear_btn.clicked.connect(lambda: self.clear_form(self.entry_widgets))
        btn_layout.addWidget(clear_btn)

        panel_layout.addLayout(btn_layout)
        panel_layout.addStretch()

        return panel

    def create_table_panel(self, columns, table_name):
        panel = QWidget()
        panel.setStyleSheet("""
            background-color: white;
            border-radius: 8px;
            border: 1px solid #e1e5eb;
        """) 
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(20, 20, 20, 20)
        panel_layout.setSpacing(12)

        # Search bar
        search_layout = QHBoxLayout()

        search_label = QLabel("🔍 Search:")
        search_label.setStyleSheet("font-weight: bold;")
        search_layout.addWidget(search_label)

        search_entry = QLineEdit()
        search_entry.setPlaceholderText("Type to search...")
        search_entry.setMinimumWidth(300)
        search_layout.addWidget(search_entry)

        search_btn = QPushButton("Search")
        search_btn.setStyleSheet("background-color: #3498db; color: white;")
        search_btn.clicked.connect(lambda: self.search_records(table_name, columns, search_entry.text()))
        search_layout.addWidget(search_btn)

        refresh_btn = QPushButton("↻ Refresh")
        refresh_btn.setStyleSheet("background-color: #2ecc71; color: white;")
        refresh_btn.clicked.connect(lambda: self.load_table_data(table_name, columns))
        search_layout.addWidget(refresh_btn)

        search_layout.addStretch()
        panel_layout.addLayout(search_layout)

        # Table
        self.table_widget = ModernTableWidget()
        self.table_widget.setColumnCount(len(columns))
        self.table_widget.setHorizontalHeaderLabels([col.replace('_', ' ').title() for col in columns])

        # Connect selection
        self.table_widget.itemSelectionChanged.connect(
            lambda: self.on_select(self.table_widget, self.entry_widgets, columns)
        )

        panel_layout.addWidget(self.table_widget)

        return panel

    def load_table_data(self, table_name, columns):
        if not hasattr(self, 'table_widget'):
            return

        query = f"SELECT * FROM {table_name}"
        results = self.db.execute_query(query)

        self.table_widget.setRowCount(0)

        if results:
            self.table_widget.setRowCount(len(results))
            for row_idx, row in enumerate(results):
                for col_idx, col in enumerate(columns):
                    value = row.get(col, '')
                    if value is None:
                        value = ''
                    item = QTableWidgetItem(str(value))
                    self.table_widget.setItem(row_idx, col_idx, item)

        # Resize columns
        self.table_widget.resizeColumnsToContents()

    def on_select(self, table_widget, entries, columns):
        selected = table_widget.currentRow()
        if selected < 0:
            return

        self.clear_form(entries)

        for col_idx, col in enumerate(columns[1:]):
            item = table_widget.item(selected, col_idx + 1)
            if item:
                value = item.text()
                widget = entries.get(col)
                if widget:
                    if isinstance(widget, QLineEdit):
                        widget.setText(value)
                    elif isinstance(widget, QDateEdit):
                        try:
                            date_parts = value.split('-')
                            if len(date_parts) == 3:
                                widget.setDate(QDate(int(date_parts[0]), int(date_parts[1]), int(date_parts[2])))
                        except:
                            pass
                    elif isinstance(widget, QComboBox):
                        idx = widget.findText(value)
                        if idx >= 0:
                            widget.setCurrentIndex(idx)
                    elif isinstance(widget, QDoubleSpinBox):
                        try:
                            widget.setValue(float(value.replace('GHc ', '').strip()))
                        except:
                            pass

    def clear_form(self, entries):
        for widget in entries.values():
            if isinstance(widget, QLineEdit):
                widget.clear()
            elif isinstance(widget, QDateEdit):
                widget.setDate(QDate.currentDate())
            elif isinstance(widget, QComboBox):
                widget.setCurrentIndex(0)
            elif isinstance(widget, QDoubleSpinBox):
                widget.setValue(0)
            elif isinstance(widget, QSpinBox):
                widget.setValue(0)

    def add_record(self, table_name, columns, entries):
        values = []
        for col in columns:
            widget = entries.get(col)
            if widget:
                if isinstance(widget, QLineEdit):
                    value = widget.text()
                elif isinstance(widget, QDateEdit):
                    value = widget.date().toString("yyyy-MM-dd")
                elif isinstance(widget, QComboBox):
                    value = widget.currentText()
                elif isinstance(widget, QDoubleSpinBox):
                    value = widget.value()
                elif isinstance(widget, QSpinBox):
                    value = widget.value()
                else:
                    value = widget.text()
                values.append(value if value else None)

        placeholders = ', '.join(['%s'] * len(columns))
        columns_str = ', '.join(columns)
        query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"

        result = self.db.execute_query(query, values)
        if result:
            QMessageBox.information(self, "Success", "Record added successfully!")
            self.load_table_data(table_name, self.current_columns)
            self.clear_form(entries)

    def update_record(self, table_name, columns, entries):
        selected = self.table_widget.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Warning", "Please select a record to update")
            return

        record_id = self.table_widget.item(selected, 0).text()

        set_clause = []
        values = []
        for col in columns[1:]:
            widget = entries.get(col)
            if widget:
                if isinstance(widget, QLineEdit):
                    value = widget.text()
                elif isinstance(widget, QDateEdit):
                    value = widget.date().toString("yyyy-MM-dd")
                elif isinstance(widget, QComboBox):
                    value = widget.currentText()
                elif isinstance(widget, QDoubleSpinBox):
                    value = widget.value()
                elif isinstance(widget, QSpinBox):
                    value = widget.value()
                else:
                    value = widget.text()

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
            self.load_table_data(table_name, columns)

    def delete_record(self, table_name, id_column):
        selected = self.table_widget.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Warning", "Please select a record to delete")
            return

        reply = QMessageBox.question(
            self, "Confirm",
            "Are you sure you want to delete this record?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        record_id = self.table_widget.item(selected, 0).text()
        query = f"DELETE FROM {table_name} WHERE {id_column} = %s"
        result = self.db.execute_query(query, (record_id,))

        if result is not None:
            QMessageBox.information(self, "Success", "Record deleted successfully!")
            self.load_table_data(table_name, self.current_columns)

    def search_records(self, table_name, columns, search_term):
        if not search_term:
            self.load_table_data(table_name, columns)
            return

        search_conditions = []
        for col in columns:
            search_conditions.append(f"{col} LIKE %s")

        query = f"SELECT * FROM {table_name} WHERE {' OR '.join(search_conditions)}"
        params = [f"%{search_term}%"] * len(columns)

        results = self.db.execute_query(query, params)

        self.table_widget.setRowCount(0)
        if results:
            self.table_widget.setRowCount(len(results))
            for row_idx, row in enumerate(results):
                for col_idx, col in enumerate(columns):
                    value = row.get(col, '')
                    if value is None:
                        value = ''
                    item = QTableWidgetItem(str(value))
                    self.table_widget.setItem(row_idx, col_idx, item)

    def go_back_to_menu(self):
        self.init_ui()

    # ============================
    # Interface Entry Points
    # ============================
    def open_customer_interface(self):
        self.create_interface(
            "👥 Customer Management",
            ['customer_id', 'first_name', 'last_name', 'email', 'phone', 'address', 'registration_date'],
            'customers'
        )

    def open_equipment_interface(self):
        self.create_interface(
            "🔧 Equipment Management",
            ['equipment_id', 'name', 'category', 'description', 'daily_rate', 'status', 'purchase_date',
             'last_maintenance_date'],
            'equipment'
        )

    def open_staff_interface(self):
        self.create_interface(
            "👨‍💼 Staff Management",
            ['staff_id', 'first_name', 'last_name', 'email', 'phone', 'position', 'hire_date', 'salary'],
            'staff'
        )

    def open_rental_interface(self):
        self.create_interface(
            "📋 Rental Management",
            ['rental_id', 'customer_id', 'equipment_id', 'staff_id', 'rental_date', 'return_date', 'total_amount',
             'status'],
            'rentals'
        )

    def open_payment_interface(self):
        self.create_interface(
            "💳 Payment Management",
            ['payment_id', 'rental_id', 'amount', 'payment_date', 'payment_method', 'status'],
            'payments'
        )

    def open_maintenance_interface(self):
        self.create_interface(
            "🔨 Maintenance Management",
            ['maintenance_id', 'equipment_id', 'staff_id', 'maintenance_date', 'description', 'cost',
             'next_maintenance_date', 'status'],
            'maintenance'
        )

    # ============================
    # Reports
    # ============================
    def open_reports(self):
        reports_widget = QWidget()
        reports_widget.setStyleSheet("background-color: #f0f2f5;")

        layout = QVBoxLayout(reports_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QWidget()
        header.setFixedHeight(70)
        header.setStyleSheet("background-color: #2c3e50;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)

        title_label = QLabel("📊 Report Generation")
        title_label.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        back_btn = QPushButton("← Back to Menu")
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 8px 20px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        back_btn.clicked.connect(self.go_back_to_menu)
        header_layout.addWidget(back_btn)

        layout.addWidget(header)

        # Content
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(40, 40, 40, 40)
        content_layout.setSpacing(20)

        reports_title = QLabel("Available Reports")
        reports_title.setStyleSheet("font-size: 22px; font-weight: bold; color: #2c3e50;")
        content_layout.addWidget(reports_title)

        reports_desc = QLabel("Select a report to generate and download as PDF")
        reports_desc.setStyleSheet("font-size: 14px; color: #6b7a8a; margin-bottom: 10px;")
        content_layout.addWidget(reports_desc)

        # Report buttons grid
        grid = QHBoxLayout()
        grid.setSpacing(15)

        reports = [
            ("👥 Customer Report", self.generate_customer_report, "#4CAF50"),
            ("🔧 Equipment Report", self.generate_equipment_report, "#2196F3"),
            ("📋 Rental Activity", self.generate_rental_report, "#9C27B0"),
            ("💳 Payment Summary", self.generate_payment_report, "#00BCD4"),
            ("🔨 Maintenance Report", self.generate_maintenance_report, "#F44336"),
            ("👨‍💼 Staff Performance", self.generate_staff_report, "#FF9800"),
        ]

        for text, callback, color in reports:
            btn = QPushButton(text)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    font-size: 14px;
                    padding: 16px 24px;
                    border-radius: 8px;
                    min-width: 180px;
                }}
                QPushButton:hover {{
                    background-color: {self.darken_color(color)};
                }}
            """)
            btn.clicked.connect(callback)
            grid.addWidget(btn)

        content_layout.addLayout(grid)
        content_layout.addStretch()

        layout.addWidget(content)
        self.setCentralWidget(reports_widget)

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
                                 ["Rental ID", "Customer", "Equipment", "Staff", "Rental Date", "Return Date", "Amount",
                                  "Status"],
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
                                 ["ID", "Equipment", "Staff", "Date", "Description", "Cost", "Status",
                                  "Next Maintenance"],
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
                                 ["ID", "Staff Name", "Position", "Hire Date", "Rentals Handled", "Maintenance Done",
                                  "Revenue Generated"],
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


# ============================
# Main Entry Point
# ============================
def main():
    app = QApplication(sys.argv)

    # Set application style
    app.setStyle('Fusion')

    # Dark palette for modern look
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(240, 242, 245))
    palette.setColor(QPalette.WindowText, QColor(44, 62, 80))
    palette.setColor(QPalette.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.AlternateBase, QColor(245, 247, 250))
    palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ToolTipText, QColor(44, 62, 80))
    palette.setColor(QPalette.Text, QColor(44, 62, 80))
    palette.setColor(QPalette.Button, QColor(255, 255, 255))
    palette.setColor(QPalette.ButtonText, QColor(44, 62, 80))
    palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.Link, QColor(66, 133, 244))
    palette.setColor(QPalette.Highlight, QColor(74, 144, 217))
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)

    window = EquipmentRentalApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()