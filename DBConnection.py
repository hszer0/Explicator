import sqlite3
from globals import *

conn = sqlite3.connect("explicator.db")
c = conn.cursor()

def open_connection():
    c.execute("PRAGMA foreign_keys = ON;")

def get_tags():
    c.execute("select tag from tag")
    return c

def get_projects(tags):
    if tags:
        c.execute("select id, name from project where id in (select pid from tag where tag in (" + ",".join(tags) + ")) order by name")
    else:
        c.execute("select id, name from project order by name")
    return c

def close_connection():
    c.close()

def get_dependencies(pid):
    c.execute("""select pid, parentid, childid from taskdependency
                 join task on task.id = taskdependency.parentid and task.pid = %(pid)s """ % {"pid":pid})
    dependencies = ""
    for row in c:
        dependencies += "P" + str(row[0]) + "T" + str(row[1]) + " -> P" + str(row[0]) + "T" + str(row[2]) + "; "
    c.execute("""
    select t.pid, t.id
    from task t
    where t.id not in
    (select parentid from taskdependency join task on task.id = taskdependency.parentid and task.pid = %(pid)s
    union
    select childid from taskdependency join task on task.id = taskdependency.parentid and task.pid = %(pid)s)
    and t.pid = %(pid)s
    """ % {"pid":pid})
    for row in c:
        dependencies += "P" + str(row[0]) + "T" + str(row[1]) + "; "
    return dependencies

def get_actionlist(tid):
    cur = conn.cursor()
    cur.execute("""
    select * from action where tid = %(tid)s
    """ % {"tid":tid})
    return cur

def get_actions(tid):
    actions = ''
    cur = conn.cursor()
    cur.execute("""
    select * from action where tid = %(tid)s
    """ % {"tid":tid})
    for row in cur:
        if row[3]:
            actions += "\[v\] - " + str(row[1]) + "\l"
        else:
            actions += "\[_\] - " + str(row[1]) + "\l"
    return actions

def generate_dotcode(projectlist=None):
    dotcode = """
    digraph explicator {
        fontname = "Bitstream Vera Sans"
        rankdir = LR
        fontsize = 8
        node [
                fontname = "Bitstream Vera Sans"
                fontsize = 10
                shape = "record"
                style=filled
                fillcolor=white
        ]
        edge [
                fontname = "Bitstream Vera Sans"
                fontsize = 8
            ]
        """
    projects = []
    for project in projectlist:
        projects.append(str(project))

    c.execute("select * from task where pid in (%(projects)s)" % {"projects":",".join(projects)})
    for row in c:
        dotcode += """
        %(pid_tid)s [
            URL = "%(pid_tid)s"
            label = "%(name)s|%(tasks)s|{Status:\l|%(status)s\l}|{Due:\l|%(due)s\l}"
            color = %(color)s
            fontcolor = %(color)s
        ]
        """ % {"tasks":get_actions(row[0]), "name":row[1], "status":row[3], "due":row[4], "pid_tid":"P" + str(row[2]) + "T" + str(row[0]),"color":get_color_from_status(row[3])}

    for pid in projectlist:
        c.execute("select name from project where id = %(id)s" % {"id":pid})
        name = c.fetchone()[0]
        dotcode += """
        subgraph cluster%(pid)s {
        style=filled;
        color=lightgrey;
        %(dependencies)s
        label = "%(label)s";
        labeljust = l
        fontname = "Bitstream Vera Sans";
        fontsize = 12;
        }
        """ % {"dependencies":get_dependencies(pid),"pid":pid,"label":name}
    dotcode += """
    }
    """
    return dotcode

def get_project_data(pid):
    c.execute("select * from project where id = %(pid)s" % {"pid":pid})
    return c.fetchone()

def get_task_data(tid):
    c.execute("select * from task where id = %(tid)s order by name" % {"tid":tid})
    return c.fetchone()

def toggle_action(id):
    c.execute("update action set completed = not completed where id = %(id)s" % {"id":id})
    conn.commit()

def update_task(command, tid):
    c.execute("update task set %(command)s where id = %(tid)s" % {"command":command, "tid":tid})
    conn.commit()

def update_project(command, pid):
    c.execute("update project set %(command)s where id = %(pid)s" % {"command":command, "pid":pid})
    conn.commit()

def add_project(name, status, priority):
    c.execute("insert into project (name, status, priority) values ('%(name)s', '%(status)s', %(priority)s)" % {"name":name, "status":status, "priority":priority})
    conn.commit()