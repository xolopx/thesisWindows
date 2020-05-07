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

        # Print the value of the most recent row.8
        if cursor.lastrowid > -1:
            print('last insert id', cursor.lastrowid)
        else:
            print('last insert id not found')

        # Commit the changes made to the database
        conn.commit()
    except Error as error:
        print(error)

    finally:
        cursor.close()
        conn.close()

def insert_books(books):
    """ Inserts more than one entry into the database. "
        :param - books: is a list of books names and id's."""



    # Define the query
    query = "INSERT INTO books(title,isbn) " \
            "VALUES(%s,%s)"

    try:
        # Read the configuration file
        db_config = read_db_config()
        # Give config to the connection object.
        conn = MySQLConnection(**db_config)
        # Create a cursor to execute queries
        cursor = conn.cursor()
        # Execute the query using the cursor and executemany method which will do for all entities in the list of books. 
        cursor.executemany(query, books)
        # Commit the changes
        conn.commit()

    except Error as e:
        print('Error:', e)

    finally:
        cursor.close()
        conn.close()



