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

# ==================== RUN APPLICATION ====================

if __name__ == "__main__":
    # Start Flask app in debug mode (auto-reload on code changes)
    app.run(debug=True)