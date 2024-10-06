from bottle import get, response, template
import x
from icecream import ic

##############################
@get("/")
def _():
    try:
        q = {
            "query": f"FOR item IN items LIMIT 4 RETURN item" 
        }
        db_response = x.db(q)
        if db_response["code"] != 201:
            raise Exception("ups", 500)
        # ic(db_response)
        return template("index", items=db_response["result"])       
    except Exception as ex:
        ic("#"*30)
        ic(ex)
        try:
            if len(ex.args) >= 2: # own created exception
                response.status = ex.args[1]
                return {"error":ex.args[0]}
            else: # python exception, not under our control
                error = "System under maintenance. Please try again"
                response.status = 500
                return {"error":f"{error}"}
        except Exception as e:
            ic("#"*50)
            ic(e)
            toast = template("__toast", message="System crashed")
            return f"<template mix-target='#toast' mix-bottom>{toast}</template>"
    finally:
        pass