from fastapi import FastAPI, Request, Response, Form
from typing import Optional
import redis, pickle
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from Task import Task


app = FastAPI(title="Laba 1", description="This is a laba 1", version="1.0")
templates = Jinja2Templates(directory="templates")

db = redis.Redis(host='redis-15797.c93.us-east-1-3.ec2.redns.redis-cloud.com',
  port=15797,
  password='2AdSepjiY8UnQ8FwuC4mfxwxd90vTykb')

db.flushdb()
db.lpush("Tasks", pickle.dumps(Task(1, "abc", 10, "rrrrrrrrrrrr")))


@app.get("/")
async def main_page(request: Request):
    params = {"tasks": [], "request": request, "current": "Tasks"}
    tasks = db.lrange("Tasks", 0, -1)

    for task in tasks:
        params["tasks"].append(pickle.loads(task).get_info())

    return templates.TemplateResponse("html/main.html", params)


@app.get("/task/{id}")
async def task_page(request: Request, id):
    params = {"request": request, "current": "Task"}
    tasks = db.lrange("Tasks", 0, -1)

    for task in tasks:
        info = pickle.loads(task).get_info()
        if str(info["Id"]) == id:
            params["task"] = info
            break
    else:
        return RedirectResponse("/")

    return templates.TemplateResponse("html/task.html", params)


@app.put("/update_task")
async def update_task(request: Request, id: Optional[int] = Form(None),
                   name: Optional[str] = Form(None), difficult: Optional[int] = Form(None),
                   description: Optional[str] = Form(None)):
    tasks = db.lrange("Tasks", 0, -1)

    for task in tasks:
        t = pickle.loads(task)
        info = t.get_info()
        if info["Id"] == id:
            db.lrem("Tasks", 0, task)
            t.update(name, difficult, description)
            db.lpush("Tasks", pickle.dumps(t))
            return RedirectResponse(f"/task/{id}", status_code=303)

    return RedirectResponse("/", status_code=303)


@app.put("/add_task")
async def add_task(request: Request, id: int = Form(None),
                   name: str = Form(None), difficult: int = Form(None),
                   description: str = Form(None)):
    tasks = db.lrange("Tasks", 0, -1)

    for task in tasks:
        info = pickle.loads(task).get_info()
        if info["Id"] == id:
            return RedirectResponse("/", status_code=303)

    task = Task(id, name, difficult, description)
    db.lpush("Tasks", pickle.dumps(task))

    return RedirectResponse(f"/task/{id}", status_code=303)


@app.get("/add_task_page")
async def add_task_page(request: Request):
    params = {"request": request, "current": "Add task"}

    return templates.TemplateResponse("html/add.html", params)


@app.post("/post_add_task")
async def add_task(request: Request, id: Optional[int] = Form(None),
                   name: Optional[str] = Form(None), difficult: Optional[int] = Form(None),
                   description: Optional[str] = Form(None)):
    tasks = db.lrange("Tasks", 0, -1)

    for task in tasks:
        info = pickle.loads(task).get_info()
        if info["Id"] == id:
            return RedirectResponse("/", status_code=303)

    task = Task(id, name, difficult, description)
    db.lpush("Tasks", pickle.dumps(task))

    return RedirectResponse(f"/task/{id}", status_code=303)


@app.delete("/delete_task/{id}")
async def delete_task(request: Request, id):
    tasks = db.lrange("Tasks", 0, -1)

    for task in tasks:
        t = pickle.loads(task)
        info = t.get_info()
        if str(info["Id"]) == id:
            db.lrem("Tasks", 0, task)
            break

    return RedirectResponse("/", status_code=303)


@app.exception_handler(404)
async def unicorn_exception_handler(request: Request, exc):
    params = {"request": request, "current": "Exception", "exception": exc}

    return templates.TemplateResponse("html/exception.html", params)


"""def custom_swagger(*args, **kwargs):
    html = get_swagger_ui_html(*args, **kwargs, title="Title", openapi_url="127.0.0.1")
    return Response(content=html, media_type="text/html")


app.openapi = custom_swagger"""
app.mount("/css", StaticFiles(directory="templates/css"), "css")