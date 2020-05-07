# 1. Create connection object
# 2. Create cursor to execute query.
# 3. Commit the changes made using the connection object.
# 4. Close the cursor and connection.

from database_interface import *

def delete_node(id):
    """ Deletes a node given it's id. """
    # Get config data for connection object
    config = read_db_config()
    # Specify query to be performed.
    query = "DELETE FROM node WHERE id = %s"

    try:
        # Pass config to connection obj
        conn = MySQLConnection(**config)
        # Create cursor from connection obj
        cursor = conn.cursor()
        # execute query
        cursor.execute(query, (id,))
        # commit the change
        conn.commit()
    except Error as error:
        print(error)
    finally:
        cursor.close()
        conn.close()