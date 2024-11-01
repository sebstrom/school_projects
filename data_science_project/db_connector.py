import mysql.connector
from mysql.connector import Error
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, filename='db_log.log', 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Guess you have to change to your login and password 
def get_db_connection():
    connection = None
    try:
        logging.info("Attempting to connect to the database...")
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='bertbot123',
            database='football_statistics'
        )
        logging.info("MySQL Connection Successful")
    except Error as e:
        logging.error(f"Database connection failed with error: {e}")
        return None, None
    
    cursor = connection.cursor()
    return connection, cursor


def close_db_connection(connection, cursor):
    if cursor:
        cursor.close()
        logging.info("Cursor closed successfully")
    if connection:
        connection.close()
        logging.info("MySQL Connection closed successfully")
