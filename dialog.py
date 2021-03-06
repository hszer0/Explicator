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

import sys
from globals import *
import DBConnection

try:
    import pygtk

    pygtk.require("2.0")
except:
    pass
try:
    import gtk
except:
    sys.exit(1)

def get_active_text(combobox):
    model = combobox.get_model()
    active = combobox.get_active()
    if active < 0:
        return None
    return model[active][0]


def show_task_dialog(pid, tid=None):
    taskdialog = gtk.Dialog(title="Task", flags=gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
        buttons=(gtk.STOCK_SAVE, gtk.RESPONSE_ACCEPT, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))

    taskdialog.vbox.set_size_request(200, 175)
    label = gtk.Label()
    label.set_alignment(0, 0)
    if tid is None:
        label.set_markup("<big><b>Add Task</b></big>")
    else:
        label.set_markup("<big><b>Edit Task</b></big>")
    taskdialog.vbox.pack_start(label, False)
    label = gtk.Label("Name")
    label.set_alignment(0.0, 0.0)
    taskdialog.vbox.pack_start(label, False)
    taskdialog.TaskNameEntry = gtk.Entry(max=50)
    taskdialog.TaskNameEntry.set_activates_default(True)
    taskdialog.vbox.pack_start(taskdialog.TaskNameEntry, False)
    hbox = gtk.HBox()
    vbox = gtk.VBox()
    label = gtk.Label("Status")
    label.set_alignment(0.0, 0.0)
    vbox.pack_start(label)
    taskdialog.TaskStatusCombo = gtk.combo_box_new_text()
    for status in statuslist:
        taskdialog.TaskStatusCombo.append_text(status)
    vbox.pack_start(taskdialog.TaskStatusCombo)
    taskdialog.TaskDateEntry = gtk.Entry(max=10)
    taskdialog.TaskDateEntry.set_activates_default(True)
    hbox.pack_start(vbox, False)
    vbox = gtk.VBox()
    label = gtk.Label("Due Date")
    label.set_alignment(0.0, 0.0)
    vbox.pack_start(label)
    vbox.pack_start(taskdialog.TaskDateEntry)
    hbox.pack_start(vbox)
    taskdialog.vbox.pack_start(hbox, False, padding=5)
    taskdialog.set_default_response(gtk.RESPONSE_ACCEPT)

    if tid is not None:
        taskdata = DBConnection.get_data("task", tid)
        taskdialog.TaskNameEntry.set_text(taskdata[1])
        for index, status in enumerate(statuslist):
            if taskdata[3] == status:
                taskdialog.TaskStatusCombo.set_active(index)
        taskdialog.TaskDateEntry.set_text(taskdata[4])
    else:
        taskdialog.TaskStatusCombo.set_active(1)

    taskdialog.set_position(gtk.WIN_POS_CENTER)
    taskdialog.show_all()
    response = taskdialog.run()

    if response == gtk.RESPONSE_ACCEPT:
        if tid is None:
            DBConnection.add_task(pid, taskdialog.TaskNameEntry.get_text(), get_active_text(taskdialog.TaskStatusCombo),
                taskdialog.TaskDateEntry.get_text())
            taskdialog.destroy()
        else:
            DBConnection.update_table("task", "name = '%(name)s', status = '%(status)s', duedate = '%(duedate)s'" %
                                              {"name": taskdialog.TaskNameEntry.get_text().replace("'", "''"),
                                               "status": get_active_text(taskdialog.TaskStatusCombo),
                                               "duedate": taskdialog.TaskDateEntry.get_text()}, tid)
            taskdialog.destroy()
        return True

    taskdialog.destroy()
    return False


def show_project_dialog(pid=None):
    projectdialog = gtk.Dialog(title="Project", flags=gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
        buttons=(gtk.STOCK_SAVE, gtk.RESPONSE_ACCEPT, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))

    projectdialog.vbox.set_size_request(250, 215)
    label = gtk.Label()
    label.set_alignment(0, 0)
    if pid is None:
        label.set_markup("<big><b>Add Project</b></big>")
    else:
        label.set_markup("<big><b>Edit Project</b></big>")
    projectdialog.vbox.pack_start(label, False)
    label = gtk.Label("Name")
    label.set_alignment(0.0, 0.0)
    projectdialog.vbox.pack_start(label, False)
    projectdialog.ProjectNameEntry = gtk.Entry(max=50)
    projectdialog.ProjectNameEntry.set_activates_default(True)
    projectdialog.vbox.pack_start(projectdialog.ProjectNameEntry, False)
    hbox = gtk.HBox()
    vbox = gtk.VBox()
    label = gtk.Label("Status")
    label.set_alignment(0.0, 0.0)
    vbox.pack_start(label)
    projectdialog.ProjectStatusCombo = gtk.combo_box_new_text()
    for status in statuslist:
        projectdialog.ProjectStatusCombo.append_text(status)
    vbox.pack_start(projectdialog.ProjectStatusCombo)
    projectdialog.ProjectPriorityEntry = gtk.Entry(max=3)
    hbox.pack_start(vbox, False)
    vbox = gtk.VBox()
    label = gtk.Label("Priority")
    label.set_alignment(0.0, 0.0)
    vbox.pack_start(label)
    vbox.pack_start(projectdialog.ProjectPriorityEntry)
    hbox.pack_start(vbox)
    projectdialog.vbox.pack_start(hbox, False, padding=5)
    label = gtk.Label("Categories (comma seperated)")
    label.set_alignment(0.0, 0.0)
    projectdialog.vbox.pack_start(label)
    projectdialog.ProjectTagEntry = gtk.Entry()
    projectdialog.ProjectTagEntry.set_activates_default(True)
    projectdialog.vbox.pack_start(projectdialog.ProjectTagEntry, False)
    projectdialog.set_default_response(gtk.RESPONSE_ACCEPT)

    if pid is not None:
        projectdata = DBConnection.get_data("project", pid)
        projectdialog.ProjectNameEntry.set_text(projectdata[1])
        for index, status in enumerate(statuslist):
            if projectdata[2] == status:
                projectdialog.ProjectStatusCombo.set_active(index)
        projectdialog.ProjectPriorityEntry.set_text(str(projectdata[3]))
        projectdialog.ProjectTagEntry.set_text(",".join(tag[0] for tag in DBConnection.get_tags(pid)))
    else:
        projectdialog.ProjectStatusCombo.set_active(1)
        projectdialog.ProjectPriorityEntry.set_text("100")
    projectdialog.set_position(gtk.WIN_POS_CENTER_ALWAYS)
    projectdialog.show_all()
    response = projectdialog.run()

    if response == gtk.RESPONSE_ACCEPT:
        if projectdialog.ProjectPriorityEntry.get_text().isdigit():
            if pid is None:
                pid = DBConnection.add_project(projectdialog.ProjectNameEntry.get_text(),
                    get_active_text(projectdialog.ProjectStatusCombo), projectdialog.ProjectPriorityEntry.get_text())
            else:
                DBConnection.update_table("project",
                    "name = '%(name)s', status = '%(status)s', priority = %(priority)s" % {
                        "name": projectdialog.ProjectNameEntry.get_text().replace("'", "''"),
                        "status": get_active_text(projectdialog.ProjectStatusCombo),
                        "priority": projectdialog.ProjectPriorityEntry.get_text()}, pid)
            DBConnection.set_tags(pid, projectdialog.ProjectTagEntry.get_text().replace(", ", ","))
            projectdialog.destroy()
        return True
    else:
        projectdialog.destroy()
        return False


def show_action_dialog(tid, aid=None):
    actiondialog = gtk.Dialog(title="Action", flags=gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
        buttons=(gtk.STOCK_SAVE, gtk.RESPONSE_ACCEPT, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))

    actiondialog.vbox.set_size_request(250, 135)
    label = gtk.Label()
    label.set_alignment(0, 0)
    if aid is None:
        label.set_markup("<big><b>Add Action</b></big>")
    else:
        label.set_markup("<big><b>Edit Action</b></big>")

    actiondialog.vbox.pack_start(label, False)
    label = gtk.Label("Name")
    label.set_alignment(0.0, 0.0)
    actiondialog.vbox.pack_start(label, False)
    actiondialog.actionentry = gtk.Entry(max=50)
    actiondialog.actionentry.set_activates_default(True)
    actiondialog.vbox.pack_start(actiondialog.actionentry, False)
    #    label = gtk.Label("Warning Date")
    #    label.set_alignment(0.0, 0.0)
    #    actiondialog.vbox.pack_start(label, False)
    #    actiondialog.warningentry = gtk.Entry(max=50)
    #    actiondialog.vbox.pack_start(actiondialog.warningentry, False)
    actiondialog.set_position(gtk.WIN_POS_CENTER_ALWAYS)
    actiondialog.set_default_response(gtk.RESPONSE_ACCEPT)

    if aid is not None:
        actiondata = DBConnection.get_data("action", aid)
        actiondialog.actionentry.set_text(actiondata[1])

    actiondialog.show_all()
    response = actiondialog.run()

    if response == gtk.RESPONSE_ACCEPT:
        if aid is None:
            DBConnection.add_action(actiondialog.actionentry.get_text(), tid, 0,
                "1901-01-01")
        else:
            DBConnection.update_table("action",
                "name = '%(name)s', tid = %(tid)s" % {
                    "name": actiondialog.actionentry.get_text().replace("'", "''"), "tid": tid}, aid)
        actiondialog.destroy()
        return True
    else:
        actiondialog.destroy()
        return False


def show_confirm_dialog(message):
    confirmdialog = gtk.Dialog(title="Confirm", flags=gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
        buttons=(gtk.STOCK_YES, gtk.RESPONSE_ACCEPT, gtk.STOCK_NO, gtk.RESPONSE_CANCEL))
    label = gtk.Label(message)
    label.set_alignment(0.0, 0.0)
    confirmdialog.vbox.pack_start(label)
    confirmdialog.set_position(gtk.WIN_POS_CENTER)
    confirmdialog.show_all()
    confirmdialog.set_default_response(gtk.RESPONSE_ACCEPT)
    response = confirmdialog.run()
    confirmdialog.destroy()
    return response == gtk.RESPONSE_ACCEPT