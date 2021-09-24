import typing as tp
from dataclasses import dataclass
from datetime import datetime

import ics


@dataclass(frozen=True)
class Lesson:
    """Lesson object with corresponding attributes"""

    title: str  # lesson name
    type: str  # type e.g. lecture, lab, etc.
    start_time: datetime  # datetime object
    end_time: datetime  # datetime object
    course_link: tp.Optional[str] = None  # moodle link
    location: tp.Optional[str] = None  # address or online
    teacher: tp.Optional[str] = None  # name of the teacher

    @property
    def ics_event(self) -> ics.Event:
        event = ics.Event()
        event.name = f"{self.title} [{self.type}]" if self.type else self.title
        event.begin = self.start_time.strftime("%Y-%m-%d %H:%M:%S")
        event.end = self.end_time.strftime("%Y-%m-%d %H:%M:%S")

        description = []
        if self.location:
            description.append(f"Место: {self.location}")
            event.location = self.location
        if self.course_link:
            description.append(f"Moodle: {self.course_link}")
        if self.teacher:
            description.append(f"Преподаватель: {self.teacher}")
        if description:
            event.description = "\n".join(description)

        return event
