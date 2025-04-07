import sqlite3

def view_database():
    # Connect to the SQLite database
    conn = sqlite3.connect('spotify_minutes.db')
    cursor = conn.cursor()

    # Query to select all rows from the weekly_minutes table
    cursor.execute('SELECT * FROM weekly_minutes')
    rows = cursor.fetchall()

    # Print the results
    if rows:
        for row in rows:
            print(f"Week Start Date: {row[1]}, Total Minutes: {row[2]}")
    else:
        print("No data found.")

    # Close the connection
    conn.close()

def reset_database():
    # Connect to the SQLite database
    conn = sqlite3.connect('spotify_minutes.db')
    cursor = conn.cursor()

    # Query to delete all rows from the weekly_minutes table
    cursor.execute('DELETE FROM weekly_minutes')
    conn.commit()  # Commit the changes to the database

    print("Database reset successfully. All records have been deleted.")

    # Close the connection
    conn.close()

# Call the function to view the database
view_database()



