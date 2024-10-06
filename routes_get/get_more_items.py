from bottle import get, template, response
import x
from icecream import ic

@get("/page/<page_number>")
def _(page_number):
    try:
        # TODO: Validate page_number
        page_number = x.validate_page_number(page_number)
        items_per_page = 4
        total_items_with_hanging = items_per_page + 1
        start = (page_number - 1) * items_per_page
        q = {
            "query":"FOR item IN items LIMIT @start, @items_per_page RETURN item",
            "bindVars":{
                "start":start,
                "items_per_page":total_items_with_hanging
            }
        }
        db_response = x.db(q)
        if db_response["code"] != 201:
            raise Exception(db_response["errorMessage"], 500)
        items = db_response["result"]        
        html = "" # Server side rendering
        for item in items[:4]:
            html_item = template("__item", item=item)
            html = html + html_item
        ic(html)
        new_button = template("___btn_get_more_items.html", next_page=3)
        if len(items) <= items_per_page:
            new_button = "<div>No more</div>"

        return f"""
            <template mix-target="#items" mix-bottom>
                {html}
            </template>
            <template mix-target="#btn_next_page" mix-replace></template>            
            <template mix-target="#items" mix-bottom>
                {new_button}
            </template>
        """
    except Exception as ex:
        return x.handle_exception(ex)
    finally:
        pass

