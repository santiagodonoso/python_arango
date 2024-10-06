from bottle import request, response, template
import re
import pathlib
import requests
from icecream import ic

############################################################
COOKIE_SECRET = "a09ac1f6-dbc7-4ffdg4567768c1-bf3e1e15842a51dd6!#¤¤564564564562e5936b-9c65-4e4a9a5f-d3d83fe883b1"


##############################
def db(aql_query):
    arango_url = "http://arangodb:8529"
    db_name = "company"
    username = "user"
    password = "password"
    auth = (username, password)
    query_url = f'{arango_url}/_db/{db_name}/_api/cursor'
    response = requests.post(query_url, auth=auth, json=aql_query)
    # ic(response.json())
    return response.json()

##############################
def handle_exception(ex):
    ic("#"*30)
    ic(ex)
    try:
        if len(ex.args) >= 2: # own created exception
            response.status = ex.args[1]
            toast = template("__toast", message="System under maintenance. Please try again")
            return f"<template mix-target='#toast' mix-bottom>{ex.args[0]}</template>"        
        else: # python exception, not under our control
            response.status = 500
            toast = template("__toast", message="System under maintenance. Please try again")
            return f"<template mix-target='#toast' mix-bottom>{toast}</template>"
    except Exception as e:
        ic("#"*50)
        ic(e)
        toast = template("__toast", message="System crashed")
        return f"<template mix-target='#toast' mix-bottom>{toast}</template>"



##############################
def disable_cache():
    response.add_header("Cache-Control", "no-cache, no-store, must-revalidate, max-age=0")
    response.add_header("Pragma", "no-cache")
    response.add_header("Expires", 0)  

##############################
UUID4_REGEX = "^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-4[a-fA-F0-9]{3}-[89abAB][a-fA-F0-9]{3}-[a-fA-F0-9]{12}$"
def validate_user_pk(user_pk):
    error = f"user id invalid"
    user_pk = user_pk.strip()
    if not re.match(UUID4_REGEX, user_pk): raise Exception(error, 400)
    return user_pk

##############################
EMAIL_REGEX = "^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$"
def validate_user_email():
    error = "email invalid"
    user_email = request.forms.get("user_email", "")
    user_email = user_email.strip()
    if not re.match(EMAIL_REGEX, user_email): raise Exception(error, 400)
    return user_email


##############################
USER_PASSWORD_MIN = 8
USER_PASSWORD_MAX = 50
USER_PASSWORD_REGEX = f"^.{{{USER_PASSWORD_MIN},{USER_PASSWORD_MAX}}}$"
def validate_user_password():
    error = f"password {USER_PASSWORD_MIN} to {USER_PASSWORD_MAX} characters"
    user_password = request.forms.get("user_password", "").strip()
    if not re.match(USER_PASSWORD_REGEX, user_password): raise Exception(error, 400)
    return user_password

##############################
USER_NAME_MIN = 2
USER_NAME_MAX = 20
USER_NAME_REGEX = f"^.{{{USER_NAME_MIN},{USER_NAME_MAX}}}$"
def validate_user_name():
    error = f"name {USER_NAME_MIN} to {USER_NAME_MAX} characters"
    user_name = request.forms.get("user_name", "").strip()
    if not re.match(USER_NAME_REGEX, user_name): raise Exception(error, 400)
    return user_name


##############################
USER_LAST_NAME_MIN = 2
USER_LAST_NAME_MAX = 20
USER_LAST_NAME_REGEX = f"^.{{{USER_LAST_NAME_MIN},{USER_LAST_NAME_MAX}}}$"
def validate_user_last_name():
    error = f"last name {USER_LAST_NAME_MIN} to {USER_LAST_NAME_MAX} characters"
    user_last_name = request.forms.get("user_last_name", "").strip()
    if not re.match(USER_LAST_NAME_REGEX, user_last_name): raise Exception(error, 400)
    return user_last_name


##############################
USER_USERNAME_MIN = 2
USER_USERNAME_MAX = 20
USER_USERNAME_REGEX = f"^.{{{USER_USERNAME_MIN},{USER_USERNAME_MAX}}}$"
def validate_user_username():
    error = f"username {USER_USERNAME_MIN} to {USER_USERNAME_MAX} characters"
    user_username = request.forms.get("user_username", "").strip()
    if not re.match(USER_USERNAME_REGEX, user_username): raise Exception(error, 400)
    return user_username

##############################
REGEX_PAGE_NUMBER = f"^([1-9][0-9]*)$"
def validate_page_number(page_number):
    error = f"page_number invalid"
    if not re.match(REGEX_PAGE_NUMBER, page_number): raise Exception(error, 400)
    return int(page_number)

##############################
REGEX_KEY = f"^([1-9][0-9]*)$"
def validate_key(key):
    error = f"key invalid"
    if not re.match(REGEX_KEY, key): raise Exception(error, 400)
    return key















