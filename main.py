#!/usr/bin/env python
import sys
import DBConnection
import dialog
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
import xdot

def get_active_text(combobox):
    model = combobox.get_model()
    active = combobox.get_active()
    if active < 0:
        return None
    return model[active][0]


class MyDotWindow(xdot.DotWindow):
    ui = '''
    <ui>
        <toolbar name="ToolBar">
            <toolitem action="ZoomIn"/>
            <toolitem action="ZoomOut"/>
            <toolitem action="ZoomFit"/>
            <toolitem action="Zoom100"/>
        </toolbar>
    </ui>
    '''

    def __init__(self):
        gtk.Window.__init__(self)
        self.graph = xdot.Graph()
        window = self
        window.set_title('Explicator')
        window.set_default_size(800, 600)
        window.set_position(gtk.WIN_POS_CENTER)
        DBConnection.open_connection()

        self.pid = None
        self.tid = None
        self.aid = None

        #Treeview with Tags
        self.taglist = gtk.ListStore(str)
        self.tagtree = gtk.TreeView(self.taglist)
        tagselection = self.tagtree.get_selection()
        tagselection.set_mode(gtk.SELECTION_MULTIPLE)
        self.tagtree.set_enable_search(True)
        self.tagtree.set_search_column(0)
        self.tagtree.get_selection().connect('changed', lambda s: self.on_tagtreeview_selection_changed(s))
        self.tagtree.append_column(gtk.TreeViewColumn("", gtk.CellRendererText(), text=0))
        self.tagtree.set_headers_visible(False)

        #Treeview with Projects
        self.projectlist = gtk.ListStore(int, str)
        self.projecttree = gtk.TreeView(self.projectlist)
        self.projecttree.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        self.projecttree.set_enable_search(True)
        self.projecttree.set_search_column(1)
        self.projecttree.append_column(gtk.TreeViewColumn("Projects", gtk.CellRendererText(), text=1))
        self.projecttree.get_selection().connect('changed', lambda s: self.on_projecttreeview_selection_changed(s))
        self.projecttree.set_headers_visible(False)

        #ProjectProperties
        ProjectProperties = gtk.VBox()
        ProjectProperties.set_size_request(150, 135)
        label = gtk.Label()
        label.set_alignment(0, 0)
        label.set_markup("<big><b>Project Details</b></big>")
        ProjectProperties.pack_start(label, False)
        label = gtk.Label("Name")
        label.set_alignment(0.0, 0.0)
        ProjectProperties.pack_start(label, False)
        self.ProjectNameEntry = gtk.Entry(max=50)
        self.ProjectNameEntry.set_state(gtk.STATE_INSENSITIVE)
        ProjectProperties.pack_start(self.ProjectNameEntry, False)
        hbox = gtk.HBox()
        vbox = gtk.VBox()
        label = gtk.Label("Status")
        label.set_alignment(0.0, 0.0)
        vbox.pack_start(label)
        self.ProjectStatusCombo = gtk.combo_box_new_text()
        for status in statuslist:
            self.ProjectStatusCombo.append_text(status)
        self.ProjectStatusCombo.connect('changed', self.on_status_change_project)
        vbox.pack_start(self.ProjectStatusCombo)
        self.ProjectPriorityEntry = gtk.Entry(max=3)
        self.ProjectPriorityEntry.set_state(gtk.STATE_INSENSITIVE)
        hbox.pack_start(vbox, False)
        vbox = gtk.VBox()
        label = gtk.Label("Priority")
        label.set_alignment(0.0, 0.0)
        vbox.pack_start(label)
        vbox.pack_start(self.ProjectPriorityEntry)
        hbox.pack_start(vbox)
        ProjectProperties.pack_start(hbox, False, padding=5)

        #TaskProperties
        TaskProperties = gtk.VBox()
        TaskProperties.set_size_request(170, 135)
        header = gtk.HBox()
        label = gtk.Label()
        label.set_alignment(0, 0)
        label.set_markup("<big><b>Task</b></big>")
        header.pack_start(label)
        btnaddtask = gtk.Button('+')
        btnaddtask.set_size_request(20, 0)
        btnaddtask.connect('clicked', self.add_task)
        btnremtask = gtk.Button('-')
        btnremtask.set_size_request(20, 0)
        btnremtask.connect('clicked', self.remove_task)
        btnedttask = gtk.Button('...')
        btnedttask.set_size_request(20, 0)
        btnedttask.connect('clicked', self.edit_task)
        header.pack_start(btnaddtask, False)
        header.pack_start(btnremtask, False)
        header.pack_start(btnedttask, False)
        TaskProperties.pack_start(header, False)
        label = gtk.Label("Name")
        label.set_alignment(0, 0)
        TaskProperties.pack_start(label, False)
        self.TaskNameEntry = gtk.Entry(max=50)
        self.TaskNameEntry.set_state(gtk.STATE_INSENSITIVE)
        TaskProperties.pack_start(self.TaskNameEntry, False)
        hbox = gtk.HBox()
        vbox = gtk.VBox()
        label = gtk.Label("Status")
        label.set_alignment(0, 0)
        vbox.pack_start(label)
        self.TaskStatusCombo = gtk.combo_box_new_text()
        for status in statuslist:
            self.TaskStatusCombo.append_text(status)
        self.TaskStatusCombo.connect('changed', self.on_status_change_task)

        vbox.pack_start(self.TaskStatusCombo)
        self.TaskDueDateEntry = gtk.Entry(max=10)
        self.TaskDueDateEntry.set_state(gtk.STATE_INSENSITIVE)
        hbox.pack_start(vbox, False)
        vbox = gtk.VBox()
        label = gtk.Label("Due Date")
        label.set_alignment(0, 0)
        vbox.pack_start(label)
        vbox.pack_start(self.TaskDueDateEntry)
        hbox.pack_start(vbox)
        TaskProperties.pack_start(hbox, False, padding=5)

        #Treeview Actions
        self.actionlist = gtk.ListStore(int, str, int, bool)
        self.actiontree = gtk.TreeView(self.actionlist)
        self.actiontree.get_selection().connect('changed', lambda s: self.on_actiontreeview_selection_changed(s))
        actionselection = self.tagtree.get_selection()
        actionselection.set_mode(gtk.SELECTION_MULTIPLE)
        self.checkbox = gtk.CellRendererToggle()
        self.checkbox.set_property('activatable', True)
        self.column1 = gtk.TreeViewColumn("Completed", self.checkbox)
        self.column1.add_attribute(self.checkbox, "active", 3)
        self.column1.set_max_width(100)
        self.checkbox.connect('toggled', self.on_action_toggled, self.actionlist)
        self.actiontree.append_column(self.column1)
        self.actiontree.append_column(gtk.TreeViewColumn("Action", gtk.CellRendererText(), text=1))
        self.actiontree.set_headers_visible(False)

        #Action box
        Actions = gtk.VBox()
        Actions.set_size_request(400, 135)

        header = gtk.HBox()
        label = gtk.Label()
        label.set_alignment(0, 0)
        label.set_markup("<big><b>Actions</b></big>")
        header.pack_start(label)
        btnaddact = gtk.Button('+')
        btnaddact.connect('clicked', self.add_action)
        btnaddact.set_size_request(20, 0)
        btnremact = gtk.Button('-')
        btnremact.connect('clicked', self.remove_action)
        btnremact.set_size_request(20, 0)
        btnedtact = gtk.Button('...')
        btnedtact.connect('clicked', self.edit_action)
        btnedtact.set_size_request(20, 0)
        header.pack_start(btnaddact, False)
        header.pack_start(btnremact, False)
        header.pack_start(btnedtact, False)
        Actions.pack_start(header, False)
        scroller = gtk.ScrolledWindow()
        scroller.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scroller.add(self.actiontree)
        Actions.pack_start(scroller)


        #set xdot
        self.widget = xdot.DotWidget()

        # Create a UIManager instance
        uimanager = self.uimanager = gtk.UIManager()

        # Add the accelerator group to the toplevel windowilttei
        accelgroup = uimanager.get_accel_group()
        window.add_accel_group(accelgroup)

        # Create an ActionGroup
        actiongroup = gtk.ActionGroup('Actions')
        self.actiongroup = actiongroup

        # Create actions
        actiongroup.add_actions((
            ('ZoomIn', gtk.STOCK_ZOOM_IN, None, None, None, self.widget.on_zoom_in),
            ('ZoomOut', gtk.STOCK_ZOOM_OUT, None, None, None, self.widget.on_zoom_out),
            ('ZoomFit', gtk.STOCK_ZOOM_FIT, None, None, None, self.widget.on_zoom_fit),
            ('Zoom100', gtk.STOCK_ZOOM_100, None, None, None, self.widget.on_zoom_100),
            ))

        # Add the actiongroup to the uimanager
        uimanager.insert_action_group(actiongroup, 0)

        # Add a UI description
        uimanager.add_ui_from_string(self.ui)

        # Set up layout
        hbox = gtk.HBox()
        window.add(hbox)

        #set Tag/Project box
        vbox = gtk.VBox()
        vbox.set_size_request(150, 300)
        header = gtk.HBox()
        label = gtk.Label()
        label.set_alignment(0, 0)
        label.set_markup("<big><b>Tags</b></big>")
        header.pack_start(label)
        btnaddtag = gtk.Button('+')
        btnaddtag.set_size_request(20, 0)
        btnremtag = gtk.Button('-')
        btnremtag.set_size_request(20, 0)
        btnedttag = gtk.Button('...')
        btnedttag.set_size_request(20, 0)
        header.pack_start(btnaddtag, False)
        header.pack_start(btnremtag, False)
        header.pack_start(btnedttag, False)
        vbox.pack_start(header, False)
        scroller = gtk.ScrolledWindow()
        scroller.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scroller.add(self.tagtree)
        vbox.pack_start(scroller)
        hseparator = gtk.HSeparator()
        vbox.pack_start(hseparator, False)
        header = gtk.HBox()
        label = gtk.Label()
        label.set_alignment(0, 0)
        label.set_markup("<big><b>Projects</b></big>")
        header.pack_start(label)
        btnaddpro = gtk.Button('+')
        btnaddpro.set_size_request(20, 0)
        btnaddpro.connect('clicked', self.add_project)
        btnrempro = gtk.Button('-')
        btnrempro.set_size_request(20, 0)
        btnrempro.connect('clicked', self.remove_project)
        btnedtpro = gtk.Button('...')
        btnedtpro.set_size_request(20, 0)
        btnedtpro.connect('clicked', self.edit_project)
        header.pack_start(btnaddpro, False)
        header.pack_start(btnrempro, False)
        header.pack_start(btnedtpro, False)
        vbox.pack_start(header, False)
        scroller = gtk.ScrolledWindow()
        scroller.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scroller.add(self.projecttree)
        vbox.pack_start(scroller)

        hbox.pack_start(vbox, False)
        vseparator = gtk.VSeparator()
        hbox.pack_start(vseparator, False)

        vbox = gtk.VBox()
        hbox.pack_start(vbox)

        # Setup property box
        hbox = gtk.HBox()
        hbox.pack_start(ProjectProperties, False)
        vseparator = gtk.VSeparator()
        hbox.pack_start(vseparator, False, padding=3)
        hbox.pack_start(TaskProperties, False)
        vseparator = gtk.VSeparator()
        hbox.pack_start(vseparator, False, padding=3)
        hbox.pack_start(Actions, False)

        # Create a Toolbar
        toolbar = uimanager.get_widget('/ToolBar')
        vbox.pack_start(toolbar, False)

        vbox.pack_start(self.widget)
        hseparator = gtk.HSeparator()
        vbox.pack_start(hseparator, False)
        vbox.pack_start(hbox, False)

        self.set_focus(self.widget)
        self.refresh_tags()
        self.refresh_projects()
        self.widget.connect('clicked', self.on_url_clicked)
        self.show_all()

    def on_url_clicked(self, widget, url, event):
        self.pid = get_project_id(url)
        self.tid = get_task_id(url)
        taskdata = DBConnection.get_data("task", self.tid)
        self.TaskNameEntry.set_text(taskdata[1])
        for index, status in enumerate(statuslist):
            if taskdata[3] == status:
                self.TaskStatusCombo.set_active(index)
        self.TaskDueDateEntry.set_text(taskdata[4])
        self.refresh_actionlist()

    def on_tagtreeview_selection_changed(self, selection):
        tags = []
        (model, rownrs) = selection.get_selected_rows()
        for row in rownrs:
            iter = model.get_iter(row)
            tags.append("'" + model.get_value(iter, 0) + "'")
        self.refresh_projects(tags)

    def on_actiontreeview_selection_changed(self, selection):
        (model, rownrs) = selection.get_selected_rows()
        for row in rownrs:
            iter = model.get_iter(row)
            self.aid = model.get_value(iter, 0)

    def on_projecttreeview_selection_changed(self, selection):
        projects = []
        (model, rownrs) = selection.get_selected_rows()
        for row in rownrs:
            iter = model.get_iter(row)
            projects.append(model.get_value(iter, 0))
        dotcode = DBConnection.generate_dotcode(projects)
        self.refresh_graph(dotcode)
        if len(rownrs) == 1:
            self.pid = projects[0]
            self.fill_project_properties()
        else:
            self.clear_project_properties()

    def fill_project_properties(self):
        projectdata = DBConnection.get_data("project", self.pid)
        self.ProjectNameEntry.set_text(projectdata[1])
        for index, status in enumerate(statuslist):
            if projectdata[2] == status:
                self.ProjectStatusCombo.set_active(index)
        self.ProjectPriorityEntry.set_text(str(projectdata[3]))


    def on_action_toggled(self, cell, path, model):
        DBConnection.toggle_action(model[path][0])
        self.refresh_actionlist()
        self.refresh_view()

    def refresh_view(self, resize=True):
        if resize:
            x, y = self.widget.get_current_pos()
            z = self.widget.zoom_ratio
        self.on_projecttreeview_selection_changed(self.projecttree.get_selection())
        if resize:
            self.widget.zoom_ratio = z
            self.widget.set_current_pos(x, y)

    def refresh_tags(self):
        self.taglist.clear()
        for row in DBConnection.get_tags():
            self.taglist.append([row[0], ])

    def refresh_projects(self, tags=None):
        self.projectlist.clear()
        for row in DBConnection.get_projects(tags):
            self.projectlist.append([row[0], row[1]])
        self.clear_project_properties()
        self.clear_task_properties()
        self.clear_actions()

    def refresh_actionlist(self):
        self.actionlist.clear()
        for row in DBConnection.get_actionlist(self.tid):
            self.actionlist.append([row[0], row[1], row[2], row[3]])

    def refresh_graph(self, dotcode):
        window.set_dotcode(dotcode)

    def on_status_change_task(self, combobox):
        taskdata = DBConnection.get_data("task", self.tid)
        if taskdata[3] != get_active_text(combobox):
            DBConnection.update_table("task", "status = '%(status)s'" % {"status": get_active_text(combobox)}, self.tid)
            self.refresh_view()

    def on_status_change_project(self, combobox):
        taskdata = DBConnection.get_data("project", self.pid)
        if taskdata[2] != get_active_text(combobox):
            DBConnection.update_table("project", "status = '%(status)s'" %
                                                 {"status": get_active_text(combobox)}, self.pid)


    def clear_project_properties(self):
        self.ProjectNameEntry.set_text("")
        self.ProjectPriorityEntry.set_text("")
        self.ProjectStatusCombo.set_active(-1)
        self.pid = None

    def clear_task_properties(self):
        self.TaskDueDateEntry.set_text("")
        self.TaskNameEntry.set_text("")
        self.TaskStatusCombo.set_active(-1)
        self.tid = None

    def clear_actions(self):
        self.actionlist.clear()
        self.aid = None

    def add_project(self, widget):
        dialog.show_project_dialog()
        selection = self.tagtree.get_selection()
        self.on_tagtreeview_selection_changed(selection)
        self.clear_actions()
        self.clear_task_properties()

    def edit_project(self, widget):
        if self.pid is not None:
            dialog.show_project_dialog(self.pid)
            selection = self.tagtree.get_selection()
            self.on_tagtreeview_selection_changed(selection)

    def add_task(self, widget):
        if self.pid is not None:
            dialog.show_task_dialog(self.pid)
            self.refresh_view()
            self.clear_actions()
            self.clear_task_properties()

    def edit_task(self, widget):
        if self.pid is not None and self.tid is not None:
            dialog.show_task_dialog(self.pid, self.tid)
            self.refresh_view()

    def remove_task(self, widget):
        taskdata = DBConnection.get_data("task", self.tid)
        if dialog.show_confirm_dialog(
            "Are you sure you want to delete '%(taskname)s'? All dependencies and actions for this task will be removed." % {
                "taskname": taskdata[1]}):
            DBConnection.remove_task(self.tid)
            self.refresh_view()
            self.clear_actions()
            self.clear_task_properties()

    def remove_project(self, widget):
        projectdata = DBConnection.get_data("project", self.pid)
        if dialog.show_confirm_dialog(
            "Are you sure you want to delete '%(projectname)s'? All items within the project will be removed." % {
                "projectname": projectdata[1]}):
            DBConnection.remove_project(self.pid)
            selection = self.tagtree.get_selection()
            self.on_tagtreeview_selection_changed(selection)
            self.refresh_tags()
            self.clear_actions()
            self.clear_task_properties()

    def add_action(self, widget):
        if self.tid is not None:
            dialog.show_action_dialog(self.tid)
            self.refresh_actionlist()
            self.refresh_view()

    def edit_action(self, widget):
        if self.tid is not None:
            dialog.show_action_dialog(self.tid, self.aid)
            self.refresh_actionlist()
            self.refresh_view()

    def remove_action(self, widget):
        if self.aid is not None:
            DBConnection.remove_action(self.aid)
            self.refresh_actionlist()
            self.refresh_view()


if __name__ == "__main__":
    window = MyDotWindow()
    window.connect('destroy', gtk.main_quit)
    gtk.main()