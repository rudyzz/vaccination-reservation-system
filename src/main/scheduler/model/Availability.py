import sys
sys.path.append("../db/*")
from db.ConnectionManager import ConnectionManager
import pymssql


class Availability:
    def __init__(self, date, caregiver_username):
        self.date = date
        self.caregiver_username = caregiver_username

    # getter
    def get(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)

        get_availability = "SELECT Username FROM Availabilities WHERE Time = %d AND Username = %s"

        try:
            cursor.execute(get_availability, (self.date, self.caregiver_username))
            # for row in cursor:
            #     curr_user = row["Username"]
            #     return curr_user
            conn.commit()
            cm.close_connection()
            return self
        except pymssql.Error:
            print("Error occurred when getting caregiver username through time!")
            cm.close_connection()
            return

    def get_date(self):
        return self.date

    def get_username(self):
        return self.caregiver_username

    def save_to_db(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)

        add_availabilities = "INSERT INTO Availabilities VALUES (%s, %s)"
        try:
            cursor.execute(add_availabilities, (self.date, self.caregiver_username))
            # you must call commit() to persist your data if you don't set autocommit to True
            conn.commit()
        except pymssql.Error as db_err:
            print("Error occurred when inserting Availabilities")
            sqlrc = str(db_err.args[0])
            print("Exception code: " + str(sqlrc))
            cm.close_connection()
        cm.close_connection()