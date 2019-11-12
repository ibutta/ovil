from flask import current_app
import configparser

def debug_print(*values, func_name=None):
    if current_app.config['ENV'] == 'development':
        if func_name:
            print('***DEBUG***', func_name, '--->', *values)
        else:
            print('***DEBUG***', *values)
    pass

def create_config_file(path):
    config = '## Configuration file for the Objects and Verbs Issue Logger application\n\n'\
    + '## --- User variables ---\n'\
    + '## In order to run the Objects and Verbs Issue Logger you need to either be\n'\
    + '## logged as root or as a sudo-enabled user. Set the following variable ONLY\n'\
    + '## if you are logged as A SUDO USER THAT REQUIRES A PASSWORD for executing\n'\
    + '## sudo commands.\n'\
    + '# SUDO_PASSWD=\'\'\n\n'\
    + '## --- Application variables ---\n'\
    +'SECRET_KEY=b\',\\xf4\\xc5\\xb0*\\xb9\\xfc\\xb6\'\n\n'\
    + '## --- SonarW variables ---\n'\
    + 'DB_CONN_STRING=\'\'\n\n'\
    + '## --- Sonargateway variables ---\n'\
    + 'SGW_PATH=\'/usr/lib/sonar/gateway/sonargateway\'\n'\
    + 'SGW_CONFIG_PATH=\'/etc/sonar/gateway/objects_and_verbs_parser.json\'\n\n'\
    + '## --- GitHub App variables ---\n'\
    + 'GITHUB_APP_REPO_OWNER=\'\'\n'\
    + 'GITHUB_APP_REPO_NAME=\'\'\n'\
    + 'GITHUB_APP_PEM_PATH=\'\'\n'\
    + 'GITHUB_APP_ID=\'\''

    cfg_path = path + '/ovil-config.cfg'
    print(cfg_path)
    with open(cfg_path, 'w') as config_file:
        config_file.write(config)
        config_file.close()
    pass