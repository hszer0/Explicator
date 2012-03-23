import re

statuslist = 'active', 'available', 'on hold', 'canceled', 'completed'
colorlist = 'forestgreen', 'black', 'blue', 'red', 'grey'
release_trigger = 'completed'
released = 'available'
hold = 'on hold'
ignore = 'canceled'
done = 'completed'

def get_project_id(url):
    return re.split(r'\D', url)[1]

def get_task_id(url):
    return re.split(r'\D', url)[2]

def get_color_from_status(status):
    for s, c in zip(statuslist, colorlist):
        if s == status:
            return c
    return 'black'

