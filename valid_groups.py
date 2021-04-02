import re
import requests
import lxml
import typing as tp
from bs4 import BeautifulSoup

# keep groups cached since they rarely change
# groups_cache[group_id] == group_name
groups_cache: tp.Dict[int, str] = dict()


def fetch_groups() -> tp.Dict[int, str]:
    # fetch groups if they are not cached
    if not groups_cache:
        # regex for finding group ids in html params
        # 5 digits after 'id_group='
        group_id_re = re.compile('(?<=id_group=)\\d{5}')

        # fetch html and make soup
        html = requests.get('https://guide.herzen.spb.ru/static/schedule.php').content
        soup = BeautifulSoup(html, features='lxml')

        # get the element with the relevant information
        schedule = soup.select('td.body > div')[0]

        # get departments (institute, faculty, etc.)
        dept_names = [d.get_text() for d in schedule.select('h3 a')]
        dept_forms = schedule.find_all('div', recursive=False)

        for i in range(len(dept_names)):
            dept = dept_forms[i]

            # get forms of education (full time, part time or both)
            form_names = [d.get_text() for d in dept.find_all('h4', recursive=False)]
            form_groups = dept.find_all('ul', recursive=False)

            for j in range(len(form_names)):
                form = form_groups[j]

                # get groups
                groups = form.find_all('li', recursive=False)

                for group in groups:
                    # get name and join it with dept and form names
                    group_name = group.contents[0]
                    group_full_name = ', '.join([dept_names[i], form_names[j], group_name])
                    # find group id param in the element
                    group_id = int(group_id_re.search(str(group)).group())
                    # capitalize first letter and write to cache
                    groups_cache[group_id] = group_full_name[0].upper() + group_full_name[1:]

    return groups_cache


# check if a group id is present among all groups
def group_id_is_valid(group_id: int) -> bool:
    # call in case groups are not fetched yet
    fetch_groups()
    return group_id in groups_cache.keys()
