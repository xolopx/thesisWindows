import mysql.connector
from mysql.connector import Error

def connect():
    """ Connect to MySQL database """
    # Connection Object
    conn = None

    # Try connection if it fails throw exception.
    try:
        conn = mysql.connector.connect(host = 'localhost',
                                       database ='python_mysql',
                                       user='root',
                                       password = 'butt')
        # Print if connection is successful.
        if conn.is_connected():
            print('Connected to MySQL database')

    except Error as e:
        print(e)

    finally:
        if conn is not None and conn.is_connected():
            conn.close()


if __name__ == '__main__':
    connect()


