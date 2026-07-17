# auto_repair_management_system.py

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import mysql.connector
from mysql.connector import Error
from datetime import datetime, date
import tkcalendar
from tkinter import font as tkfont

class AutoRepairManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("🚗 Auto Repair Shop Management System")
        self.root.geometry("1200x700")
        self.root.configure(bg='#2c3e50')
        
        # Database connection
        self.db_connection = None
        self.cursor = None
        self.connect_to_database()
        
        # Configure styles
        self.setup_styles()
        
        # Create main container
        self.main_container = tk.Frame(self.root, bg='#2c3e50')
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        self.create_header()
        
        # Navigation buttons
        self.create_navigation()
        
        # Content area
        self.content_frame = tk.Frame(self.main_container, bg='white', relief=tk.RAISED, bd=2)
        self.content_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Status bar
        self.create_status_bar()
        
        # Show home page
        self.show_home()
    
    def setup_styles(self):
        """Configure ttk styles for modern look"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('Title.TLabel', 
                       background='#2c3e50', 
                       foreground='white', 
                       font=('Helvetica', 24, 'bold'))
        
        style.configure('Header.TLabel',
                       background='white',
                       foreground='#2c3e50',
                       font=('Helvetica', 16, 'bold'))
        
        style.configure('Custom.TButton',
                       font=('Helvetica', 11, 'bold'),
                       padding=10)
        
        style.configure('Treeview',
                       font=('Helvetica', 10),
                       rowheight=25)
        
        style.configure('Treeview.Heading',
                       font=('Helvetica', 10, 'bold'))
    
    def connect_to_database(self):
        """Establish connection to MySQL database"""
        try:
            self.db_connection = mysql.connector.connect(
                host='localhost',
                user='root',  # Change this to your MySQL username
                password='5757',  # Change this to your MySQL password
                database='auto_repair_shop'
            )
            self.cursor = self.db_connection.cursor()
            print("Successfully connected to database")
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to connect to database: {e}")
            self.root.destroy()
    
    def create_header(self):
        """Create application header"""
        header_frame = tk.Frame(self.main_container, bg='#34495e', height=80)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        header_frame.pack_propagate(False)
        
        title_label = ttk.Label(header_frame, 
                               text="🔧 Auto Repair Shop Management System",
                               style='Title.TLabel',
                               background='#34495e')
        title_label.pack(expand=True)
    
    def create_navigation(self):
        """Create navigation buttons"""
        nav_frame = tk.Frame(self.main_container, bg='#2c3e50')
        nav_frame.pack(fill=tk.X, pady=(0, 10))
        
        entities = [
            ("👥 Customers", self.show_customers, '#e74c3c'),
            ("🏭 Workshops", self.show_workshops, '#3498db'),
            ("🚘 Vehicles", self.show_vehicles, '#2ecc71'),
            ("👨‍🔧 Mechanics", self.show_mechanics, '#f39c12'),
            ("🔧 Service Records", self.show_service_records, '#9b59b6'),
            ("⚙️ Parts", self.show_parts, '#1abc9c'),
            ("💳 Payments", self.show_payments, '#e67e22'),
            ("📊 Reports", self.show_reports, '#95a5a6')
        ]
        
        for text, command, color in entities:
            btn = tk.Button(nav_frame, 
                          text=text,
                          command=command,
                          bg=color,
                          fg='white',
                          font=('Helvetica', 10, 'bold'),
                          relief=tk.RAISED,
                          bd=2,
                          padx=15,
                          pady=5,
                          cursor='hand2')
            btn.pack(side=tk.LEFT, padx=5)
            btn.bind('<Enter>', lambda e, b=btn, c=color: b.configure(bg=self.lighten_color(c)))
            btn.bind('<Leave>', lambda e, b=btn, c=color: b.configure(bg=c))
    
    def lighten_color(self, color):
        """Lighten a hex color"""
        rgb = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        lightened = tuple(min(255, c + 30) for c in rgb)
        return f'#{lightened[0]:02x}{lightened[1]:02x}{lightened[2]:02x}'
    
    def create_status_bar(self):
        """Create status bar at bottom"""
        status_frame = tk.Frame(self.main_container, bg='#34495e', height=30)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(status_frame, 
                                    text="Ready | Database Connected",
                                    bg='#34495e',
                                    fg='white',
                                    font=('Helvetica', 9))
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        datetime_label = tk.Label(status_frame,
                                 text=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                 bg='#34495e',
                                 fg='white',
                                 font=('Helvetica', 9))
        datetime_label.pack(side=tk.RIGHT, padx=10)
    
    def clear_content(self):
        """Clear content frame"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_home(self):
        """Display home page with dashboard"""
        self.clear_content()
        self.status_label.config(text="Home | Dashboard")
        
        # Welcome message
        welcome_frame = tk.Frame(self.content_frame, bg='white')
        welcome_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(welcome_frame,
                text="Welcome to Auto Repair Shop Management System",
                font=('Helvetica', 20, 'bold'),
                bg='white',
                fg='#2c3e50').pack(pady=20)
        
        tk.Label(welcome_frame,
                text="Manage your auto repair shop efficiently with integrated database management",
                font=('Helvetica', 12),
                bg='white',
                fg='#7f8c8d').pack(pady=10)
        
        # Quick stats
        stats_frame = tk.Frame(welcome_frame, bg='white')
        stats_frame.pack(pady=30)
        
        stats = [
            ("Total Customers", "SELECT COUNT(*) FROM customer"),
            ("Active Services", "SELECT COUNT(*) FROM service_record WHERE status='In Progress'"),
            ("Pending Payments", "SELECT COUNT(*) FROM payment WHERE payment_status='Pending'"),
            ("Active Mechanics", "SELECT COUNT(*) FROM mechanic WHERE status='Active'")
        ]
        
        for label, query in stats:
            try:
                self.cursor.execute(query)
                count = self.cursor.fetchone()[0]
                
                stat_frame = tk.Frame(stats_frame, bg='white', relief=tk.RAISED, bd=1)
                stat_frame.pack(side=tk.LEFT, padx=10, pady=10)
                
                tk.Label(stat_frame, text=str(count), font=('Helvetica', 24, 'bold'),
                        bg='white', fg='#3498db').pack(padx=30, pady=5)
                tk.Label(stat_frame, text=label, font=('Helvetica', 10),
                        bg='white', fg='#7f8c8d').pack(pady=5)
            except Error as e:
                print(f"Error fetching stats: {e}")
    
    # ==================== ENTITY MANAGEMENT PAGES ====================
    
    def create_entity_page(self, title, entity_name, columns, fetch_query, add_query, update_query, delete_query):
        """Create a generic entity management page"""
        self.clear_content()
        self.status_label.config(text=f"Managing {entity_name}")
        
        # Title
        title_frame = tk.Frame(self.content_frame, bg='#3498db')
        title_frame.pack(fill=tk.X)
        tk.Label(title_frame, text=title, font=('Helvetica', 16, 'bold'),
                bg='#3498db', fg='white', padx=20, pady=10).pack()
        
        # Search frame
        search_frame = tk.Frame(self.content_frame, bg='white')
        search_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(search_frame, text="Search:", font=('Helvetica', 10),
                bg='white').pack(side=tk.LEFT, padx=5)
        
        search_entry = tk.Entry(search_frame, font=('Helvetica', 10), width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Button(search_frame, text="🔍 Search", bg='#3498db', fg='white',
                 command=lambda: self.search_records(entity_name, search_entry.get(), tree),
                 font=('Helvetica', 9)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(search_frame, text="🔄 Refresh", bg='#27ae60', fg='white',
                 command=lambda: self.refresh_tree(tree, entity_name),
                 font=('Helvetica', 9)).pack(side=tk.LEFT, padx=5)
        
        # Treeview
        tree_frame = tk.Frame(self.content_frame, bg='white')
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        scrollbar_y = ttk.Scrollbar(tree_frame)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        scrollbar_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings',
                           yscrollcommand=scrollbar_y.set,
                           xscrollcommand=scrollbar_x.set)
        
        scrollbar_y.config(command=tree.yview)
        scrollbar_x.config(command=tree.xview)
        
        for col in columns:
            tree.heading(col, text=col.replace('_', ' ').title())
            tree.column(col, width=120)
        
        tree.pack(fill=tk.BOTH, expand=True)
        
        # Buttons frame
        button_frame = tk.Frame(self.content_frame, bg='white')
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Button(button_frame, text="➕ Add New", bg='#27ae60', fg='white',
                 font=('Helvetica', 10, 'bold'), padx=20, pady=5,
                 command=lambda: self.add_record(entity_name, tree)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="✏️ Update", bg='#f39c12', fg='white',
                 font=('Helvetica', 10, 'bold'), padx=20, pady=5,
                 command=lambda: self.update_record(entity_name, tree)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="🗑️ Delete", bg='#e74c3c', fg='white',
                 font=('Helvetica', 10, 'bold'), padx=20, pady=5,
                 command=lambda: self.delete_record(entity_name, tree)).pack(side=tk.LEFT, padx=5)
        
        # Load data
        self.refresh_tree(tree, entity_name)
        
        return tree
    
    def refresh_tree(self, tree, entity_name):
        """Refresh treeview with data from database"""
        for item in tree.get_children():
            tree.delete(item)
        
        queries = {
            'customer': 'SELECT * FROM customer',
            'workshop': 'SELECT * FROM workshop',
            'vehicle': 'SELECT * FROM vehicle',
            'mechanic': 'SELECT * FROM mechanic',
            'service_record': 'SELECT * FROM service_record',
            'part': 'SELECT * FROM part',
            'payment': 'SELECT * FROM payment'
        }
        
        try:
            self.cursor.execute(queries[entity_name])
            records = self.cursor.fetchall()
            
            for record in records:
                tree.insert('', 'end', values=record)
            
            self.status_label.config(text=f"Loaded {len(records)} {entity_name} records")
        except Error as e:
            messagebox.showerror("Error", f"Failed to load data: {e}")
    
    def search_records(self, entity_name, search_term, tree):
        """Search records in treeview"""
        search_term = search_term.lower()
        
        for item in tree.get_children():
            values = tree.item(item)['values']
            match = any(search_term in str(value).lower() for value in values)
            
            if match:
                tree.selection_set(item)
                tree.see(item)
                break
        else:
            messagebox.showinfo("Search", "No matching records found")
    
    def add_record(self, entity_name, tree):
        """Add new record dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Add New {entity_name.replace('_', ' ').title()}")
        dialog.geometry("500x600")
        dialog.configure(bg='white')
        
        self.create_record_form(dialog, entity_name, tree, 'add')
    
    def update_record(self, entity_name, tree):
        """Update selected record"""
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a record to update")
            return
        
        values = tree.item(selected[0])['values']
        
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Update {entity_name.replace('_', ' ').title()}")
        dialog.geometry("500x600")
        dialog.configure(bg='white')
        
        self.create_record_form(dialog, entity_name, tree, 'update', values)
    
    def delete_record(self, entity_name, tree):
        """Delete selected record"""
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a record to delete")
            return
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this record?"):
            values = tree.item(selected[0])['values']
            id_value = values[0]
            
            id_columns = {
                'customer': 'customer_id',
                'workshop': 'workshop_id',
                'vehicle': 'vehicle_id',
                'mechanic': 'mechanic_id',
                'service_record': 'service_id',
                'part': 'part_id',
                'payment': 'payment_id'
            }
            
            try:
                query = f"DELETE FROM {entity_name} WHERE {id_columns[entity_name]} = %s"
                self.cursor.execute(query, (id_value,))
                self.db_connection.commit()
                
                self.refresh_tree(tree, entity_name)
                messagebox.showinfo("Success", "Record deleted successfully")
            except Error as e:
                messagebox.showerror("Error", f"Failed to delete record: {e}")
    
    def create_record_form(self, dialog, entity_name, tree, mode, values=None):
        """Create form for adding/updating records"""
        # Form fields definition for each entity
        fields = {
            'customer': [
                ('First Name', 'first_name', 'entry'),
                ('Last Name', 'last_name', 'entry'),
                ('Phone', 'phone', 'entry'),
                ('Email', 'email', 'entry'),
                ('Address', 'address', 'entry'),
                ('City', 'city', 'entry'),
                ('State', 'state', 'entry'),
                ('ZIP Code', 'zip_code', 'entry')
            ],
            'workshop': [
                ('Workshop Name', 'workshop_name', 'entry'),
                ('Location', 'location', 'entry'),
                ('Contact Number', 'contact_number', 'entry'),
                ('Manager Name', 'manager_name', 'entry'),
                ('Capacity', 'capacity', 'entry'),
                ('Opening Hours', 'opening_hours', 'entry'),
                ('Status', 'status', 'combo', ['Active', 'Inactive', 'Maintenance'])
            ],
            'vehicle': [
                ('Customer ID', 'customer_id', 'entry'),
                ('Workshop ID', 'workshop_id', 'entry'),
                ('Make', 'make', 'entry'),
                ('Model', 'model', 'entry'),
                ('Year', 'year', 'entry'),
                ('License Plate', 'license_plate', 'entry'),
                ('VIN', 'vin', 'entry'),
                ('Color', 'color', 'entry'),
                ('Mileage', 'mileage', 'entry'),
                ('Vehicle Type', 'vehicle_type', 'entry')
            ],
            'mechanic': [
                ('Workshop ID', 'workshop_id', 'entry'),
                ('First Name', 'first_name', 'entry'),
                ('Last Name', 'last_name', 'entry'),
                ('Specialization', 'specialization', 'entry'),
                ('Certification Level', 'certification_level', 'entry'),
                ('Phone', 'phone', 'entry'),
                ('Email', 'email', 'entry'),
                ('Hire Date', 'hire_date', 'date'),
                ('Hourly Rate', 'hourly_rate', 'entry'),
                ('Status', 'status', 'combo', ['Active', 'On Leave', 'Terminated'])
            ],
            'service_record': [
                ('Vehicle ID', 'vehicle_id', 'entry'),
                ('Mechanic ID', 'mechanic_id', 'entry'),
                ('Service Date', 'service_date', 'date'),
                ('Service Type', 'service_type', 'entry'),
                ('Description', 'description', 'text'),
                ('Labor Hours', 'labor_hours', 'entry'),
                ('Status', 'status', 'combo', ['Pending', 'In Progress', 'Completed', 'Cancelled']),
                ('Priority', 'priority', 'combo', ['Low', 'Medium', 'High', 'Urgent'])
            ],
            'part': [
                ('Service ID', 'service_id', 'entry'),
                ('Part Name', 'part_name', 'entry'),
                ('Manufacturer', 'manufacturer', 'entry'),
                ('Part Number', 'part_number', 'entry'),
                ('Quantity', 'quantity', 'entry'),
                ('Unit Price', 'unit_price', 'entry'),
                ('Supplier', 'supplier', 'entry'),
                ('Warranty Period', 'warranty_period', 'entry')
            ],
            'payment': [
                ('Service ID', 'service_id', 'entry'),
                ('Customer ID', 'customer_id', 'entry'),
                ('Amount', 'amount', 'entry'),
                ('Payment Date', 'payment_date', 'date'),
                ('Payment Method', 'payment_method', 'combo', 
                 ['Cash', 'Credit Card', 'Debit Card', 'Check', 'Bank Transfer']),
                ('Payment Status', 'payment_status', 'combo', 
                 ['Paid', 'Pending', 'Partial', 'Refunded']),
                ('Transaction ID', 'transaction_id', 'entry'),
                ('Due Date', 'due_date', 'date'),
                ('Discount', 'discount', 'entry'),
                ('Tax', 'tax', 'entry')
            ]
        }
        
        # Canvas with scrollbar for forms with many fields
        canvas = tk.Canvas(dialog, bg='white')
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create form fields
        entries = {}
        for i, field in enumerate(fields[entity_name]):
            label_text, field_name, field_type = field[0], field[1], field[2]
            
            tk.Label(scrollable_frame, text=label_text + ":", 
                    font=('Helvetica', 10, 'bold'), bg='white').grid(
                row=i, column=0, sticky='e', padx=10, pady=5)
            
            if field_type == 'entry':
                entry = tk.Entry(scrollable_frame, font=('Helvetica', 10), width=30)
                entry.grid(row=i, column=1, padx=10, pady=5)
                if values and mode == 'update':
                    entry.insert(0, values[i])
                entries[field_name] = entry
            
            elif field_type == 'combo':
                combo = ttk.Combobox(scrollable_frame, values=field[3], 
                                    font=('Helvetica', 10), width=28)
                combo.grid(row=i, column=1, padx=10, pady=5)
                if values and mode == 'update':
                    combo.set(values[i])
                entries[field_name] = combo
            
            elif field_type == 'date':
                date_entry = tkcalendar.DateEntry(scrollable_frame, 
                                                font=('Helvetica', 10), width=28)
                date_entry.grid(row=i, column=1, padx=10, pady=5)
                if values and mode == 'update':
                    date_entry.set_date(datetime.strptime(str(values[i]), '%Y-%m-%d'))
                entries[field_name] = date_entry
            
            elif field_type == 'text':
                text = tk.Text(scrollable_frame, font=('Helvetica', 10), 
                             width=30, height=4)
                text.grid(row=i, column=1, padx=10, pady=5)
                if values and mode == 'update':
                    text.insert('1.0', values[i])
                entries[field_name] = text
        
        # Submit button
        submit_btn = tk.Button(scrollable_frame, 
                              text="Save Record",
                              bg='#27ae60',
                              fg='white',
                              font=('Helvetica', 11, 'bold'),
                              padx=20, pady=10,
                              command=lambda: self.submit_record(
                                  entity_name, entries, mode, values, dialog, tree))
        submit_btn.grid(row=len(fields[entity_name]), column=0, columnspan=2, pady=20)
    
    def submit_record(self, entity_name, entries, mode, values, dialog, tree):
        """Submit form data to database"""
        # Get values from form fields
        data = {}
        for field_name, widget in entries.items():
            if isinstance(widget, tk.Text):
                data[field_name] = widget.get('1.0', 'end-1c')
            elif isinstance(widget, tkcalendar.DateEntry):
                data[field_name] = widget.get_date().strftime('%Y-%m-%d')
            else:
                data[field_name] = widget.get()
        
        try:
            if mode == 'add':
                # Build INSERT query
                columns = ', '.join(data.keys())
                placeholders = ', '.join(['%s'] * len(data))
                query = f"INSERT INTO {entity_name} ({columns}) VALUES ({placeholders})"
                self.cursor.execute(query, tuple(data.values()))
                
            elif mode == 'update':
                # Build UPDATE query
                id_columns = {
                    'customer': 'customer_id',
                    'workshop': 'workshop_id',
                    'vehicle': 'vehicle_id',
                    'mechanic': 'mechanic_id',
                    'service_record': 'service_id',
                    'part': 'part_id',
                    'payment': 'payment_id'
                }
                
                set_clause = ', '.join([f"{key} = %s" for key in data.keys()])
                query = f"UPDATE {entity_name} SET {set_clause} WHERE {id_columns[entity_name]} = %s"
                params = tuple(data.values()) + (values[0],)
                self.cursor.execute(query, params)
            
            self.db_connection.commit()
            self.refresh_tree(tree, entity_name)
            dialog.destroy()
            messagebox.showinfo("Success", f"Record {mode}ed successfully")
            
        except Error as e:
            messagebox.showerror("Error", f"Failed to {mode} record: {e}")
    
    # ==================== ENTITY PAGES ====================
    
    def show_customers(self):
        columns = ['ID', 'First Name', 'Last Name', 'Phone', 'Email', 'Address', 
                  'City', 'State', 'ZIP Code', 'Registration Date']
        self.create_entity_page("Customer Management", "customer", columns,
                              "SELECT * FROM customer",
                              "", "", "")
    
    def show_workshops(self):
        columns = ['ID', 'Workshop Name', 'Location', 'Contact Number', 
                  'Manager Name', 'Capacity', 'Opening Hours', 'Status']
        self.create_entity_page("Workshop Management", "workshop", columns,
                              "SELECT * FROM workshop",
                              "", "", "")
    
    def show_vehicles(self):
        columns = ['ID', 'Customer ID', 'Workshop ID', 'Make', 'Model', 
                  'Year', 'License Plate', 'VIN', 'Color', 'Mileage', 
                  'Vehicle Type', 'Registration Date']
        self.create_entity_page("Vehicle Management", "vehicle", columns,
                              "SELECT * FROM vehicle",
                              "", "", "")
    
    def show_mechanics(self):
        columns = ['ID', 'Workshop ID', 'First Name', 'Last Name', 
                  'Specialization', 'Certification', 'Phone', 'Email', 
                  'Hire Date', 'Hourly Rate', 'Status']
        self.create_entity_page("Mechanic Management", "mechanic", columns,
                              "SELECT * FROM mechanic",
                              "", "", "")
    
    def show_service_records(self):
        columns = ['ID', 'Vehicle ID', 'Mechanic ID', 'Service Date', 
                  'Service Type', 'Description', 'Labor Hours', 
                  'Status', 'Priority', 'Notes', 'Completion Date']
        self.create_entity_page("Service Record Management", "service_record", columns,
                              "SELECT * FROM service_record",
                              "", "", "")
    
    def show_parts(self):
        columns = ['ID', 'Service ID', 'Part Name', 'Manufacturer', 
                  'Part Number', 'Quantity', 'Unit Price', 'Supplier', 
                  'Warranty Period', 'Installation Date']
        self.create_entity_page("Part Management", "part", columns,
                              "SELECT * FROM part",
                              "", "", "")
    
    def show_payments(self):
        columns = ['ID', 'Service ID', 'Customer ID', 'Amount', 
                  'Payment Date', 'Payment Method', 'Payment Status', 
                  'Transaction ID', 'Due Date', 'Discount', 'Tax', 'Total Amount']
        self.create_entity_page("Payment Management", "payment", columns,
                              "SELECT * FROM payment",
                              "", "", "")
    
    # ==================== REPORTS ====================
    
    def show_reports(self):
        """Show reports page"""
        self.clear_content()
        self.status_label.config(text="Reports Dashboard")
        
        # Title
        title_frame = tk.Frame(self.content_frame, bg='#34495e')
        title_frame.pack(fill=tk.X)
        tk.Label(title_frame, text="📊 Reports Dashboard", font=('Helvetica', 16, 'bold'),
                bg='#34495e', fg='white', padx=20, pady=10).pack()
        
        # Reports grid
        reports_frame = tk.Frame(self.content_frame, bg='white')
        reports_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        reports = [
            ("Customer Service History", "📋", self.report_customer_service_history),
            ("Mechanic Performance", "👨‍🔧", self.report_mechanic_performance),
            ("Revenue by Service", "💰", self.report_revenue_by_service),
            ("Parts Inventory Usage", "⚙️", self.report_parts_usage),
            ("Payment Status Summary", "💳", self.report_payment_status),
            ("Workshop Capacity", "🏭", self.report_workshop_capacity),
            ("Vehicle Service Schedule", "🚗", self.report_vehicle_schedule),
            ("Monthly Revenue Report", "📈", self.report_monthly_revenue)
        ]
        
        row = 0
        col = 0
        for title, icon, command in reports:
            report_frame = tk.Frame(reports_frame, bg='white', relief=tk.RAISED, bd=2)
            report_frame.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
            
            tk.Label(report_frame, text=icon, font=('Helvetica', 36), bg='white').pack(pady=10)
            tk.Label(report_frame, text=title, font=('Helvetica', 10, 'bold'),
                    bg='white', wraplength=150).pack(pady=5)
            
            tk.Button(report_frame, text="Generate Report", 
                     bg='#3498db', fg='white',
                     font=('Helvetica', 9, 'bold'),
                     command=command).pack(pady=10)
            
            col += 1
            if col > 3:
                col = 0
                row += 1
        
        # Configure grid weights
        for i in range(4):
            reports_frame.grid_columnconfigure(i, weight=1)
    
    def create_report_window(self, title, query, columns):
        """Create a report display window"""
        report_window = tk.Toplevel(self.root)
        report_window.title(title)
        report_window.geometry("1000x600")
        report_window.configure(bg='white')
        
        # Header
        tk.Label(report_window, text=title, font=('Helvetica', 16, 'bold'),
                bg='white', fg='#2c3e50').pack(pady=10)
        
        # Date
        tk.Label(report_window, 
                text=f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                font=('Helvetica', 10), bg='white', fg='#7f8c8d').pack()
        
        # Results frame
        results_frame = tk.Frame(report_window, bg='white')
        results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Treeview
        scrollbar_y = ttk.Scrollbar(results_frame)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        scrollbar_x = ttk.Scrollbar(results_frame, orient=tk.HORIZONTAL)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        tree = ttk.Treeview(results_frame, columns=columns, show='headings',
                           yscrollcommand=scrollbar_y.set,
                           xscrollcommand=scrollbar_x.set)
        
        scrollbar_y.config(command=tree.yview)
        scrollbar_x.config(command=tree.xview)
        
        for col in columns:
            tree.heading(col, text=col.replace('_', ' ').title())
            tree.column(col, width=120)
        
        tree.pack(fill=tk.BOTH, expand=True)
        
        # Execute query and populate
        try:
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            
            for row in results:
                tree.insert('', 'end', values=row)
            
            # Summary
            summary_frame = tk.Frame(report_window, bg='#ecf0f1')
            summary_frame.pack(fill=tk.X, padx=20, pady=10)
            
            tk.Label(summary_frame, 
                    text=f"Total Records: {len(results)}",
                    font=('Helvetica', 10, 'bold'),
                    bg='#ecf0f1').pack(pady=10)
            
            # Export button
            tk.Button(report_window, text="📥 Export to CSV",
                     bg='#27ae60', fg='white',
                     font=('Helvetica', 10, 'bold'),
                     command=lambda: self.export_to_csv(title, columns, results)).pack(pady=10)
            
        except Error as e:
            messagebox.showerror("Error", f"Failed to generate report: {e}")
    
    def export_to_csv(self, title, columns, data):
        """Export report data to CSV"""
        from tkinter import filedialog
        import csv
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"{title.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(columns)
                    writer.writerows(data)
                messagebox.showinfo("Success", f"Report exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {e}")
    
    # ==================== REPORT FUNCTIONS ====================
    
    def report_customer_service_history(self):
        query = """
        SELECT 
            c.first_name, c.last_name, v.make, v.model, 
            v.license_plate, sr.service_type, sr.service_date, 
            sr.status, p.amount as payment_amount
        FROM customer c
        JOIN vehicle v ON c.customer_id = v.customer_id
        JOIN service_record sr ON v.vehicle_id = sr.vehicle_id
        LEFT JOIN payment p ON sr.service_id = p.service_id
        ORDER BY sr.service_date DESC
        """
        columns = ['First Name', 'Last Name', 'Make', 'Model', 
                  'License Plate', 'Service Type', 'Service Date', 
                  'Status', 'Payment Amount']
        self.create_report_window("Customer Service History Report", query, columns)
    
    def report_mechanic_performance(self):
        query = """
        SELECT 
            m.first_name, m.last_name, m.specialization,
            COUNT(sr.service_id) as total_services,
            SUM(sr.labor_hours) as total_hours,
            AVG(p.amount) as avg_service_value
        FROM mechanic m
        LEFT JOIN service_record sr ON m.mechanic_id = sr.mechanic_id
        LEFT JOIN payment p ON sr.service_id = p.service_id
        WHERE sr.status = 'Completed'
        GROUP BY m.mechanic_id
        ORDER BY total_services DESC
        """
        columns = ['First Name', 'Last Name', 'Specialization', 
                  'Total Services', 'Total Hours', 'Avg Service Value']
        self.create_report_window("Mechanic Performance Report", query, columns)
    
    def report_revenue_by_service(self):
        query = """
        SELECT 
            sr.service_type,
            COUNT(*) as service_count,
            SUM(p.amount) as total_revenue,
            AVG(p.amount) as avg_revenue,
            MIN(p.amount) as min_revenue,
            MAX(p.amount) as max_revenue
        FROM service_record sr
        JOIN payment p ON sr.service_id = p.service_id
        WHERE p.payment_status = 'Paid'
        GROUP BY sr.service_type
        ORDER BY total_revenue DESC
        """
        columns = ['Service Type', 'Count', 'Total Revenue', 
                  'Avg Revenue', 'Min Revenue', 'Max Revenue']
        self.create_report_window("Revenue by Service Type Report", query, columns)
    
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
        columns = ['Part Name', 'Manufacturer', 'Total Used', 
                  'Total Cost', 'Supplier', 'Times Used']
        self.create_report_window("Parts Inventory Usage Report", query, columns)
    
    def report_payment_status(self):
        query = """
        SELECT 
            payment_status,
            COUNT(*) as count,
            SUM(amount) as total_amount,
            AVG(amount) as avg_amount,
            SUM(discount) as total_discounts,
            SUM(tax) as total_tax
        FROM payment
        GROUP BY payment_status
        ORDER BY total_amount DESC
        """
        columns = ['Payment Status', 'Count', 'Total Amount', 
                  'Avg Amount', 'Total Discounts', 'Total Tax']
        self.create_report_window("Payment Status Summary Report", query, columns)
    
    def report_workshop_capacity(self):
        query = """
        SELECT 
            workshop_name, location, capacity,
            (SELECT COUNT(*) FROM mechanic m WHERE m.workshop_id = w.workshop_id AND m.status = 'Active') as active_mechanics,
            (SELECT COUNT(*) FROM vehicle v WHERE v.workshop_id = w.workshop_id) as assigned_vehicles,
            status
        FROM workshop w
        ORDER BY capacity DESC
        """
        columns = ['Workshop Name', 'Location', 'Capacity', 
                  'Active Mechanics', 'Assigned Vehicles', 'Status']
        self.create_report_window("Workshop Capacity Report", query, columns)
    
    def report_vehicle_schedule(self):
        query = """
        SELECT 
            v.make, v.model, v.license_plate,
            c.first_name, c.last_name,
            sr.service_type, sr.service_date, sr.status,
            m.first_name as mechanic_name
        FROM vehicle v
        JOIN customer c ON v.customer_id = c.customer_id
        JOIN service_record sr ON v.vehicle_id = sr.vehicle_id
        LEFT JOIN mechanic m ON sr.mechanic_id = m.mechanic_id
        WHERE sr.status IN ('Pending', 'In Progress')
        ORDER BY sr.service_date
        """
        columns = ['Make', 'Model', 'License Plate', 'Customer Name', 
                  'Customer Last Name', 'Service Type', 'Service Date', 
                  'Status', 'Mechanic']
        self.create_report_window("Vehicle Service Schedule Report", query, columns)
    
    def report_monthly_revenue(self):
        query = """
        SELECT 
            DATE_FORMAT(payment_date, '%Y-%m') as month,
            COUNT(*) as transactions,
            SUM(amount) as total_revenue,
            SUM(discount) as total_discounts,
            SUM(tax) as total_tax,
            SUM(amount) + SUM(tax) - SUM(discount) as net_revenue
        FROM payment
        WHERE payment_status = 'Paid'
        GROUP BY DATE_FORMAT(payment_date, '%Y-%m')
        ORDER BY month DESC
        LIMIT 12
        """
        columns = ['Month', 'Transactions', 'Total Revenue', 
                  'Discounts', 'Tax', 'Net Revenue']
        self.create_report_window("Monthly Revenue Report", query, columns)
    
    def __del__(self):
        """Clean up database connections"""
        if self.cursor:
            self.cursor.close()
        if self.db_connection:
            self.db_connection.close()

def main():
    root = tk.Tk()
    app = AutoRepairManagementSystem(root)
    root.mainloop()

if __name__ == "__main__":
    main()