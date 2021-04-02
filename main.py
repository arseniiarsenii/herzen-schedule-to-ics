from os import path, mkdir
from threading import Thread

from bottle import route, run, template, static_file, default_app, HTTPResponse, get

from funcs import status_in_queue, set_up_schedule
from valid_groups import fetch_groups, group_id_is_valid


# create necessary directories if missing
directory_names = ['raw_schedule', 'processed_schedule']
for dir in directory_names:
    if not path.isdir(dir):
        mkdir(dir)


# display index page
@route('/')
def index():
    return template("templates/index")


# route for static files (css, js, etc)
@route('/static/<filename>')
def static(filename: str):
    return static_file(filename, "static")


# get group names and ids
@get('/get_valid_groups')
def get_valid_groups():
    return fetch_groups()


# download a file or start preparing it
@get('/<group_id>/<subgroup_no>')
def form_handler(group_id: int, subgroup_no: int = 1):
    print(f'User requested schedule for group_id={group_id}.')
    # cors header for javascript requests
    cors_k, cors_v = 'Access-Control-Allow-Origin', '*'
    cors_header = {cors_k: cors_v}
    
    # validate data, for invalid data return 400 Bad Request
    try:
        group_id = int(group_id)
        subgroup_no = int(subgroup_no)
    except ValueError:
        return HTTPResponse(status=400, body='Номера группы и подгруппы должны быть числами.', headers=cors_header)
    if not group_id_is_valid(group_id):
        return HTTPResponse(status=400, body='Группы с таким ID нет.', headers=cors_header)

    filename: str = f"{group_id}-{subgroup_no}.ics"
    # check if file already exists
    if path.exists(f'processed_schedule/{filename}'):
        print(f'{filename} already exists. No need to generate.')
        file_response = static_file(filename, root='processed_schedule', download=filename)
        file_response.set_header(cors_k, cors_v)
        return file_response

    # if a schedule is being worked on, return 202 Accepted
    # so that the client requests it again after some time
    # if an error is logged, return that
    schedule_status = status_in_queue(group_id)
    if schedule_status:
        if schedule_status is "Working":
            return HTTPResponse(status=202, headers=cors_header)
        else:
            return HTTPResponse(status=500, body=schedule_status, headers=cors_header)

    # start fetching and setting up schedule
    Thread(target=set_up_schedule, args=(group_id, subgroup_no)).start()

    # return 202 Accepted to have the client request again later
    return HTTPResponse(status=202, headers=cors_header)


# define "app" object for the WSGI server to run
app = default_app()


# start a web server
if __name__ == "__main__":
    run(app=app, host='0.0.0.0', port=8080, server='gunicorn', debug=True)
