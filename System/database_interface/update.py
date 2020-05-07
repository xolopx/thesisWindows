from database_interface import *

def update_node(id, node_name, perspective, latitude, longitude):
    """ Checks if node exists and if it does, performs an update and returns True
        If the node doesn't exist returns false and no update is performed.

        NB: Will worry about statistics later.
        """

    # Read database configuration
    db_config = read_db_config()
    # Creates query to update the Node.
    query = """ UPDATE node 
                SET node_name = %s,
                perspective = %s,
                latitude = %s,
                longitude = %s
                WHERE id = %s
            """

    data = (node_name, perspective, latitude, longitude, id)

    try:
        # Create the connection
        conn = MySQLConnection(**db_config)
        # Create the cursor
        cursor = conn.cursor()
        # Execute the query
        cursor.execute(query, data)
        # Accept the changes
        conn.commit()



    except Error as error:
        print(error)

    finally:
        cursor.close()
        conn.close()
