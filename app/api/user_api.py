
from ..db_utilities import get_users_connection,execute_update,insert_dict_serial_id,contains_value,execute_query
from werkzeug.security import generate_password_hash,check_password_hash


#adds new user and returns the id assigned to the user
#paramaters required are a dictionary of values:-
#username,email,password,firstname,lastname,department,institution,city,country
#the password is hashed before storing  
def insert_new_user(values):
    con = get_users_connection()
    if username_exists(values['username']):
        return -1, "Username already exists"
    if email_exists(values['email']):
        return -1, "Email already exists"
    values['password']= generate_password_hash(values['password'])
    id =insert_dict_serial_id("users", "id", values, con)
    return id


def change_user_email(id,new_email):
    con = get_users_connection()
    
    sql = "UPDATE users SET email = '%s' WHERE id = '%s'" % (new_email,id)
    execute_update(sql, con)    
    
def change_user_password(id,new_password):
    con = get_users_connection()
    password_hash = generate_password_hash(new_password)
    sql = "UPDATE users SET password = '%s' WHERE id = '%s'" % (password_hash,id)
    execute_update(sql, con)

def email_exists(email):
    con = get_users_connection()
    if (contains_value("users", con,"email", email)):
        return True
    return False
    
def username_exists(username):
    con = get_users_connection()
    if (contains_value("users", con,"username", username)):
        return True
    return False    
    
 
def confirm_user(id):
    con = get_users_connection()
    sql ="UPDATE users SET confirmed = 'True' WHERE id ='%s'" % (id)
    execute_update(sql, con)
  
#validates user with username or password
def validate_user(username,password):
    con = get_users_connection()
    sql ="SELECT password FROM users WHERE username='%s'" % (username)
    results = execute_query(sql,con)
    password_hash = results[0]['password']
    return check_password_hash(password_hash, password)
    
#deded
def get_user_details(id):
    con = get_users_connection()
    sql = "SELECT * FROM users WHERE id = '%s'" % id
    results = execute_query(sql, con)
    return results[0]
    
