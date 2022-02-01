import sys
import typing as tp
from os import mkdir, path
from threading import Thread

from bottle import HTTPResponse, default_app, get, route, run, static_file, template
from loguru import logger

from funcs import fetch_subgroups, set_up_schedule, status_in_queue
from valid_groups import fetch_groups, group_id_is_valid

logger_conf = {
    "colorize": True,
    "backtrace": True,
    "diagnose": True,
    "catch": True,
    "level": "DEBUG",
    "sink": sys.stdout,
}
logger.configure(handlers=[logger_conf])

# cors header for javascript requests
CORS = {"Access-Control-Allow-Origin": "*"}

# create necessary directories if missing
directory_names = ["raw_schedule", "processed_schedule"]
for dir_name in directory_names:
    if not path.isdir(dir_name):
        mkdir(dir_name)


@route("/")
def index() -> template:
    """display index page"""
    return template("templates/index")


@route("/static/<filename>")
def static(filename: str) -> static_file:
    """route for static files (css, js, etc)"""
    return static_file(filename, "static")


@get("/get_valid_groups")
def get_valid_groups() -> tp.Dict[int, str]:
    """get group names and ids"""
    return fetch_groups()


@get("/get_subgroups/<group_id>")
def get_subgroups(group_id: int) -> str:
    """get number of subgroups for given group"""
    return str(fetch_subgroups(group_id))


@get("/get_schedule/<group_id>/<subgroup_no>")
def form_handler(group_id: int, subgroup_no: int = 1) -> HTTPResponse:
    """download a file or start preparing it"""
    logger.info(f"User requested schedule for group_id={group_id}.")
    # cors header for javascript requests
    cors_k, cors_v = "Access-Control-Allow-Origin", "*"
    cors_header = {cors_k: cors_v}

    # validate data, for invalid data return 400 Bad Request
    try:
        group_id = int(group_id)
        subgroup_no = int(subgroup_no)
    except ValueError:
        return HTTPResponse(
            status=400,
            body="Номера группы и подгруппы должны быть числами.",
            headers=cors_header,
        )
    if not group_id_is_valid(group_id):
        return HTTPResponse(status=400, body="Группы с таким ID нет.", headers=cors_header)

    filename: str = f"{group_id}-{subgroup_no}.ics"
    # check if file already exists
    if path.exists(f"processed_schedule/{filename}"):
        logger.info(f"{filename} already exists. No need to generate.")
        file_response = static_file(filename, root="processed_schedule", download=filename)
        file_response.set_header(cors_k, cors_v)
        return file_response

    # if a schedule is being worked on, return 202 Accepted
    # so that the client requests it again after some time
    # if an error is logged, return that
    schedule_status = status_in_queue(group_id)
    if schedule_status:
        if schedule_status == "Working":
            return HTTPResponse(status=202, headers=cors_header)
        else:
            return HTTPResponse(status=500, body=schedule_status, headers=cors_header)

    # start fetching and setting up schedule
    Thread(target=set_up_schedule, args=(group_id, subgroup_no)).start()

    # return 202 Accepted to have the client request again later
    return HTTPResponse(status=202, headers=cors_header)


# define 'app' object for the WSGI server to run
app = default_app()

# start a web server
if __name__ == "__main__":
    logger.info("Starting server")
    run(app=app, host="0.0.0.0", port=8080, debug=True)
