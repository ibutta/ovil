from flask import current_app

def debug_print(*values, func_name=None):
    if current_app.config['ENV'] == 'development':
        if func_name:
            print('***DEBUG***', func_name, '--->', *values)
        else:
            print('***DEBUG***', *values)
    pass