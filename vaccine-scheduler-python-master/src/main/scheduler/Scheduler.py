from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
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
    """
    TODO: Part 1
    """
    # create_patient <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Failed to create user.")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_patient(username):
        print("Username taken, try again!")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the patient
    patient = Patient(username, salt=salt, hash=hash)

    # save to patient information to our database
    try:
        patient.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user ", username)


def create_caregiver(tokens):
    # create_caregiver <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Failed to create user.")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_caregiver(username):
        print("Username taken, try again!")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the caregiver
    caregiver = Caregiver(username, salt=salt, hash=hash)

    # save to caregiver information to our database
    try:
        caregiver.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user ", username)

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
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
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
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False


def login_patient(tokens):
    """
    TODO: Part 1
    """
    # login_patient <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_patient
    if current_patient is not None or current_caregiver is not None:
        print("User already logged in.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1]
    password = tokens[2]

    patient = None
    try:
        patient = Patient(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if patient is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_patient = patient


def login_caregiver(tokens):
    # login_caregiver <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_caregiver
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1]
    password = tokens[2]

    caregiver = None
    try:
        caregiver = Caregiver(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if caregiver is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_caregiver = caregiver


def search_caregiver_schedule(tokens):
    """
    TODO: Part 2
    """
    # check 1: if no user is logged in, print “Please login first!”
    global current_caregiver
    global current_patient
    if current_caregiver is None and current_patient is None:
        print("Please login first!")
        return
    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return

    date = tokens[1]
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    d = datetime.datetime(year, month, day)

    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor(as_dict=True)

    get_availability = "SELECT Username FROM Availabilities WHERE Time = %s ORDER BY Username"

    available_caregivers = set()
    available_doses = []

    # conditionA, conditionB = False, False
    
    try:
        cursor.execute(get_availability, d)
        for row in cursor: 
            available_caregivers.add(row['Username']) 
        # you must call commit() to persist your data if you don't set autocommit to True
        conn.commit()
    except pymssql.Error as e:
        print("Error occurred when getting caregiver availability")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Please try again!")
        print(e)
        return
    finally:
        cm.close_connection()

    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor(as_dict=True)

    show_doses = "SELECT * FROM Vaccines" 
    
    try:
        cursor.execute(show_doses)
        for row in cursor: 
            available_doses.append((row["Name"],row["Doses"]))
        # you must call commit() to persist your data if you don't set autocommit to True
        conn.commit()
    except pymssql.Error as e:
        print("Error occurred when searching available doses")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Please try again!")
        print(e)
        return
    finally:
        cm.close_connection()

    if not available_caregivers: print("No caregiver is available!")
    if not available_doses: print("All vaccines are out of stock!")

    if available_caregivers and available_doses:

        print("The caregivers that are available for " + str(d) + " are:")
        for thename in available_caregivers:
            print(str(thename))
        print(" ")
        print("The vaccines that are available for " + str(d) + " are:")
        for thevname,num in available_doses:
            print(str(thevname) + " : " + str(num) + " doses.")


def if_date_available(d):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT Username FROM Availabilities WHERE Time = %s ORDER BY Username"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, d)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking availablility")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking availablility")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False

def if_vaccine_available(vaccine):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_vaccine = "SELECT Name, Doses FROM Vaccines WHERE Name = (%s)"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_vaccine, vaccine)
        for row in cursor:
            return row['Name'] is not None and int(row["Doses"]) 
    except pymssql.Error as e:
        print("Error occurred when checking availablility")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking availablility")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False


def reserve(tokens):
    """
    TODO: Part 2
    """
    # check 1: if no user is logged in, print “Please login first!”
    global current_caregiver
    global current_patient

    if current_caregiver is not None:
        print("Please login as a patient!")
        return

    global current_patient
    if current_patient is None:
        print("Please login first!")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    date = tokens[1]
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    d = datetime.datetime(year, month, day)

    vaccine = tokens[2]

    # find availability for `d`

    if not if_date_available(d):
        print("No Caregiver is available!")
        return

    if not if_vaccine_available(vaccine):
        print("Not enough available doses!")
        return

####
    get_availability = "SELECT Username FROM Availabilities WHERE Time = %s ORDER BY Username"

    available_caregivers = set()

    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor(as_dict=True)  

    try:
        cursor.execute(get_availability, d)
        for row in cursor: 
            available_caregivers.add(row['Username']) 
        # you must call commit() to persist your data if you don't set autocommit to True
        conn.commit()
    except pymssql.Error as e:
        print("Error occurred when getting caregiver availability")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Please try again!")
        print(e)
        return
    finally:
        cm.close_connection()

    cname = list(available_caregivers)[0]
####

    # make a reservation id: RID
    RID = 0
    get_RID = "SELECT RID FROM MakeReservation ORDER BY RID DESC"
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor(as_dict=True)
    try:
        cursor.execute(get_RID)
        for row in cursor: 
            if row["RID"]:
                RID = row["RID"]
                break
            else: 
                RID = 0
                break
        RID += 1
        conn.commit()
    except pymssql.Error as e:
        print('Error occurred while getting ReservationID')
        cm.close_connection()


    # update MakeReservation
    make_reservation = "INSERT INTO MakeReservation VALUES (%s, %s, %s, %s, %s)"
    cm = ConnectionManager()
    conn = cm.create_connection()
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(make_reservation, (current_patient.username,vaccine,cname,d,RID))
        conn.commit()
    except pymssql.Error as e:
        print("Error occurred when checking availablility")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking availablility")
        print("Error:", e)
    finally:
        cm.close_connection()


    # update vaccines
    try:
        this_vac = Vaccine(vaccine,0).get()
        this_vac.decrease_available_doses(1)
    except pymssql.Error as e:
        print("Error occurred when decreasing doses num")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when decreasing doses num")
        print("Error:", e)
        return
#############################################################################
    # update availabilities
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor(as_dict=True)

    remove_availability = "DELETE FROM Availabilities WHERE Username=%s AND Time=%s"
    try:
        cursor.execute(remove_availability, (cname,d))
        # you must call commit() to persist your data if you don't set autocommit to True
        conn.commit()
    except pymssql.Error as e:
        print(e)
        print("Error occurred when updating caregiver availability")
    finally:
        cm.close_connection()
#############################################################################        

    print(f"Appointment ID: {RID}, Caregiver username: {cname}")




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
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    try:
        d = datetime.datetime(year, month, day)
        current_caregiver.upload_availability(d)
    except pymssql.Error as e:
        print("Upload Availability Failed")
        print("Db-Error:", e)
        quit()
    except ValueError:
        print("Please enter a valid date!")
        return
    except Exception as e:
        print("Error occurred when uploading availability")
        print("Error:", e)
        return
    print("Availability uploaded!")


def cancel(tokens):
    """
    TODO: Extra Credit
    """
    # check 1: if no user is logged in, print “Please login first!”
    global current_caregiver
    global current_patient

    if current_patient is None and current_caregiver is None:
        print("Please login first!")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return

    RID = tokens[1]

#############################################################################
    d = None
    cname = None
    vaccine = None
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor(as_dict=True)

    selectDCn = "SELECT Time, Cname, Vname FROM MakeReservation WHERE RID = %s"
    try:
        cursor.execute(selectDCn, (RID))
        for row in cursor:
            d = row["Time"]
            cname = row["Cname"]
            vaccine = row["Vname"]
        # you must call commit() to persist your data if you don't set autocommit to True
        conn.commit()
    except pymssql.Error as e:
        print(e)
        print("Error occurred when updating caregiver availability")
    finally:
        cm.close_connection()

    if not d:
        print("You do not have any reservation to cancel!")
        return

#################################################################

    # update MakeReservation
    make_reservation = "DELETE FROM MakeReservation WHERE RID=%s"
    cm = ConnectionManager()
    conn = cm.create_connection()
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(make_reservation, (RID))
        conn.commit()
    except pymssql.Error as e:
        print("Error occurred when updating MakeReservation")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when updating MakeReservation")
        print("Error:", e)
    finally:
        cm.close_connection()


    # update vaccines
    try:
        this_vac = Vaccine(vaccine,0).get()
        this_vac.increase_available_doses(1)
    except pymssql.Error as e:
        print("Error occurred when decreasing doses num")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when decreasing doses num")
        print("Error:", e)
        return

    # update availabilities
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor(as_dict=True)

    add_availability = "INSERT INTO Availabilities VALUES (%s, %s)"
    try:
        cursor.execute(add_availability, (d,cname))
        # you must call commit() to persist your data if you don't set autocommit to True
        conn.commit()
    except pymssql.Error as e:
        print(e)
        print("Error occurred when updating caregiver availability")
    finally:
        cm.close_connection()




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

    vaccine_name = tokens[1]
    doses = int(tokens[2])
    vaccine = None
    try:
        vaccine = Vaccine(vaccine_name, doses).get()
    except pymssql.Error as e:
        print("Error occurred when adding doses")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when adding doses")
        print("Error:", e)
        return

    # if the vaccine is not found in the database, add a new (vaccine, doses) entry.
    # else, update the existing entry by adding the new doses
    if vaccine is None:
        vaccine = Vaccine(vaccine_name, doses)
        try:
            vaccine.save_to_db()
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    else:
        # if the vaccine is not null, meaning that the vaccine already exists in our table
        try:
            vaccine.increase_available_doses(doses)
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    print("Doses updated!")


def show_appointments(tokens):
    '''
    TODO: Part 2
    '''
    # check 1: if no user is logged in, print “Please login first!”
    global current_caregiver
    global current_patient
    if current_caregiver is None and current_patient is None:
        print("Please login first!")
        return
    # check 2: only one token”   
    if len(tokens) != 1:
        print("Please try again!")
        return

    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor(as_dict=True)

    schedules = []

    if current_caregiver:
        print_appointments = "SELECT RID, Vname, Time, Pname FROM MakeReservation WHERE Cname = %s ORDER BY RID"
        try:
            cursor.execute(print_appointments, (current_caregiver.username))
            
            for row in cursor:
                schedules.append((str(row["RID"]),str(row["Vname"]), str(row["Time"]), str(row["Pname"])))
            conn.commit()
        except pymssql.Error:
            print("pymssql error occurred when showing appointments for current_caregiver")
            raise
        except Exception as e:
            print("Error occurred when showing appointments for current_caregiver")
            print("Error:", e)
            return
        finally:
            cm.close_connection()

    elif current_patient:
        print_appointments = "SELECT RID, Vname, Time, Cname FROM MakeReservation WHERE Pname = %s ORDER BY RID"
        try:
            cursor.execute(print_appointments, (current_patient.username))
            
            for row in cursor:
                schedules.append((str(row["RID"]), str(row["Vname"]), str(row["Time"]), str(row["Cname"])))
            conn.commit()
        except pymssql.Error:
            print("pymssql error occurred when showing appointments for current_patient")
            raise
        except Exception as e:
            print("Error occurred when showing appointments for current_patient")
            print("Error:", e)
            return
        finally:
            cm.close_connection()

    if not schedules: 
        print("There is no any appointment in the system!")
    else:
        print("Below is the scheduled appointments for you:")
        for item in schedules:
            print(item[0]+" "+item[1]+" "+item[2]+" "+item[3])



def logout(tokens):
    """
    TODO: Part 2
    """
    global current_caregiver
    global current_patient

    if current_caregiver is None and current_patient is None:
        print("Please login first!")
        return

    if len(tokens) != 1:
        print("Please try again!")
        return

    else:
        current_caregiver = None
        current_patient = None
        print("Successfully logged out!")
    


def start():
    stop = False
    print()
    print(" *** Please enter one of the following commands *** ")
    print("> create_patient <username> <password>")  # //TODO: implement create_patient (Part 1)
    print("> create_caregiver <username> <password>")
    print("> login_patient <username> <password>")  # // TODO: implement login_patient (Part 1)
    print("> login_caregiver <username> <password>")
    print("> search_caregiver_schedule <date>")  # // TODO: implement search_caregiver_schedule (Part 2)
    print("> reserve <date> <vaccine>")  # // TODO: implement reserve (Part 2)
    print("> upload_availability <date>")
    print("> cancel <appointment_id>")  # // TODO: implement cancel (extra credit)
    print("> add_doses <vaccine> <number>")
    print("> show_appointments")  # // TODO: implement show_appointments (Part 2)
    print("> logout")  # // TODO: implement logout (Part 2)
    print("> Quit")
    print()
    while not stop:
        response = ""
        print("> ", end='')

        try:
            response = str(input())
        except ValueError:
            print("Please try again!")
            break

        response = response.lower()
        tokens = response.split(" ")
        if len(tokens) == 0:
            ValueError("Please try again!")
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
            print("Bye!")
            stop = True
        else:
            print("Invalid operation name!")


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
