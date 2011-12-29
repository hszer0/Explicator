#!/usr/bin/env python
import sys
import DBConnection
from globals import *

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


def show_project_dialog(pid=None):
    projectdialog = gtk.Dialog(title = "Project", flags = gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, buttons = (gtk.STOCK_SAVE, gtk.RESPONSE_ACCEPT, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
    dhbox = gtk.HBox()

    ProjectProperties = gtk.VBox()
    ProjectProperties.set_size_request(150, 135)
    label = gtk.Label()
    label.set_alignment(0,0)
    label.set_markup("<big><b>Project Details</b></big>")
    ProjectProperties.pack_start(label, False)
    label = gtk.Label("Name")
    label.set_alignment(0.0, 0.0)
    ProjectProperties.pack_start(label, False)
    projectdialog.ProjectNameEntry = gtk.Entry(max=50)
    ProjectProperties.pack_start(projectdialog.ProjectNameEntry, False)
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
    ProjectProperties.pack_start(hbox, False, padding = 5)
    dhbox.pack_start(ProjectProperties)
    projectdialog.vbox.pack_start(dhbox)

    if pid is not None:
        projectdata = DBConnection.get_project_data(pid)
        projectdialog.ProjectNameEntry.set_text(projectdata[1])
        for index, status in enumerate(statuslist):
            if projectdata[2] == status:
                projectdialog.ProjectStatusCombo.set_active(index)
        projectdialog.ProjectPriorityEntry.set_text(str(projectdata[3]))

    projectdialog.show_all()
    response = projectdialog.run()
    if response == gtk.RESPONSE_ACCEPT:
        if pid is None:
            DBConnection.add_project(projectdialog.ProjectNameEntry.get_text(), get_active_text(projectdialog.ProjectStatusCombo), projectdialog.ProjectPriorityEntry.get_text())
        else:
            DBConnection.update_project("name = '%(name)s', status = '%(status)s', priority = %(priority)s" % {"name":projectdialog.ProjectNameEntry.get_text(), "status":get_active_text(projectdialog.ProjectStatusCombo), "priority":projectdialog.ProjectPriorityEntry.get_text()}, pid)

    projectdialog.destroy()