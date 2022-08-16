import sys
import time
from os import mkdir, path
from threading import Thread

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from loguru import logger

from funcs import fetch_subgroups, set_up_schedule, status_in_queue
from valid_groups import fetch_groups, group_id_is_valid

# set up logging
logger_conf = {
    "colorize": True,
    "backtrace": True,
    "diagnose": True,
    "catch": True,
    "level": "DEBUG",
    "sink": sys.stdout,
}
logger.configure(handlers=[logger_conf])

# create ASGI app
app = FastAPI(title="Herzen schedule to ICS")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

# create necessary directories if missing
directory_names = ["raw_schedule", "processed_schedule"]
for dir_name in directory_names:
    if not path.isdir(dir_name):
        mkdir(dir_name)


@app.get("/")
def index(request: Request):
    """display index page"""
    return templates.TemplateResponse("index.html", context={"request": request})


@app.get("/static/{filename}")
def static(filename: str) -> FileResponse:
    """route for static files (css, js, etc)"""
    return FileResponse(f"static/{filename}")


@app.get("/get_valid_groups")
def get_valid_groups():
    """get group names and ids"""
    return fetch_groups()


@app.get("/get_subgroups/{group_id}")
def get_subgroups(group_id: int) -> int:
    """get number of subgroups for given group"""
    return fetch_subgroups(group_id)


@app.get("/get_schedule/{group_id}/{subgroup_no}")
def form_handler(group_id: int, subgroup_no: int = 1):
    """download a file or start preparing it"""
    logger.info(f"User requested schedule for group_id={group_id}.")

    # validate data, for invalid data return 400 Bad Request
    try:
        group_id = int(group_id)
        subgroup_no = int(subgroup_no)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Номера группы и подгруппы должны быть числами.",
        )
    if not group_id_is_valid(group_id):
        raise HTTPException(status_code=400, detail="Группы с таким ID нет.")

    filename: str = f"{group_id}-{subgroup_no}.ics"
    # check if file already exists
    file_path = f"processed_schedule/{filename}"

    if path.exists(file_path) and time.time() - path.getctime(file_path) <= 60 * 60 * 24:
        logger.info(f"{filename} already exists. No need to generate.")
        return FileResponse(file_path)

    # if a schedule is being worked on, return 202 Accepted
    # so that the client requests it again after some time
    # if an error is logged, return that
    schedule_status = status_in_queue(group_id)
    if schedule_status:
        if schedule_status == "Working":
            raise HTTPException(status_code=202)
        else:
            raise HTTPException(status_code=500, detail=schedule_status)

    # start fetching and setting up schedule
    Thread(target=set_up_schedule, args=(group_id, subgroup_no)).start()

    # return 202 Accepted to have the client request again later
    raise HTTPException(status_code=202)


# start a web server
if __name__ == "__main__":
    logger.info("Starting server")
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
