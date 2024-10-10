from fastapi import FastAPI, Request, Response, Form
from typing import Optional
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from Task import Task


app = FastAPI(title="Laba 1", description="This is a laba 1", version="1.0")
templates = Jinja2Templates(directory="templates")

tasks = [Task(1, "abc", 10, "rrrrrrrrrrrr")]


@app.get("/")
async def main_page(request: Request):
    global tasks

    params = {"tasks": [], "request": request, "current": "Tasks"}
    for task in tasks:
        params["tasks"].append(task.get_info())

    return templates.TemplateResponse("html/main.html", params)


@app.get("/task/{id}")
async def task_page(request: Request, id):
    global tasks

    params = {"request": request, "current": "Task"}
    for task in tasks:
        info = task.get_info()
        if str(info["Id"]) == id:
            params["task"] = info
            break
    else:
        return RedirectResponse("/")

    return templates.TemplateResponse("html/task.html", params)


@app.put("/add_task")
async def add_task(request: Request, id: Optional[int] = Form(None),
                   name: Optional[str] = Form(None), difficult: Optional[int] = Form(None),
                   description: Optional[str] = Form(None)):
    global tasks

    for task in tasks:
        info = task.get_info()
        if info["Id"] == id:
            return RedirectResponse("/", status_code=303)

    task = Task(id, name, difficult, description)
    tasks.append(task)

    return RedirectResponse(f"/task/{id}", status_code=303)


@app.get("/add_task_page")
async def add_task_page(request: Request):
    params = {"request": request, "current": "Add task"}

    return templates.TemplateResponse("html/add.html", params)


@app.post("/post_add_task")
async def add_task(request: Request, id: Optional[int] = Form(None),
                   name: Optional[str] = Form(None), difficult: Optional[int] = Form(None),
                   description: Optional[str] = Form(None)):
    global tasks

    for task in tasks:
        info = task.get_info()
        if info["Id"] == id:
            return RedirectResponse("/", status_code=303)

    task = Task(id, name, difficult, description)
    tasks.append(task)

    return RedirectResponse(f"/task/{id}", status_code=303)


@app.delete("/delete_task/{id}")
async def delete_task(request: Request, id):
    global tasks

    for i in range(len(tasks) - 1, -1, -1):
        if str(tasks[i].get_info()["Id"]) == id:
            tasks.remove(tasks[i])
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