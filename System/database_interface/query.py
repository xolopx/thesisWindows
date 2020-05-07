from database_interface import *

def node_exists(id):
    results = None
    flag = None
    try:
        # Grab method from mysql module
        dbconfig = read_db_config()
        # create connection object
        conn = MySQLConnection(**dbconfig)
        # Create cursor from connection object
        cursor = conn.cursor()
        # Execute a query using the cursor. Check if the node exists.
        # cursor.execute("SELECT EXISTS(SELECT * FROM node WHERE id = %s)",(id,))
        cursor.execute("SELECT 1 FROM node WHERE id = %s",(id,))
        results = cursor.fetchone()

        # If no entries are found
        if results is None:
            flag = False
        # If an entry is found
        else:
            flag = True

    except Error as e:
        print(e)

    finally:
        # close the cursor and the connection
        cursor.close()
        conn.close()
        # Return the result
        return flag


def query_with_fetchone():
    try:
        # Grab method from mysql module
        dbconfig = read_db_config()
        # create connection object
        conn = MySQLConnection(**dbconfig)
        # Create cursor from connection object
        cursor = conn.cursor()
        # Execute a query using the cursor.
        cursor.execute("SELECT * FROM books")
        # Fetch the first row from the query result.
        row = cursor.fetchone()
        # Keep fetching rows until there are none left.
        while row is not None:
            print(row)
            row = cursor.fetchone()

    except Error as e:
        print(e)

    finally:
        # close the cursor and the connection
        cursor.close()
        conn.close()

def query_with_fetchall():
    try:
        dbconfig= read_db_config()
        conn = MySQLConnection(**dbconfig)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM books")
        # Store the result of the query in rows
        rows = cursor.fetchall()

        print('Total Row(s):', cursor.rowcount)
        # Print contents of the rows.
        for row in rows:
            print(row)

    except Error as e:
        print(row)

    finally:
        cursor.close()
        conn.close()

def iter_row(cursor, size=10):
    while True:
        # Get a specific number of rows from the table.
        rows = cursor.fetchmany(size)
        if not rows:
            break
        for row in rows:
            # Yield returns a result each time one is created and then returns to where it left off.
            yield row

def query_with_fetchmany():
    try:
        dbconfig = read_db_config()
        conn = MySQLConnection(**dbconfig)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM books")

        for row in iter_row(cursor, 10):
            print(row)

    except Error as e:
        print(e)

    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    # query_with_fetchone()
    # query_with_fetchall()
    query_with_fetchmany()