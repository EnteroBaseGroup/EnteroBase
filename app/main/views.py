from flask import render_template,g
from . import main
from ..models import User,get_user
from ..api.user_api import get_user_details
from flask import current_app

@main.route('/')
def index():
   
    print "ssss"
    
    #jkc = get_user(1)
    #print jkc.id
    print current_app.config['MAIL_PASSWORD']
    print current_app.config['MAIL_USERNAME']
    return render_template('index.html')

@main.teardown_app_request
def teardownrequest(ex):
    if hasattr(g, 'user_dbcon'):      
        g.user_dbcon.close()
        