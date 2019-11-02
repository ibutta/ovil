from flask import jsonify
import json
import requests

USERNAME = 'ibutta'
TOKEN = '29776fc0c1e5c95f8bc62a640d4068d3165e48f4'

REPO_OWNER = 'ibutta'
REPO_NAME = 'flask-tutorial'

def request_user_id(client_id='', ):
    # url = 'https://github.com/login/oauth/authorize'

    # issue_data = {
    #     'client_id': title,
    #     'body': body,
    #     # 'assignee': assignee, --> deprecated
    #     'milestone': milestone,
    #     'labels': labels,
    #     'assignees': assignees
    # }

    # payload = json.dumps(issue_data)
    # response = requests.request('POST', url, data=payload, headers=headers)

    pass

def create_github_issue(title='OVParser Bug', body=None, assignees=None, milestone=None, labels=['bug']):

    url = 'https://api.github.com/repos/{0}/{1}/issues'.format(REPO_OWNER, REPO_NAME)

    headers = {
        'Authorization': 'token {0}'.format(TOKEN)
    }

    issue_data = {
        'title': title,
        'body': body,
        # 'assignee': assignee, --> deprecated
        'milestone': milestone,
        'labels': labels,
        'assignees': assignees
    }

    payload = json.dumps(issue_data)
    response = requests.request('POST', url, data=payload, headers=headers)

    if response.status_code == 201:
        print('Issue "{0}" successfully created!'.format(title))
        content = response.content.decode('utf8')
        json_content = json.loads(content)
        return {
            'success': True,
            'status_code': response.status_code,
            'html_url': json_content['html_url']
        }
    else:
        print('Could not create issue "{0}"'.format(title))
        print('Server returned:', response.content)
        return {
            'success': False,
            'status_code': response.status_code
        }

if __name__ == "__main__":
    create_github_issue('This is an issue 33', 'This is the body of the issue created with an authentication token.', ['ibutta',], labels=['bug'])