from fastapi import FastAPI, Request, Response, Form
from typing import Optional
import redis, pickle, requests, json
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from Task import Task
from bson.objectid import ObjectId
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# uri = "mongodb+srv://kartem423:aR33kodWQ6IfJ362@cluster0.rtark.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
# client = MongoClient(uri, server_api=ServerApi('1'))

client = MongoClient("mongodb://localhost:27017")
mongo_db = client["db"]
#mongo_db["Tasks"].create_index("Name", unique=True)

app = FastAPI(title="Laba 3", description="This is a laba 3", version="1.0")
templates = Jinja2Templates(directory="templates")

radis_db = redis.Redis(host='redis-15797.c93.us-east-1-3.ec2.redns.redis-cloud.com',
                       port=15797,
                       password='2AdSepjiY8UnQ8FwuC4mfxwxd90vTykb')


@app.get("/", include_in_schema=False)
async def main_page(request: Request):
    params = {"tasks": [], "request": request, "current": "Tasks"}

    tasks = mongo_db["Tasks"].find({})

    for task in tasks:
        task["_id"] = str(task["_id"])
        params["tasks"].append(task)

    return templates.TemplateResponse("html/main.html", params, media_type="text/html")


@app.get("/tasks")
async def get_tasks():
    global mongo_db

    params = {"tasks": []}
    tasks = mongo_db["Tasks"].find({})

    for task in tasks:
        task["_id"] = str(task["_id"])
        params["tasks"].append(task)

    return JSONResponse(content=jsonable_encoder(params), media_type="application/json")


@app.get("/task/{id}")
async def task_by_name(id: str):
    global radis_db, mongo_db

    #task = radis_db.get(name)
    task = radis_db.get(id)
    #mongo_db["Tasks"].find_one({"_id": ObjectId("67137be69c77f1643544ff80")})
    if task == None:
        #task = mongo_db["Tasks"].find_one({"Name": name})
        task = mongo_db["Tasks"].find_one({"_id": ObjectId(id)})
        if not task == None:
            radis_db.set(id, pickle.dumps(task))
    else:
        task = pickle.loads(task)

    if task:
        task["_id"] = str(task["_id"])
        return JSONResponse(content=jsonable_encoder(task), media_type="application/json")
    else:
        return Response(status_code=404)


@app.put("/update_task")
async def update_task(id: str, name: Optional[str] = Form(None),
                      difficult: Optional[int] = Form(None), description: Optional[str] = Form(None)):
    global radis_db, mongo_db

    task = await task_by_name(id)
    if task.status_code != 200:
        return Response(status_code=task.status_code)

    task = json.loads(task.body)
    if name is not None:
        task["Name"] = difficult
    if difficult is not None:
        task["Difficult"] = difficult
    if description is not None:
        task["Description"] = description

    #mongo_db["Tasks"].find_one_and_update({"Name": name}, {"$set": task}, upsert=True)
    radis_db.set(id, pickle.dumps(task))
    task.pop("_id", None)
    mongo_db["Tasks"].find_one_and_update({"_id": ObjectId(id)}, {"$set": task}, upsert=True)

    return RedirectResponse("/", status_code=200)


@app.get("/add_task_page", include_in_schema=False)
async def add_task_page(request: Request):
    params = {"request": request, "current": "Add task"}

    return templates.TemplateResponse("html/add.html", params, media_type="text/html")


@app.post("/add_task")
async def add_task(name: str, difficult: int, description: str):
    global mongo_db

    """
    if name == "":
        return RedirectResponse("/", status_code=303)

    task = await task_by_name(name)
    if task.status_code == 200:
        return RedirectResponse("/", status_code=303)
    """

    mongo_db["Tasks"].insert_one({"Name": name, "Description": description, "Difficult": difficult})

    return Response(status_code=200)


@app.post("/post_add_task", include_in_schema=False)
async def post_add_task(name: str = Form(None), difficult: int = Form(None),
                   description: str = Form(None)):
    return await add_task(name, difficult, description)


@app.delete("/delete_task/{id}")
async def delete_task(id: str):
    global radis_db, mongo_db

    task = await task_by_name(id)
    if task.status_code != 200:
        return Response(status_code=404)

    mongo_db["Tasks"].delete_one({"_id": ObjectId(id)})
    radis_db.delete(id)

    return Response(status_code=200)


@app.exception_handler(404)
async def unicorn_exception_handler(request: Request, exc):
    params = {"request": request, "current": "Exception", "exception": exc}

    return templates.TemplateResponse("html/exception.html", params)


app.mount("/css", StaticFiles(directory="templates/css"), "css")
