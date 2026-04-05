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


def get_assets_with_locations():
    """
    Return all assets with their location information.
    Used for the assets page and for reloading the page after an error.
    """
    conn = get_db_connection()
    cur = conn.cursor()

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

    return assets


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
    GET: Retrieves all assets with location details and returns assets.html
    """
    assets = get_assets_with_locations()
    return render_template("assets.html", assets=assets)


@app.route("/add_asset", methods=["GET", "POST"])
def add_asset():
    """
    Add a new IT asset to the system.
    GET: Returns the add_asset.html form with available locations
    POST: Inserts new asset into database and redirects to assets list
    """
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == "POST":
        asset_name = request.form["asset_name"]
        asset_type = request.form["asset_type"]
        serial_number = request.form["serial_number"].strip()
        location_id = request.form["location_id"]

        try:
            cur.execute("""
                INSERT INTO Assets (asset_name, asset_type, serial_number, location_id)
                VALUES (%s, %s, %s, %s)
            """, (asset_name, asset_type, serial_number, location_id))

            conn.commit()
            cur.close()
            conn.close()

            return redirect(url_for("assets"))

        except psycopg2.Error as e:
            conn.rollback()

            cur.execute("""
                SELECT location_id, building_name, room_number
                FROM Locations
                ORDER BY location_id;
            """)
            locations = cur.fetchall()

            cur.close()
            conn.close()

            if "assets_serial_number_key" in str(e):
                error_message = "That serial number already exists. Please enter a unique serial number."
            else:
                error_message = "An error occurred while adding the asset. Please try again."

            return render_template(
                "add_asset.html",
                locations=locations,
                error_message=error_message,
                entered_asset_name=asset_name,
                entered_asset_type=asset_type,
                entered_serial_number=serial_number,
                entered_location_id=location_id
            )

    cur.execute("""
        SELECT location_id, building_name, room_number
        FROM Locations
        ORDER BY location_id;
    """)
    locations = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("add_asset.html", locations=locations)


@app.route("/edit_asset/<int:asset_id>", methods=["GET", "POST"])
def edit_asset(asset_id):
    """
    Edit an existing IT asset.
    GET: Loads the current asset data into the form
    POST: Updates the asset in the database
    """
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == "POST":
        asset_name = request.form["asset_name"]
        asset_type = request.form["asset_type"]
        serial_number = request.form["serial_number"].strip()
        location_id = request.form["location_id"]

        try:
            cur.execute("""
                UPDATE Assets
                SET asset_name = %s,
                    asset_type = %s,
                    serial_number = %s,
                    location_id = %s
                WHERE asset_id = %s
            """, (asset_name, asset_type, serial_number, location_id, asset_id))

            conn.commit()
            cur.close()
            conn.close()

            return redirect(url_for("assets"))

        except psycopg2.Error as e:
            conn.rollback()

            cur.execute("""
                SELECT location_id, building_name, room_number
                FROM Locations
                ORDER BY location_id;
            """)
            locations = cur.fetchall()

            cur.close()
            conn.close()

            if "assets_serial_number_key" in str(e):
                error_message = "That serial number already exists. Please enter a unique serial number."
            else:
                error_message = "An error occurred while updating the asset. Please try again."

            asset = (asset_id, asset_name, asset_type, serial_number, int(location_id))

            return render_template(
                "edit_asset.html",
                asset=asset,
                locations=locations,
                error_message=error_message
            )

    cur.execute("""
        SELECT asset_id, asset_name, asset_type, serial_number, location_id
        FROM Assets
        WHERE asset_id = %s
    """, (asset_id,))
    asset = cur.fetchone()

    cur.execute("""
        SELECT location_id, building_name, room_number
        FROM Locations
        ORDER BY location_id;
    """)
    locations = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("edit_asset.html", asset=asset, locations=locations)


@app.route("/delete_asset/<int:asset_id>", methods=["POST"])
def delete_asset(asset_id):
    """
    Delete an asset from the system.
    If the asset is linked to one or more tickets, show a friendly error instead of crashing.
    """
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("DELETE FROM Assets WHERE asset_id = %s", (asset_id,))
        conn.commit()

    except psycopg2.Error as e:
        conn.rollback()
        cur.close()
        conn.close()

        if "tickets_asset_id_fkey" in str(e):
            return render_template(
                "assets.html",
                assets=get_assets_with_locations(),
                error_message="This asset cannot be deleted because it is linked to one or more tickets."
            )
        else:
            return render_template(
                "assets.html",
                assets=get_assets_with_locations(),
                error_message="An error occurred while deleting the asset."
            )

    cur.close()
    conn.close()

    return redirect(url_for("assets"))


# ==================== TICKETS ROUTES ====================

@app.route("/tickets")
def tickets():
    """
    Displays all tickets with related user, asset, status, and location information.
    """
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            t.ticket_id,
            t.title,
            t.description,
            t.created_at,
            u1.first_name || ' ' || u1.last_name AS created_by,
            u2.first_name || ' ' || u2.last_name AS assigned_to,
            ts.status_name,
            a.asset_name,
            a.asset_type,
            a.serial_number,
            l.building_name,
            l.room_number
        FROM Tickets t
        JOIN Users u1 ON t.created_by = u1.user_id
        LEFT JOIN Users u2 ON t.assigned_to = u2.user_id
        JOIN Ticket_Status ts ON t.status_id = ts.status_id
        LEFT JOIN Assets a ON t.asset_id = a.asset_id
        LEFT JOIN Locations l ON a.location_id = l.location_id
        ORDER BY t.ticket_id;
    """)

    tickets = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("tickets.html", tickets=tickets)


@app.route("/add_ticket", methods=["GET", "POST"])
def add_ticket():
    """
    Add a new service ticket to the system.
    GET: Loads dropdown data for users, statuses, and assets
    POST: Inserts a new ticket into the database
    """
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        created_by = request.form["created_by"]
        assigned_to = request.form["assigned_to"]
        status_id = request.form["status_id"]
        asset_id = request.form["asset_id"]

        cur.execute("""
            INSERT INTO Tickets (title, description, created_by, assigned_to, status_id, asset_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (title, description, created_by, assigned_to, status_id, asset_id))

        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for("tickets"))

    cur.execute("SELECT user_id, first_name, last_name FROM Users ORDER BY user_id;")
    users = cur.fetchall()

    cur.execute("SELECT status_id, status_name FROM Ticket_Status ORDER BY status_id;")
    statuses = cur.fetchall()

    cur.execute("SELECT asset_id, asset_name FROM Assets ORDER BY asset_id;")
    assets = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("add_ticket.html", users=users, statuses=statuses, assets=assets)


@app.route("/edit_ticket/<int:ticket_id>", methods=["GET", "POST"])
def edit_ticket(ticket_id):
    """
    Edit an existing service ticket.
    GET: Loads current ticket data and dropdown values
    POST: Updates the ticket in the database
    """
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        created_by = request.form["created_by"]
        assigned_to = request.form["assigned_to"]
        status_id = request.form["status_id"]
        asset_id = request.form["asset_id"]

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

        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for("tickets"))

    cur.execute("""
        SELECT ticket_id, title, description, created_by, assigned_to, status_id, asset_id
        FROM Tickets
        WHERE ticket_id = %s
    """, (ticket_id,))
    ticket = cur.fetchone()

    cur.execute("SELECT user_id, first_name, last_name FROM Users ORDER BY user_id;")
    users = cur.fetchall()

    cur.execute("SELECT status_id, status_name FROM Ticket_Status ORDER BY status_id;")
    statuses = cur.fetchall()

    cur.execute("SELECT asset_id, asset_name FROM Assets ORDER BY asset_id;")
    assets = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("edit_ticket.html", ticket=ticket, users=users, statuses=statuses, assets=assets)


@app.route("/delete_ticket/<int:ticket_id>", methods=["POST"])
def delete_ticket(ticket_id):
    """
    Delete a service ticket from the system.
    POST: Removes ticket from database and redirects to tickets list
    """
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM Tickets WHERE ticket_id = %s", (ticket_id,))
    conn.commit()

    cur.close()
    conn.close()

    return redirect(url_for("tickets"))


# ==================== RUN APPLICATION ====================

if __name__ == "__main__":
    # Start Flask app in debug mode (auto-reload on code changes)
    app.run(debug=True)