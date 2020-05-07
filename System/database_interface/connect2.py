from database_interface import *

def connect():
    """ Connect to MySQL database """

    # db config reader method
    db_config = read_db_config()
    # Empty connection object
    conn = None
    # Try to connect to the database
    try:
        print(' Connecting to MySQL databas ...')
        # ** unpacks the dictionary returned by the method into keyword arguments
        conn = MySQLConnection(**db_config)

        if conn.is_connected():
            print('Connected to database')
        else:
            print('Connection failed')

    except Error as e:
        print(e)
    finally:
        if conn is not None and conn.is_connected():
            conn.close()
            print('Connection closed')

if __name__ == '__main__':
    connect()
