import uvicorn

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.2", port=9000, log_level="info", reload=True)
