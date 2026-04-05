/*
 * Campus IT Service Desk Database Schema
 * This script creates the database tables for managing IT assets and service tickets
 */

-- Roles Table: Stores different user roles (Admin, Staff, User, etc.)
CREATE TABLE Roles (
    role_id SERIAL PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL
);

-- Users Table: Stores user information and authentication data
CREATE TABLE Users (
    user_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100) UNIQUE,
    password_hash VARCHAR(255),
    role_id INT REFERENCES Roles(role_id)
);

-- Ticket Status Table: Stores ticket statuses (Open, In Progress, Resolved, Closed, etc.)
CREATE TABLE Ticket_Status (
    status_id SERIAL PRIMARY KEY,
    status_name VARCHAR(50)
);

-- Locations Table: Stores building and room information where assets are located
CREATE TABLE Locations (
    location_id SERIAL PRIMARY KEY,
    building_name VARCHAR(100),
    room_number VARCHAR(50)
);

-- Assets Table: Stores IT asset information (computers, printers, projectors, etc.)
CREATE TABLE Assets (
    asset_id SERIAL PRIMARY KEY,
    asset_name VARCHAR(100),
    asset_type VARCHAR(50),
    serial_number VARCHAR(100) UNIQUE,
    location_id INT REFERENCES Locations(location_id)
);

-- Tickets Table: Stores IT service tickets/requests made by users
CREATE TABLE Tickets (
    ticket_id SERIAL PRIMARY KEY,
    title VARCHAR(100),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INT REFERENCES Users(user_id),
    assigned_to INT REFERENCES Users(user_id),
    status_id INT REFERENCES Ticket_Status(status_id),
    asset_id INT REFERENCES Assets(asset_id)
);