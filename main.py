from fastapi import FastAPI, Request, Response, Form
from typing import Optional
import redis, pickle, requests, json
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from Task import Task
from bson.objectid import ObjectId
from pymongo.mongo_client import MongoClient
from fastapi_utils.tasks import repeat_every
from confluent_kafka import Producer, Consumer

# uri = "mongodb+srv://kartem423:aR33kodWQ6IfJ362@cluster0.rtark.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
# client = MongoClient(uri, server_api=ServerApi('1'))

config = {
    'bootstrap.servers': 'localhost:9092',
    'default.topic.config': {'api.version.request': True},
    'group.id': 'mygroup',
    'auto.offset.reset': 'earliest'
}

producer = Producer(config)
consumer = Consumer(config)
consumer.subscribe(['tasks_confirm_answer'])

client = MongoClient("mongodb://localhost:27017")
mongo_db = client["db"]

app = FastAPI(title="Laba 4", description="This is a laba 4", version="1.0")
templates = Jinja2Templates(directory="templates")

radis_db = redis.Redis(host='redis-15797.c93.us-east-1-3.ec2.redns.redis-cloud.com',
                       port=15797,
                       password='2AdSepjiY8UnQ8FwuC4mfxwxd90vTykb')


@app.on_event('startup')
@repeat_every(seconds=0)
async def process_consumer():
    global consumer, mongo_db

    while True:
        msg = consumer.poll(timeout=0)
        if msg is None:
            break

        req = json.loads(msg.value().decode('utf-8'))
        print(req)
        up = {"Status": req["verdict"]}
        mongo_db["Tasks"].update_one({"_id": ObjectId(req["task_id"])}, {"$set": up})



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

    task = radis_db.get("Task" + id)
    if task == None:
        task = mongo_db["Tasks"].find_one({"_id": ObjectId(id)})
        if not task == None:
            radis_db.set("Task" + id, pickle.dumps(task))
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
        task["Name"] = name
    if difficult is not None:
        task["Difficult"] = difficult
    if description is not None:
        task["Description"] = description

    radis_db.set("Task" + id, pickle.dumps(task))
    task.pop("_id", None)
    mongo_db["Tasks"].find_one_and_update({"_id": ObjectId(id)}, {"$set": task}, upsert=True)

    return RedirectResponse("/", status_code=200)


@app.get("/add_task_page", include_in_schema=False)
async def add_task_page(request: Request):
    params = {"request": request, "current": "Add task"}

    return templates.TemplateResponse("html/add.html", params, media_type="text/html")


@app.post("/add_task")
async def add_task(name: str, difficult: int, description: str, user_id: str):
    global mongo_db, producer

    id = mongo_db["Tasks"].insert_one({"Name": name, "Description": description,
                                  "Difficult": difficult, "Status": "waiting"}).inserted_id

    print(id)
    print(json.dumps({"task_id": str(id), "user_id": user_id}))

    producer.produce("tasks_to_confirm", value=json.dumps({"task_id": str(id), "user_id": user_id}))
    producer.flush()

    return Response(status_code=200)


@app.post("/post_add_task", include_in_schema=False)
async def post_add_task(name: str, difficult: int,
                        description: str, user_id: str):
    return await add_task(name, difficult, description, user_id)


@app.delete("/delete_task/{id}")
async def delete_task(id: str):
    global radis_db, mongo_db

    task = await task_by_name(id)
    if task.status_code != 200:
        return Response(status_code=404)

    mongo_db["Tasks"].delete_one({"_id": ObjectId(id)})
    radis_db.delete("Task" + id)

    return Response(status_code=200)


@app.delete("/delete_all_tasks")
async def delete_all_tasks():
    global radis_db, mongo_db

    mongo_db["Tasks"].delete_many({})
    radis_db.flushdb()

    return Response(status_code=200)


@app.exception_handler(404)
async def unicorn_exception_handler(request: Request, exc):
    params = {"request": request, "current": "Exception", "exception": exc}

    return templates.TemplateResponse("html/exception.html", params)


app.mount("/css", StaticFiles(directory="templates/css"), "css")
