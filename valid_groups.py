import re
import requests
import lxml
from bs4 import BeautifulSoup

groups_cache = dict()


def fetch_groups():
    if not groups_cache:
        html = requests.get("https://guide.herzen.spb.ru/static/schedule.php").content
        soup = BeautifulSoup(html, features="lxml")

        schedule = soup.select("td.body > div")[0]
        dept_names = [d.get_text() for d in schedule.select("h3 a")]
        dept_forms = schedule.find_all("div", recursive=False)

        for i in range(len(dept_names)):
            dept = dept_forms[i]

            form_names = [d.get_text() for d in dept.find_all("h4", recursive=False)]
            form_groups = dept.find_all("ul", recursive=False)

            group_id_re = re.compile("(?<=id_group=)\\d{5}")
            for j in range(len(form_names)):
                form = form_groups[j]

                groups = form.find_all("li", recursive=False)

                for group in groups:
                    group_name = ", ".join([dept_names[i], form_names[j], group.contents[0]])
                    group_id = int(group_id_re.search(str(group)).group())
                    groups_cache[group_id] = group_name[0].upper() + group_name[1:]

    return groups_cache


def group_id_is_valid(group_id: int):
    return group_id in groups_cache.keys()
