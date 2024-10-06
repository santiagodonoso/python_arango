import requests

# Define the base URL of the API
BASE_URL = "http://127.0.0.1"  # Replace with your API base URL


def ok(message): print(f"\033[32m{message}\033[0m")
def error(message): print(f"\033[31m{message}\033[0m")

def test(rules):
    print("#"*30)
    print(rules["name"])
    response = requests.get(f"{BASE_URL}{rules['url']}")
    # Check if the response status code is 200 OK
    if rules.get("status_code"):
        message = "GET /items"
        if response.status_code == 200:
            ok(message)
        else:
            error(message)
    
    # Check if the response is a JSON object
    if rules.get("is_json"):
        message = "Content-Type is JSON"
        if response.headers.get('Content-Type') == 'application/json; charset=utf-8':
            print(response.headers.get('Content-Type'))
            ok(message)
        else:
            error(message)

    if rules.get("contains"):
        message = f"Response contains {rules.get("contains")}"
        if rules.get("contains") in response.text:
            ok(message)
        else:
            error(message)    


    data = response.text
    print(data)

def test_get_items():
    
    rules = {
        "name":"Check main site",
        "url":"/",
        "status_code" : 200,
        "is_json": True,
        "contains": "x"
    }
    test(rules)
    



##############################
def test_post_item():
    """Test POST request to create an item."""
    new_item = {'name': 'New Item'}
    response = requests.post(f"{BASE_URL}/items", json=new_item)
    
    # Check if the response status code is 201 Created
    if response.status_code == 201:
        print("POST /items: Passed")
    else:
        print(f"POST /items: Failed (Status Code: {response.status_code})")

    # Check if the response returns the created item
    created_item = response.json()
    if 'id' in created_item:
        print("Created item contains 'id': Passed")
    else:
        print("Created item does not contain 'id': Failed")

if __name__ == '__main__':
    test_get_items()
    # test_post_item()
