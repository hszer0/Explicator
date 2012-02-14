import sqlite3, shutil, ConfigParser
from globals import *

try:
    open("settings.cfg").close()
except IOError:
    shutil.copy("default.cfg", "settings.cfg")

config = ConfigParser.ConfigParser()
config.readfp(open("settings.cfg"))
dbpath = config.get('Database', 'Path')
dbpath = dbpath.replace("\\", "\\\\")

try:
    open(dbpath).close()
except IOError:
    shutil.copy("tutorial.db", dbpath)

conn = sqlite3.connect(dbpath)
conn.isolation_level = None
c = conn.cursor()

def open_connection():
    c.execute("PRAGMA foreign_keys = ON;")


def get_tags(pid = None):
    tg = conn.cursor()
    if pid is None:
        tg.execute("select distinct tag from tag order by tag")
    else:
        tg.execute("select distinct tag from tag where pid = %(pid)s order by tag" % {"pid":pid})
    return tg


def get_projects(taglist):
    if taglist:
        tags = []
        for tag in taglist:
            tags.append("'" + tag + "'")
        c.execute("select id, name from project where id in (select pid from tag where tag in (" + ",".join(
            tags) + ")) order by name")
    else:
        c.execute("select id, name from project order by name")
    return c


def close_connection():
    c.close()


def get_dependencies(pid):
    c.execute("""select pid, parentid, childid from taskdependency
                 join task on task.id = taskdependency.parentid and task.pid = %(pid)s """ % {"pid": pid})
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
    """ % {"pid": pid})
    for row in c:
        dependencies += "P" + str(row[0]) + "T" + str(row[1]) + "; "
    return dependencies


def get_actionlist(tid):
    cur = conn.cursor()
    cur.execute("""
    select * from action where tid = %(tid)s
    """ % {"tid": tid})
    return cur


def get_actions(tid):
    actions = ''
    cur = conn.cursor()
    cur.execute("""
    select * from action where tid = %(tid)s
    """ % {"tid": tid})
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
        projects.append(str(project).replace('"',r'\"'))

    c.execute("select * from task where pid in (%(projects)s)" % {"projects": ",".join(projects)})
    for row in c:
        dotcode += """
        %(pid_tid)s [
            URL = "%(pid_tid)s"
            label = "%(name)s|%(tasks)s|{Status:\l|%(status)s\l}|{Due:\l|%(due)s\l}"
            color = %(color)s
            fontcolor = %(color)s
        ]
        """ % {"tasks": get_actions(row[0]).replace('"',r'\"'), "name": row[1].replace('"',r'\"'), "status": row[3], "due": row[4],
               "pid_tid": "P" + str(row[2]) + "T" + str(row[0]), "color": get_color_from_status(row[3])}

    for pid in projectlist:
        c.execute("select name from project where id = %(id)s" % {"id": pid})
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
        """ % {"dependencies": get_dependencies(pid), "pid": pid, "label": name}
    dotcode += """
    }
    """
    return dotcode


def get_data(table, id):
    c.execute("select * from %(table)s where id = %(id)s" % {"table": table, "id": id})
    return c.fetchone()


def toggle_action(id):
    c.execute("update action set completed = not completed where id = %(id)s" % {"id": id})


def add_project(name, status, priority):
    c.execute(
        "insert into project (name, status, priority) values ('%(name)s', '%(status)s', %(priority)s)" %
        {"name": name.replace("'", "''"), "status": status, "priority": priority})
    c.execute("select max(id) from project")
    row = c.fetchone()
    return row[0]


def add_task(pid, name, status, date):
    c.execute("insert into task (name, pid, status, duedate) values ('%(name)s', %(pid)s, '%(status)s', '%(date)s')" % {
        "name": name.replace("'", "''"), "pid": pid, "status": status, "date": date})


def remove_project(pid):
    c.execute("delete from tag where pid = %(pid)s" % {"pid": pid})
    c.execute("select id from task where pid = %(pid)s" % {"pid": pid})
    for row in c:
        remove_task(row[0])
    c.execute("delete from project where id = %(pid)s" % {"pid": pid})


def remove_task(tid):
    cur = conn.cursor()
    cur.execute("delete from taskdependency where %(tid)s in (parentid, childid)" % {"tid": tid})
    cur.execute("delete from action where tid = %(tid)s" % {"tid": tid})
    cur.execute("delete from task where id = %(tid)s" % {"tid": tid})


def update_table(table, command, id):
    c.execute("update %(table)s set %(command)s where id = %(id)s" % {"table": table, "command": command, "id": id})


def add_action(name, tid, completed, warningdate):
    c.execute(
        "insert into action (name, tid, completed, warningdate) values ('%(name)s', %(tid)s, %(completed)s, '%(warningdate)s')" % {
            "name": name.replace("'", "''"), "tid": tid, "completed": completed, "warningdate": warningdate})


def remove_action(aid):
    c.execute("delete from action where id = %(aid)s" % {"aid": aid})

def toggle_dependency(parent, child):
    c.execute("select * from taskdependency where parentid = %(parent)s and childid = %(child)s" % {"parent":parent, "child":child})
    i = 0
    for row in c:
        i += 1
    if i == 0:
        c.execute("insert into taskdependency (parentid, childid) values (%(parent)s, %(child)s)" % {"parent":parent, "child":child})
    else:
        c.execute("delete from taskdependency where parentid = %(parent)s and childid = %(child)s" % {"parent":parent, "child":child})

def set_tags(pid, tags):
    c.execute("delete from tag where pid = %(pid)s" % {"pid":pid})
    for tag in tags.split(","):
        c.execute("insert into tag (pid, tag) values (%(pid)s, '%(tag)s')" % {"pid":pid, "tag":tag})