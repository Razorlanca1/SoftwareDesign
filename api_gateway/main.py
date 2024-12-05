import datetime

from fastapi import FastAPI, Request, Response, Form
from fastapi.responses import JSONResponse
from typing import Optional
import requests


app = FastAPI(title="Laba 5", description="This is a laba 5 API Gateway", version="1.0")


@app.get("/v1/tasks/")
async def get_tasks():
    return JSONResponse(content=requests.get("http://127.0.0.1:8000/tasks").json(), media_type="application/json")


@app.get("/v1/task/{id}")
async def task_by_name(id: str):
    return JSONResponse(content=requests.get(f"http://127.0.0.1:8000/task/{id}").json(),
                        media_type="application/json")


@app.put("/v1/update_task")
async def update_task(id: str, name: str = None,
                      difficult: int = None, description: str = None):
    return Response(status_code=requests.put(f"http://127.0.0.1:8000/update_task",
                                             params={"id": id, "name": name, "difficult": difficult,
                                                     "description": description}).status_code)


@app.post("/v1/add_task")
async def add_task(name: str, difficult: int, description: str, user_id: str):
    return Response(status_code=requests.post(f"http://127.0.0.1:8000/add_task",
                                             params={"name": name, "difficult": difficult,
                                                     "description": description, "user_id": user_id}).status_code)


@app.delete("/v1/delete_task/{id}")
async def delete_task(id: str):
    return Response(status_code=requests.delete(f"http://127.0.0.1:8000/delete_task/{id}").status_code)


@app.delete("/v1/delete_all_tasks")
async def delete_all_tasks():
    return Response(status_code=requests.delete(f"http://127.0.0.1:8000/delete_all_tasks").status_code)


@app.get("/v2/users/")
async def get_users():
    return JSONResponse(content=requests.get("http://127.0.0.2:9000/users").json(), media_type="application/json")


@app.get("/v2/user/{id}")
async def user_by_name(id: str):
    return JSONResponse(content=requests.get(f"http://127.0.0.2:9000/user/{id}").json(),
                        media_type="application/json")


@app.put("/v2/update_user")
async def update_user(id: str, name: str = None,):
    return Response(status_code=requests.put(f"http://127.0.0.2:9000/update_user",
                                             params={"id": id, "name": name}).status_code)


@app.post("/v2/add_user")
async def add_user(name: str):
    return Response(status_code=requests.post(f"http://127.0.0.2:9000/add_user",
                                             params={"name": name}).status_code)


@app.delete("/v1/delete_user/{id}")
async def delete_user(id: str):
    return Response(status_code=requests.delete(f"http://127.0.0.2:9000/delete_user/{id}").status_code)

