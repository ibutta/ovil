import json
import requests

USERNAME = 'ibutta'
PASSWD = 'hiwhiwywH1'

REPO_OWNER = 'ibutta'
REPO_NAME = 'flask-tutorial'

def create_github_issue(title, body=None, assignee=None, milestone=None, labels=['bug']):

    url = 'https://api.github.com/repos/{0}/{1}/issues'.format(REPO_OWNER, REPO_NAME)

    session = requests.Session()
    session.auth = (USERNAME, PASSWD)

    issue = {
        'title': title,
        'body': body,
        'assignee': assignee,
        'milestone': milestone,
        'labels': labels
    }

    req = session.post(url, json.dumps(issue))

    if req.status_code == 201:
        print('Issue "{0}" successfully created!'.format(title))
    else:
        print('Could not create issue "{0}"'.format(title))
        print('Server returned:', req.content)

if __name__ == "__main__":
    create_github_issue('This is an issue', 'This is the body of the issue.', 'ibutta', labels=['bug'])