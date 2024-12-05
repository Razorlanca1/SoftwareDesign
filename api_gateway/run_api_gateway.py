import uvicorn

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.3", port=8002, log_level="info", reload=True)
