import subprocess
import os
from flask import Blueprint, redirect, session, flash
from flask import render_template, request, url_for, current_app, g
from uuid import uuid1
from ovil.db_module import get_db
from ovil.github_api import create_github_issue, get_access_token
from ovil.aux_funcs import debug_print

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

    debug_print('starting...', func_name='parse_query')

    query = request.form['sql_script']
    if query:

        debug_print('query fetch from html:', query, func_name='parse_query')

        #TODO Improve the method used to call the gateway.
        # Right now it's executing one sudo command just to gain "sudo trust"
        # and immediatelly starting a new connection to the terminal to actually
        # call the gateway with the query. That was necessary because the gateway
        # was concatenating the sudo password with the query ID from stdin and inserting as
        # the entry ID on the db.


        # The '-S' options is used so the 'sudo' command would write the prompt to the standard error
        #output and read the password from the stdin without using the terminal. That way the password
        #can be inserted programatically ending with an EOL character.

        sgw_path = str(current_app.config.get('SGW_PATH'))
        

        if current_app.config.get('SUDO_PASSWD'):
            debug_print('acquiring "sudo trust"...', func_name='parse_query')
            sgw_path_split = os.path.split(sgw_path)

            try:
                # gwProc = subprocess.Popen(['sudo', '-S', 'ls', '/usr/lib/sonar/gateway/'],
                gwProc = subprocess.Popen(['sudo', '-S', 'ls', sgw_path_split[0]],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE
                )

                # gwProc.stdin.write('hiwhiwywH1\n'.encode())
                sudo_passwd = str(current_app.config.get('SUDO_PASSWD'))
                sudo_passwd = sudo_passwd + '\n'
                gwProc.stdin.write(sudo_passwd.encode())
                gwProc.communicate()[0]
            except:
                debug_print('ERROR acquiring "sudo trust"...', func_name='parse_query')
            else:
                debug_print('"sudo trust" successfully acquired!', func_name='parse_query')

        debug_print('Calling sonargateway to parse the query', func_name='parse_query')
        sgw_config_path = str(current_app.config.get('SGW_CONFIG_PATH'))
        gwProc = subprocess.Popen(['sudo', '-S', sgw_path, '--config', 
            # '/etc/sonar/gateway/objects_and_verbs_parser.json',
            sgw_config_path,
            '--input_del',
            '_^_'
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE
        )

        id = uuid1()

        gwProc.stdin.write('{0} {1} _^_\n'.format(id.hex, query).encode())
        gwProc.communicate()[0]

        db_URI = str(current_app.config.get('DB_CONN_STRING'))
        # dbClient = get_db('mongodb://admin:jS0nar$@127.0.0.1:27117/admin')
        dbClient = get_db(db_URI)

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

                debug_print('query parsed successfully!', func_name='parse_query')

            except:
                flash('Error fetching objects and verbs from database...')
                debug_print('ERROR! could not fetch objects and verbs', func_name='parse_query')
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

        if not session.get('app_access_token'):
            session['app_access_token'] = get_access_token()

        query_id = session.get('query_id')
        query = session.get('query')
        actual_output = session.get('objs_verbs')

        expected_output = request.form['expected_output']
        user_credential = request.form['user_credential']
        github_user = request.form['github_user']

        issue_body = 'OVParser collection entry ID:\n\t{0}\n\n\
        Original Query:\n\t{1}\n\n\
        Actual output:\n\n\t{2}\n\n\
        Expected output:\n\n\t{3}\n\n\
        Logged by: {4}\n\
        Email: {5}@jsonar.com'.format(
            query_id, query, actual_output, 
            expected_output, github_user, user_credential
        )

        response = create_github_issue(body=issue_body, assignees=['ibutta',])

        if response['success']:
            session['issue_url'] = response['html_url']
            return redirect(url_for('.success'))
        else:
            return redirect(url_for('.issue_err'))
        return redirect(url_for('.success'))

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