import mariadb
from flask import Flask, request, Response
import json
import dbcreds
from flask_cors import CORS
import random
import string

app = Flask(__name__)
CORS(app)
# GENERATE LOGIN TOKEN
def get_loginToken(length):
    password_characters = string.ascii_letters + string.digits
    login_token = ''.join(random.choice(password_characters) for i in range(length))
    return login_token

# USER LOGGING IN LOGGING OUT 
@app.route('/api/login', methods=['POST', 'DELETE'])
def login():
    if request.method == 'POST':
        conn = None
        cursor = None
        userEmail = request.json.get("email")
        userPassword = request.json.get("password")
        rows = None
        user = None
        user_info = {}
        
        try:
            conn = mariadb.connect(host=dbcreds.host, port=dbcreds.port,user=dbcreds.user, password=dbcreds.password,database=dbcreds.database)
            cursor=conn.cursor()
            cursor.execute("SELECT * FROM user WHERE email=? and password=?", [userEmail, userPassword])
            user = cursor.fetchall()
            rows = cursor.rowcount
            if (rows == 1):
                loginToken = get_loginToken(30)
                print(loginToken)
                cursor.execute("INSERT INTO user_session(userId, loginToken) VALUES(?,?)", [user[0][0], loginToken])
                conn.commit()
        except mariadb.ProgrammingError as error:
                print("Programming Error.. ")
                print(error)
        except mariadb.DatabaseError as error:
                print("Database Error...")
                print(error)
        except mariadb.OperationalError as error:
                print("Connection Error...")
                print(error)
        except Exception as error:
                print("This is a general error to be checked! ")
                print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows == 1):
                user_info = {
                    "userId": user[0][0],
                    "email": user[0][1],
                    "username": user[0][2],
                    "birthdate": user[0][4],
                    "loginToken": loginToken
                }
                return Response(json.dumps(user_info, default=str), mimetype="application/json", status=201)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)

    elif request.method == 'DELETE':
        conn = None
        cursor = None
        rows = None
        loginToken = request.json.get("loginToken")
        try:
            conn = mariadb.connect(host=dbcreds.host, port=dbcreds.port,user=dbcreds.user, password=dbcreds.password,database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM user_session WHERE loginToken = ?", [loginToken,])
            conn.commit()
            rows = cursor.rowcount
        except mariadb.ProgrammingError as error:
                print("Programming Error.. ")
                print(error)
        except mariadb.DatabaseError as error:
                print("Database Error...")
                print(error)
        except mariadb.OperationalError as error:
                print("Connection Error...")
                print(error)
        except Exception as error:
                print("This is a general error to be checked! ")
                print(error)        
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows == 1):
                return Response("Successfully Logged out!", mimetype = "text/html", status = 201)
            else:
                return Response("Something went wrong... please try again", mimetype = "text/html", status = 500)

# CREATE USERS, GET THEIR INFORMATION, UPDATE, DELETE A USER
@app.route('/api/users', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def users():
    if request.method == 'GET':
        conn = None
        cursor = None
        rows = None
        users_dict={}
        users_info=[]
        user_Id = request.args.get("id")
        try:
            conn = mariadb.connect(host=dbcreds.host, port=dbcreds.port,user=dbcreds.user, password=dbcreds.password,database=dbcreds.database)
            cursor=conn.cursor()
            if user_Id == None and user_Id == "":
                cursor.execute("SELECT * FROM user WHERE id=?", [user_Id,])
            else:
                cursor.execute("SELECT * FROM user")
            rows = cursor.fetchall()
        except mariadb.ProgrammingError as error:
                print("Programming Error.. ")
                print(error)
        except mariadb.DatabaseError as error:
                print("Database Error...")
                print(error)
        except mariadb.OperationalError as error:
                print("Connection Error...")
                print(error)
        except Exception as error:
                print("This is a general error to be checked! ")
                print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows):
                users=[]
                for row in rows:
                    users_dict={
                        "userId": row[0],
                        "email" : row[1],
                        "username": row[2],
                        "birthdate" : row[4]
                    }
                    users_info.append(users_dict)
                return Response(json.dumps(users_info, default=str), mimetype="application/json", status=200)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)
    elif request.method == 'POST':
        conn = None
        cursor = None
        rows = None
        user = None
        user_info={}
        userEmail = request.json.get("email")
        userName = request.json.get("username")
        userPassword = request.json.get("password")
        userBirthdate = request.json.get("birthdate")
        loginToken = request.json.get("loginToken")

       
        try:
            conn = mariadb.connect(host=dbcreds.host, port=dbcreds.port,user=dbcreds.user, password=dbcreds.password,database=dbcreds.database)
            cursor=conn.cursor()
            cursor.execute("INSERT INTO user(email, username, password, birthdate) VALUES (?,?,?,?)", [userEmail, userName, userPassword, userBirthdate, ])
            user_id = cursor.lastrowid
            rows = cursor.rowcount
            if rows == 1:
                loginToken = get_loginToken(30)
                print(loginToken)
                cursor.execute("INSERT INTO user_session(userId, loginToken) VALUES(?,?)", [user_id, loginToken])
                conn.commit()
                rows = cursor.rowcount
                print(rows)
        except mariadb.ProgrammingError as error:
                print("Programming Error.. ")
                print(error)
        except mariadb.DatabaseError as error:
                print("Database Error...")
                print(error)
        except mariadb.OperationalError as error:
                print("Connection Error...")
                print(error)
        except Exception as error:
                print("This is a general error to be checked! ")
                print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows == 1):
                user_info = {
                    "email": userEmail,
                    "username": userName,
                    "birthdate": userBirthdate,
                    "userId": user_id,
                    "loginToken": loginToken
                }
                return Response(json.dumps(user_info, default=str), mimetype="application/json", status=200)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)
    elif request.method == 'PATCH':
        conn = None
        cursor = None
        rows = None
        user = None
        users_data={}
        userBio = request.json.get("bio")
        loginToken = request.json.get("loginToken")
        try:
            conn = mariadb.connect(host=dbcreds.host, port=dbcreds.port,user=dbcreds.user, password=dbcreds.password,database=dbcreds.database)
            cursor=conn.cursor()
            cursor.execute("SELECT userId FROM user_session WHERE loginToken = ?",[loginToken,])
            user_update = cursor.fetchone()
            print(user_update)
            if user_update:
                if (userEmail != "" and userEmail != None):
                    cursor.execute("UPDATE user SET email = ? WHERE id = ?", [userEmail, user_update[0],])
                if (userName != "" and userName != None):
                    cursor.execute("UPDATE user SET username = ? WHERE id = ?", [userName, user_update[0],])
                if (userPassword != "" and userPassword != None):
                    cursor.execute("UPDATE user SET password = ? WHERE id = ?", [userPassword, user_update[0],])
                if (userBirthdate != "" and userBirthdate != None):
                    cursor.execute("UPDATE user SET birthdate = ? WHERE id = ?", [userBirthdate, user_update[0]],)
                conn.commit()
                rows = cursor.rowcount
                cursor.execute("SELECT * FROM user WHERE id=?", [user_update[0],])
                user = cursor.fetchall()
        except mariadb.ProgrammingError as error:
                print("Programming Error.. ")
                print(error)
        except mariadb.DatabaseError as error:
                print("Database Error...")
                print(error)
        except mariadb.OperationalError as error:
                print("Connection Error...")
                print(error)
        except Exception as error:
                print("This is a general error to be checked! ")
                print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows != None): 
                users_data={
                        "userId": user_update[0],
                        "email" : user[0][1],
                        "username": user[0][2],
                        "birthdate" : user[0][4],
                    } 
                return Response(json.dumps(users_data, default=str), mimetype="application/json", status=200)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500) 
    
    # DELETE A USER
    # JSON DATA (loginToke and password )
          
    elif request.method == 'DELETE':
        conn = None
        cursor = None
        rows = None
        userPassword = request.json.get("password")
        loginToken = request.json.get("loginToken")
        try:
            conn = mariadb.connect(host=dbcreds.host, port=dbcreds.port,user=dbcreds.user, password=dbcreds.password,database=dbcreds.database)
            cursor=conn.cursor()
            cursor.execute("SELECT * FROM user_session WHERE loginToken=?", [loginToken,])
            user = cursor.fetchone()
            print(user)
            if user !=None:
                cursor.execute("DELETE FROM user WHERE id=? AND password=?", [user[0],userPassword, ])            
                rows= cursor.rowcount
                conn.commit()      
        except mariadb.ProgrammingError as error:
                print("Programming Error.. ")
                print(error)
        except mariadb.DatabaseError as error:
                print("Database Error...")
                print(error)
        except mariadb.OperationalError as error:
                print("Connection Error...")
                print(error)
        except Exception as error:
                print("This is a general error to be checked! ")
                print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows == 1):
                return Response("Account deleted!", mimetype = "text/html", status = 204)
            else:
                return Response("Error occured while deleting your account...", mimetype = "text/html", status = 500)
# CREATE MESSAGES, VIEW/CHECK MESSAGES, OR DELETE A MESSAGE
@app.route('/api/message', methods=['GET', 'POST', 'DELETE'])
# JSON DATA (loginToke )

def message():
    if request.method == 'GET':
        conn = None
        cursor = None
        rows = None
        message_info=[]
        message_dict={}
        loginToken = request.args.get("loginToken")
        
        try:
            conn = mariadb.connect(host=dbcreds.host, port=dbcreds.port,user=dbcreds.user, password=dbcreds.password,database=dbcreds.database)
            cursor=conn.cursor()
            cursor.execute("SELECT * FROM user_session WHERE loginToken =?", [loginToken,])
            user=cursor.fetchall()
            print(user)
            user_id = user[0][0]
            
            if user_id != None:
                cursor.execute("SELECT m.id, m.userId, m.createdAt, m.to, m.from , m.subject, m.message FROM message_center m INNER JOIN user u ON m.userId = u.id WHERE u.id=?", [user_id, ])
                rows = cursor.fetchall()
            print (rows)
        except mariadb.ProgrammingError as error:
                print("Programming Error.. ")
                print(error)
        except mariadb.DatabaseError as error:
                print("Database Error...")
                print(error)
        except mariadb.OperationalError as error:
                print("Connection Error...")
                print(error)
        except Exception as error:
                print("This is a general error to be checked! ")
                print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows!= None):
                for row in rows:
                    message_dict={
                        "id": row[0],
                        "userId" : row[1],
                        "createdAt" : row[2],
                        "to": row[3],
                        "from": row[4],
                        "subject": row[5],
                        "message": row[6]
                    }
                    message_info.append(message_dict)
                return Response(json.dumps(message_info, default=str), mimetype="application/json", status=200)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)
    # CREATE A NEW MESSAGE
    # JSON DATA (loginToke, messagecontent and  )

    elif request.method == 'POST':
        conn = None
        cursor = None
        rows = None
        user = None
        createdAt=None
        message_info={}
        loginToken = request.json.get("loginToken")
        message_content = request.json.get("message")
        try:
            conn = mariadb.connect(host=dbcreds.host, port=dbcreds.port,user=dbcreds.user, password=dbcreds.password,database=dbcreds.database)
            cursor=conn.cursor()           
            cursor.execute("SELECT * FROM user_session WHERE loginToken =?", [loginToken,])
            user=cursor.fetchall()
            print(user)
            if user !=None:
                cursor.execute("INSERT INTO message_center(userId, message) VALUES(?,?)", [user[0][0],message_content, ])
                conn.commit()
                rows= cursor.rowcount      
                print (tweetId)
        except mariadb.ProgrammingError as error:
                print("Programming Error.. ")
                print(error)
        except mariadb.DatabaseError as error:
                print("Database Error...")
                print(error)
        except mariadb.OperationalError as error:
                print("Connection Error...")
                print(error)
        except Exception as error:
                print("This is a general error to be checked! ")
                print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows==1):
                message_info={
                    "userId" : user[0][0] ,
                    "content": message_content,
                    "createdAt" :createdAt ,
                    "username": user[0][1],
                    }
                return Response(json.dumps(message_info, default=str), mimetype="application/json", status=200)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)

    # DELETE A MESSAGE
    # JSON DATA (loginToke and messageId )

    elif request.method == 'DELETE':
        conn = None
        cursor = None
        rows = None
        user = None
        loginToken = request.json.get("loginToken")
        messageId = request.json.get("messageId") 
        try:
            conn = mariadb.connect(host=dbcreds.host, port=dbcreds.port,user=dbcreds.user, password=dbcreds.password,database=dbcreds.database)
            cursor=conn.cursor()
            cursor.execute("SELECT * FROM user_session WHERE loginToken=?", [loginToken,])
            user = cursor.fetchone()
            print(user)
            if user !=None:
                print(messageId)
                cursor.execute("DELETE FROM message_center WHERE id=? AND userId=?", [messageId,user[0],])
                conn.commit()
                rows=cursor.rowcount
        except mariadb.ProgrammingError as error:
                print("Programming Error.. ")
                print(error)
        except mariadb.DatabaseError as error:
                print("Database Error...")
                print(error)
        except mariadb.OperationalError as error:
                print("Connection Error...")
                print(error)
        except Exception as error:
                print("This is a general error to be checked! ")
                print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows == 1):           
                return Response("Deleted successfully", mimetype="text/html", status=204)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)



# CREATE AN ENTRY, VIEW/CHECK AN ENTRY, EDIT OR DELETE AN ENTRY
@app.route('/api/entry', methods=['GET', 'POST', 'PATCH','DELETE'])
 # JSON DATA PARAMS (entryId ) (works)
def entry():
    if request.method == 'GET':
        conn = None
        cursor = None
        rows = None
        entry_info=[]
        entry_dict={}
        user_id = request.args.get("userId")
        try:
            conn = mariadb.connect(host=dbcreds.host, port=dbcreds.port,user=dbcreds.user, password=dbcreds.password,database=dbcreds.database)
            cursor=conn.cursor()
            if user_id == None:
                cursor.execute("SELECT * FROM entry e INNER JOIN user u ON e.userId = u.id")
            else:
                cursor.execute("SELECT * FROM entry e INNER JOIN user u ON e.userId = u.id WHERE u.id=?", [user_id, ])
            rows = cursor.fetchall()
            print (rows)
        except mariadb.ProgrammingError as error:
                print("Programming Error.. ")
                print(error)
        except mariadb.DatabaseError as error:
                print("Database Error...")
                print(error)
        except mariadb.OperationalError as error:
                print("Connection Error...")
                print(error)
        except Exception as error:
                print("This is a general error to be checked! ")
                print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows!= None):
                for row in rows:
                    entry_dict={
                        "id": row[0],
                        "userId" : row[1],
                        "childname": row[2],
                        "createdAt" : row[3],
                        "options": row[4],
                        "title": row[5],
                        "description": row[6],
                        "photo": row[7]
                    }
                    entry_info.append(entry_dict)
                return Response(json.dumps(entry_info, default=str), mimetype="application/json", status=200)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)
    # CREATE A NEW ENTRY (works)
    # JSON DATA (loginToke,userId, childname,  options, title, description, photo )

    elif request.method == 'POST':
        conn = None
        cursor = None
        rows = None
        user = None
        createdAt=None
        entry_info={}
        loginToken = request.json.get("loginToken")
        e_childname= request.json.get("childname")
        e_options= request.json.get ("options")
        e_title = request.json.get("title")
        e_description = request.json.get("description")
        e_photo = request.json.get ("photo")

        try:
            conn = mariadb.connect(host=dbcreds.host, port=dbcreds.port,user=dbcreds.user, password=dbcreds.password,database=dbcreds.database)
            cursor=conn.cursor()           
            cursor.execute("SELECT * FROM user_session WHERE loginToken =?", [loginToken,])
            user=cursor.fetchall()
            print(user)
            if user !=None:
                cursor.execute("INSERT INTO entry(userId, childname, options, title, description, photo ) VALUES(?,?,?,?,?,?)", [user[0][0],e_childname, e_options, e_title, e_description, e_photo ])
                conn.commit()
                rows= cursor.rowcount      
        except mariadb.ProgrammingError as error:
                print("Programming Error.. ")
                print(error)
        except mariadb.DatabaseError as error:
                print("Database Error...")
                print(error)
        except mariadb.OperationalError as error:
                print("Connection Error...")
                print(error)
        except Exception as error:
                print("This is a general error to be checked! ")
                print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows==1):
                entry_info={
                    "userId" : user[0][0] ,
                    "childname": e_childname,
                    "options": e_options,
                    "title" : e_title,
                    "description" : e_description,
                    "photo": e_photo

                    }
                return Response(json.dumps(entry_info, default=str), mimetype="application/json", status=200)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)
# UPDATE AN ENTRY (works)
# JSON DATA (loginToke, entryId, title, description, photo )
    elif request.method == 'PATCH':
        conn = None
        cursor = None
        rows = None
        updated_tweet = None
        user=None
        updated_entry={}
        loginToken = request.json.get("loginToken")
        entryId = request.json.get("entryId")
        e_title = request.json.get("title")
        e_description = request.json.get("description")
        e_photo = request.json.get("photo")
        try:
            conn = mariadb.connect(host=dbcreds.host, port=dbcreds.port,user=dbcreds.user, password=dbcreds.password,database=dbcreds.database)
            cursor=conn.cursor()

            cursor.execute("SELECT * FROM user_session WHERE loginToken =? ", [loginToken,])
            user=cursor.fetchall()

            cursor.execute("UPDATE entry SET title = ?, description=?, photo=? WHERE id=? AND userId=?", [e_title,e_description,e_photo, entryId, user[0][0] ])
            conn.commit()
            rows = cursor.rowcount
        except mariadb.ProgrammingError as error:
                print("Programming Error.. ")
                print(error)
        except mariadb.DatabaseError as error:
                print("Database Error...")
                print(error)
        except mariadb.OperationalError as error:
                print("Connection Error...")
                print(error)
        except Exception as error:
                print("This is a general error to be checked! ")
                print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows == 1):
                updated_entry={
                    "title": e_title,
                    "description": e_description,
                    "photo": e_photo
                    }
                return Response(json.dumps(updated_entry, default=str), mimetype="application/json", status=200)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)
    # DELETE AN ENTRY
    # JSON DATA (loginToke, entryId )
    elif request.method == 'DELETE':
        conn = None
        cursor = None
        rows = None
        user = None
        loginToken = request.json.get("loginToken")
        entryId = request.json.get("entryId")
        try:
            conn = mariadb.connect(host=dbcreds.host, port=dbcreds.port,user=dbcreds.user, password=dbcreds.password,database=dbcreds.database)
            cursor=conn.cursor()
            cursor.execute("SELECT * FROM user_session WHERE loginToken=?", [loginToken,])
            user = cursor.fetchone()
            print(user)
            if user !=None:
                cursor.execute("DELETE FROM entry WHERE id=? AND userId=?", [entryId,user[0],])
                conn.commit()
                rows=cursor.rowcount
        except mariadb.ProgrammingError as error:
                print("Programming Error.. ")
                print(error)
        except mariadb.DatabaseError as error:
                print("Database Error...")
                print(error)
        except mariadb.OperationalError as error:
                print("Connection Error...")
                print(error)
        except Exception as error:
                print("This is a general error to be checked! ")
                print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows == 1):           
                return Response("Deleted successfully", mimetype="text/html", status=204)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)


# SHOW, CREATE, EDIT AND DELETE AN ACTIVITY
@app.route('/api/activity', methods=['GET', 'POST', 'PATCH','DELETE'])

# JSON DATA AS PARAMS(userId )
def activity():
    if request.method == 'GET':
        conn = None
        cursor = None
        rows = None
        report_info=[]
        report_dict={}
        user_id = request.args.get("userId")
        try:
            conn = mariadb.connect(host=dbcreds.host, port=dbcreds.port,user=dbcreds.user, password=dbcreds.password,database=dbcreds.database)
            cursor=conn.cursor()
            if user_id == None:
                cursor.execute("SELECT * FROM activity a INNER JOIN user u ON e.userId = u.id")
            else:
                cursor.execute("SELECT * FROM activity a INNER JOIN user u ON a.userId = u.id WHERE u.id=?", [user_id, ])
            rows = cursor.fetchall()
            print (rows)
        except mariadb.ProgrammingError as error:
                print("Programming Error.. ")
                print(error)
        except mariadb.DatabaseError as error:
                print("Database Error...")
                print(error)
        except mariadb.OperationalError as error:
                print("Connection Error...")
                print(error)
        except Exception as error:
                print("This is a general error to be checked! ")
                print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows!= None):
                for row in rows:
                    report_dict={
                        "reportId": row[0], 
                        "userId" : row[1],
                        "activityType": row[2],
                        "activityName": row[3],
                        "createdAt" : row[4],
                        "description": row[5]
                    }
                    report_info.append(report_dict)
                return Response(json.dumps(report_info, default=str), mimetype="application/json", status=200)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)
    # CREATE A NEW ACTIVITY
    # JSON DATA AS PARAMS(loginToken, activityType, activityName, description )

    elif request.method == 'POST':
        conn = None
        cursor = None
        rows = None
        user = None
        activityId=None
        createdAt=None
        activity_info={}
        loginToken = request.json.get("loginToken")
        activity_type= request.json.get("activityType")
        activity_name = request.json.get("activityName")
        activity_description = request.json.get("description")
        try:
            conn = mariadb.connect(host=dbcreds.host, port=dbcreds.port,user=dbcreds.user, password=dbcreds.password,database=dbcreds.database)
            cursor=conn.cursor()           
            cursor.execute("SELECT * FROM user_session WHERE loginToken =?", [loginToken,])
            user=cursor.fetchall()
            print(user)
            if user !=None:
                cursor.execute("INSERT INTO activity(userId, activityType, activityName, description) VALUES(?,?,?,?)", [user[0][0],activity_type,activity_name,activity_description ])
                conn.commit()
                rows= cursor.rowcount      
                print (activityId)
        except mariadb.ProgrammingError as error:
                print("Programming Error.. ")
                print(error)
        except mariadb.DatabaseError as error:
                print("Database Error...")
                print(error)
        except mariadb.OperationalError as error:
                print("Connection Error...")
                print(error)
        except Exception as error:
                print("This is a general error to be checked! ")
                print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows==1):
                activity_info={
                    "userId" : user[0][0] ,
                    "activityType": activity_type,
                    "activityName":activity_name,
                    "createdAt" :createdAt ,
                    "description": activity_description
                    }
                return Response(json.dumps(activity_info, default=str), mimetype="application/json", status=200)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)

# UPDATE AN ACTIVITY (works)
# JSON DATA AS PARAMS(loginToken, activityId, activityType, activityName, description )

    elif request.method == 'PATCH':
        conn = None
        cursor = None
        rows = None
        user=None
        updated_activity={}
        loginToken = request.json.get("loginToken")
        activityId = request.json.get("activityId")
        activity_type= request.json.get("activityType")
        activity_name = request.json.get("activityName")
        activity_description = request.json.get("description")
        try:
            conn = mariadb.connect(host=dbcreds.host, port=dbcreds.port,user=dbcreds.user, password=dbcreds.password,database=dbcreds.database)
            cursor=conn.cursor()

            cursor.execute("SELECT * FROM user_session WHERE loginToken =? ", [loginToken,])
            user=cursor.fetchall()

            cursor.execute("UPDATE activity SET  activityType= ?, activityName=?, description=? WHERE id=? AND userId=?", [activity_type,activity_name,activity_description,activityId,user[0][0] ])
            conn.commit()
            rows = cursor.rowcount
        except mariadb.ProgrammingError as error:
                print("Programming Error.. ")
                print(error)
        except mariadb.DatabaseError as error:
                print("Database Error...")
                print(error)
        except mariadb.OperationalError as error:
                print("Connection Error...")
                print(error)
        except Exception as error:
                print("This is a general error to be checked! ")
                print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows == 1):
                updated_activity={
                    "activityType": activity_type,
                    "activityName": activity_name,
                    "description": activity_description,
                    }
              
                return Response(json.dumps(updated_activity, default=str), mimetype="application/json", status=200)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)
    # JSON DATA (loginToke, activityId )
    elif request.method == 'DELETE':
        conn = None
        cursor = None
        rows = None
        user = None
        loginToken = request.json.get("loginToken")
        activityId = request.json.get("activityId")
        try:
            conn = mariadb.connect(host=dbcreds.host, port=dbcreds.port,user=dbcreds.user, password=dbcreds.password,database=dbcreds.database)
            cursor=conn.cursor()
            cursor.execute("SELECT * FROM user_session WHERE loginToken=?", [loginToken,])
            user = cursor.fetchone()
            print(user)
            if user !=None:
                cursor.execute("DELETE FROM activity WHERE id=? AND userId=?", [activityId,user[0],])
                conn.commit()
                rows=cursor.rowcount
        except mariadb.ProgrammingError as error:
                print("Programming Error.. ")
                print(error)
        except mariadb.DatabaseError as error:
                print("Database Error...")
                print(error)
        except mariadb.OperationalError as error:
                print("Connection Error...")
                print(error)
        except Exception as error:
                print("This is a general error to be checked! ")
                print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows == 1):           
                return Response("Deleted successfully", mimetype="text/html", status=204)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)

# CREATE A REPORT, VIEW/CHECK  A REPORT, EDIT OR DELETE  A REPORT
@app.route('/api/report', methods=['GET', 'POST', 'PATCH','DELETE'])
# JSON DATA AS PARAMS(userId )
def report():
    if request.method == 'GET':
        conn = None
        cursor = None
        rows = None
        createdAt = None
        report_info=[]
        report_dict={}
        user_id = request.args.get("userId")
        try:
            conn = mariadb.connect(host=dbcreds.host, port=dbcreds.port,user=dbcreds.user, password=dbcreds.password,database=dbcreds.database)
            cursor=conn.cursor()
            if user_id == None:
                cursor.execute("SELECT * FROM report r INNER JOIN user u ON r.userId = u.id")
            else:
                cursor.execute("SELECT * FROM report r INNER JOIN user u ON r.userId = u.id WHERE u.id=?", [user_id, ])
            rows = cursor.fetchall()
            print (rows)
        except mariadb.ProgrammingError as error:
                print("Programming Error.. ")
                print(error)
        except mariadb.DatabaseError as error:
                print("Database Error...")
                print(error)
        except mariadb.OperationalError as error:
                print("Connection Error...")
                print(error)
        except Exception as error:
                print("This is a general error to be checked! ")
                print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows!= None):
                for row in rows:
                    report_dict={
                        "reportId": row[0], 
                        "userId" : row[1],
                        "createdAt" : row[2],
                        "classroom": row[3],
                        "actions": row[4],

                    }
                    report_info.append(report_dict)
                return Response(json.dumps(report_info, default=str), mimetype="application/json", status=200)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)
    # CREATE A NEW ACTIVITY
    # JSON DATA AS PARAMS(loginToken, classroom, actions )

    elif request.method == 'POST':
        conn = None
        cursor = None
        rows = None
        user = None
        reportId=None
        createdAt=None
        report_info={}
        loginToken = request.json.get("loginToken")
        classroom_report = request.json.get("classroom")
        classroom_action = request.json.get("actions")
        try:
            conn = mariadb.connect(host=dbcreds.host, port=dbcreds.port,user=dbcreds.user, password=dbcreds.password,database=dbcreds.database)
            cursor=conn.cursor()           
            cursor.execute("SELECT * FROM user_session WHERE loginToken =?", [loginToken,])
            user=cursor.fetchall()
            print(user)
            if user !=None:
                cursor.execute("INSERT INTO report(userId, classroom, actions) VALUES(?,?,?)", [user[0][0],classroom_report,classroom_action, ])
                conn.commit()
                rows= cursor.rowcount      
                print (reportId)
        except mariadb.ProgrammingError as error:
                print("Programming Error.. ")
                print(error)
        except mariadb.DatabaseError as error:
                print("Database Error...")
                print(error)
        except mariadb.OperationalError as error:
                print("Connection Error...")
                print(error)
        except Exception as error:
                print("This is a general error to be checked! ")
                print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows==1):
                report_info={
                    "userId" : user[0][0] ,
                    "reportId": reportId,
                    "createdAt" :createdAt ,
                    "classroom":classroom_report ,
                    "actions":classroom_action,
                    }
                return Response(json.dumps(report_info, default=str), mimetype="application/json", status=200)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)

# UPDATE AN ACTIVITY (works)
# JSON DATA AS PARAMS(loginToken, reportId, classroom, actions )

    elif request.method == 'PATCH':
        conn = None
        cursor = None
        rows = None
        user=None
        updated_report={}
        loginToken = request.json.get("loginToken")
        reportId = request.json.get("reportId")
        classroom_report = request.json.get("classroom")
        classroom_action = request.json.get("actions")
        try:
            conn = mariadb.connect(host=dbcreds.host, port=dbcreds.port,user=dbcreds.user, password=dbcreds.password,database=dbcreds.database)
            cursor=conn.cursor()

            cursor.execute("SELECT * FROM user_session WHERE loginToken =? ", [loginToken,])
            user=cursor.fetchall()

            cursor.execute("UPDATE report SET  classroom= ?, actions=? WHERE id=? AND userId=?", [classroom_report,classroom_action,reportId,user[0][0] ])
            conn.commit()
            rows = cursor.rowcount
        except mariadb.ProgrammingError as error:
                print("Programming Error.. ")
                print(error)
        except mariadb.DatabaseError as error:
                print("Database Error...")
                print(error)
        except mariadb.OperationalError as error:
                print("Connection Error...")
                print(error)
        except Exception as error:
                print("This is a general error to be checked! ")
                print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows == 1):
                updated_report={
                    "classroom":classroom_report ,
                    "actions":classroom_action,
                    }
              
                return Response(json.dumps(updated_report, default=str), mimetype="application/json", status=200)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)
    # JSON DATA (loginToke, reportId )
    elif request.method == 'DELETE':
        conn = None
        cursor = None
        rows = None
        user = None
        loginToken = request.json.get("loginToken")
        reportId = request.json.get("reportId")
        try:
            conn = mariadb.connect(host=dbcreds.host, port=dbcreds.port,user=dbcreds.user, password=dbcreds.password,database=dbcreds.database)
            cursor=conn.cursor()
            cursor.execute("SELECT * FROM user_session WHERE loginToken=?", [loginToken,])
            user = cursor.fetchone()
            print(user)
            if user !=None:
                cursor.execute("DELETE FROM report WHERE id=? AND userId=?", [reportId,user[0],])
                conn.commit()
                rows=cursor.rowcount
        except mariadb.ProgrammingError as error:
                print("Programming Error.. ")
                print(error)
        except mariadb.DatabaseError as error:
                print("Database Error...")
                print(error)
        except mariadb.OperationalError as error:
                print("Connection Error...")
                print(error)
        except Exception as error:
                print("This is a general error to be checked! ")
                print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows == 1):           
                return Response("Deleted successfully", mimetype="text/html", status=204)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)