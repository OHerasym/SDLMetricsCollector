import github3
import datetime
import random, string
from getpass import getpass

CREDENTIALS_FILE = "/tmp/.github_credantials"


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
        with open(CREDENTIALS_FILE, 'w') as fd:
            print("token %s" %auth.token)
            print("id %s" %auth.id)
            fd.write(str(auth.token) + '\n')
            fd.write(str(auth.id))
            fd.close()
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
    print(now)
    print(repo)
    try:
        open_pull_requests = list(repo.iter_pulls(state='open'))
    except AttributeError:
	return  res
    for pull_request in open_pull_requests:
        delta = now.date() - pull_request.created_at.date()
        res.append(PullRequest(pull_request.user.login,  pull_request.title, pull_request.html_url, delta.days))
    return res
