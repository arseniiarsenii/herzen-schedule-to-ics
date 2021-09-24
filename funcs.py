import re
import typing as tp
from datetime import datetime
from os import path

import requests
from bs4 import BeautifulSoup
from dateutil import tz
from ics import Calendar
from loguru import logger

from classes import Lesson

# keep track of schedules that are currently being worked on
# or have caused an error
request_queue: tp.Dict[int, str] = dict()


def status_in_queue(group_id: int) -> tp.Optional[str]:
    """check if a schedule is currently being worked on or has an error logged"""
    return request_queue.get(group_id)


def add_to_queue(group_id: int) -> None:
    """add to queue with working status"""
    request_queue[group_id] = "Working"


def remove_from_queue(group_id: int) -> None:
    """remove from queue to indicate finishing work on a schedule"""
    request_queue.pop(group_id, None)


def log_error_in_queue(group_id: int, message: str, dev_message: tp.Optional[str] = None) -> None:
    """log an error in queue and terminal"""
    request_queue[group_id] = message
    logger.info(dev_message or message)


@logger.catch
def set_up_schedule(group_id: int, subgroup_no: int) -> None:
    """download html, parse it and make the .ics file"""
    add_to_queue(group_id)

    # download schedule HTML page if not present
    if path.exists(f"raw_schedule/{group_id}.html"):
        logger.info(f"Schedule for group_id={group_id} already saved. Loading up.")
    elif fetch_schedule(group_id):
        logger.info(f"Schedule for group_id={group_id} retrieved successfully.")
    else:
        message = "Ошибка при загрузке расписания с серверов РГПУ. Возможно, сервера недоступны?"
        dev_message = f"Error retrieving schedule for group_id={group_id}."
        log_error_in_queue(group_id, message, dev_message)
        return
    # convert HTML schedule to an array of Lesson objects
    try:
        lessons = convert_html_to_lesson(f"{group_id}.html", subgroup_no)
    except Exception as E:
        message = "Ошибка при обработке расписания. Возможно, неверно указан номер подгруппы?"
        dev_message = f"Error converting HTML for group {group_id}, subgroup {subgroup_no} into Lesson objects: {E}"
        log_error_in_queue(group_id, message, dev_message)
        return

    if convert_lesson_to_ics(lessons, group_id, subgroup_no):
        remove_from_queue(group_id)
        logger.info(f"Successful ics conversion for group_id={group_id}, subgroup_no={subgroup_no}. File saved.")
    else:
        message = "Ошибка при конвертации расписания в файл."
        dev_message = f"Failed to convert to ics for group_id={group_id}, subgroup_no={subgroup_no}."
        log_error_in_queue(group_id, message, dev_message)
        return


@logger.catch
def convert_html_to_lesson(filename: str, subgroup: int) -> tp.List[Lesson]:
    """convert schedule html page with a given filename into a list of Lesson objects"""
    # parse schedule
    with open(f"raw_schedule/{filename}", "r") as f:
        soup = BeautifulSoup(f, "html.parser")
    schedule = soup.find("table", class_="schedule")
    table_rows = schedule.find("tbody").find_all("tr")
    logger.debug(f"Schedule table contains {len(table_rows)} rows.")
    all_lessons = []
    date = None

    # iterate through the rows of the schedule table
    for row in table_rows:
        # if row contains date, parse it
        day_name = row.find("th", class_="dayname")
        if day_name is not None:
            date = day_name.text.split(",")[0]
            continue

        # if row is not date, assume it is a lesson entry.
        # initialize a Lesson object and fill it's fields with data parsed from the row

        # get lesson's start and end times
        try:
            timeframe: tp.List[str] = row.find("th").text.split(" — ")
            logger.debug(timeframe)
        except AttributeError:
            logger.debug(repr(row))
            continue

        # get string timestamps
        start_time_: str = f"{date} {timeframe[0]}"
        end_time_: str = f"{date} {timeframe[1]}"
        # convert to datetime objects
        start_time: datetime = (
            datetime.strptime(start_time_, "%d.%m.%Y %H:%M")
            .replace(tzinfo=tz.gettz("Europe/Moscow"))
            .astimezone(tz.tzutc())
        )
        end_time: datetime = (
            datetime.strptime(end_time_, "%d.%m.%Y %H:%M")
            .replace(tzinfo=tz.gettz("Europe/Moscow"))
            .astimezone(tz.tzutc())
        )

        # extract lesson type
        lesson_data = row.find_all("td")

        if len(lesson_data) > 1:
            lesson_data = lesson_data[subgroup - 1]
        elif not 1 <= subgroup <= 2:
            raise IndexError
        else:
            lesson_data = lesson_data[0]

        try:
            lesson_type = re.findall("\[.*\]", lesson_data.text)[0][1:-1]
        except IndexError:
            lesson_type = None

        # extract lesson title
        try:
            lesson_title = lesson_data.find("strong").text
        except AttributeError:
            try:
                lesson_title = lesson_data.find("strong").find("a").text
            except AttributeError:
                continue

        # extract lesson's online course link if present
        course_link = lesson_data.find("strong").find("a")
        lesson_course_link = course_link["href"] if course_link else None

        # extract lesson's location
        try:
            lesson_location = re.findall("</a>, .*</td>", str(lesson_data))[-1][6:-5]
        except IndexError:
            lesson_location = None

        # extract teacher
        teacher = None

        try:
            for hl in lesson_data.find_all("a"):
                if "atlas" in hl["href"]:
                    teacher = hl.text.strip()
        except TypeError:
            pass

        # save lesson instance for future use
        lesson = Lesson(
            title=lesson_title,
            start_time=start_time,
            end_time=end_time,
            teacher=teacher,
            type=lesson_type,
            location=lesson_location,
            course_link=lesson_course_link,
        )
        all_lessons.append(lesson)

    return all_lessons


@logger.catch
def convert_lesson_to_ics(lessons: tp.List[Lesson], group_id: int, subgroup: int = 1) -> bool:
    """convert a list of Lesson object instances into an ics file and save it. returns status"""
    try:
        calendar = Calendar()
        for lesson in lessons:
            calendar.events.add(lesson.ics_event)
        with open(f"processed_schedule/{group_id}-{subgroup}.ics", "w") as file:
            file.writelines(calendar)
        return True

    except Exception as E:
        logger.error(f"An error occurred while converting lessons:\n{E}")
        return False


@logger.catch
def fetch_schedule(group_id: int) -> bool:
    """fetch schedule"""
    base_url = "https://guide.herzen.spb.ru/static/schedule_dates.php"
    today = datetime.today()
    start_of_year = datetime(today.year, 1, 1)
    start_of_school_year = datetime(today.year, 9, 1)

    if start_of_year <= today <= start_of_school_year:
        start = start_of_year.isoformat().split("T")[0]
    else:
        start = start_of_school_year.isoformat().split("T")[0]

    schedule_url = f"{base_url}?id_group={group_id}&date1={start}&date2="
    request = requests.get(schedule_url)

    if not request.ok:
        logger.error(f"Error retrieving schedule for group_id={group_id}. Request code: {request.status_code}.")
        return False

    else:
        with open(f"raw_schedule/{group_id}.html", "w") as file:
            file.writelines(request.text)

        return True


def fetch_subgroups(group_id: int) -> int:
    """fetch static schedule and count the number of subgroups"""
    today = datetime.today().isoformat().split("T")[0]
    url = f"https://guide.herzen.spb.ru/static/schedule_dates.php?id_group={group_id}&date1={today}&date2={today}"
    html = requests.get(url).text
    return html.count("подгруппа")
