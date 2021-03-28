import re
import typing as tp
from datetime import datetime
from dateutil import tz
from sys import exit

import requests
from bs4 import BeautifulSoup
from ics import Calendar, Event

# CONFIG
BASE_URL = 'https://guide.herzen.spb.ru/static/schedule_dates.php'
GROUP_ID = '12460'
SCHEDULE_URL = f'{BASE_URL}?id_group={GROUP_ID}'


# Lesson object with corresponding attributes
class Lesson:
    def __init__(self) -> None:
        self.title: str  # lesson name
        self.type: str  # type e.g. lecture, lab, etc.
        self.start_time: tp.Optional[datetime] = None  # datetime object
        self.end_time: tp.Optional[datetime] = None  # datetime object
        self.course_link: str = ''  # moodle link
        self.location: str = ''  # address or online


# retrieve schedule
request = requests.get(SCHEDULE_URL)

if not request.ok:
    exit(f'Error retrieving schedule. Server returned code {request.status_code}.')

# parse schedule
soup = BeautifulSoup(request.content, 'html.parser')
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

# form an ics calendar
calendar = Calendar()

# create a calendar event for each lesson
for lesson in all_lessons:
    lesson_event = Event()
    lesson_event.name = f'{lesson.title} [{lesson.type}]'
    lesson_event.begin = lesson.start_time.strftime('%Y-%m-%d %H:%M:%S')
    lesson_event.end = lesson.end_time.strftime('%Y-%m-%d %H:%M:%S')
    if lesson.location:
        lesson_event.location = lesson.location
    if lesson.course_link:
        lesson_event.description = f'Moodle: {lesson.course_link}'

    calendar.events.add(lesson_event)

# save the calendar to an ics file
with open('schedule.ics', 'w') as file:
    file.writelines(calendar)
