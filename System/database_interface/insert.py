from database_interface import *

def insert_node(id, node_name, perspective, longitude, latitude):
    """ Inserts a new book into the database. """
    # This is the query
    query = """ INSERT INTO node(id, node_name, perspective, longitude, latitude) 
                VALUES(%s,%s,%s,%s,%s)
            """
    args = (id, node_name, perspective, longitude, latitude)

    try:
        # Read out the database configurations
        db_config = read_db_config()
        # GIve the configurations to the MySQLConnection object.
        conn = MySQLConnection(**db_config)
        # Create a cursor from the connection object
        cursor = conn.cursor()
        # Execute the query using the cursor object.
        cursor.execute(query, args)
        # Commit the changes made to the database
        conn.commit()

    except Error as error:
        print(error)

    finally:
        cursor.close()
        conn.close()

def insert_count_minute(vehicle_count, record_time, node_id, direction):
    """ Creates a new entry for a count reading for a minute. """

    # define the query
    query = """
            INSERT INTO count_minute(vehicle_count, record_time, node_id, direction) 
                VALUES(%s,%s,%s,%s)
            """
    # Specify the arguments for the placeholders
    args = (vehicle_count, record_time, node_id,direction)

    try:
        # Read out the database configurations
        db_config = read_db_config()
        # GIve the configurations to the MySQLConnection object.
        conn = MySQLConnection(**db_config)
        # Create a cursor from the connection object
        cursor = conn.cursor()
        # Execute the query using the cursor object.
        cursor.execute(query, args)
        # Commit the changes made to the database
        conn.commit()

    except Error as error:
        print(error)

    finally:
        cursor.close()
        conn.close()




