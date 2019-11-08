from flask import current_app, flash
from ovil.aux_funcs import debug_print
from ovil import cache
from jwt import JWT, jwk_from_pem 
from json import JSONDecodeError
import json
import requests
import time

def search_user(user_name):
    url = 'https://api.github.com/search/users?q=user:{0}'.format(str(user_name))
    debug_print('URL for searching user: {0}'.format(url), func_name='search_user')
    response = requests.get(url)
    debug_print('Response from github api has code {0} and content: {1}'.format(response.status_code, response.text), func_name='search_user')
    if response.status_code == 200: #OK
        json_content = json.loads(response.content.decode('utf8'))
        total_count = int(json_content.get('total_count'))
        if total_count == 1:
            return True
        else:
            return False
    return False


def get_access_token():
    try:
        debug_print('Starting app authentication against GitHub', func_name='get_access_token')
        pem_file_path = str(current_app.config.get('GITHUB_APP_PEM_PATH'))

        # This is the flow to request data about the app
        # https://developer.github.com/apps/building-github-apps/authenticating-with-github-apps/#authenticating-as-a-github-app

        time_now = int(time.time())

        payload = {
            'iss': current_app.config.get('GITHUB_APP_ID'),
            'iat': time_now,
            'exp': time_now + (5 * 60)
        }

        debug_print('Opening PEM file for reading. PEM file path: {0}'.format(pem_file_path), func_name='get_access_token')

        with open(pem_file_path, 'rb') as f:
            private_key = jwk_from_pem(f.read())
            f.close()
        
        debug_print('PEM file successfully read', func_name='get_access_token') 

        jwtoken = JWT()
        jwsignature = jwtoken.encode(payload, private_key, 'RS256')

        api_app_url = 'https://api.github.com/app/installations'

        headers = {
            'Authorization': 'Bearer {0}'.format(str(jwsignature)),
            'Accept': 'application/vnd.github.machine-man-preview+json'
        }

        debug_print('Sending GET request to {0}'.format(api_app_url), func_name='get_access_token')
        response = requests.get(api_app_url, headers=headers)

        # Here starts the flow to acquire the access token
        # https://developer.github.com/apps/building-github-apps/authenticating-with-github-apps/#authenticating-as-an-installation

        if response.status_code == 200: #OK
            debug_print('GET request to {0} returned 200 OK'.format(api_app_url), func_name='get_access_token')

            json_content = json.loads(response.content.decode('utf8'))
            debug_print('Response content: {0}'.format(json_content), func_name='get_access_token')

            if type(json_content) is list: 

                debug_print('Content is list...', func_name='get_access_token')

                # the github account may have more than one application installed
                for l in json_content:
                    debug_print('json within content list: {0}'.format(l), func_name='get_access_token')
                    if l.get('app_id') == int(current_app.config.get('GITHUB_APP_ID')):
                        debug_print('found the right json: {0}'.format(l), func_name='get_access_token')
                        json_content = l
                        break

            debug_print('json_content before posting to the access tokens url: {0}'.format(json_content), func_name='get_access_token')
            access_tokens_url = json_content.get('access_tokens_url')

            debug_print('Sending POST request to {0}'.format(access_tokens_url), func_name='get_access_token')
            response = requests.post(access_tokens_url, headers=headers)

            if response.status_code == 201: #OK Created
                debug_print('POST request to {0} returned 201 OK Created'.format(access_tokens_url), func_name='get_access_token')
                json_content = json.loads(response.content.decode('utf8'))
                return json_content.get('token')
                
        else:
            debug_print('Unexpected response from github api with code: {0}'.format(response.status_code), func_name='get_access_token')    

    except JSONDecodeError:
        debug_print('ERROR reading json returned by github... (JSONDecodeError)', func_name='get_access_token')  

    except OSError:
        debug_print('ERROR reading PEM file...', func_name='get_access_token')      
        
    except:
        # debug_print('ERROR authorizing app...', func_name='get_access_token')
        return False
    else:
        debug_print('GitHub app authentication successful!', func_name='get_access_token')
        return True

def create_github_issue(title='OVParser Bug', body=None, assignees=None, milestone=None, labels=['bug'], auth_attempt=False):

    repo_owner = current_app.config.get('GITHUB_APP_REPO_OWNER')
    repo_name = current_app.config.get('GITHUB_APP_REPO_NAME')

    url = 'https://api.github.com/repos/{0}/{1}/issues'.format(repo_owner, repo_name)

    token = cache.get('token')
    if token:
        headers = {
            'Authorization': 'token {0}'.format(token),
            'Accept': 'application/vnd.github.machine-man-preview+json'
        }

        issue_data = {
            'title': title,
            'body': body,
            'milestone': milestone,
            'labels': labels,
            'assignees': assignees
        }

        payload = json.dumps(issue_data)
        response = requests.request('POST', url, data=payload, headers=headers)

        if response.status_code == 401: #Unauthorized
            debug_print('GitHub returned 401. The access token is probably expired', func_name='create_github_issue')
            #maybe the jwt expired so we need another one
            if not auth_attempt:
                debug_print('Trying to generate a new access token', func_name='create_github_issue')
                cache.set('token', get_access_token())
                create_github_issue(title=title, body=body, assignees=assignees, milestone=milestone, labels=labels, auth_attempt=True)
            else:
                flash('Could not authenticate against GitHub...')
                debug_print('Authentication against github failed with 401 two times consecutively...', func_name='create_github_issue')


        if response.status_code == 201: #OK Created
            debug_print('Issue "{0}" successfully created!'.format(title), func_name='create_github_issue')
            json_content = json.loads(response.text)
            return {
                'success': True,
                'status_code': response.status_code,
                'html_url': json_content['html_url']
            }
        else:
            debug_print('Could not create issue "{0}"'.format(title), func_name='create_github_issue')
            debug_print('GitHub returned code {0} with content {1}:'.format(response.status_code, response.content), func_name='create_github_issue')
            return {
                'success': False,
                'status_code': response.status_code
            }
    
    else:
        flash('Could not authenticate against GitHub...')
        debug_print('ERROR! There is no access token defined...', func_name='create_github_issue')
        return {
            'success': False,
            'status_code': ''
        }