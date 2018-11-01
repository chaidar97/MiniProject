import sqlite3
import getpass
import datetime
import time
import os
import sys

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
            print("Enter 'SMR' to see your rides\nEnter 'Exit' to quit.\nEnter 'Location' to search a pickup location\nEnter 'offer' to offer a ride.\nEnter 'search' to search for a ride."
                  "\nEnter 'Post' to post a new ride.\nEnter 'Bookings' to book a ride.\nEnter 'Logout' to logout.")
        elif(answer.lower() == "exit"):
            print("Goodbye.")
            break
        elif (answer.lower() == "logout"):
            print("Goodbye.")
            # Restarting the program, safer than calling main again(?)
            os.execl(sys.executable, sys.executable, *sys.argv)
            break
        elif(answer.lower() == "smr"):
            searchRideRequests(c, conn, loginEmail)
        elif (answer.lower() == "location"):
            searchLocations(c, conn, loginEmail)
        elif (answer.lower() == "offer"):
            offerRide(c, conn, loginEmail)
        elif (answer.lower() == "search"):
            searchRides(c, conn, loginEmail)
        elif (answer.lower() == "post"):
            postRide(c, conn, loginEmail)
        elif (answer.lower() == "bookings"):
            book(c, conn, loginEmail)
        #elif (answer.lower() == "dev"):
        #    getLocation(c, conn, loginEmail)


    conn.close()


# Use this function to query the database, just give it a query and the input for the query
def runSQL(c, conn, query, input):
    info = []
    try:
        # Query the database on login info
        if(input == None):
            c.execute(query)
        else:
            c.execute(query, input)
        info = c.fetchall()
        conn.commit()
        return info
    except Exception as e:
        print("This cannot be done, please try again.")
        print(str(e))
        return info


# Posts a new ride
def postRide(c, conn, loginEmail):
    date = getDate()
    locationQuery = ("SELECT distinct locations.lcode FROM locations;")
    locations = runSQL(c, conn, locationQuery, None)
    pickup = input("Enter a pickup location code: ")
    dropoff = input("Enter a dropoff location code: ")

    validPickup = False
    validDropoff = False
    for location in locations:
        if((pickup,)== location):
            validPickup = True
        if ((dropoff,) == location):
            validDropoff = True
    if(validPickup and validDropoff):
        price = getPrice()
        rQuery = ("SELECT MAX(requests.rid) FROM requests;")
        maxRNO = runSQL(c, conn, rQuery, None)
        rideNum = (str(maxRNO[0][0] + 1))
        insertQuery = ("INSERT INTO requests VALUES(?,?,?,?,?,?);")
        values = (rideNum, loginEmail, date, pickup, dropoff, price)
        runSQL(c, conn, insertQuery, values)
        print("Your request has been posted!")
    else:
        print("One of your location codes does not exist.")
        return

def book(c, conn, loginEmail):

    query = "SELECT b.bno, b.rno, b.email,b.cost,b.seats,b.pickup,b.dropoff " \
            " FROM bookings b,rides r WHERE r.driver=? AND b.rno=r.rno ;"    
    booking = runSQL(c, conn, query,(loginEmail,))
    if(len(booking) == 0):
        print("You have no bookings")
    else:
        print("Here are your bookings:\n")
        for book in booking:
            print("Booking ID: %s    Ride ID: %s    MEMBER: %s    COST: %s    SEATS: %s    PICKUP: %s  DROPOFF: %s" % (book[0], book[1], book[2], book[3], book[4], book[5], book[6]))
            
        

        while (len(booking)!=0):
            answer = input("If you wish to cancel a booking, enter the ride no. If you wish to book a member, enter 'book'. If you wish to go back, enter anything else: ")
                  
            if(answer.isdigit()):
                # Looks through bookings to see if the value entered matches a rno
                for books in booking:
                    if(int(answer) == int(books[1])):
                        query = "DELETE FROM bookings WHERE bookings.rno = ?;"
                        runSQL(c,conn,query,(answer,))
                        print("Booking #%s Canceled.\n"%answer)
                        
                        message = "Your booking has been cancelled "
                        t = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
                        values = (books[2], t, loginEmail, message, books[1], "n" )
                        query = "INSERT INTO inbox VALUES(?,?,?,?,?,?);"
                        runSQL(c, conn, query, values)
                        print("Message sent!\n")                        
                    else:
                        break
                    
            
                    
            elif(answer=='book'):
                
                
                decision=input("do you wish to book a particular member for a ride, if yes, then enter his email if no, enter 'no' - ")
                if(decision.lower=="no"):
                    break

                
                else:
                    flag=0
                    query="SELECT email FROM members "\
                        "WHERE members.email= ?;"
                    valid=runSQL(c,conn,query,(decision,))
                    if(valid==0):
                        print("Invalid email")

                    else:
                        query="SELECT r.rno,r.seats,r.seats-ifnull((b.seats),0),r.price,r.rdate,r.lugDesc,r.src, r.dst,r.driver,r.cno FROM rides r left outer join bookings b on b.rno=r.rno "\
                            "WHERE r.driver= ?;"
                        available=runSQL(c,conn,query,(loginEmail,))
                        printMatchRides(available)
                        
                        book_rno=input("Enter the rno that you want to book the member in- ")
                        book_seats=input("Enter the number of seats that you want to book - ")
                        query="SELECT r.rno,r.seats,r.seats-ifnull((b.seats),0) FROM rides r left outer join bookings b on b.rno=r.rno "\
                            "WHERE r.driver=? AND r.rno= ?;"                        
                     
                        value=runSQL(c,conn,query,(loginEmail,book_rno,))
                        if(value==[]):
                            print("Sorry, You can only book members on rides where you are the driver. ")
                            break
                        
                    
                        
                        difference=value[0][2]-int(book_seats)
                       if(difference<0):
                            confirm=input("Seats are overbooked. Do you still want to continue?If yes, enter'yes' or, press anything ")
                            if(confirm!='yes'):
                                flag==1
                                break
                            
                   
                            
                        if flag==1:
                            break
                        
                        locationQuery = ("SELECT distinct locations.lcode FROM locations;")
                        locations = runSQL(c, conn, locationQuery, None)
                        pickup = input("Enter a pickup location code: ")
                        dropoff = input("Enter a dropoff location code: ")
                    
                        validPickup = False
                        validDropoff = False
                        for location in locations:
                            if((pickup,)== location):
                                validPickup = True
                            if ((dropoff,) == location):
                                validDropoff = True
                                
                        
                        
                                               
                        
                        
                        if(validPickup and validDropoff):
                            
                            cost=input("enter the cost per seat- ")
                            book_id_query=("SELECT MAX(bno) FROM bookings ;")
                            maxBNO = runSQL(c, conn, book_id_query, None)
                            
                            book_id_new = (str(maxBNO[0][0] + 1))                             
                            insertQuery = ("INSERT INTO bookings VALUES(?,?,?,?,?,?,?);")
                            values = (book_id_new, decision,book_rno,cost,book_seats,pickup, dropoff)
                            runSQL(c, conn, insertQuery, values,)
                            
                            message = "Your have a new booking"
                            t = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
                            values = (decision, t, loginEmail, message, book_rno, "n" )
                            query = "INSERT INTO inbox VALUES(?,?,?,?,?,?);"
                            runSQL(c, conn, query, values)
                            print("Message sent!\n")                                                         
                            
                            
                        else:
                            print("One of your location codes does not exist.")
                            break  
                
            else:
                break
                        
                        
                        
           #left= comments
        
def printMatchRides(ride):
    index = 0
    limit = 5
    # See up to 5 rides at a time
    for book in ride:
        # Checks to see if the user wants to see 5 more rides
        if (index == limit):
            response = input("\nIf you wish to see 5 more rides, enter 'y', otherwise, enter anything else: \n")
            if (response.lower() == 'y'):
                limit += 5
            else:
                break
            
        print("RIDE NO: %s Seats: %s Offered: %s Seats Available: %s  Price: %s Ride date: %s Luggage Desc: %s Start Destination: %s Driver: %s CNO: %s"%(ride[index][0], ride[index][1], ride[index][2], ride[index][3], ride[index][4], ride[index][5],ride[index][6],ride[index][7],ride[index][8],ride[index][9]))
        index += 1
    print("\n")
                        
                        
                      

# Shows all of the users ride requests
def searchRideRequests(c, conn, loginEmail):
    query = "SELECT requests.rid, requests.email, requests.pickup, requests.dropoff, requests.amount, requests.rdate" \
            " FROM requests, members WHERE lower(members.email) = ? AND requests.email = members.email "
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
                "FROM requests WHERE lower(requests.pickup) = ?;"
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
            loginQuery = 'SELECT Members.name from members WHERE lower(members.email) = ? AND members.pwd = ?;'
            # Query the database on login info
            loginInfo = (email.lower(), pswd)
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
            userQuery = 'SELECT Members.name from members WHERE lower(members.email) = ?;'
            # Get registration info
            email = input("Registration email: ")
            # Check if the email already exists
            result = runSQL(c, conn, userQuery, (email.lower(),))
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
    return email.lower()


# Displays all the messages that are unseen for that user
def displayMessages(c, conn, email):
    query = 'SELECT inbox.sender, inbox.content, inbox.msgTimestamp FROM inbox, members WHERE lower(members.email) = ? AND inbox.email = members.email AND inbox.seen = ?'
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
        query = "UPDATE inbox SET seen = ? WHERE lower(email) = ?;"
        runSQL(c, conn, query, values)


# Retrieves date input from user
def getDate():
    # Get day month and year from user
    while True:
        date = input("Enter ride date (MM-DD-YYYY), or 'stop' to exit: ")
        if(date == "stop"):
            return
        try:
            month, day, year = map(int, date.split('-'))
            date = datetime.date(year, month, day)
            break
        except:
            print("Please enter a valid date")
    return date


# Retrieves the price input from user
def getPrice():
    # Get the price per seat
    while True:
        priceInput = input("Enter the price per seat: ")
        try:
            price = int(priceInput)
            break
        except:
            print("Please enter a valid price per seat")
    return price


# Get a location off of user keywords
def getLocation(c, conn, loginEmail):
    while True:

        # Get keyword or location code from user
        location = input("Please enter a location keyword or code: ")
        query = "SELECT location.lcode FROM locations location WHERE location.lcode = ?;"
        info = runSQL(c, conn, query, (location,))

        # Check if its a valid code
        if(len(info) == 0):

            # The code is invalid, search for it as a keyword
            query = "SELECT * FROM locations WHERE city LIKE ? OR prov LIKE ? OR address LIKE ?;"
            location = "%" + location + "%"
            info = runSQL(c, conn, query, (location, location, location,))

            # Keyword is invalid if this is false. Try searching again
            if(len(info) == 0):
                print("No results found.")
            else:

                # Display results from the query, only showing 5 at a time
                start = 0
                end = 5
                while True:

                    # Print Locations from index start to end
                    for i in range (start, end):
                        if(i >= len(info)):
                            print("Reached end of locations")
                            break
                        print(info[i])

                    # Ask for location code or y to see more
                    location = input("Enter the location code or enter 'y' to see more: ")
                    if(location == "y"):

                        # Increment the data displayed
                        start += 5
                        end += 5
                    else:
                        # Check if the provided lcode is valid again, if it is we return the information
                        query = "SELECT location.lcode FROM locations location WHERE location.lcode = ?;"
                        info = runSQL(c, conn, query, (location,))
                        if(len(info) == 0):
                            print("Please enter a correct location code.")
                        else:
                            return info[0][0]
        else:

            # If the code is valid return the code
            return info[0][0]




# Offer a ride
def offerRide(c, conn, loginEmail):
    # Retrieve the date input
    date = getDate()
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
    # Retrieve the price input
    priceInput = getPrice()
    # Get the luggage description
    while True:
        lugDesc = input("Enter a luggage description (Max Length: " + str(LUGGAGE_MAX_LEN) + "): ")
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
