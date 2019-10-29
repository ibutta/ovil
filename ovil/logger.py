from flask import Blueprint, redirect
from flask import render_template, request, url_for
from flask import current_app, g
from uuid import uuid1
from . import db
from . import github_api
import subprocess
import re

bp = Blueprint('logger', __name__)


@bp.route('/', methods=('GET', 'POST'))
def log_form():
    return render_template('logger/issue_logging.html')

@bp.route('/<query>&<objs_verbs>', methods=('GET', 'POST'))
def log_form_filled(query, objs_verbs):
    return render_template('logger/issue_logging.html', query=query, objs_verbs=objs_verbs)

@bp.route('/parse_query', methods=('POST',))
def parse_query():

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

    query = request.form['sql_script']
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
        except:
            print('parse_query --> ERROR! could not fetch objects and verbs')
            pass
        return redirect(url_for('.log_form_filled', query=query, objs_verbs=objs_verbs))
    else:
        return redirect(url_for('.log_form_filled', query=query, objs_verbs='Unnable to connect to database...'))

@bp.route('/create_issue', methods=('POST',))
def create_issue():
    # request.form[]
    issue_body = request.form['issue_body']
    print('create_issue --> issue_body:', issue_body)
    return render_template('logger/issue_logging.html')




