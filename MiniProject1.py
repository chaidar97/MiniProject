import sqlite3
import getpass

def main():
    loginEmail = ""
    conn = sqlite3.connect('./testdb.db')
    c = conn.cursor()
    ## Login loop
    while True:
        ## Gather user input for email and password
        username = input("Email:")
        pswd = getpass.getpass('Password:')
        loginQuery = 'SELECT Members.name from members WHERE members.email = ? AND members.pwd = ?;'
        ## Query the database on login info
        loginInfo = (username, pswd)
        c.execute(loginQuery, loginInfo)
        conn.commit()
        info = c.fetchall()
        ## If we get nothing returned, make user re-enter
        if(len(info) == 0):
            print("Invalid login")
        # Otherwise we allow the login and store the login email
        else:
            loginEmail = username
            print("Welcome, Master.")
            break
    conn.close()

main()
