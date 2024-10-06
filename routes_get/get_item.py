from bottle import get, response, template
import x
from icecream import ic

##############################
@get("/items/<item_key>")
def _(item_key):
    try:
        key = x.validate_key(item_key)
        ic(key)
        q = {
            "query": f"RETURN DOCUMENT(@collection, @key)",
            "bindVars":{
                "collection":"items",
                "key":key
            } 
        }
        db_response = x.db(q)
        # ic(db_response)
        ic(db_response["result"][0])
        if db_response["code"] != 201: raise Exception("ups", 500)
        html = template("__item_details", item=db_response["result"][0])       
        return f"""
            <template mix-target="#item_details">
                {html}
            </template>
        """
    except Exception as ex:
        # ic(ex)
        response.status = 303
        response.headers["location"] = "/"
        return ""
    finally:
        pass