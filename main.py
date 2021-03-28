from funcs import *
from os import path
from sys import exit
from bottle import route, run, request, template, static_file


# retrieve the ics file for specified group
def main(group_id: str, subgroup_no: int) -> None:
    # download schedule HTML page if not present
    if not path.exists(f"raw_schedule/{group_id}.html"):
        if retrieve_schedule(group_id):
            print('Schedule retrieved successfully')
        else:
            exit('Error retrieving schedule')
    else:
        print('Schedule already saved. Loading up.')

    if not path.exists(f"processed_schedule/{group_id}-{subgroup_no}.ics"):
        # convert HTML schedule to an array of Lesson objects
        try:
            lessons = convert_html_to_lesson(f'{group_id}.html', subgroup_no)
        except Exception as E:
            exit(f'Error converting HTML into Lesson objects:\n{E}')

        # convert array of Lesson objects into an ics file
        if convert_lesson_to_ics(lessons, group_id, subgroup_no):
            print('Successful ics conversion, file saved.')
        else:
            exit('Failed to convert to ics.')
    else:
        print('File already exists. Exiting.')


# display index page
@route('/')
def index():
    return template("templates/index")


# serve a file to download when ready
@route('/', method="POST")
def form_handler():
    group_id = request.forms.get("group_id")
    subgroup_no = int(request.forms.get("subgroup"))
    main(group_id, subgroup_no)
    return static_file(
        f"{group_id}-{subgroup_no}.ics", root='processed_schedule', download=f"{group_id}-{subgroup_no}.ics")



# start a web server
if __name__ == "__main__":
    run(host='localhost', port=8080, debug=True)
