import sqlite3
import getpass
import time

def main():
    loginEmail = ""
    conn = sqlite3.connect('./testdb.db')
    c = conn.cursor()
    loginEmail = login(c, conn)
    displayMessages(c,conn,loginEmail)
    # Main thread
    while True:
        answer = input("What would you like to do? Type 'O' for options: ")
        if(answer.lower() == "o"):
            print("Type 'SMR' to see your rides\nType 'Exit' to quit.\n")
        elif(answer.lower() == "exit"):
            print("Goodbye.")
            break
        elif(answer.lower() == "smr"):
            searchRideRequests(c, conn, loginEmail)

    conn.close()


# Shows all of the users ride requests
def searchRideRequests(c, conn, loginEmail):
    query = "SELECT requests.rid, requests.pickup, requests.dropoff, requests.amount, requests.rdate" \
            " FROM requests, members WHERE members.email = ? AND requests.email = members.email "
    rides = runSQL(c, conn, query, (loginEmail,))
    index = 0
    limit = 5
    if(len(rides) == 0):
        print("You have no ride requests")
    else:
        print("Here are your ride requests:\n")
        # See up to 5 ride requests at a time
        for ride in rides:
            # Checks to see if the user wants to see 5 more requests
            if(index == limit):
                response = input("If you wish to see 5 more rides, enter 'y', otherwise, enter anything else: ")
                if(response.lower() == 'y'):
                    limit += 5
                else:
                    break
            print("Ride ID: %s    Pickup: %s    Dropoff: %s    Price: %s    Date: %s"%(ride[0], ride[1], ride[2], ride[3], ride[4]))
            index +=1
        # Allows the user to delete any ride request given
        while True:
            answer = input("If you wish to delete a request, simply enter the ride ID. If you wish to go back, enter anything else: ")
            if(answer.isdigit()):
                for ride in rides:
                    if(int(answer) == int(ride[0])):
                        query = "DELETE FROM requests WHERE rid = ?;"
                        runSQL(c,conn,query,(answer,))
                        print("Ride request #%s Deleted."%answer)
            else:
                break




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

def runSQL(c, conn, query, input):
    # Query the database on login info
    c.execute(query, input)
    info = c.fetchall()
    conn.commit()
    return info

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

main()
