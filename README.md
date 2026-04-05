# Campus IT Service Desk

A Flask-based web application for managing IT assets and service tickets on a campus.

---

## Project Overview

This application helps IT departments track and manage:

* **Assets**: Computers, printers, routers, projectors, and other IT equipment
* **Tickets**: Service requests and issues reported by users
* **Locations**: Buildings and rooms where assets are located
* **Users**: Different roles (Student, Staff, Technician, Admin)

---

## Features

* Full CRUD operations for Assets (Create, Read, Update, Delete)
* Relational database with multiple linked tables
* Dynamic web pages using Flask and Jinja2
* SQL JOIN queries to combine related data
* Form handling for user input
* Clean modular structure for scalability

---

## Project Structure

```
campus-it-service-desk/
├── app.py                    # Main Flask application and routes
├── requirements.txt          # Python package dependencies
├── schema.sql               # Database table definitions
├── seed.sql                 # Sample data for testing
├── README.md                # This file
├── templates/               # HTML templates (web pages)
│   ├── base.html           # Base template (navigation, layout)
│   ├── assets.html         # Display all assets
│   ├── add_asset.html      # Form to add new asset
│   ├── edit_asset.html     # Form to edit existing asset
│   └── tickets.html        # Display all tickets (to be implemented)
└── static/                  # Static files (CSS, images, JavaScript)
    └── style.css           # Stylesheet
```

---

## How the Application Works

### 1. app.py - The Main Application

This file contains:

* **Flask Setup**: Initializes the web application
* **Database Connection**: `get_db_connection()` function manages database access
* **Routes (URL endpoints)**:

  * `/` - Home page
  * `/assets` - View all assets
  * `/add_asset` - Create new asset (GET shows form, POST saves data)
  * `/edit_asset/<id>` - Edit existing asset
  * `/delete_asset/<id>` - Delete an asset

---

### 2. Database (PostgreSQL)

The application uses PostgreSQL (adapted from the original MySQL design in the proposal).

Tables:

* **Roles**: User role definitions
* **Users**: User accounts
* **Assets**: IT equipment inventory
* **Locations**: Buildings and rooms
* **Ticket_Status**: Status types (Open, In Progress, Closed)
* **Tickets**: Service requests

---

## Database Relationships and JOIN Usage

This application uses SQL JOIN operations to combine data across multiple tables.

Example:

* The `/assets` page performs a JOIN between:

  * `Assets`
  * `Locations`

This allows each asset to display its building and room.

Future ticket functionality will use JOINs across:

* `Users` (created_by and assigned_to)
* `Ticket_Status`
* `Assets`

This demonstrates proper relational database design.

---

## Templates (HTML Files)

These are the web pages users interact with:

* **base.html**: Shared layout and navigation
* **assets.html**: Displays all assets
* **add_asset.html**: Form to create assets
* **edit_asset.html**: Form to update assets

---

## Setup Instructions

### 1. Install Dependencies

```
pip install -r requirements.txt
```

---

### 2. Setup Database

Run the following SQL scripts in your PostgreSQL database:

```
schema.sql
seed.sql
```

---

### 3. Create .env File

Create a `.env` file in the root directory:

```
DATABASE_URL=postgresql://username:password@host/database_name?sslmode=require
```

---

### 4. Run the Application

```
python app.py
```

Then open:

```
http://127.0.0.1:5000/
```

---

## How Routes Work

### Viewing Assets (GET)

1. User visits `/assets`
2. Flask executes SQL query with JOIN
3. Data is passed to template
4. Assets are displayed in a table

---

### Adding Asset (POST)

1. User fills form
2. Data sent via POST
3. Flask inserts into database
4. Redirects back to `/assets`

---

### Editing Asset (POST)

1. User loads existing data
2. Updates fields
3. Flask runs UPDATE query
4. Redirects to `/assets`

---

### Deleting Asset (POST)

1. User clicks delete
2. Confirmation appears
3. Flask deletes record
4. Page refreshes

---

## Key Concepts

### Flask Routes

```
@app.route("/path", methods=["GET", "POST"])
```

Maps URL paths to Python functions.

---

### Database Pattern

```
conn = get_db_connection()
cur = conn.cursor()
cur.execute(query)
conn.commit()
cur.close()
conn.close()
```

---

### Jinja2 Templates

```
{% for item in items %}
    {{ item }}
{% endfor %}
```

Used to dynamically render HTML.

---

## Troubleshooting

* **Port in use** → change port in `app.py`
* **DB connection error** → check `.env` file
* **404 error** → verify route names
* **Form not working** → check field names

---

## Screenshots

### Homepage
![Homepage](screenshots/homepage.png)

### Assets Page
![Assets](screenshots/assets_view.png)

### Add Asset Form
![Add Asset](screenshots/add_asset_form.png)

### Edit Asset Form
![Edit Asset](screenshots/edit_asset_form.png)

### Asset Created
![Asset Created](screenshots/asset_created.png)

### Database (Assets Table)
![Database](screenshots/database_assets.png)

### Tickets Page
![Assets](screenshots/tickets_view.png)

### Add Ticket Form
![Add Asset](screenshots/add_ticket_form.png)

### Edit Asset Form
![Edit Asset](screenshots/edit_ticket_form.png)

