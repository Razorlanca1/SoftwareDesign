import datetime

from fastapi import FastAPI, Request, Response, Form, Cookie
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
import requests

SECRET_KEY = "09d25e094faa9154613450832486f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"


app = FastAPI(title="Laba 5", description="This is a laba 5 API Gateway", version="1.0")


@app.get("/auth")
async def auth():
    to_encode = {}
    expire = datetime.datetime.now() + datetime.timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    resp = Response(status_code=200)
    resp.set_cookie("token", encoded_jwt)
    return resp


@app.get("/v1/tasks/")
async def get_tasks(request: Request):
    try:
        token = request.cookies.get('token')
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception:
        return Response(status_code=401)
    return JSONResponse(content=requests.get("http://127.0.0.1:8000/tasks").json(), media_type="application/json")


@app.get("/v1/task/{id}")
async def task_by_name(request: Request, id: str):
    try:
        token = request.cookies.get('token')
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception:
        return Response(status_code=401)
    return JSONResponse(content=requests.get(f"http://127.0.0.1:8000/task/{id}").json(),
                        media_type="application/json")


@app.put("/v1/update_task")
async def update_task(request: Request, id: str, name: str = None,
                      difficult: int = None, description: str = None):
    try:
        token = request.cookies.get('token')
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception:
        return Response(status_code=401)
    return Response(status_code=requests.put(f"http://127.0.0.1:8000/update_task",
                                             params={"id": id, "name": name, "difficult": difficult,
                                                     "description": description}).status_code)


@app.post("/v1/add_task")
async def add_task(request: Request, name: str, difficult: int, description: str, user_id: str):
    try:
        token = request.cookies.get('token')
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception:
        return Response(status_code=401)
    return Response(status_code=requests.post(f"http://127.0.0.1:8000/add_task",
                                             params={"name": name, "difficult": difficult,
                                                     "description": description, "user_id": user_id}).status_code)


@app.delete("/v1/delete_task/{id}")
async def delete_task(request: Request, id: str):
    try:
        token = request.cookies.get('token')
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception:
        return Response(status_code=401)
    return Response(status_code=requests.delete(f"http://127.0.0.1:8000/delete_task/{id}").status_code)


@app.delete("/v1/delete_all_tasks")
async def delete_all_tasks(request: Request):
    try:
        token = request.cookies.get('token')
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception:
        return Response(status_code=401)
    return Response(status_code=requests.delete(f"http://127.0.0.1:8000/delete_all_tasks").status_code)


@app.get("/v2/users/")
async def get_users(request: Request):
    try:
        token = request.cookies.get('token')
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception:
        return Response(status_code=401)
    return JSONResponse(content=requests.get("http://127.0.0.2:9000/users").json(), media_type="application/json")


@app.get("/v2/user/{id}")
async def user_by_name(request: Request, id: str):
    try:
        token = request.cookies.get('token')
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception:
        return Response(status_code=401)
    return JSONResponse(content=requests.get(f"http://127.0.0.2:9000/user/{id}").json(),
                        media_type="application/json")


@app.put("/v2/update_user")
async def update_user(request: Request, id: str, name: str = None):
    try:
        token = request.cookies.get('token')
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception:
        return Response(status_code=401)
    return Response(status_code=requests.put(f"http://127.0.0.2:9000/update_user",
                                             params={"id": id, "name": name}).status_code)


@app.post("/v2/add_user")
async def add_user(request: Request, name: str):
    try:
        token = request.cookies.get('token')
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception:
        return Response(status_code=401)
    return Response(status_code=requests.post(f"http://127.0.0.2:9000/add_user",
                                             params={"name": name}).status_code)


@app.delete("/v1/delete_user/{id}")
async def delete_user(request: Request, id: str):
    try:
        token = request.cookies.get('token')
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception:
        return Response(status_code=401)
    return Response(status_code=requests.delete(f"http://127.0.0.2:9000/delete_user/{id}").status_code)

