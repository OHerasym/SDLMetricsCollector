import jira
from getpass import getpass
import base64
import github3
import datetime
import random, string

JIRA_FILE = "jira_credantials"
GITHUB_FILE = "github_credantials"

def get_credantials():
    try:
        with open(JIRA_FILE, 'r') as fd:
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
        with open(JIRA_FILE, 'w') as credentials:
            credentials.write(base64.b64encode(user) + '\n')
            credentials.write(base64.b64encode((password)))
    except(jira.exceptions.JIRAError):
        print("Incorrect jira credantials")
        return manual_login(server)
    return access

def jira_login(server):
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

def randomword(length):
    return ''.join(random.choice(string.lowercase) for i in range(length))


def get_token():
    try:
        with open(GITHUB_FILE, 'r') as fd:
            token = fd.readline().strip()
            id = fd.readline().strip()
            return token, id
    except(IOError):
        return None, None

def login():
    token, id = get_token()
    if not token:
        user = raw_input("Github login: ")
        password = ''
        while not password:
            password = getpass('Password for {0}: '.format(user))
            note = "SDLMetricsCollector_hash" + randomword(10)
            note_url = "https://github.com/LuxoftAKutsan/SDLMetricsCollector"
            scopes = ['user', 'repo']
            auth = github3.authorize(user, password, scopes, note, note_url)
        with open(GITHUB_FILE, 'w') as fd:
            print("token %s" %auth.token)
            print("id %s" %auth.id)
            fd.write(str(auth.token) + '\n')
            fd.write(str(auth.id))
            return login()
    return github3.login(token=token)


class PullRequest:
    def __init__(self, developer, caption, url, days_old):
        self.developer = developer
        self.caption = caption
        self.url = url
        self.days_old = days_old

def open_pull_request_for_repo(repo):
    res = []
    now = datetime.datetime.now()
    print(repo)
    try:
        open_pull_requests = list(repo.pull_requests(state='open'))
    except AttributeError:
	return  res
    for pull_request in open_pull_requests:
        delta = now.date() - pull_request.created_at.date()
        res.append(PullRequest(pull_request.user.login,  pull_request.title, pull_request.html_url, delta.days))
    return res
