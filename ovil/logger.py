from flask import Blueprint, redirect, session, flash
from flask import render_template, request, url_for, app
from uuid import uuid1
from . import db
from ovil.github_api import create_github_issue
import subprocess

bp = Blueprint('logger', __name__)

@bp.route('/')
def home():
    session.clear()
    session['query_parsed'] = False
    return render_template('logger/issue_logging.html')

@bp.route('/query_parsed', methods=('GET', 'POST'))
def log_form_filled():
    return render_template('logger/issue_logging.html', query=session.get('query'), objs_verbs=session.get('objs_verbs'))

@bp.route('/parse_query', methods=('POST',))
def parse_query():

    debug_print('parse_query ---> starting...')

    query = request.form['sql_script']
    if query:

        #TODO Improve the method used to call the gateway.
        # Right now it's executing one sudo command just to gain "sudo trust"
        # and immediatelly starting a new connection to the terminal to actually
        # call the gateway with the query. That was necessary because the gateway
        # was concatenating the sudo password with the query ID from stdin and inserting as
        # the entry ID on the db.

        # gwProc = subprocess.Popen(['sudo', '-S', 'ls', '/usr/lib/sonar/gateway/'],
        #     stdin=subprocess.PIPE,
        #     stdout=subprocess.PIPE
        # )

        # gwProc.stdin.write('hiwhiwywH1\n'.encode())
        # gwProc.communicate()[0]

        gwProc = subprocess.Popen(['sudo', '-S', '/usr/lib/sonar/gateway/sonargateway','--config', 
            '/etc/sonar/gateway/objects_and_verbs_parser.json',
            '--input_del',
            '_^_'
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE
        )

        
        debug_print("parse_query -> query fetch from html:", query)

        id = uuid1()

        gwProc.stdin.write('{0} {1} _^_\n'.format(id.hex, query).encode())
        gwProc.communicate()[0]

        # dbClient = db.get_db('mongodb://admin:jS0nar$@127.0.0.1:27117/admin')
        dbClient = db.get_db('mongodb://uadmin:pjS0n@r$@127.0.0.1:27117/admin')

        if dbClient:
            dbase = dbClient.sonargateway_test
            entry = dbase.ovparser.find_one({"_id": str(id.hex)})
            objs_verbs = 'Error fetching Objects and Verbs from database...'
            try:
                objs_verbs = str(entry["Objects and Verbs"])
                #insert a space after each objects and verbs to improve readability
                objs_verbs = '; '.join(objs_verbs.split(';'))

                session['objs_verbs'] = objs_verbs
                session['query_id'] = id.hex
                session['query'] = query
                session['query_parsed'] = True
                
                if not objs_verbs:
                    flash('Oops... The query parsing response returned empty. Please check the input query...')

                debug_print("parse_query -> query parsed successfully:")

            except:
                flash('Error fetching objects and verbs from database...')
                debug_print('parse_query --> ERROR! could not fetch objects and verbs')
                pass
            finally:
                return redirect(url_for('.log_form_filled'))
        else:
            flash('Unnable to connect to database...')
            return redirect(url_for('.log_form_filled'))
    else:
        return redirect(url_for('.home'))

@bp.route('/create_issue', methods=('POST',))
def create_issue():
    if session.get('query_parsed'):

        #github oauth required application flow starts here
        
        
        
        #github oauth required application flow ends here


        query_id = session.get('query_id')
        actual_output = session.get('objs_verbs')

        expected_output = request.form['expected_output']
        user_name = request.form['user_name']
        user_email = request.form['user_email']

        issue_body = 'Query ID:\n\t{0}\n\nActual output:\n\n\t{1}\n\nExpected output:\n\n\t{2}\n\nLogged by: {3}\nemail: {4}'.format(
            query_id, actual_output, expected_output, user_name, user_email)

        response = create_github_issue(body=issue_body, assignees=['ibutta',])

        if response['success']:
            session['issue_url'] = response['html_url']
            return redirect(url_for('.success'))
        else:
            return redirect(url_for('.issue_err'))
    else:
        return redirect(url_for('.consistency_err'))
        
@bp.route('/form_consistency_error', methods=('POST','GET'))
def consistency_err():
    return render_template('logger/consistency_err.html')

@bp.route('/creating_issue_error', methods=('POST','GET'))
def issue_err():
    return render_template('logger/issue_err.html')

@bp.route('/issue_creating_success', methods=('POST','GET'))
def success():
    return render_template('logger/success.html')

def debug_print(*values):
    if app.get_debug_flag():
        print('***DEBUG***', *values)
    pass