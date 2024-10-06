from bottle import default_app, get, post, request, response, run, template, static_file, redirect
from icecream import ic
import os
import x
import uuid
import time
import json


@get("/images/<image_name>")
def _(image_name):
    return static_file(image_name, root="images")

##############################
@get("/mixhtml.js")
def _():
    return static_file("mixhtml.js", root="js")

##############################
@get("/mojocss.js")
def _():
    return static_file("mojocss.js", root="js")

##############################
@get("/mixhtml.css")
def _():
    return static_file("mixhtml.css", root="css")

##############################
@get("/logo.jpg")
def _():
    return static_file("logo.jpg", root="images")


##############################
import routes_get.get_index
import routes_get.get_more_items
import routes_get.get_item




##############################
@post("/test")
def _():
    try:
        # TODO: validate
        item_pk = str(uuid.uuid4())
        item = {"id":item_pk, "name":"A"}
        db, cursor = x.db()
        db.start_transaction()
        cursor.execute("INSERTs INTO items VALUES(%s, %s)", (item_pk, json.dumps(item)))
        db.commit()
        # cursor.rowcount
        return "test"
    except Exception as ex:
        print("#"*30)
        if "db" in locals(): db.rollback()
        ic(ex)
        try:
            if len(ex.args) >= 2: # own created exception
                response.status = ex.args[1]
                return {"error":ex.args[0]}
            else: # python exception, not under our control
                error = "System under maintenance. Please try again"
                response.status = 500
                return {"error":f"{error}"}
        except Exception as e: # Exception from unknown source like database
            ic(e)
            error = "Server maintanance"
            response.status = 500
            return {"error":f"{error}"}            
    finally:        
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()



##############################
@get("/login")
def _():
    try:
        x.disable_cache()
        user = request.get_cookie("user", secret=x.COOKIE_SECRET)
        if user:
            response.status = 303
            response.set_header("location", "/admin")
            return
        return template("login.html", user=user)
    except Exception as ex:
        print(ex)
        if len(ex.args) >= 2: # own created exception
            response.status = ex.args[1]
            return {"error":ex.args[0]}
        else: # python exception, not under our control
            error = "System under maintenance. Please try again"
            response.status = 500
            return {"error":f"{error}"}
    finally:
        pass


##############################
@get("/profile")
def _():
    try:
        x.disable_cache()
        user = request.get_cookie("user", secret=x.COOKIE_SECRET)          
        if user is None or user.get("role", "") != "partner": # not a valid cookie. Someone tempered with it
            response.status = 303
            response.set_header("location", "/login")
            return           
        return template("profile.html", user_name=user["name"], user=user)
    except Exception as ex:
        print(ex)
        if len(ex.args) >= 2: # own created exception
            response.status = ex.args[1]
            return {"error":ex.args[0]}
        else: # python exception, not under our control
            error = "System under maintenance. Please try again"
            response.status = 500
            return {"error":f"{error}"}
    finally:
        pass


##############################
@get("/admin")
def _():
    try:
        x.disable_cache()
        user = request.get_cookie("user", secret=x.COOKIE_SECRET)
        if user is None: # not a valid cookie. Someone tempered with it
            response.status = 303
            response.set_header("location", "/login")
            return   
        db, cursor = x.db()
        # cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        return template("admin.html", user_name=user["user_name"], user=user, users=users)
    except Exception as ex:
        ic(ex)
        if len(ex.args) >= 2: # own created exception
            response.status = ex.args[1]
            return {"error":ex.args[0]}
        else: # python exception, not under our control
            error = "System under maintenance. Please try again"
            response.status = 500
            return {"error":f"{error}"}
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

##############################
@get("/signup")
def _():
    try:
        user = request.get_cookie("user", secret=x.COOKIE_SECRET)
        return template("signup.html", user=user)
    except Exception as ex:
        if len(ex.args) >= 2: # own created exception
            response.status = ex.args[1]
            return {"error":ex.args[0]}
        else: # python exception, not under our control
            error = "System under maintenance. Please try again"
            response.status = 500
            return {"error":f"{error}"}
    finally:
        pass


##############################
@get("/logout")
def _():
    response.delete_cookie("user")
    return redirect("/login")


##############################
@post("/login")
def _():
    try:

        user_email = x.validate_user_email()
        user_password = x.validate_user_password()

        db, cursor = x.db()
        # cursor = db.cursor(dictionary=True)
        cursor.execute("""
                        SELECT user_pk, user_name, user_last_name, user_email FROM users 
                        WHERE user_email = %s AND 
                        user_password= %s LIMIT 1
                       """, (user_email, user_password))
        user = cursor.fetchone()
        ic(user)
        if not user:
            toast = template("__toast", message="Invalid credentials")
            return toast
        response.set_cookie("user", user, secret=x.COOKIE_SECRET)
        return "<template mix-redirect='/admin'></template>"
    except Exception as ex:
        print(ex)
        if "db" in locals():db.rollback()
        if len(ex.args) >= 2: # own created exception
            response.status = ex.args[1]
            return {"error":ex.args[0]}
        else: # python exception, not under our control
            error = "System under maintenance. Please try again"
            response.status = 500
            return {"error":f"{error}"}
    finally:
        if "db" in locals(): db.close()


##############################
@post("/signup")
def _():
    try:
        user = {
            "user_pk": str(uuid.uuid4()),
            "user_username": x.validate_user_username(),
            "user_name" : x.validate_user_name(),
            "user_last_name" : x.validate_user_last_name(),
            "user_email" : x.validate_user_email(),
            "user_password" : x.validate_user_password(),
            "user_blocked_at" : 0,
            "user_updated_at" : 0,
            "user_deleted_at" : 0,
        }


        db = x.db()
        # binding variables by value, # bind parameters
        q = db.execute("""
                       INSERT INTO users 
                       VALUES(:user_pk, :user_username, :user_name, :user_last_name, :user_email,:user_password, 
                       :user_blocked_at, :user_updated_at, :user_deleted_at)""", user)

        # q = db.execute("INSERT INTO users VALUES(?,?,?,?,?)",(
        #     user_pk, user_name, user_last_name, user_email, user_password
        # ))
        db.commit()
        # toast = template("__toast.html", message="SUCCESS")
        return "<template mix-redirect='/login'></template>"
    except Exception as ex:
        print(ex)
        if "db" in locals(): db.rollback()
        if len(ex.args) >= 2: # own created exception
            response.status = ex.args[1]            
            toast = template("__toast.html", message=ex.args[0])
            return toast
        else: # python exception, not under our control. The exception will always have an error message in ex.args[0]
            if "users.user_username" in ex.args[0]: # UNIQUE constraint failed: users.user_email
                response.status = 409 # conflict
                toast = template("__toast", message="Username not available")
                return f"<template mix-target='#toast' mix-bottom>{toast}</template>"
            if "users.user_email" in ex.args[0]: # UNIQUE constraint failed: users.user_email
                response.status = 409 # conflict
                toast = template("__toast", message="Email not available")
                return f"<template mix-target='#toast' mix-bottom>{toast}</template>"
            response.status = 500
            toast = template("__toast", message="System under maintenance. Please try again later")
            return f"<template mix-target='#toast' mix-bottom>{toast}</template>"
    finally:
        if "db" in locals(): db.close()


##############################
@get("/transaction")
def _():
    try:
        db = x.db()
        q = db.execute("INSERT INTO users VALUES(?,?)",("1","A"))
        db.commit()
    except Exception as ex:
        db.rollback()
        if len(ex.args) >= 2: # own created exception
            response.status = ex.args[1]
            return {"error":ex.args[0]}
        else: # python exception, not under our control
            error = "System under maintenance. Please try again"
            response.status = 500
            return {"error":f"{error}"}
    finally:
        if "db" in locals(): db.close()

##############################
@get("/users/delete/<user_pk>")
def _(user_pk):
    try:
        # TODO: Validate the uuid4
        user = {
            "user_pk" : x.validate_user_pk(user_pk),
            "user_deleted_at": int(time.time())
        }
        db, cursor = x.db()
        cursor.execute("""UPDATE users SET user_deleted_at = %s WHERE user_pk = %s""", 
                       (user["user_deleted_at"], user["user_pk"]))
        if cursor.rowcount == 0: # UPDATE DELETE INSERT
            raise Exception("User could not be deleted", 404)        
        db.commit()
        toast = template("__toast", message = "user deleted")
        return f"""
                <template mix-target='#u{user_pk}' mix-replace></template>
                <template mix-target="#toast" mix-bottom>
                    {toast}
                </template>                
            """
    except Exception as ex:
        print(ex)
        if "db" in locals():db.rollback()
        if len(ex.args) >= 2: # own created exception
            response.status = ex.args[1]
            toast = template("__toast", message = ex.args[0])
            return f"""
                    <template mix-target="#toast" mix-bottom>
                        {toast}
                    </template>
                    """
        else: # python exception, not under our control
            error = "System under maintenance. Please try again"
            response.status = 500
            return {"error":f"{error}"}
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

##############################
@get("/users/block/<user_pk>")
def _(user_pk):
    try:
        print(user_pk)
        
        user = {
            "user_pk" : x.validate_user_pk(user_pk),
            "user_blocked_at" : int(time.time())
        }

        db, cursor = x.db()
        cursor.execute("""UPDATE users SET user_blocked_at = %s
                       WHERE user_pk = %s AND user_blocked_at = 0""", (user["user_blocked_at"], user["user_pk"]))
        if cursor.rowcount == 0: # UPDATE DELETE INSERT
            raise Exception("User could not be blocked", 404)
        db.commit()
        btn_unblock = template("___btn_unblock_user.html", user=user)
        toast = template("__toast.html", message="User blocked")
        return f"""
                <template 
                mix-target='#block-{user_pk}' 
                mix-replace>
                    {btn_unblock}
                </template>
                <template mix-target="#toast" mix-bottom>
                    {toast}
                </template>
                """
    except Exception as ex:
        print(ex)
        if "db" in locals():db.rollback()
        if len(ex.args) >= 2: # own created exception
            response.status = ex.args[1]
            toast = template("__toast", message = ex.args[0])
            return f"""
                    <template mix-target="#toast" mix-bottom>
                        {toast}
                    </template>
                    """
        else: # python exception, not under our control
            error = "System under maintenance. Please try again"
            response.status = 500
            return {"error":f"{error}"}
    finally:
        if "db" in locals(): db.close()



##############################
@get("/users/unblock/<user_pk>")
def _(user_pk):
    try:
        print(user_pk)
        user = {
            "user_pk" : x.validate_user_pk(user_pk)
        }
        db, cursor = x.db()
        cursor.execute("UPDATE users SET user_blocked_at = 0 WHERE user_pk = %s AND user_blocked_at != 0", (user["user_pk"],))
        if cursor.rowcount == 0:
            raise Exception("User could not be blocked", 404)
        db.commit()
        btn_block = template("___btn_block_user.html", user=user)
        toast = template("__toast.html", message="User unblocked")
        return f"""
                <template 
                mix-target='#unblock-{user_pk}' 
                mix-replace>
                    {btn_block}
                </template>
                <template mix-target="#toast" mix-bottom>
                    {toast}
                </template>
                """
    except Exception as ex:
        print("#"*1000)
        print(ex)

        try:
            if "db" in locals():db.rollback()
            if len(ex.args) >= 2: # own created exception
                response.status = ex.args[1]
                return {"error":ex.args[0]}
            else: # python exception, not under our control
                error = "System under maintenance. Please try again"
                response.status = 500
                return {"error":f"{error}"}
        except Exception as e:
            print("#"*50)
            print(e)
            toast = template("__toast", message="System crashed")
            return f"<template mix-target='#toast' mix-bottom>{toast}</template>"
        
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()







application = default_app()
##############################
# if "PYTHONANYWHERE_DOMAIN" in os.environ:
#     application = default_app()
# else:
#     ic("Server listening...")
#     run(host="0.0.0.0", port=80, debug=True, reloader=True, interval=0.5)

##############################

