/*
 * Seed Data for Campus IT Service Desk Database
 * This script populates the database with sample data for testing and development
 */

-- Insert sample user roles
INSERT INTO Roles (role_name) VALUES
('Student'),
('Staff'),
('Technician'),
('Admin');

-- Insert sample users
INSERT INTO Users (first_name, last_name, email, password_hash, role_id) VALUES
('Ritik', 'Gautam', 'ritik@email.com', 'hash', 1),
('Tech', 'Guy', 'tech@email.com', 'hash', 3);

-- Insert sample ticket statuses
INSERT INTO Ticket_Status (status_name) VALUES
('Open'),
('In Progress'),
('Closed');

-- Insert sample locations (buildings and rooms)
INSERT INTO Locations (building_name, room_number) VALUES
('SIRC', '101'),
('UB', '202');

-- Insert sample IT assets
INSERT INTO Assets (asset_name, asset_type, serial_number, location_id) VALUES
('Router 1', 'Router', 'SN123', 1),
('Switch A', 'Switch', 'SN456', 2);