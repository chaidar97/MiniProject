import sqlite3
import getpass

def main():
    loginEmail = ""
    conn = sqlite3.connect('./testdb.db')
    c = conn.cursor()
    login(c, conn)

    conn.close()

def login(c, conn):
    # Find out if user wishes to login or register
    answer = input("Do you wish to login or register (L/R)? ")
    # Login loop
    while True:
        if(answer.lower() == 'l'):
            # Gather user input for email and password
            username = input("Email:")
            pswd = getpass.getpass('Password:')
            loginQuery = 'SELECT Members.name from members WHERE members.email = ? AND members.pwd = ?;'
            # Query the database on login info
            loginInfo = (username, pswd)
            c.execute(loginQuery, loginInfo)
            conn.commit()
            info = c.fetchall()
            # If we get nothing returned, make user re-enter
            if(len(info) == 0):
                print("Invalid login")
            # Otherwise we allow the login and store the login email
            else:
                loginEmail = username
                print("Welcome, Master.")
                break
        elif(answer.lower() == 'r'):
            print("Registered.")
            break
        else:
            print("Invalid response.")
            answer = input("Do you wish to login or register (L/R)? ")


main()
