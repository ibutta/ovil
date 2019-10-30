from flask import Blueprint, redirect
from flask import render_template, request, url_for
from flask import current_app, g
from uuid import uuid1
from . import db
from . import github_api
import subprocess
import re

bp = Blueprint('logger', __name__)

globalData:dict = {}
globalData['query_parsed'] = False


@bp.route('/')
def home():
    globalData['query_parsed'] = False
    return render_template('logger/issue_logging.html')

@bp.route('/<query>&<objs_verbs>', methods=('GET', 'POST'))
def log_form_filled(query, objs_verbs):
    return render_template('logger/issue_logging.html', query=query, objs_verbs=objs_verbs)

@bp.route('/parse_query', methods=('POST',))
def parse_query():

    print('parse_query ---> starting...')

    query = request.form['sql_script']
    if query:

        #TODO Improve the method used to call the gateway.
        # Right now it's executing one sudo command just to gain "sudo trust"
        # and immediatelly starting a new connection to the terminal to actually
        # call the gateway with the query. That was necessary because the gateway
        # was concatenating the sudo password with the query ID from stdin and inserting as
        # the entry ID on the db.

        gwProc = subprocess.Popen(['sudo', '-S', 'ls', '/usr/lib/sonar/gateway/'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE
        )

        gwProc.stdin.write('hiwhiwywH1\n'.encode())
        gwProc.communicate()[0]

        gwProc = subprocess.Popen(['sudo', '-S', '/usr/lib/sonar/gateway/sonargateway','--config', 
            '/etc/sonar/gateway/objects_and_verbs_parser.json',
            '--input_del',
            '_^_'
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE
        )

        
        print("parse_query -> query fetch from html:", query)

        id = uuid1()

        gwProc.stdin.write('{0} {1} _^_\n'.format(id.hex, query).encode())
        gwProc.communicate()[0]

        dbClient = db.get_db('mongodb://admin:jS0nar$@127.0.0.1:27117/admin')

        if dbClient:
            dbase = dbClient.sonargateway_test
            entry = dbase.ovparser.find_one({"_id": str(id.hex)})
            objs_verbs = 'Error fetching Objects and Verbs from database...'
            try:
                objs_verbs = str(entry["Objects and Verbs"])
                print('parse_query line 65--> objs_verbs:', objs_verbs)
                #insert a space after each objects and verbs to improve readability
                objs_verbs = '; '.join(objs_verbs.split(';'))
                print('parse_query line 68--> objs_verbs:', objs_verbs)
                globalData['objs_verbs'] = objs_verbs
                globalData['query_id'] = id
                globalData['query_parsed'] = True
            except:
                print('parse_query --> ERROR! could not fetch objects and verbs')
                pass
            return redirect(url_for('.log_form_filled', query=query, objs_verbs=objs_verbs))
        else:
            return redirect(url_for('.log_form_filled', query=query, objs_verbs='Unnable to connect to database...'))
    else:
        return redirect(url_for('.home'))

@bp.route('/create_issue', methods=('POST',))
def create_issue():
    if globalData['query_parsed']:
        query_id = str(globalData['query_id'])
        actual_output = globalData['objs_verbs']

        expected_output = request.form['expected_output']
        user_name = request.form['user_name']
        user_email = request.form['user_email']

        issue_body = 'Query ID:\n\t{0}\n\nActual output:\n\n\t{1}\n\nExpected output:\n\n\t{2}\n\nLogged by: {3}\nemail: {4}'.format(
            query_id, actual_output, expected_output, user_name, user_email)

        response = github_api.create_github_issue(body=issue_body, assignees=['ibutta',])

        if response['success']:
            globalData['issue_url'] = response['html_url']
            return redirect(url_for('.success'))
        else:
            return render_template('logger/issue_err.html')
    else:
        return render_template('logger/consistency_err.html')
        
@bp.route('/err', methods=('POST','GET'))
def err_test():
    return render_template('logger/issue_err.html')

@bp.route('/success', methods=('POST','GET'))
def success():
    return render_template('logger/success.html', issue_url=globalData['issue_url'])

