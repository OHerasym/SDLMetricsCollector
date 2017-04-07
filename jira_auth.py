import jira
from getpass import getpass
import base64

CREDENTIALS_FILE = "jira_credantials"
def get_credantials():
    try:
        with open(CREDENTIALS_FILE, 'r') as fd:
            login = base64.b64decode(fd.readline().strip())
            passwd = base64.b64decode(fd.readline().strip())
            return login, passwd
    except(IOError):
        return None, None


def manual_login(server):
    user = raw_input("Jira login: ")
    password = getpass('Password for {0}: '.format(user))
    try:
        access = jira.JIRA(server, basic_auth=(user, password))
        with open(CREDENTIALS_FILE, 'w') as credentials:
            credentials.write(base64.b64encode(user) + '\n')
            credentials.write(base64.b64encode((password)))
    except(jira.exceptions.JIRAError):
        print("Incorrect jira credantials")
        return manual_login(server)
    return access

def login(server):
        user, password =  get_credantials()
        access = None
        if user and password:
            try:
                access = jira.JIRA(server, basic_auth=(user, password))
            except:
                print("Saved incorrect jira credantials")
        if not access:
            access = manual_login(server)
        return access
