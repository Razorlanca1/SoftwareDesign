import requests, json

cookies = 0
user_id = 0

def check_auth():
    global cookies

    try:
        ans = []
        ans.append(requests.get("http://127.0.0.3:8002/v1/tasks").status_code)
        ans.append(requests.get("http://127.0.0.3:8002/v1/task/1").status_code)
        ans.append(requests.post("http://127.0.0.3:8002/v1/add_task", params={"name": "1", "difficult": 1, "description": "1", "user_id": "1"}).status_code)
        ans.append(requests.delete("http://127.0.0.3:8002/v1/delete_task/1").status_code)
        ans.append(requests.get("http://127.0.0.3:8002/v2/users").status_code)
        ans.append(requests.get("http://127.0.0.3:8002/v2/user/1").status_code)
        resp = requests.get("http://127.0.0.3:8002/auth")
        cookies = resp.cookies
        if resp.status_code != 200 or ans != [401] * len(ans):
            raise Exception
        print("Auth tests success")
    except Exception:
        print("Auth tests failed")


def check_v2_service():
    global user_id

    try:
        ans = []
        resp = requests.get("http://127.0.0.3:8002/auth")
        cookies = resp.cookies
        ans.append(resp.status_code)
        resp = requests.post("http://127.0.0.3:8002/v2/add_user", params={"name": "1"}, cookies=cookies)
        ans.append(resp.status_code)
        resp = requests.get("http://127.0.0.3:8002/v2/users", cookies=cookies)
        ans.append(resp.status_code)
        id = json.loads(resp.content)["users"][0]["_id"]
        resp = requests.delete(f"http://127.0.0.3:8002/v2/delete_user/{id}", cookies=cookies)
        ans.append(resp.status_code)
        resp = requests.post("http://127.0.0.3:8002/v2/add_user", params={"name": "1"}, cookies=cookies)
        ans.append(resp.status_code)
        resp = requests.get("http://127.0.0.3:8002/v2/users", cookies=cookies)
        ans.append(resp.status_code)
        id = json.loads(resp.content)["users"][0]["_id"]
        resp = requests.put("http://127.0.0.3:8002/v2/update_user", params={"id": id, "name": "2"}, cookies=cookies)
        ans.append(resp.status_code)
        resp = requests.get(f"http://127.0.0.3:8002/v2/user/{id}", cookies=cookies)
        ans.append(resp.status_code)
        if json.loads(resp.content)["Name"] != "2" or ans != [200] * len(ans):
            raise Exception
        print("Users microservice tests success")
    except Exception:
        print("Users microservice tests failed")


def check_v1_service():
    global user_id

    try:
        ans = []
        resp = requests.get("http://127.0.0.3:8002/auth")
        cookies = resp.cookies
        ans.append(resp.status_code)
        resp = requests.post("http://127.0.0.3:8002/v1/add_task", params={"name": "1", "difficult": 1,
                                                     "description": "1", "user_id": user_id}, cookies=cookies)
        ans.append(resp.status_code)
        resp = requests.get("http://127.0.0.3:8002/v1/tasks", cookies=cookies)
        ans.append(resp.status_code)
        task_id = json.loads(resp.content)["tasks"][0]["_id"]
        resp = requests.delete(f"http://127.0.0.3:8002/v1/delete_task/{task_id}", cookies=cookies)
        ans.append(resp.status_code)
        resp = requests.get("http://127.0.0.3:8002/v1/tasks", cookies=cookies)
        ans.append(resp.status_code)
        task_id = json.loads(resp.content)["tasks"][0]["_id"]
        resp = requests.put("http://127.0.0.3:8002/v1/update_task", params={"id": task_id, "name": "2"}, cookies=cookies)
        ans.append(resp.status_code)
        resp = requests.get(f"http://127.0.0.3:8002/v1/task/{task_id}", cookies=cookies)
        ans.append(resp.status_code)
        if json.loads(resp.content)["Name"] != "2" or ans != [200] * len(ans):
            raise Exception
        print("Tasks microservice tests success")
    except Exception:
        print("Tasks microservice tests failed")


def start_all_tests():
    check_auth()
    check_v2_service()
    check_v1_service()


if __name__ == "__main__":
    start_all_tests()
