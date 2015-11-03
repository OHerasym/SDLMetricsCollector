import github3
import datetime
import random, string
from getpass import getuser, getpass

CREDENTIALS_FILE = "/tmp/git_hub_login"


def randomword(length):
    return ''.join(random.choice(string.lowercase) for i in range(length))


def get_token():
    try:
        with open(CREDENTIALS_FILE, 'r') as fd:
            token = fd.readline().strip()  # Can't hurt to be paranoid
            id = fd.readline().strip()
            fd.close()
            return token, id
    except(IOError):
        return None


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
        with open(CREDENTIALS_FILE, 'w') as fd:
            print("token %s" %auth.token)
            print("id %s" %auth.id)
            fd.write(str(auth.token) + '\n')
            fd.write(str(auth.id))
            fd.close()
            return login()
    return github3.login(token=token)


def open_pull_request_for_repo(repo):
    res = []
    now = datetime.datetime.now()
    open_pull_requests = list(repo.pull_requests(state='open'))
    for pull_request in open_pull_requests:
        delta = now.date() - pull_request.created_at.date()
        res.append([pull_request.assignee, pull_request.body_text, pull_request.comments_url, delta])
    return res