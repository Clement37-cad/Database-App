# equipment_rental_app.py
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import mysql.connector
from mysql.connector import Error
from datetime import datetime, date
import tkcalendar
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import subprocess
import os

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
            messagebox.showerror("Database Error", f"Error connecting to database: {e}")
    
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
            messagebox.showerror("Query Error", f"Error executing query: {e}")
            return None
    
    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()

class EquipmentRentalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Equipment Rental Management System")
        self.root.geometry("1200x700")
        self.root.configure(bg='#f0f0f0')
        
        # Initialize database
        self.db = DatabaseConnection()
        
        # Configure styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('Title.TLabel', font=('Helvetica', 24, 'bold'), background='#f0f0f0')
        self.style.configure('Header.TLabel', font=('Helvetica', 14, 'bold'), background='#f0f0f0')
        self.style.configure('Custom.TButton', font=('Helvetica', 11), padding=10)
        
        self.create_main_menu()
        
    def create_main_menu(self):
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Main container
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(main_frame, text="Equipment Rental Management System", 
                               style='Title.TLabel')
        title_label.pack(pady=(0, 30))
        
        # Subtitle
        subtitle_label = ttk.Label(main_frame, text="Select an option to manage", 
                                  style='Header.TLabel')
        subtitle_label.pack(pady=(0, 40))
        
        # Buttons grid
        button_frame = tk.Frame(main_frame, bg='#f0f0f0')
        button_frame.pack(expand=True)
        
        buttons = [
            ("Customers", self.open_customer_interface, "#4CAF50"),
            ("Equipment", self.open_equipment_interface, "#2196F3"),
            ("Staff", self.open_staff_interface, "#FF9800"),
            ("Rentals", self.open_rental_interface, "#9C27B0"),
            ("Payments", self.open_payment_interface, "#00BCD4"),
            ("Maintenance", self.open_maintenance_interface, "#F44336"),
            ("Generate Reports", self.open_reports, "#607D8B")
        ]
        
        for i, (text, command, color) in enumerate(buttons):
            btn = tk.Button(button_frame, text=text, command=command,
                          font=('Helvetica', 14, 'bold'), bg=color, fg='white',
                          activebackground=color, activeforeground='white',
                          width=20, height=3, cursor='hand2', relief='flat')
            btn.pack(pady=5)
        
        # Footer
        footer_label = ttk.Label(main_frame, text="© 2024 Equipment Rental System", 
                                font=('Helvetica', 10), background='#f0f0f0')
        footer_label.pack(side='bottom', pady=10)
    
    def create_interface(self, title, columns, table_name, additional_widgets=None):
        # Create new window
        window = tk.Toplevel(self.root)
        window.title(title)
        window.geometry("1200x700")
        window.configure(bg='white')
        
        # Header
        header_frame = tk.Frame(window, bg='#2c3e50', height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text=title, font=('Helvetica', 20, 'bold'),
                              bg='#2c3e50', fg='white')
        title_label.pack(side='left', padx=20, pady=20)
        
        back_btn = tk.Button(header_frame, text="← Back to Menu", command=window.destroy,
                           font=('Helvetica', 11), bg='#e74c3c', fg='white',
                           cursor='hand2', relief='flat', padx=20)
        back_btn.pack(side='right', padx=20, pady=20)
        
        # Main content
        content_frame = tk.Frame(window, bg='white')
        content_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Left panel for form
        form_frame = tk.Frame(content_frame, bg='#f8f9fa', relief='solid', bd=1)
        form_frame.pack(side='left', fill='y', padx=(0, 10), pady=0)
        
        form_title = tk.Label(form_frame, text="Add/Edit Record", font=('Helvetica', 16, 'bold'),
                            bg='#f8f9fa', fg='#2c3e50')
        form_title.pack(pady=10)
        
        # Create form entries
        entries = {}
        for col in columns[1:]:  # Skip ID column
            frame = tk.Frame(form_frame, bg='#f8f9fa')
            frame.pack(pady=5, padx=20, fill='x')
            
            label = tk.Label(frame, text=col.replace('_', ' ').title() + ':', 
                           font=('Helvetica', 10), bg='#f8f9fa', anchor='w')
            label.pack()
            
            entry = tk.Entry(frame, font=('Helvetica', 10), bd=2, relief='solid')
            entry.pack(fill='x', ipady=3)
            entries[col] = entry
        
        # Buttons
        btn_frame = tk.Frame(form_frame, bg='#f8f9fa')
        btn_frame.pack(pady=15, padx=20)
        
        add_btn = tk.Button(btn_frame, text="Add Record", bg='#27ae60', fg='white',
                          font=('Helvetica', 11, 'bold'), cursor='hand2', relief='flat',
                          command=lambda: self.add_record(table_name, columns[1:], entries))
        add_btn.pack(side='left', padx=5)
        
        update_btn = tk.Button(btn_frame, text="Update Selected", bg='#f39c12', fg='white',
                             font=('Helvetica', 11, 'bold'), cursor='hand2', relief='flat',
                             command=lambda: self.update_record(table_name, columns, entries))
        update_btn.pack(side='left', padx=5)
        
        delete_btn = tk.Button(btn_frame, text="Delete Selected", bg='#e74c3c', fg='white',
                             font=('Helvetica', 11, 'bold'), cursor='hand2', relief='flat',
                             command=lambda: self.delete_record(table_name, columns[0]))
        delete_btn.pack(side='left', padx=5)
        
        clear_btn = tk.Button(btn_frame, text="Clear Form", bg='#95a5a6', fg='white',
                            font=('Helvetica', 11, 'bold'), cursor='hand2', relief='flat',
                            command=lambda: self.clear_form(entries))
        clear_btn.pack(side='left', padx=5)
        
        # Right panel for table
        table_frame = tk.Frame(content_frame, bg='white', relief='solid', bd=1)
        table_frame.pack(side='right', expand=True, fill='both')
        
        # Search frame
        search_frame = tk.Frame(table_frame, bg='white')
        search_frame.pack(fill='x', pady=10, padx=10)
        
        search_label = tk.Label(search_frame, text="Search:", font=('Helvetica', 11),
                              bg='white')
        search_label.pack(side='left', padx=5)
        
        search_entry = tk.Entry(search_frame, font=('Helvetica', 10), width=30)
        search_entry.pack(side='left', padx=5)
        
        search_btn = tk.Button(search_frame, text="Search", bg='#3498db', fg='white',
                             font=('Helvetica', 10), cursor='hand2',
                             command=lambda: self.search_records(table_name, columns, search_entry.get()))
        search_btn.pack(side='left', padx=5)
        
        refresh_btn = tk.Button(search_frame, text="Refresh", bg='#2ecc71', fg='white',
                              font=('Helvetica', 10), cursor='hand2',
                              command=lambda: self.refresh_table(table_name, columns))
        refresh_btn.pack(side='left', padx=5)
        
        # Create Treeview
        tree_frame = tk.Frame(table_frame, bg='white')
        tree_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        tree_scroll_y = tk.Scrollbar(tree_frame)
        tree_scroll_y.pack(side='right', fill='y')
        
        tree_scroll_x = tk.Scrollbar(tree_frame, orient='horizontal')
        tree_scroll_x.pack(side='bottom', fill='x')
        
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings',
                          yscrollcommand=tree_scroll_y.set,
                          xscrollcommand=tree_scroll_x.set)
        
        tree_scroll_y.config(command=tree.yview)
        tree_scroll_x.config(command=tree.xview)
        
        # Configure columns
        for col in columns:
            tree.heading(col, text=col.replace('_', ' ').title())
            tree.column(col, width=120, minwidth=80)
        
        tree.pack(expand=True, fill='both')
        
        # Bind selection event
        tree.bind('<<TreeviewSelect>>', lambda e: self.on_select(tree, entries, columns))
        
        # Load initial data
        self.refresh_table(table_name, columns)
        
        return window, tree, entries
    
    def refresh_table(self, table_name, columns):
        query = f"SELECT * FROM {table_name}"
        results = self.db.execute_query(query)
        
        # Clear table
        if hasattr(self, 'current_tree'):
            for item in self.current_tree.get_children():
                self.current_tree.delete(item)
            
            # Insert data
            if results:
                for row in results:
                    values = [row[col] for col in columns]
                    self.current_tree.insert('', 'end', values=values)
    
    def on_select(self, tree, entries, columns):
        selection = tree.selection()
        if selection:
            item = tree.item(selection[0])
            values = item['values']
            
            # Clear and populate form
            self.clear_form(entries)
            for i, col in enumerate(columns[1:]):
                if col in entries and i < len(values) - 1:
                    entries[col].delete(0, tk.END)
                    if values[i + 1] is not None:
                        entries[col].insert(0, str(values[i + 1]))
    
    def clear_form(self, entries):
        for entry in entries.values():
            entry.delete(0, tk.END)
    
    def add_record(self, table_name, columns, entries):
        # Get values from entries
        values = []
        for col in columns:
            value = entries[col].get()
            values.append(value if value else None)
        
        # Create query
        placeholders = ', '.join(['%s'] * len(columns))
        columns_str = ', '.join(columns)
        query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"# Execute query
        result = self.db.execute_query(query, values)
        if result:
            messagebox.showinfo("Success", "Record added successfully!")
            self.refresh_table(table_name, columns)
            self.clear_form(entries)
    
    def update_record(self, table_name, columns, entries):
        selection = self.current_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a record to update")
            return
        
        # Get ID of selected record
        item = self.current_tree.item(selection[0])
        record_id = item['values'][0]
        
        # Get updated values
        set_clause = []
        values = []
        for col in columns[1:]:
            value = entries[col].get()
            if value:
                set_clause.append(f"{col} = %s")
                values.append(value)
        
        if not set_clause:
            messagebox.showwarning("Warning", "No values to update")
            return
        
        # Create query
        set_clause_str = ', '.join(set_clause)
        values.append(record_id)
        query = f"UPDATE {table_name} SET {set_clause_str} WHERE {columns[0]} = %s"
        
        # Execute query
        result = self.db.execute_query(query, values)
        if result is not None:
            messagebox.showinfo("Success", "Record updated successfully!")
            self.refresh_table(table_name, columns)
    
    def delete_record(self, table_name, id_column):
        selection = self.current_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a record to delete")
            return
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm", "Are you sure you want to delete this record?"):
            return
        
        # Get ID
        item = self.current_tree.item(selection[0])
        record_id = item['values'][0]
        
        # Delete query
        query = f"DELETE FROM {table_name} WHERE {id_column} = %s"
        result = self.db.execute_query(query, (record_id,))
        
        if result is not None:
            messagebox.showinfo("Success", "Record deleted successfully!")
            self.refresh_table(table_name, [id_column] + list(self.entries.keys()))
    
    def search_records(self, table_name, columns, search_term):
        if not search_term:
            self.refresh_table(table_name, columns)
            return
        
        # Create search query across all text columns
        search_conditions = []
        for col in columns:
            search_conditions.append(f"{col} LIKE %s")
        
        query = f"SELECT * FROM {table_name} WHERE {' OR '.join(search_conditions)}"
        params = [f"%{search_term}%"] * len(columns)
        
        results = self.db.execute_query(query, params)
        
        # Clear and populate table
        for item in self.current_tree.get_children():
            self.current_tree.delete(item)
        
        if results:
            for row in results:
                values = [row[col] for col in columns]
                self.current_tree.insert('', 'end', values=values)
    
    # Interface methods for each entity
    def open_customer_interface(self):
        self.window, self.current_tree, self.entries = self.create_interface(
            "Customer Management",
            ['customer_id', 'first_name', 'last_name', 'email', 'phone', 'address', 'registration_date'],
            'customers'
        )
    
    def open_equipment_interface(self):
        self.window, self.current_tree, self.entries = self.create_interface(
            "Equipment Management",
            ['equipment_id', 'name', 'category', 'description', 'daily_rate', 'status', 'purchase_date', 'last_maintenance_date'],
            'equipment'
        )
    
    def open_staff_interface(self):
        self.window, self.current_tree, self.entries = self.create_interface(
            "Staff Management",['staff_id', 'first_name', 'last_name', 'email', 'phone', 'position', 'hire_date', 'salary'],
            'staff'
        )
    
    def open_rental_interface(self):
        self.window, self.current_tree, self.entries = self.create_interface(
            "Rental Management",
            ['rental_id', 'customer_id', 'equipment_id', 'staff_id', 'rental_date', 'return_date', 'total_amount', 'status'],
            'rentals'
        )
    
    def open_payment_interface(self):
        self.window, self.current_tree, self.entries = self.create_interface(
            "Payment Management",
            ['payment_id', 'rental_id', 'amount', 'payment_date', 'payment_method', 'status'],
            'payments'
        )
    
    def open_maintenance_interface(self):
        self.window, self.current_tree, self.entries = self.create_interface(
            "Maintenance Management",
            ['maintenance_id', 'equipment_id', 'staff_id', 'maintenance_date', 'description', 'cost', 'next_maintenance_date', 'status'],
            'maintenance'
        )
    
    def open_reports(self):
        # Create reports window
        report_window = tk.Toplevel(self.root)
        report_window.title("Generate Reports")
        report_window.geometry("800x600")
        report_window.configure(bg='white')
        
        # Header
        header_frame = tk.Frame(report_window, bg='#2c3e50', height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="Report Generation", font=('Helvetica', 20, 'bold'),
                              bg='#2c3e50', fg='white')
        title_label.pack(side='left', padx=20, pady=20)
        
        back_btn = tk.Button(header_frame, text="← Back", command=report_window.destroy,
                           font=('Helvetica', 11), bg='#e74c3c', fg='white',
                           cursor='hand2', relief='flat', padx=20)
        back_btn.pack(side='right', padx=20, pady=20)
        
        # Reports content
        content = tk.Frame(report_window, bg='white')
        content.pack(expand=True, fill='both', padx=30, pady=30)
        
        reports_title = tk.Label(content, text="Available Reports", font=('Helvetica', 18, 'bold'),
                                bg='white', fg='#2c3e50')
        reports_title.pack(pady=20)
        
        # Report buttons
        reports = [
            ("Customer Report", self.generate_customer_report, "#4CAF50"),
            ("Equipment Report", self.generate_equipment_report, "#2196F3"),
            ("Rental Activity Report", self.generate_rental_report, "#9C27B0"),
            ("Payment Summary Report", self.generate_payment_report, "#00BCD4"),
            ("Maintenance Report", self.generate_maintenance_report, "#F44336"),
            ("Staff Performance Report", self.generate_staff_report, "#FF9800")
        ]
        
        for text, command, color in reports:
            btn = tk.Button(content, text=text, command=command,
                          font=('Helvetica', 13, 'bold'), bg=color, fg='white',
                          activebackground=color, activeforeground='white',
                          width=30, height=2, cursor='hand2', relief='flat')
            btn.pack(pady=8)
    
    # Report generation methods
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
        results = self.db.executequery(query)
        
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

                    # Create reports directory if it doesn't exist
                    if not os.path.exists('reports'):
                        os.makedirs('reports')
                    
                    filepath = f"reports/{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                    
                    doc = SimpleDocTemplate(filepath, pagesize=letter)
                    elements = []
                    
                    # Add title
                    styles = getSampleStyleSheet()
                    title_style = styles['Heading1']
                    title = Paragraph(f"<u>{filename.replace('_', ' ')}</u>", title_style)
                    elements.append(title)
                    elements.append(Spacer(1, 20))
            
                    # Add timestamp
                    timestamp = Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                                        styles['Normal'])
                    elements.append(timestamp)
                    elements.append(Spacer(1, 20))
                    
                    # Prepare table data
                    table_data = [headers]
                    for row in data:
                        table_data.append([str(val) if val is not None else '' for val in row.values()])
                    
                    # Create table
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
                            
                    # Build PDF
                    doc.build(elements)
                    
                    messagebox.showinfo("Success", f"Report generated successfully!\nSaved to: {filepath}")
                    
                    # Open the PDF
                    if os.name == 'nt':  # Windows
                        os.startfile(filepath)
                    elif os.name == 'posix':  # macOS and Linux
                        subprocess.call(['open', filepath])
                
                except Exception as e:

                    messagebox.showerror("Error", f"Error generating report: {e}")

def main():
    root = tk.Tk()
    app = EquipmentRentalApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()