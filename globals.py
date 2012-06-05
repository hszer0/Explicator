#Copyright 2011-2012 Patrick Liem
#
#This file is part of Explicator.
#
#Explicator is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#Explicator is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with Explicator.  If not, see <http://www.gnu.org/licenses/>.

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

