import jira
from getpass import getpass

CREDENTIALS_FILE = "/tmp/.jira_credantials"
def get_credantials():
    try:
        with open(CREDENTIALS_FILE, 'r') as fd:
            login = fd.readline().strip()  # Can't hurt to be paranoid
            passwd = fd.readline().strip()
            fd.close()
            return login, passwd
    except(IOError):
        return None, None


def manual_login(server):
    user = user = raw_input("Jira login: ")
    password = getpass('Password for {0}: '.format(user))
    try:
        access = jira.JIRA(server, basic_auth=(user, password))
        fd = open(CREDENTIALS_FILE, 'w')
        fd.write(user + '\n')
        fd.write(password)
        fd.close()
    except(jira.exceptions.JIRAError):
        print("Incorrect jira credantials")
        manual_login(server)

def login(server):
        user, password =  get_credantials()
        access = None
        if user and password:
            try:
                access = jira.JIRA(server, basic_auth=(user, password))
            except:
                print("Saved incorrect jira credantials")
        if not access:
            manual_login(server)
        return access
