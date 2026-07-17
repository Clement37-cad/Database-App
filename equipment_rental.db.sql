-- equipment_rental_db.sql
CREATE DATABASE IF NOT EXISTS equipment_rental;
USE equipment_rental;

-- Customer table
CREATE TABLE customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    registration_date DATE DEFAULT (CURRENT_DATE)
);

-- Staff table
CREATE TABLE staff (
    staff_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    position VARCHAR(50),
    hire_date DATE,
    salary DECIMAL(10,2)
);

-- Equipment table
CREATE TABLE equipment (
    equipment_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    description TEXT,
    daily_rate DECIMAL(10,2) NOT NULL,
    status ENUM('Available', 'Rented', 'Maintenance', 'Retired') DEFAULT 'Available',
    purchase_date DATE,
    last_maintenance_date DATE
);

-- Rentals table
CREATE TABLE rentals (
    rental_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    equipment_id INT NOT NULL,
    staff_id INT NOT NULL,
    rental_date DATE DEFAULT (CURRENT_DATE),
    return_date DATE,
    total_amount DECIMAL(10,2),
    status ENUM('Active', 'Completed', 'Overdue', 'Cancelled') DEFAULT 'Active',
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (equipment_id) REFERENCES equipment(equipment_id),
    FOREIGN KEY (staff_id) REFERENCES staff(staff_id)
);

-- Payments table
CREATE TABLE payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    rental_id INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    payment_date DATE DEFAULT (CURRENT_DATE),
    payment_method ENUM('Cash', 'Credit Card', 'Debit Card', 'Bank Transfer', 'Check') NOT NULL,
    status ENUM('Pending', 'Completed', 'Failed', 'Refunded') DEFAULT 'Completed',
    FOREIGN KEY (rental_id) REFERENCES rentals(rental_id)
);

-- Maintenance table
CREATE TABLE maintenance (
    maintenance_id INT AUTO_INCREMENT PRIMARY KEY,
    equipment_id INT NOT NULL,
    staff_id INT NOT NULL,
    maintenance_date DATE DEFAULT (CURRENT_DATE),
    description TEXT,
    cost DECIMAL(10,2),
    next_maintenance_date DATE,
    status ENUM('Scheduled', 'In Progress', 'Completed', 'Cancelled') DEFAULT 'Scheduled',
    FOREIGN KEY (equipment_id) REFERENCES equipment(equipment_id),
    FOREIGN KEY (staff_id) REFERENCES staff(staff_id)
);

-- Insert sample data
INSERT INTO customers (first_name, last_name, email, phone, address) VALUES
('John', 'Doe', 'john.doe@email.com', '555-0101', '123 Main St, City'),
('Jane', 'Smith', 'jane.smith@email.com', '555-0102', '456 Oak Ave, Town'),
('Bob', 'Johnson', 'bob.johnson@email.com', '555-0103', '789 Pine Rd, Village');

INSERT INTO staff (first_name, last_name, email, phone, position, hire_date, salary) VALUES
('Mike', 'Wilson', 'mike.wilson@email.com', '555-0201', 'Manager', '2020-01-15', 55000.00),
('Sarah', 'Brown', 'sarah.brown@email.com', '555-0202', 'Technician', '2021-03-20', 42000.00);

INSERT INTO equipment (name, category, description, daily_rate, status, purchase_date) VALUES
('Excavator EX200', 'Heavy Machinery', '20-ton hydraulic excavator', 350.00, 'Available', '2022-06-01'),
('Concrete Mixer CM150', 'Construction', '150L portable concrete mixer', 75.00, 'Available', '2022-08-15'),
('Generator G5000', 'Power Equipment', '5000W portable generator', 45.00, 'Rented', '2023-01-10'),
('Scaffolding Set', 'Construction', 'Standard scaffolding set 10m height', 30.00, 'Available', '2023-03-20');