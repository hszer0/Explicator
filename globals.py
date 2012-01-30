import re

statuslist = 'active', 'available', 'canceled', 'completed', 'on hold'
colorlist = 'forestgreen', 'black', 'red', 'grey', 'blue'

def get_project_id(url):
    return re.split(r'\D', url)[1]


def get_task_id(url):
    return re.split(r'\D', url)[2]


def get_color_from_status(status):
    for s, c in zip(statuslist, colorlist):
        if s == status:
            return c
    return 'black'


