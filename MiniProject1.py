import sqlite3
import getpass
import datetime
import time

# Looks like we have to do a design doc and a readme also. We can do it at the end.

LUGGAGE_MAX_LEN = 10 

def main():
    loginEmail = ""
    conn = sqlite3.connect("testdb.db")
    # conn = sqlite3.connect("C:/Users/Thomas/Desktop/MiniProject/testdb.db") # Windows you need a direct folder link. Please keep this here for me :)
    c = conn.cursor()
    c.execute("PRAGMA foreign_keys = 1")
    loginEmail = login(c, conn)
    displayMessages(c,conn,loginEmail)
    # Main thread
    while True:
        answer = input("What would you like to do? Type 'O' for options: ")
        if(answer.lower() == "o"):
            print("Enter 'SMR' to see your rides\nEnter 'Exit' to quit.\nEnter 'PCode' to search a pickup location\nEnter 'offer' to offer a ride.\nEnter 'search' to search for a ride.")
        elif(answer.lower() == "exit"):
            print("Goodbye.")
            break
        elif(answer.lower() == "smr"):
            searchRideRequests(c, conn, loginEmail)
        elif (answer.lower() == "pcode"):
            searchLocations(c, conn, loginEmail)
        elif (answer.lower() == "offer"):
            offerRide(c, conn, loginEmail)
        elif (answer.lower() == "search"):
            searchRides(c, conn, loginEmail)

    conn.close()


# Use this function to query the database, just give it a query and the input for the query
def runSQL(c, conn, query, input):
    try:
        # Query the database on login info
        c.execute(query, input)
        info = c.fetchall()
        conn.commit()
        return info
    except:
        print("This cannot be done, please try again.")


# Shows all of the users ride requests
def searchRideRequests(c, conn, loginEmail):
    query = "SELECT requests.rid, requests.email, requests.pickup, requests.dropoff, requests.amount, requests.rdate" \
            " FROM requests, members WHERE members.email = ? AND requests.email = members.email "
    rides = runSQL(c, conn, query, (loginEmail,))
    if(len(rides) == 0):
        print("You have no ride requests")
    else:
        print("Here are your ride requests:\n")
        # Print out queried rides
        printRequests(rides)
        # Allows the user to delete any ride request given
        while True:
            answer = input("If you wish to delete a request, simply enter the ride ID. If you wish to go back, enter anything else: ")
            if(answer.isdigit()):
                # Looks through rides to see if the value entered matches a ride id
                for ride in rides:
                    if(int(answer) == int(ride[0])):
                        query = "DELETE FROM requests WHERE rid = ?;"
                        runSQL(c,conn,query,(answer,))
                        print("Ride request #%s Deleted.\n"%answer)
            else:
                break


def searchLocations(c, conn, loginEmail):
    location = input("Would you like to search a location reference or a city (L/C)? ")
    valid = True
    if(location.lower() == "l"):
        location = input("Please enter the location code: ")
        query = "SELECT requests.rid, requests.email, requests.pickup, requests.dropoff, requests.amount, requests.rdate " \
                "FROM requests WHERE requests.pickup = ?;"
        info = runSQL(c, conn, query, (location.lower(),))
        if(len(info) == 0):
            valid = False
            print("No results found.")
        # Print out queried rides
        printRequests(info)
    elif(location.lower() == "c"):
        location = input("Please enter the city: ")
        query = "SELECT requests.rid, requests.email, requests.pickup, requests.dropoff, requests.amount, requests.rdate FROM requests " \
                "INNER JOIN locations ON (requests.pickup = locations.lcode) WHERE lower(locations.city) = ?;"
        info = runSQL(c, conn, query, (location.lower(),))
        if(len(info) == 0):
            valid = False
            print("No results found.")
        # Print out queried rides
        printRequests(info)
    else:
        valid = False
        print("Invalid input.\n")
    if(valid):
        # Ask the user if they wish to message requester
        answer = input("If you would like to message a user providing the ride, enter the Ride ID, otherwise enter anything else: ")
        if (answer.isdigit()):
            # Looks through rides to see if the value entered matches a ride id
            for ride in info:
                if (int(answer) == int(ride[0])):
                    # Gather information for new message
                    message = input("Enter the message you wish to send: ")
                    t = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
                    values = (ride[1], t, loginEmail, message, answer, "n" )
                    query = "INSERT INTO inbox VALUES(?,?,?,?,?,?);"
                    runSQL(c, conn, query, values)
                    print("Message sent!\n")


# Prints out the ride requests 5 at a time
def printRequests(rides):
    index = 0
    limit = 5
    # See up to 5 ride requests at a time
    for ride in rides:
        # Checks to see if the user wants to see 5 more requests
        if (index == limit):
            response = input("\nIf you wish to see 5 more rides, enter 'y', otherwise, enter anything else: \n")
            if (response.lower() == 'y'):
                limit += 5
            else:
                break
        print("Ride ID: %s    Provider: %s    Pickup: %s    Dropoff: %s    Price: %s    Date: %s" % (ride[0], ride[1], ride[2], ride[3], ride[4], ride[5]))
        index += 1
    print("\n")


# Find out if user wishes to login or register
def login(c, conn):
    answer = input("Do you wish to login or register (L/R)? ")
    # Login loop
    while True:
        if(answer.lower() == 'l'):
            # Gather user input for email and password
            email = input("Email: ")
            pswd = getpass.getpass('Password: ')
            loginQuery = 'SELECT Members.name from members WHERE members.email = ? AND members.pwd = ?;'
            # Query the database on login info
            loginInfo = (email, pswd)
            info = runSQL(c, conn, loginQuery, loginInfo)
            # If we get nothing returned, make user re-enter
            if(len(info) == 0):
                print("Invalid login")
            # Otherwise we allow the login and store the login email
            else:
                print("Welcome, %s.\n"%email)
                break
        # If user wants to register
        elif(answer.lower() == 'r'):
            userQuery = 'SELECT Members.name from members WHERE members.email = ?;'
            # Get registration info
            email = input("Registration email: ")
            # Check if the email already exists
            result = runSQL(c, conn, userQuery, (email,))
            if(len(result) != 0):
                print("This username already exists, sorry.")
            # Insert new user into the database
            else:
                name = input("Name: ")
                phone = input("Phone: ")
                pswd = getpass.getpass('Password: ')
                regInfo = (email, name, phone, pswd)
                registerQuery = 'INSERT INTO members(email, name, phone, pwd) VALUES(?,?,?,?);'
                runSQL(c, conn, registerQuery, regInfo)
                print("Registered and logged in.")
                break
        else:
            print("Invalid response.")
            answer = input("Do you wish to login or register (L/R)? ")
    return email


# Displays all the messages that are unseen for that user
def displayMessages(c, conn, email):
    query = 'SELECT inbox.sender, inbox.content, inbox.msgTimestamp FROM inbox, members WHERE members.email = ? AND inbox.email = members.email AND inbox.seen = ?'
    values = (email, "n")
    # Retrieve unseen messages
    messages = runSQL(c, conn, query, values)
    if(len(messages) == 0):
        print("No new messages!")
    else:
        # Format and print each message
        for v in messages:
            message = "From %s: %s\t\t%s\n" % (v[0], v[1], v[2])
            print(message)
        values = ("y", email)
        # Update DB to set messages as seen
        query = "UPDATE inbox SET seen = ? WHERE email = ?;"
        runSQL(c, conn, query, values)


# Offer a ride
def offerRide(c, conn, loginEmail):

    # Get day month and year from user
    while True:
        date = input("Enter ride date (MM-DD-YYYY), or 'stop' to exit: ")
        if(date == "stop"):
            return
        try:
            year, month, day = map(int, date.split('-'))
            break
        except:
            print("Please enter a valid date")

    # Get the number of seats offered
    while True:
        seatInput = input("Enter the number of seats offered, or 'stop' to exit: ")
        if(seatInput == "stop"):
            return
        try:
            seats = int(seatInput)
            break
        except:
            print("Please enter a valid number of seats")

    # Get the price per seat
    while True:
        priceInput = input("Enter the price per seat, or 'stop' to exit: ")
        if(seatInput == "stop"):
            return
        try:
            seats = float(seatInput)
            break
        except:
            print("Please enter a valid price per seat")

    # Get the luggage description
    while True:
        lugDesc = input("Enter a luggage description (Max Length: " + LUGGAGE_MAX_LEN + "): ")
        if(len(lugDesc) > LUGGAGE_MAX_LEN):
            print("Please enter a valid luggage description")
        else:
            break

     # TODO: Get source and destination location

    val = input("If you wish to add a car number, enter 'y', otherwise, enter anything else: ")
    if(val == 'y'):
        while True:
            cno = input("Enter your car number: ")
            try:
                cno = int(cno)
                # TODO: Ensure that the cno is valid
                break
            except:
                print("Please enter a valid car number.")

    val = input("If you wish to add enroute locations, enter 'y', otherwise, enter anything else: ")
    enroute = []
    if(val == 'y'):
        pass # TODO: While the user doesnt say no, keep asking for keywords, getting the location, and adding it in an enroute array


# Return a location number from a provided keyword
def locFromKeyword(keyword):
    pass

# Ask the user for a location repeatedly
def pollForLocation():
    pass
    #while True:
    #    key = input("Enter a location keyword: ")

# Search for a ride
def searchRides(c, conn, loginEmail):
    pass


main()
