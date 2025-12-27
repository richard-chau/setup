import os
import pyodbc
import logging

# Global variable to hold the connection
_connection = None

def get_connection():
    """
    Gets a connection to the Azure SQL Database.
    Retains the connection globally to reuse it across function invocations (connection pooling).
    """
    global _connection
    
    conn_str = os.environ.get("SqlConnectionString")
    if not conn_str:
        logging.error("SqlConnectionString environment variable is not set.")
        raise ValueError("SqlConnectionString environment variable is not set.")

    if "yourserver.database.windows.net" in conn_str:
        logging.error("SqlConnectionString is still set to the default placeholder. Please update local.settings.json with valid credentials.")
        raise ValueError("SqlConnectionString is set to default placeholder.")

    # Check if connection is already established and active
    if _connection:
        try:
            # Simple check to see if connection is alive (optional, but good practice)
            # cursor = _connection.cursor()
            # cursor.execute("SELECT 1")
            # return _connection
            pass # Simplified for this example, usually pyodbc handles some pooling or we just reuse object
        except Exception:
            logging.warning("Existing connection lost. Reconnecting...")
            _connection = None

    if _connection is None:
        logging.info("Creating new SQL connection...")
        try:
            _connection = pyodbc.connect(conn_str)
        except Exception as e:
            logging.error(f"Failed to connect to SQL Database: {e}")
            raise e
            
    return _connection

def execute_query(query, params=None):
    """
    Helper function to execute a query.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        # Determine if it's a SELECT or INSERT/UPDATE
        if query.strip().upper().startswith("SELECT"):
            columns = [column[0] for column in cursor.description]
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            return results
        else:
            conn.commit()
            return cursor.rowcount
    finally:
        cursor.close()
        # Do NOT close the connection here, so it can be reused
