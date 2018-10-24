import sqlite3
import getpass
import time

def main():
    loginEmail = ""
    conn = sqlite3.connect('./testdb.db')
    c = conn.cursor()
    loginEmail = login(c, conn)
    conn.close()

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
                print("Welcome, Master.")
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

main()
