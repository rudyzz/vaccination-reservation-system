import sys
from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
from model.Availability import Availability
from model.Appointment import Appointment
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql
import datetime


'''
objects to keep track of the currently logged-in user
Note: it is always true that at most one of currentCaregiver and currentPatient is not null
        since only one user can be logged-in at a time
'''
current_patient = None

current_caregiver = None


def create_patient(tokens):
    if len(tokens) != 3:
        print("Please input in correct format.")
        return

    username = tokens[1]
    password = tokens[2]

    if username_exists_patient(username):
        print("Whoops! " + username + " was taken, please try another one.")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    try:
        patient = Patient(username, salt=salt, hash=hash)
        patient.save_to_db()
        print(" *** Account created successfully *** ")
    except pymssql.Error:
        print("Create Patient User Failed! "
              "Please try again")
        return


def create_caregiver(tokens):
    # create_caregiver <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please input in correct format.")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_caregiver(username):
        print("Whoops! " + username + " was taken, please try another one.")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the caregiver
    try:
        caregiver = Caregiver(username, salt=salt, hash=hash)
        # save to caregiver information to our database
        caregiver.save_to_db()
        print(" *** Account created successfully *** ")
    except pymssql.Error:
        print("Create Caregiver User Failed! "
              "Please try again")
        return


def username_exists_patient(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Patients WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error:
        print("Error occurred when checking username!")
        cm.close_connection()
    cm.close_connection()
    return False


def username_exists_caregiver(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Caregivers WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error:
        print("Error occurred when checking username!")
        cm.close_connection()
    cm.close_connection()
    return False


def login_patient(tokens):
    # login_patient <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_patient
    global current_caregiver
    if current_patient is not None:
        print("You've already logged in as Patient. Username: " + current_patient.get_username())
        print("Please log out first if you want to log in another account.")
        return

    elif current_caregiver is not None:
        print("You've already logged in as Caregiver. Username: " + current_caregiver.get_username())
        print("Please log out first if you want to log in another account.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please input in correct format.")
        return

    username = tokens[1]
    password = tokens[2]

    patient = None
    try:
        patient = Patient(username, password=password).get()
    except pymssql.Error:
        print("Error occurred when logging in! ")

    # check if the login was successful
    if patient is None:
        print("Login Failed! Please check your username and password.")
    else:
        print("Patient logged in as: " + username)
        current_patient = patient


def login_caregiver(tokens):
    # login_caregiver <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_patient
    global current_caregiver
    if current_patient is not None:
        print("You've already logged in as Patient. Username: " + current_patient.get_username())
        print("Please log out first if you want to log in another username.")
        return
    elif current_caregiver is not None:
        print("You've already logged in as Caregiver. Username: " + current_caregiver.get_username())
        print("Please log out first if you want to log in another account.")
        return

    if len(tokens) != 3:
        print("Please input in correct format.")
        return
    username = tokens[1]
    password = tokens[2]

    caregiver = None
    try:
        caregiver = Caregiver(username, password=password).get()
    except pymssql.Error:
        print("Error occurred when logging in!")

    # check if the login was successful
    if caregiver is None:
        print("Login Failed! Please check your username and password.")
    else:
        print("Caregiver logged in as: " + username)
        current_caregiver = caregiver


def search_caregiver_schedule(tokens):
    """
    TODO: Part 2
    """
    global current_caregiver
    global current_patient
    if current_caregiver is None and current_patient is None:
        print("Please log in as a patient or caregiver first!")
        return

    if len(tokens) != 2:
        print("Please try again!")
        return

    date = tokens[1]

    try:
        date_tokens = date.split("-")
        month = int(date_tokens[0])
        day = int(date_tokens[1])
        year = int(date_tokens[2])
    except Exception:
        print("Please input in correct format.")
        return

    try:
        d = datetime.datetime(year, month, day)
        if current_caregiver is not None:
            current_caregiver.search_caregiver_schedule(d)
        elif current_patient is not None:
            current_patient.search_caregiver_schedule(d)
    except ValueError:
        print("Please enter a valid date!")
    except pymssql.Error:
        print("Error occurred when searching caregiver schedule")


def reserve(tokens):
    """
    TODO: Part 2
    """
    #  check 1: check if the current logged-in user is a patient
    global current_patient
    if current_patient is None:
        print("Please login as a patient first!")
        return

    # check 2: the length for tokens need to be exactly 3
    if len(tokens) != 3:
        print("Please check your input is in correct format.")
        return

    date_mdy = tokens[1]
    vaccine = tokens[2]
    #  Process on date
    try:
        date_tokens = date_mdy.split("-")
        month = int(date_tokens[0])
        day = int(date_tokens[1])
        year = int(date_tokens[2])
        date = datetime.datetime(year, month, day)
    except Exception:
        print("Please input in correct format.")
        return

    #  check 3: check if caregiver available on this date
    if not is_available(date):
        print("No caregiver available on that day! Please choose another day")
        return

    #  check 4: check if vaccine is available
    if not vaccine_available(vaccine):
        print("Whoops! The vaccine is not enough. Please try later")
        return

    #  Now, let's reserve an appointment~
    #  Step 1: Generate a unique appointment ID, assuming it be "patient_username + date".
    #          And assure a patient can't get vaccinated more than once on the same day.
    if already_reserved(current_patient.get_username(), date):
        print("You've already reserved an appointment on that day, please choose another date")
        return
    appointment_id = str(date_tokens[0])+str(date_tokens[1])+str(date_tokens[2])+str(current_patient.get_username())

    #  Step 2: Decrease one vaccine dose and one availability of a random caregiver
    use_one_vaccine(vaccine)
    caregiver_name = occupy_one_availability(date)

    #  Step 3: Insert the appointment to Appointments table
    new_appointment = Appointment(appointment_id, current_patient.get_username(), caregiver_name, date, vaccine)
    new_appointment.save_to_db()

    print("Successfully reserved!")


def is_available(d):
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor(as_dict=True)

    get_availability = "SELECT Username FROM Availabilities WHERE Time = %s"

    try:
        cursor.execute(get_availability, d)
        for row in cursor:
            curr_user = row["Username"]
            return curr_user is not None
        conn.commit()
    except pymssql.Error:
        print("Error occurred when getting caregiver username through time!")
        cm.close_connection()
    cm.close_connection()
    return False


def vaccine_available(vaccine):
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor(as_dict=True)

    check_vaccine = "SELECT * FROM Vaccines WHERE Name = %s ORDER BY Doses ASC"

    try:
        cursor.execute(check_vaccine, vaccine)
        for row in cursor:
            return row["Doses"] > 0
    except pymssql.Error:
        print("Error occurred when checking vaccine availability")
        cm.close_connection()
    cm.close_connection()
    return False


def already_reserved(username, date):
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor(as_dict=True)

    check_once = "SELECT * FROM Appointments WHERE Patient_Username = %s AND Time = %d"

    try:
        cursor.execute(check_once, (username, date))
        r = cursor.fetchone()
        return r is not None
    except pymssql.Error:
        print("Error occurred when checking if the patient has already reserved")
        cm.close_connection()

    cm.close_connection()
    return True


def use_one_vaccine(name):
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor(as_dict=True)

    get_current_doses = "SELECT Doses FROM Vaccines WHERE Name = %s"
    update_vaccine_doses = "UPDATE Vaccines SET Doses = %d WHERE name = %s"

    try:
        cursor.execute(get_current_doses, name)
        for row in cursor:
            curr_doses = row["Doses"]
        conn.commit()
    except pymssql.Error:
        print("Error occurred when using the vaccine")
        cm.close_connection()
        return

    if curr_doses == 0:
        print("Vaccine is not enough")
        cm.close_connection()
        return
    else:
        curr_doses -= 1
        try:
            cursor.execute(update_vaccine_doses, (curr_doses, name))
            conn.commit()
        except pymssql.Error:
            print("Error occurred when updating vaccine doses")
            cm.close_connection()

    cm.close_connection()
    return


def occupy_one_availability(date):
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor()

    select_random_caregiver = "SELECT Username FROM Availabilities WHERE Time = %s"
    remove_availability = "DELETE FROM Availabilities WHERE Time = %d AND Username = %s"

    try:
        cursor.execute(select_random_caregiver, date)
        curr_caregiver = cursor.fetchone()
    except pymssql.Error:
        print("Error occurred when selecting the caregiver")
        cm.close_connection()
        return

    if curr_caregiver is None:
        print("No caregiver available this day")
        cm.close_connection()
        return
    else:
        cursor.execute(remove_availability, (date, curr_caregiver))
        conn.commit()
        cm.close_connection()
        return curr_caregiver


def upload_availability(tokens):
    #  upload_availability <date>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return

    date = tokens[1]
    # assume input is hyphenated in the format mm-dd-yyyy
    try:
        date_tokens = date.split("-")
        month = int(date_tokens[0])
        day = int(date_tokens[1])
        year = int(date_tokens[2])
    except Exception:
        print("Please input in correct format")
        return
    try:
        d = datetime.datetime(year, month, day)
        if not availability_exists(d, current_caregiver.get_username()):
            current_caregiver.upload_availability(d)
            print("Availability uploaded!")
        else:
            print("***You can only upload one availability per day.*** \n"
                  "***Please try another day.***")
    except ValueError:
        print("Please enter a valid date!")
    except pymssql.Error as db_err:
        print("Error occurred when uploading availability")


def availability_exists(d, username):
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor()

    check_availability = "SELECT * FROM Availabilities WHERE Time = %d AND Username = %s"
    check_appointment = "SELECT * FROM Appointments WHERE Time = %d AND Caregiver_Username = %s"

    try:
        cursor.execute(check_availability, (d, username))
        r = cursor.fetchone()
        if r is None:
            cursor.execute(check_appointment, (d, username))
            r = cursor.fetchone()
            if r is None:
                cm.close_connection()
                return False
        cm.close_connection()
        return True
    except pymssql.Error:
        print("Error occurred when checking availability existence.")
        cm.close_connection()
        return


def cancel(tokens):
    """
    TODO: Extra Credit
    """
    #  check 1: check if logged-in
    if current_caregiver is None and current_patient is None:
        print("Please login first!")
        return

    #  check 2: the length for tokens need to be exactly 2
    if len(tokens) != 2:
        print("Please try again!")
        return

    appointmentid = tokens[1]

    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor(as_dict=True)

    patient_get_appointment = "SELECT * FROM Appointments WHERE AppointmentID = %s AND Patient_Username = %s"
    caregiver_get_appointment = "SELECT * FROM Appointments WHERE AppointmentID = %s AND Caregiver_Username = %s"
    delete_appointment = "DELETE FROM Appointments WHERE AppointmentID = %s"

    try:
        if current_patient is not None:
            cursor.execute(patient_get_appointment, (appointmentid, current_patient.get_username()))
        elif current_caregiver is not None:
            cursor.execute(caregiver_get_appointment, (appointmentid, current_caregiver.get_username()))
        r = cursor.fetchone()
        if r is None:
            print("No corresponding appointment record. Please check the appointment ID is correct.\n"
                  "And only the patient and the caregiver of that appointment can cancel it.\n"
                  "Also please check your authority.")
            cm.close_connection()
            return
        else:
            reserved_vaccine = r["Vaccine_Name"]
            reserved_date = r["Time"]
            reserved_caregiver = r["Caregiver_Username"]
            conn.commit()
    except pymssql.Error:
        print("Error occurred when getting the details of the appointment.")
        cm.close_connection()
        return

    try:
        returned_vaccine = Vaccine(reserved_vaccine, 0).get()
        returned_vaccine.increase_available_doses(1)
    except pymssql.Error:
        print("Error occurred when returning the vaccine")
        cm.close_connection()
        return

    try:
        returned_availability = Availability(reserved_date, reserved_caregiver)
        returned_availability.save_to_db()
    except pymssql.Error:
        print("Error occurred when returning the availability")
        cm.close_connection()
        return

    try:
        cursor.execute(delete_appointment, appointmentid)
        conn.commit()
    except pymssql.Error:
        print("Error occurred when deleting the appointment.")
        cm.close_connection()
        return

    print("Your appointment has been cancelled successfully.")

    cm.close_connection()
    return


def add_doses(tokens):
    #  add_doses <vaccine> <number>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    #  check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    vaccine_name = str(tokens[1])
    doses = int(tokens[2])
    vaccine = None
    try:
        vaccine = Vaccine(vaccine_name, doses).get()
    except pymssql.Error:
        print("Error occurred when adding doses")

    # check 3: if getter returns null, it means that we need to create the vaccine and insert it into the Vaccines
    #          table

    if vaccine is None:
        try:
            vaccine = Vaccine(vaccine_name, doses)
            vaccine.save_to_db()
        except pymssql.Error:
            print("Error occurred when adding doses")
    else:
        # if the vaccine is not null, meaning that the vaccine already exists in our table
        try:
            vaccine.increase_available_doses(doses)
        except pymssql.Error:
            print("Error occurred when adding doses")

    print("Doses updated!")


def show_appointments(tokens):
    """
    TODO: Part 2
    """
    global current_patient
    global current_caregiver
    if current_caregiver is None and current_patient is None:
        print("Please login first!")
        return

    try:
        if current_patient is not None:
            current_patient.show_appointments()
        elif current_caregiver is not None:
            current_caregiver.show_appointments()
    except pymssql.Error:
        print("Error occurred when showing appointments!")


def logout(tokens):
    """
    TODO: Part 2
    """
    global current_patient
    global current_caregiver
    if current_caregiver is None and current_patient is None:
        print("You haven't logged in yet...")
        return

    else:
        current_patient = None
        current_caregiver = None
        print("Logged out!")
        return


def start():
    stop = False
    while not stop:
        print()
        print(" *** Please enter one of the following commands *** ")
        print("> create_patient <username> <password>")  # //TODO: implement create_patient (Part 1)
        print("> create_caregiver <username> <password>")
        print("> login_patient <username> <password>")  # // TODO: implement login_patient (Part 1)
        print("> login_caregiver <username> <password>")
        print("> search_caregiver_schedule <date> (FORMAT: MM-DD-YYYY)")
        # // TODO: implement search_caregiver_schedule (Part 2)
        print("> reserve <date> <vaccine> (FORMAT: MM-DD-YYYY)")  # // TODO: implement reserve (Part 2)
        print("> upload_availability <date> (FORMAT: MM-DD-YYYY)")
        print("> cancel <appointment_id> (FORMAT: MMDDYYYYusername)")  # // TODO: implement cancel (extra credit)
        print("> add_doses <vaccine> <number>")
        print("> show_appointments")  # // TODO: implement show_appointments (Part 2)
        print("> logout")  # // TODO: implement logout (Part 2)
        print("> Quit")
        print()
        response = ""
        print("> Enter: ", end='')

        try:
            response = str(input())
        except ValueError:
            print("Type in a valid argument")
            break

        response = response.lower()
        tokens = response.split(" ")
        if len(tokens) == 0:
            ValueError("Try Again")
            continue
        operation = tokens[0]
        if operation == "create_patient":
            create_patient(tokens)
        elif operation == "create_caregiver":
            create_caregiver(tokens)
        elif operation == "login_patient":
            login_patient(tokens)
        elif operation == "login_caregiver":
            login_caregiver(tokens)
        elif operation == "search_caregiver_schedule":
            search_caregiver_schedule(tokens)
        elif operation == "reserve":
            reserve(tokens)
        elif operation == "upload_availability":
            upload_availability(tokens)
        elif operation == "cancel":
            cancel(tokens)
        elif operation == "add_doses":
            add_doses(tokens)
        elif operation == "show_appointments":
            show_appointments(tokens)
        elif operation == "logout":
            logout(tokens)
        elif operation == "quit":
            print("Thank you for using the scheduler, Goodbye!")
            stop = True
        else:
            print("Sorry, I don't understand.")


if __name__ == "__main__":
    '''
    // pre-define the three types of authorized vaccines
    // note: it's a poor practice to hard-code these values, but we will do this ]
    // for the simplicity of this assignment
    // and then construct a map of vaccineName -> vaccineObject
    '''

    # start command line
    print()
    print("Welcome to the COVID-19 Vaccine Reservation Scheduling Application!")

    start()
