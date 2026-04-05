"""
Campus IT Service Desk Application
This Flask app manages IT assets and service tickets for campus facilities.
Users can view, add, edit, and delete assets, as well as create and manage tickets.
"""

from flask import Flask, render_template, request, redirect, url_for
import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env file (contains database credentials)
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Get database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    """
    Establishes and returns a connection to the PostgreSQL database.
    Uses DATABASE_URL from environment variables.
    Returns: psycopg2 connection object
    """
    return psycopg2.connect(DATABASE_URL)


# ==================== HOME ROUTE ====================

@app.route("/")
def home():
    """
    Home page route - displays the landing page.
    GET: Returns the index.html template
    """
    return render_template("index.html")


# ==================== ASSETS ROUTES ====================

@app.route("/assets")
def assets():
    """
    Displays all IT assets in the system.
    GET: Retrieves all assets from database and returns assets.html
    - Joins Assets table with Locations table to show building/room info
    - Orders assets by asset_id
    """
    conn = get_db_connection()
    cur = conn.cursor()

    # SQL query to fetch all assets with their location details
    cur.execute("""
        SELECT a.asset_id, a.asset_name, a.asset_type, a.serial_number,
               l.building_name, l.room_number
        FROM Assets a
        JOIN Locations l ON a.location_id = l.location_id
        ORDER BY a.asset_id;
    """)

    assets = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("assets.html", assets=assets)

@app.route("/add_asset", methods=["GET", "POST"])
def add_asset():
    """
    Add a new IT asset to the system.
    GET: Returns the add_asset.html form with available locations
    POST: Inserts new asset into database and redirects to assets list
    - Collects: asset_name, asset_type, serial_number, location_id from form
    """
    conn = get_db_connection()
    cur = conn.cursor()

    # Handle form submission
    if request.method == "POST":
        # Get form data
        asset_name = request.form["asset_name"]
        asset_type = request.form["asset_type"]
        serial_number = request.form["serial_number"]
        location_id = request.form["location_id"]

        # Insert new asset into database
        cur.execute("""
            INSERT INTO Assets (asset_name, asset_type, serial_number, location_id)
            VALUES (%s, %s, %s, %s)
        """, (asset_name, asset_type, serial_number, location_id))

        # Save changes and close connection
        conn.commit()
        cur.close()
        conn.close()

        # Redirect back to assets list after successful save
        return redirect(url_for("assets"))

    # GET request - fetch available locations for dropdown menu
    cur.execute("SELECT location_id, building_name, room_number FROM Locations ORDER BY location_id;")
    locations = cur.fetchall()

    cur.close()
    conn.close()

    # Return form with locations
    return render_template("add_asset.html", locations=locations)

@app.route("/edit_asset/<int:asset_id>", methods=["GET", "POST"])
def edit_asset(asset_id):
    """
    Edit an existing IT asset.
    GET: Returns edit_asset.html form pre-filled with asset details
    POST: Updates asset in database and redirects to assets list
    - URL parameter: asset_id (integer) - the asset to edit
    """
    conn = get_db_connection()
    cur = conn.cursor()

    # Handle form submission
    if request.method == "POST":
        # Get updated form data
        asset_name = request.form["asset_name"]
        asset_type = request.form["asset_type"]
        serial_number = request.form["serial_number"]
        location_id = request.form["location_id"]

        # Update asset in database
        cur.execute("""
            UPDATE Assets
            SET asset_name = %s,
                asset_type = %s,
                serial_number = %s,
                location_id = %s
            WHERE asset_id = %s
        """, (asset_name, asset_type, serial_number, location_id, asset_id))

        # Save changes and close connection
        conn.commit()
        cur.close()
        conn.close()

        # Redirect back to assets list after successful update
        return redirect(url_for("assets"))

    # GET request - fetch specific asset by ID
    cur.execute("""
        SELECT asset_id, asset_name, asset_type, serial_number, location_id
        FROM Assets
        WHERE asset_id = %s
    """, (asset_id,))
    asset = cur.fetchone()

    # Fetch all locations for dropdown menu
    cur.execute("""
        SELECT location_id, building_name, room_number
        FROM Locations
        ORDER BY location_id
    """)
    locations = cur.fetchall()

    cur.close()
    conn.close()

    # Return form with asset details and available locations
    return render_template("edit_asset.html", asset=asset, locations=locations)

@app.route("/delete_asset/<int:asset_id>", methods=["POST"])
def delete_asset(asset_id):
    """
    Delete an IT asset from the system.
    POST: Removes asset from database and redirects to assets list
    - URL parameter: asset_id (integer) - the asset to delete
    """
    conn = get_db_connection()
    cur = conn.cursor()

    # Delete the asset by its ID
    cur.execute("DELETE FROM Assets WHERE asset_id = %s", (asset_id,))
    
    # Save changes and close connection
    conn.commit()
    cur.close()
    conn.close()

    # Redirect back to assets list
    return redirect(url_for("assets"))

@app.route("/tickets")
def tickets():
    """
    Displays all service tickets with their details.
    GET: Retrieves all tickets from database and returns tickets.html
    - Joins Tickets table with Users, Ticket_Status, Assets, and Locations tables
    - Shows who created/is assigned to each ticket, asset info, and location
    - Uses LEFT JOIN for optional asset/location (ticket may not have asset assigned)
    """
    conn = get_db_connection()
    cur = conn.cursor()

    # Complex query that pulls together all ticket info from multiple related tables
    cur.execute("""
        SELECT 
            t.ticket_id,
            t.title,
            t.description,
            t.created_at,
            u1.first_name || ' ' || u1.last_name AS created_by,  -- Combines first and last name of user who created ticket
            u2.first_name || ' ' || u2.last_name AS assigned_to,  -- Combines first and last name of assigned user
            ts.status_name,
            a.asset_name,
            a.asset_type,
            a.serial_number,
            l.building_name,
            l.room_number
        FROM Tickets t
        JOIN Users u1 ON t.created_by = u1.user_id  -- Get creator's full name
        LEFT JOIN Users u2 ON t.assigned_to = u2.user_id  -- Get assignee's full name (optional if unassigned)
        JOIN Ticket_Status ts ON t.status_id = ts.status_id  -- Get the status name
        LEFT JOIN Assets a ON t.asset_id = a.asset_id  -- Get asset details if ticket relates to an asset
        LEFT JOIN Locations l ON a.location_id = l.location_id  -- Get location details of the asset
        ORDER BY t.ticket_id;
    """)

    tickets = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("tickets.html", tickets=tickets)

@app.route("/add_ticket", methods=["GET", "POST"])
def add_ticket():
    """
    Create a new service ticket in the system.
    GET: Returns the add_ticket.html form with available users, statuses, and assets
    POST: Inserts new ticket into database and redirects to tickets list
    - Collects: title, description, created_by, assigned_to, status_id, asset_id from form
    """
    conn = get_db_connection()
    cur = conn.cursor()

    # Handle form submission - POST request
    if request.method == "POST":
        # Extract all form fields
        title = request.form["title"]
        description = request.form["description"]
        created_by = request.form["created_by"]
        assigned_to = request.form["assigned_to"]
        status_id = request.form["status_id"]
        asset_id = request.form["asset_id"]

        # Insert new ticket into database with all the collected data
        cur.execute("""
            INSERT INTO Tickets (title, description, created_by, assigned_to, status_id, asset_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (title, description, created_by, assigned_to, status_id, asset_id))

        # Save changes and close connection
        conn.commit()
        cur.close()
        conn.close()

        # Redirect back to tickets list after successful creation
        return redirect(url_for("tickets"))

    # GET request - fetch all data needed for the form dropdowns
    # Retrieve all users so they can be selected as creator/assignee
    cur.execute("SELECT user_id, first_name, last_name FROM Users ORDER BY user_id;")
    users = cur.fetchall()

    # Retrieve all ticket statuses (Open, In Progress, Closed, etc.)
    cur.execute("SELECT status_id, status_name FROM Ticket_Status ORDER BY status_id;")
    statuses = cur.fetchall()

    # Retrieve all assets so they can be linked to the ticket
    cur.execute("SELECT asset_id, asset_name FROM Assets ORDER BY asset_id;")
    assets = cur.fetchall()

    cur.close()
    conn.close()

    # Return form with all dropdown options
    return render_template("add_ticket.html", users=users, statuses=statuses, assets=assets)

@app.route("/edit_ticket/<int:ticket_id>", methods=["GET", "POST"])
def edit_ticket(ticket_id):
    """
    Edit an existing service ticket.
    GET: Returns edit_ticket.html form pre-filled with ticket details
    POST: Updates ticket in database and redirects to tickets list
    - URL parameter: ticket_id (integer) - the ticket to edit
    """
    conn = get_db_connection()
    cur = conn.cursor()

    # Handle form submission - POST request
    if request.method == "POST":
        # Extract updated form fields
        title = request.form["title"]
        description = request.form["description"]
        created_by = request.form["created_by"]
        assigned_to = request.form["assigned_to"]
        status_id = request.form["status_id"]
        asset_id = request.form["asset_id"]

        # Update the ticket with all new values
        cur.execute("""
            UPDATE Tickets
            SET title = %s,
                description = %s,
                created_by = %s,
                assigned_to = %s,
                status_id = %s,
                asset_id = %s
            WHERE ticket_id = %s
        """, (title, description, created_by, assigned_to, status_id, asset_id, ticket_id))

        # Save changes and close connection
        conn.commit()
        cur.close()
        conn.close()

        # Redirect back to tickets list after successful update
        return redirect(url_for("tickets"))

    # GET request - fetch the specific ticket by ID to pre-fill the form
    cur.execute("""
        SELECT ticket_id, title, description, created_by, assigned_to, status_id, asset_id
        FROM Tickets
        WHERE ticket_id = %s
    """, (ticket_id,))
    ticket = cur.fetchone()

    # Fetch all users for the dropdown menus
    cur.execute("SELECT user_id, first_name, last_name FROM Users ORDER BY user_id;")
    users = cur.fetchall()

    # Fetch all statuses for the status dropdown
    cur.execute("SELECT status_id, status_name FROM Ticket_Status ORDER BY status_id;")
    statuses = cur.fetchall()

    # Fetch all assets for the asset dropdown
    cur.execute("SELECT asset_id, asset_name FROM Assets ORDER BY asset_id;")
    assets = cur.fetchall()

    cur.close()
    conn.close()

    # Return form with current ticket details and all dropdown options
    return render_template("edit_ticket.html", ticket=ticket, users=users, statuses=statuses, assets=assets)

@app.route("/delete_ticket/<int:ticket_id>", methods=["POST"])
def delete_ticket(ticket_id):
    """
    Delete a service ticket from the system.
    POST: Removes ticket from database and redirects to tickets list
    - URL parameter: ticket_id (integer) - the ticket to delete
    """
    conn = get_db_connection()
    cur = conn.cursor()

    # Delete the ticket by its ID
    cur.execute("DELETE FROM Tickets WHERE ticket_id = %s", (ticket_id,))
    
    # Save changes and close connection
    conn.commit()

    cur.close()
    conn.close()

    # Redirect back to tickets list
    return redirect(url_for("tickets"))

# ==================== RUN APPLICATION ====================

if __name__ == "__main__":
    # Start Flask app in debug mode (auto-reload on code changes)
    app.run(debug=True)