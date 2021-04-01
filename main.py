from os import path, mkdir
from threading import Thread

from bottle import route, run, template, static_file, default_app, HTTPResponse, response, get

from funcs import is_valid_id, is_id_in_queue, set_up_schedule


# create necessary directories if missing
directory_names = ['raw_schedule', 'processed_schedule']
for dir in directory_names:
    if not path.isdir(dir):
        mkdir(dir)


# display index page
@route('/')
def index():
    return template("templates/index.tpl")


# download a file or start preparing it
@get('/<group_id:int>/<subgroup_no:int>')
def form_handler(group_id: int, subgroup_no: int = 1):
    print(group_id)
    # set CORS headers
    response.add_header('Access-Control-Allow-Origin', '*')
    # validate data
    if not isinstance(group_id, int) or not isinstance(subgroup_no, int):
        return HTTPResponse(status=400, body='Номера группы и подгруппы должны быть числами.')
    elif not is_valid_id(group_id):
        return HTTPResponse(status=400, body='Группы с таким ID нет.')
    elif is_id_in_queue(group_id):
        return HTTPResponse(status=202)
    yield
    filename: str = f"{group_id}-{subgroup_no}.ics"
    # check if file already exists
    if path.exists(f'processed_schedule/{filename}'):
        print('File already exists. No need to generate.')
        return static_file(filename, root='processed_schedule', download=filename)

    # start fetching and setting up schedule
    Thread(target=set_up_schedule, args=(group_id, subgroup_no)).start()

    return HTTPResponse(status=202)


# define "app" object for the WSGI server to run
app = default_app()


# start a web server
if __name__ == "__main__":
    run(app=app, host='0.0.0.0', port=8080, server='gunicorn', debug=True)
