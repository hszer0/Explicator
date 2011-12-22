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
    projectdialog.show_all()
    response = projectdialog.run()


show_project_dialog()