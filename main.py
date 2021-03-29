from os import path, mkdir
from sys import exit

from bottle import route, run, request, template, static_file

from funcs import *

# create necessary directories if missing
directory_names = ['raw_schedule', 'processed_schedule']
for dir in directory_names:
    if not path.isdir(dir):
        mkdir(dir)


# display index page
@route('/')
def index():
    return template("templates/index")


# serve a file to download when ready
@route('/', method="POST")
def form_handler():
    group_id = request.forms.get("group_id")
    subgroup_no = request.forms.get("subgroup")
    filename = f"{group_id}-{subgroup_no}.ics"

    # validate data
    if not is_valid_id(group_id):
        return 'Группы с таким ID нет.'

    try:
        subgroup_no = int(subgroup_no)
    except ValueError:
        return 'Номер подгруппы должен быть числом.'

    # check if file already exists
    if path.exists(f'processed_schedule/{filename}'):
        print('File already exists. No need to generate.')
        return static_file(filename, root='processed_schedule', download=filename)

    # download schedule HTML page if not present
    if not path.exists(f"raw_schedule/{group_id}.html"):
        if retrieve_schedule(group_id):
            print('Schedule retrieved successfully')
        else:
            exit('Error retrieving schedule')
    else:
        print('Schedule already saved. Loading up.')

    # convert HTML schedule to an array of Lesson objects
    try:
        lessons = convert_html_to_lesson(f'{group_id}.html', subgroup_no)
    except IndexError:
        return 'Неверный номер подгруппы.'
    except Exception as E:
        exit(f'Error converting HTML into Lesson objects: {E}')

    # convert array of Lesson objects into an ics file
    if convert_lesson_to_ics(lessons, group_id, subgroup_no):
        print('Successful ics conversion, file saved.')
    else:
        exit('Failed to convert to ics.')

    return static_file(filename, root='processed_schedule', download=filename)


# start a web server
if __name__ == "__main__":
    run(host='localhost', port=8080, debug=True)
