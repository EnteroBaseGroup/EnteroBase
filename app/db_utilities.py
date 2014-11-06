
from flask import g,current_app
from psycopg2 import connect
from psycopg2.extras import DictCursor
import traceback

#determines whether the table already contains a value
def contains_value(table,con,col_name,value):
    sql = "SELECT * FROM %s WHERE %s = '%s'" % (table, col_name, value)
    print sql
    cursor = con.cursor()
    cursor.execute(sql)
    results = cursor.fetchall()
    cursor.close() 
    if not results:
        return False
    return True
    

# get the user database connection attached to this request
# or create a new one if not present
# returns a psycopg2 connection or none if connection could not be opened
# The connection will be closed at the end of the request
def get_users_connection():
    
    
    if not hasattr(g, 'user_dbcon'):
        user_database_uri=current_app._get_current_object().config['USER_DATABASE_URI']
        try:
            g.user_dbcon = connect(user_database_uri)
        except:
            print "Cannot connect to "+ user_database_uri
            return None       
        
    return g.user_dbcon


def execute_update(sql,con):
    cursor = con.cursor()
    cursor.execute(sql)
    con.commit()
    cursor.close()

def execute_query(sql,con):
    
    cursor = con.cursor(cursor_factory=DictCursor)
    cursor.execute(sql)
    results = cursor.fetchall()
    cursor.close()
       
    return results

#Paramaters: name of table, the name of the column containing the auto incremented value (serial_col)
#The dictionary containing column name: value and connection
#will insert the values and returns the newly assigned value or -1 if the operation failed
def insert_dict_serial_id(table,serial_col,dic,con):
    sql = "INSERT INTO "+table+" ("+",".join(dic.iterkeys())+") VALUES('"
    sql = sql + "','".join(dic.itervalues())+"') RETURNING "+serial_col
    try:
        cursor = con.cursor()
        cursor.execute(sql)
        id =cursor.fetchone()[0]
        con.commit() 
        cursor.close()
    except Exception as e:
        traceback.print_exc()
        return -1
        
    return id