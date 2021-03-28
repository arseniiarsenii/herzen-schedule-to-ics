import requests
import re
import typing as tp
from datetime import datetime
from dateutil import tz
from bs4 import BeautifulSoup
from ics import Calendar, Event
from classes import Lesson


def convert_html_to_lesson(filename: str, subgroup: int) -> tp.List[Lesson]:
    schedule_html =  open(f'raw_schedule/{filename}', 'r')

    # parse schedule
    soup = BeautifulSoup(schedule_html, 'html.parser')
    schedule = soup.find('table', class_='schedule')
    table_rows = schedule.find_all('tr')
    header_skipped = False
    all_lessons = []

    # iterate through the rows of the schedule table
    for row in table_rows:
        # skip the first row of the table (header)
        if not header_skipped:
            header_skipped = True
            continue

        # if row contains date, parse it
        dayname = row.find('th', class_='dayname')
        if dayname is not None:
            date: str = dayname.text.split(',')[0]
            dayname = None
            continue

        # if row is nor header nor date, assume it is a lesson entry.
        # initialize a Lesson object and fill it's fields with data parsed from the row
        lesson = Lesson()

        # get lesson's start and end times
        timeframe: tp.List[str] = row.find('th').text.split(' — ')
        # get string timestamps
        start_time = f'{date} {timeframe[0]}'
        end_time = f'{date} {timeframe[1]}'
        # convert to datetime objects
        start_time = datetime.strptime(start_time, '%d.%m.%Y %H:%M')
        start_time = start_time.replace(tzinfo=tz.gettz('Europe/Moscow'))
        start_time = start_time.astimezone(tz.tzutc())
        end_time = datetime.strptime(end_time, '%d.%m.%Y %H:%M')
        end_time = end_time.replace(tzinfo=tz.gettz('Europe/Moscow'))
        end_time = end_time.astimezone(tz.tzutc())
        lesson.start_time = start_time
        lesson.end_time = end_time

        # extract lesson type
        lesson_data = row.find('td')
        lesson.type = re.findall('\[.*\]', lesson_data.text)[0][1:-1]

        # extract lesson title
        lesson.title = lesson_data.find("strong").text

        # extract lesson's online course link if present
        course_link = lesson_data.find("strong").find("a")
        if course_link is not None:
            lesson.course_link = course_link['href']

        # save lesson instance for future use
        all_lessons.append(lesson)

    return all_lessons


def convert_lesson_to_ics(lessons: tp.List[Lesson], group_id: str, subgroup: int = 1) -> bool:
    try:
        # form an ics calendar
        calendar = Calendar()

        # create a calendar event for each lesson
        for lesson in lessons:
            lesson_event = Event()
            lesson_event.name = f'{lesson.title} [{lesson.type}]'
            lesson_event.begin = lesson.start_time.strftime('%Y-%m-%d %H:%M:%S')
            lesson_event.end = lesson.end_time.strftime('%Y-%m-%d %H:%M:%S')

            description = []
            if lesson.location:
                description.append(f'Место: {lesson.location}')
            if lesson.course_link:
                description.append(f'Moodle: {lesson.course_link}')
            if description:
                lesson_event.description = '\n'.join(description)

            # add event to the calendar
            calendar.events.add(lesson_event)

        # save the calendar to an ics file
        with open(f'processed_schedule/{group_id}-{subgroup}.ics', 'w') as file:
            file.writelines(calendar)

        return True

    except Exception as E:
        print(f'An error occured while converting lessons:\n{E}')
        return False


# retrieve schedule
def retrieve_schedule(group_id: str) -> bool:
    base_url: str = 'https://guide.herzen.spb.ru/static/schedule_dates.php'
    schedule_url: str = f'{base_url}?id_group={group_id}&date1=2021-01-01&date2='
    request = requests.get(schedule_url)

    if not request.ok:
        print(f'Error retrieving schedule. Request code: {request.status_code}.')
        return False
    else:
        with open(f'raw_schedule/{group_id}.html', 'w') as file:
            file.writelines(request.text)
        return True
