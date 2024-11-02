from fastapi import FastAPI, Response
import redis, pickle, json
from pymongo.mongo_client import MongoClient
from fastapi_utils.tasks import repeat_every
from fastapi.encoders import jsonable_encoder
from fastapi.responses import RedirectResponse, JSONResponse
from bson.objectid import ObjectId
from confluent_kafka import Producer, Consumer

config = {
    'bootstrap.servers': 'localhost:9092',
    'default.topic.config': {'api.version.request': True},
    'group.id': 'mygroup',
    'auto.offset.reset': 'earliest'
}

producer = Producer(config)
consumer = Consumer(config)
consumer.subscribe(['tasks_to_confirm'])

client = MongoClient("mongodb://localhost:27017")
mongo_db = client["db"]

app = FastAPI(title="Laba 4", description="This is a laba 4 users mircoservice", version="1.0")

radis_db = redis.Redis(host='redis-15797.c93.us-east-1-3.ec2.redns.redis-cloud.com',
                       port=15797,
                       password='2AdSepjiY8UnQ8FwuC4mfxwxd90vTykb')


@app.on_event('startup')
@repeat_every(seconds=0)
async def process_consumer():
    global consumer, producer, mongo_db

    while True:
        msg = consumer.poll(timeout=0)
        if msg is None:
            break

        req = json.loads(msg.value().decode('utf-8'))
        print(req)

        try:
            user = mongo_db["Users"].find_one({"_id": ObjectId(req["user_id"])})
            print("confirmed")
            up = {"RegisteredObjects": user["RegisteredObjects"] + 1}
            mongo_db["Users"].update_one({"_id": ObjectId(req["user_id"])}, {"$set": up})
            producer.produce(topic="tasks_confirm_answer",
                             value=json.dumps({"task_id": req["task_id"], "verdict": "confirmed"}))
        except Exception:
            print("denied")
            producer.produce(topic="tasks_confirm_answer",
                             value=json.dumps({"task_id": req["task_id"], "verdict": "denied"}))


@app.get("/users")
async def get_users():
    global mongo_db

    params = {"users": []}
    users = mongo_db["Users"].find({})

    for user in users:
        user["_id"] = str(user["_id"])
        params["users"].append(user)

    return JSONResponse(content=jsonable_encoder(params), media_type="application/json")


@app.get("/user/{id}")
async def user_by_name(id: str):
    global radis_db, mongo_db

    user = radis_db.get("User" + id)
    if user == None:
        user = mongo_db["Users"].find_one({"_id": ObjectId(id)})
        if not user == None:
            radis_db.set("User" + id, pickle.dumps(user))
    else:
        user = pickle.loads(user)

    if user:
        user["_id"] = str(user["_id"])
        return JSONResponse(content=jsonable_encoder(user), media_type="application/json")
    else:
        return Response(status_code=404)


@app.put("/update_user")
async def update_task(id: str, name: str):
    global radis_db, mongo_db

    user = await user_by_name(id)
    if user.status_code != 200:
        return Response(status_code=user.status_code)

    user = json.loads(user.body)
    user["Name"] = name

    radis_db.set("User" + id, pickle.dumps(user))
    user.pop("_id", None)
    mongo_db["Users"].find_one_and_update({"_id": ObjectId(id)}, {"$set": user}, upsert=True)

    return RedirectResponse("/", status_code=200)


@app.post("/add_user")
async def add_user(name: str):
    global mongo_db

    mongo_db["Users"].insert_one({"Name": name, "RegisteredObjects": 0})

    return Response(status_code=200)


@app.delete("/delete_user/{id}")
async def delete_user(id: str):
    global radis_db, mongo_db

    user = await user_by_name(id)
    if user.status_code != 200:
        return Response(status_code=404)

    mongo_db["Users"].delete_one({"_id": ObjectId(id)})
    radis_db.delete("Users" + id)

    return Response(status_code=200)

