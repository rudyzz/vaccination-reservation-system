import sys
sys.path.append("../db/*")
from db.ConnectionManager import ConnectionManager
import pymssql


class Appointment:
    def __init__(self, appointment_id, patient_name, caregiver_name, date, vaccine_name):
        self.appointment_id = appointment_id
        self.patient_name = patient_name
        self.caregiver_name = caregiver_name
        self.date = date
        self.vaccine_name = vaccine_name

    # getter
    def get(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)

        get_appointment_details = "SELECT AppointmentID, Vaccine_Name, Patient_Username, Caregiver_Username, Time" \
                                  " FROM Appointments WHERE AppointmentID = %s"

        try:
            cursor.execute(get_appointment_details, self.appointment_id)
            for row in cursor:
                self.vaccine_name = row["Vaccine_Name"]
                self.patient_name = row["Patient_Username"]
                self.caregiver_name = row["Caregiver_Username"]
                self.date = row["Time"]
                return self
        except pymssql.Error:
            print("Error occurred when getting Appointment")
            cm.close_connection()

        cm.close_connection()
        return None

    def save_to_db(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)

        add_appointment = "INSERT INTO Appointments VALUES (%s, %s, %s, %s, %s)"

        try:
            cursor.execute(add_appointment, (self.appointment_id, self.patient_name, self.caregiver_name, self.date,
                                             self.vaccine_name))
            conn.commit()
        except pymssql.Error as db_err:
            print("Error occurred when inserting Appointment")
            sqlrc = str(db_err.args[0])
            print("Exception code: " + str(sqlrc))
            cm.close_connection()
        cm.close_connection()