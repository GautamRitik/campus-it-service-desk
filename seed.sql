/*
 * Seed Data for Campus IT Service Desk Database
 * This script populates the database with sample data for testing and development
 */

-- Roles
INSERT INTO Roles (role_name) VALUES
('Student'),
('Staff'),
('Technician'),
('Admin');

-- Users
INSERT INTO Users (first_name, last_name, email, password_hash, role_id) VALUES
('Ritik', 'Gautam', 'ritik@email.com', 'hash', 1),
('Tech', 'Guy', 'tech@email.com', 'hash', 3),
('Brahith', 'Pavanantharajah', 'brahith@email.com', 'hash', 1),
('Hashir', 'Khan', 'hashir@email.com', 'hash', 1),
('Afeef', 'Hossain', 'afeef@email.com', 'hash', 1),
('Richard', 'Pazzi', 'rpazzi@email.com', 'hash', 2),
('John', 'Smith', 'john.smith@email.com', 'hash', 3),
('Sarah', 'Lee', 'sarah.lee@email.com', 'hash', 2),
('Michael', 'Brown', 'michael.brown@email.com', 'hash', 4),
('Emily', 'Davis', 'emily.davis@email.com', 'hash', 1);

-- Status
INSERT INTO Ticket_Status (status_name) VALUES
('Open'),
('In Progress'),
('Closed');

-- Locations
INSERT INTO Locations (building_name, room_number) VALUES
('SIRC', '101'),
('UB', '202'),
('ERC', '201'),
('Library', '120'),
('UA', '305'),
('ER', '110');

-- Assets
INSERT INTO Assets (asset_name, asset_type, serial_number, location_id) VALUES
('Router 1', 'Router', 'SN123', 1),
('Switch A', 'Switch', 'SN456', 2),
('Cisco Router B', 'Router', 'SN789', 3),
('Access Point 3A', 'Access Point', 'AP333', 4),
('Lab PC 12', 'Computer', 'PC1200', 5),
('Projector UB-2', 'Projector', 'PJ2201', 2);

-- Tickets
INSERT INTO Tickets (title, description, created_by, assigned_to, status_id, asset_id) VALUES
('Projector cleaning', 'Dust filter cleaning and software update', 1, 2, 1, 6),
('Wi-Fi outage in library', 'Students reported intermittent wireless connection issues', 3, 6, 2, 4),
('Lab computer not starting', 'PC in lab does not boot properly', 4, 2, 1, 5),
('Router inspection', 'Routine maintenance check for campus router', 5, 6, 3, 3);