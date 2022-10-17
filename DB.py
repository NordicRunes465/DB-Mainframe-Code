
from mysql.connector import connect, connection
import mysql.connector

from mysql.connector import Error

def Connect_to_Database():
    try:
        connection = mysql.connector.connect(
                                             user="student",
                                             password="eDeskTopdb2022!",
                                             database="edesktopdb",
                                             port="3306"
                                             )
        return connection
    except Error as e:
        print(e)
Data = Connect_to_Database()
