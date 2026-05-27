-- Insert Mock Users
INSERT INTO users (name, email) VALUES 
('Amit Sharma', 'amit.sharma@gmail.com'),
('Priya Patel', 'priya.patel@yahoo.com'),
('Rohan Das', 'rohan.das@outlook.com'),
('Sneha Reddy', 'sneha.reddy@gmail.com'),
('Ananya Mishra', 'ananya.mishra@gmail.com');

-- Insert Mock Drivers with Vehicles and Contact Info
INSERT INTO drivers (name, license_number, vehicle_type,phone_number, is_available) VALUES 
('Rajesh Kumar', 'DL3C-1234', 'Maruti Suzuki Swift (White)-DL-3C-AA-1111', '+919876543210', TRUE),
('Sunita Rao', 'MH12-5678', 'Hyundai i20 (Silver)-MH-12-BB-2222', '+919876543211', TRUE),
('Vikram Singh', 'KA03-9101', 'Toyota Innova (Black)-KA-03-CC-3333', '+919876543212', TRUE),
('Gaurav Joshi', 'HR26-1122', 'Tata Nexon (Blue)-HR-26-DD-4444', '+919876543213', TRUE);