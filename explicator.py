#!/usr/bin/env python
import DBConnection
import dialog
from globals import *
import gtk
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
        window.set_default_size(800, 600)
        window.set_position(gtk.WIN_POS_CENTER)
        DBConnection.open_connection()

        self.pid = None
        self.tid = None
        self.aid = None
        self.selectparent = False
        self.selectchild = False
        self.tooltips = gtk.Tooltips()

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
        self.projectlist = gtk.ListStore(int, str, str)
        self.projecttree = gtk.TreeView(self.projectlist)
        self.projecttree.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        self.projecttree.set_enable_search(True)
        self.projecttree.set_search_column(1)
        self.projecttree.append_column(gtk.TreeViewColumn("Projects", gtk.CellRendererText(), text=1, foreground=2))
        self.projecttree.get_selection().connect('changed', lambda s: self.on_projecttreeview_selection_changed(s))
        self.projecttree.set_headers_visible(False)

        #projectproperties
        self.projectproperties = gtk.VBox()
        self.projectproperties.set_size_request(175, 155)
        label = gtk.Label()
        label.set_alignment(0, 0)
        label.set_markup("<big><b>Project Details</b></big>")
        self.projectproperties.pack_start(label, False)
        label = gtk.Label("Name")
        label.set_alignment(0.0, 0.0)
        self.projectproperties.pack_start(label, False)
        self.ProjectNameEntry = gtk.Entry(max=50)
        self.ProjectNameEntry.set_sensitive(False)
        self.ProjectNameEntry.modify_text(gtk.STATE_INSENSITIVE, gtk.gdk.color_parse("#000000"))
        self.projectproperties.pack_start(self.ProjectNameEntry, False)
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
        self.ProjectPriorityEntry.set_sensitive(False)
        self.ProjectPriorityEntry.modify_text(gtk.STATE_INSENSITIVE, gtk.gdk.color_parse("#000000"))
        hbox.pack_start(vbox, False)
        vbox = gtk.VBox()
        label = gtk.Label("Priority")
        label.set_alignment(0.0, 0.0)
        vbox.pack_start(label)
        vbox.pack_start(self.ProjectPriorityEntry)
        hbox.pack_start(vbox)
        self.projectproperties.pack_start(hbox, False, padding=5)

        #TaskProperties
        self.TaskProperties = gtk.VBox()
        self.TaskProperties.set_size_request(200, 155)
        header = gtk.HBox()
        label = gtk.Label()
        label.set_alignment(0, 0)
        label.set_markup("<big><b>Task</b></big>")
        header.pack_start(label)
        image = gtk.Image()
        image.set_from_file("data/add.png")
        btnaddtask = gtk.Button()
        self.tooltips.set_tip(btnaddtask, "Add Task")
        btnaddtask.add(image)
        btnaddtask.connect('clicked', self.add_task)
        image = gtk.Image()
        image.set_from_file("data/remove.png")
        btnremtask = gtk.Button()
        self.tooltips.set_tip(btnremtask, "Remove Task")
        btnremtask.add(image)
        btnremtask.connect('clicked', self.remove_task)
        image = gtk.Image()
        image.set_from_file("data/edit.png")
        btnedttask = gtk.Button()
        self.tooltips.set_tip(btnedttask, "Edit Task")
        btnedttask.add(image)
        btnedttask.connect('clicked', self.edit_task)
        header.pack_start(btnaddtask, False)
        header.pack_start(btnremtask, False)
        header.pack_start(btnedttask, False)
        self.TaskProperties.pack_start(header, False)
        label = gtk.Label("Name")
        label.set_alignment(0, 0)
        self.TaskProperties.pack_start(label, False)
        self.TaskNameEntry = gtk.Entry(max=50)
        self.TaskNameEntry.set_sensitive(False)
        self.TaskNameEntry.modify_text(gtk.STATE_INSENSITIVE, gtk.gdk.color_parse("#000000"))
        self.TaskProperties.pack_start(self.TaskNameEntry, False)
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
        self.TaskDueDateEntry.set_sensitive(False)
        self.TaskDueDateEntry.modify_text(gtk.STATE_INSENSITIVE, gtk.gdk.color_parse("#000000"))
        hbox.pack_start(vbox, False)
        vbox = gtk.VBox()
        label = gtk.Label("Due Date")
        label.set_alignment(0, 0)
        vbox.pack_start(label)
        vbox.pack_start(self.TaskDueDateEntry)
        hbox.pack_start(vbox)
        self.TaskProperties.pack_start(hbox, False, padding=5)
        hbox = gtk.HBox()
        btntoggleparent = gtk.Button('Toggle Parent')
        btntoggleparent.connect('clicked', self.toggle_parent_selection)
        hbox.pack_start(btntoggleparent)
        btntogglechild = gtk.Button('Toggle Child')
        btntogglechild.connect('clicked', self.toggle_child_selection)
        hbox.pack_start(btntogglechild)
        self.TaskProperties.pack_start(hbox)


        #Treeview actions
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
        self.actions = gtk.VBox()
        self.actions.set_size_request(400, 155)

        header = gtk.HBox()
        label = gtk.Label()
        label.set_alignment(0, 0)
        label.set_markup("<big><b>Actions</b></big>")
        header.pack_start(label)
        image = gtk.Image()
        image.set_from_file("data/add.png")
        btnaddact = gtk.Button()
        self.tooltips.set_tip(btnaddact, "Add Action")
        btnaddact.add(image)
        btnaddact.connect('clicked', self.add_action)
        image = gtk.Image()
        image.set_from_file("data/remove.png")
        btnremact = gtk.Button()
        self.tooltips.set_tip(btnremact, "Remove Action")
        btnremact.add(image)
        btnremact.connect('clicked', self.remove_action)
        image = gtk.Image()
        image.set_from_file("data/edit.png")
        btnedtact = gtk.Button()
        self.tooltips.set_tip(btnedtact, "Edit Action")
        btnedtact.add(image)
        btnedtact.connect('clicked', self.edit_action)
        btncnvact = gtk.Button('To Task')
        self.tooltips.set_tip(btncnvact, "Convert Action to Task")
        btncnvact.connect('clicked', self.convert_action_to_task)
        header.pack_start(btnaddact, False)
        header.pack_start(btnremact, False)
        header.pack_start(btnedtact, False)
        header.pack_start(btncnvact, False)
        self.actions.pack_start(header, False)
        scroller = gtk.ScrolledWindow()
        scroller.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scroller.add(self.actiontree)
        self.actions.pack_start(scroller)


        #set xdot
        self.widget = xdot.DotWidget()

        # Create a UIManager instance
        uimanager = self.uimanager = gtk.UIManager()

        # Add the accelerator group to the toplevel windowilttei
        accelgroup = uimanager.get_accel_group()
        window.add_accel_group(accelgroup)

        # Create an ActionGroup
        actiongroup = gtk.ActionGroup('actions')
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
        self.navbox = gtk.VBox()
        self.navbox.set_size_request(175, 300)
        header = gtk.HBox()
        label = gtk.Label()
        label.set_alignment(0, 0)
        label.set_markup("<big><b>Categories</b></big>")
        header.pack_start(label)
        self.navbox.pack_start(header, False)
        scroller = gtk.ScrolledWindow()
        scroller.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scroller.add(self.tagtree)
        self.navbox.pack_start(scroller)
        hseparator = gtk.HSeparator()
        self.navbox.pack_start(hseparator, False)
        header = gtk.HBox()
        label = gtk.Label()
        label.set_alignment(0, 0)
        label.set_markup("<big><b>Projects</b></big>")
        header.pack_start(label)
        image = gtk.Image()
        image.set_from_file("data/add.png")
        btnaddpro = gtk.Button()
        self.tooltips.set_tip(btnaddpro, "Add Project")
        btnaddpro.add(image)
        btnaddpro.connect('clicked', self.add_project)
        image = gtk.Image()
        image.set_from_file("data/remove.png")
        btnrempro = gtk.Button()
        self.tooltips.set_tip(btnrempro, "Remove Project")
        btnrempro.add(image)
        btnrempro.connect('clicked', self.remove_project)
        image = gtk.Image()
        image.set_from_file("data/edit.png")
        btnedtpro = gtk.Button()
        self.tooltips.set_tip(btnedtpro, "Edit Project")
        btnedtpro.add(image)
        btnedtpro.connect('clicked', self.edit_project)
        header.pack_start(btnaddpro, False)
        header.pack_start(btnrempro, False)
        header.pack_start(btnedtpro, False)
        self.navbox.pack_start(header, False)
        scroller = gtk.ScrolledWindow()
        scroller.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scroller.add(self.projecttree)
        self.navbox.pack_start(scroller)

        hbox.pack_start(self.navbox, False)
        vseparator = gtk.VSeparator()
        hbox.pack_start(vseparator, False)

        vbox = gtk.VBox()
        hbox.pack_start(vbox)

        # Setup property box
        hbox = gtk.HBox()
        hbox.pack_start(self.projectproperties, False)
        vseparator = gtk.VSeparator()
        hbox.pack_start(vseparator, False, padding=3)
        hbox.pack_start(self.TaskProperties, False)
        vseparator = gtk.VSeparator()
        hbox.pack_start(vseparator, False, padding=3)
        hbox.pack_start(self.actions, False)

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

    def check_dependency(self, tid):
        if DBConnection.get_task_status(tid) == hold:
            set_released = True
            for status in DBConnection.get_status_all_parents(tid):
                if DBConnection.get_task_status(status) != done:
                    set_released = False
            if set_released:
                DBConnection.update_table("task", "status = '%(status)s'" % {"status":released}, tid)
        elif DBConnection.get_task_status(tid) == released:
            set_released = True
            for status in DBConnection.get_status_all_parents(tid):
                if DBConnection.get_task_status(status) != done:
                    set_released = False
            if not set_released:
                DBConnection.update_table("task", "status = '%(status)s'" % {"status":hold}, tid)
        self.cascade(tid)

    def on_url_clicked(self, widget, url, event):
        if self.selectparent and self.tid is not None:
            DBConnection.toggle_dependency(get_task_id(url), self.tid)
            self.selectparent = False
            self.refresh_view()
        elif self.selectchild and self.tid is not None:
            DBConnection.toggle_dependency(self.tid, get_task_id(url))
            self.selectchild = False
            self.check_dependency(self.tid)
            self.check_dependency(get_task_id(url))
            self.refresh_view()
        else:
            self.pid = get_project_id(url)
            self.tid = get_task_id(url)
            self.aid = None
            taskdata = DBConnection.get_data("task", self.tid)
            self.TaskNameEntry.set_text(taskdata[1])
            for index, status in enumerate(statuslist):
                if taskdata[3] == status:
                    self.TaskStatusCombo.set_active(index)
            self.TaskDueDateEntry.set_text(taskdata[4])
            self.refresh_actionlist()
        self.set_interface_lock(False)

    def on_tagtreeview_selection_changed(self, selection):
        self.refresh_projects(self.get_selection_strings(selection))

    def on_actiontreeview_selection_changed(self, selection):
        (model, rownrs) = selection.get_selected_rows()
        for row in rownrs:
            iter = model.get_iter(row)
            self.aid = model.get_value(iter, 0)

    def on_projecttreeview_selection_changed(self, selection, clear=True):
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
        if clear:
            self.clear_task_properties()
            self.clear_actions()

    def fill_project_properties(self):
        projectdata = DBConnection.get_data("project", self.pid)
        self.ProjectNameEntry.set_text(projectdata[1])
        for index, status in enumerate(statuslist):
            if projectdata[2] == status:
                self.ProjectStatusCombo.set_active(index)
        self.ProjectPriorityEntry.set_text(str(projectdata[3]))

    def on_action_toggled(self, cell, path, model):
        DBConnection.toggle_action(model[path][0])
        initial_status = DBConnection.get_task_status(self.tid)
        completed_all = True
        for row in DBConnection.get_actionlist(self.tid):
            if not row[3]:
                completed_all = False
        if completed_all:
            DBConnection.update_table("task", "status = '%(status)s'" % {"status":done}, self.tid)
            self.check_dependency(self.tid)
        elif initial_status == done:
            DBConnection.update_table("task", "status = '%(status)s'" % {"status":released}, self.tid)
            self.check_dependency(self.tid)
        self.refresh_actionlist()
        self.refresh_view()

    def refresh_view(self, resize=True):
        if resize:
            x, y = self.widget.get_current_pos()
            z = self.widget.zoom_ratio
        self.on_projecttreeview_selection_changed(self.projecttree.get_selection(), False)
        if resize:
            self.widget.zoom_ratio = z
            self.widget.set_current_pos(x, y)

    def refresh_tags(self):
        tags = self.get_selection_strings(self.tagtree.get_selection())
        self.taglist.clear()
        for row in DBConnection.get_tags():
            self.taglist.append([row[0], ])
        selection = self.tagtree.get_selection()
        self.tagtree.get_model().foreach(self.set_selection, (tags, selection))

    def set_selection(self, model, path, iter, data):
        tree_iter = model.get_iter(path)
        if model.get_value(tree_iter, 0) in data[0]:
            data[1].select_path(path)

    def refresh_projects(self, tags=None):
        projects = self.get_selection_strings(self.projecttree.get_selection())
        self.projectlist.clear()
        for row in DBConnection.get_projects(tags):
            self.projectlist.append([row[0], row[1], get_color_from_status(row[2])])
        selection = self.projecttree.get_selection()
        self.projecttree.get_model().foreach(self.set_selection, (projects, selection))

    def refresh_actionlist(self):
        self.actionlist.clear()
        for row in DBConnection.get_actionlist(self.tid):
            self.actionlist.append([row[0], row[1], row[2], row[3]])

    def refresh_graph(self, dotcode):
        window.set_dotcode(dotcode)

    def on_status_change_task(self, combobox):
        if self.tid is not None:
            taskdata = DBConnection.get_data("task", self.tid)
            if taskdata[3] != get_active_text(combobox):
                DBConnection.update_table("task", "status = '%(status)s'" % {"status": get_active_text(combobox)},
                    self.tid)
                self.cascade(self.tid)
                self.refresh_view()

    def on_status_change_project(self, combobox):
        if self.pid is not None:
            taskdata = DBConnection.get_data("project", self.pid)
            if taskdata[2] != get_active_text(combobox):
                DBConnection.update_table("project", "status = '%(status)s'" %
                                                     {"status": get_active_text(combobox)}, self.pid)


    def clear_project_properties(self):
        self.pid = None
        self.ProjectNameEntry.set_text("")
        self.ProjectPriorityEntry.set_text("")
        self.ProjectStatusCombo.set_active(-1)

    def clear_task_properties(self):
        self.tid = None
        self.TaskDueDateEntry.set_text("")
        self.TaskNameEntry.set_text("")
        self.TaskStatusCombo.set_active(-1)

    def clear_actions(self):
        self.actionlist.clear()
        self.aid = None

    def add_project(self, widget):
        if dialog.show_project_dialog():
            self.refresh_tags()
            self.clear_actions()
            self.clear_task_properties()

    def edit_project(self, widget):
        if self.pid is not None:
            if dialog.show_project_dialog(self.pid):
                selection = self.tagtree.get_selection()
                self.refresh_tags()
                self.on_tagtreeview_selection_changed(selection)

    def add_task(self, widget):
        if self.pid is not None:
            if dialog.show_task_dialog(self.pid):
                self.refresh_view(False)
                self.clear_task_properties()

    def edit_task(self, widget):
        if self.pid is not None and self.tid is not None:
            if dialog.show_task_dialog(self.pid, self.tid):
                self.cascade(self.tid)
                self.cascade(self.tid)
                self.refresh_view()

    def remove_task(self, widget):
        taskdata = DBConnection.get_data("task", self.tid)
        if dialog.show_confirm_dialog(
            "Are you sure you want to delete '%(taskname)s'? All dependencies and actions for this task will be removed." % {
                "taskname": taskdata[1]}):
            DBConnection.remove_task(self.tid)
            for child in DBConnection.get_childs(self.tid):
                self.check_dependency(child)
            self.refresh_view()
            self.clear_actions()
            self.clear_task_properties()

    def remove_project(self, widget):
        if self.pid is not None:
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
            if dialog.show_action_dialog(self.tid):
                self.refresh_actionlist()
                self.refresh_view()

    def edit_action(self, widget):
        if self.tid is not None:
            if dialog.show_action_dialog(self.tid, self.aid):
                self.refresh_actionlist()
                self.refresh_view()

    def remove_action(self, widget):
        if self.aid is not None:
            DBConnection.remove_action(self.aid)
            self.refresh_actionlist()
            self.refresh_view()

    def toggle_parent_selection(self, widget):
        if not self.selectparent:
            self.selectparent = True
            self.selectchild = False
            self.set_interface_lock(True)
        else:
            self.selectparent = False
            self.selectchild = False
            self.set_interface_lock(False)


    def toggle_child_selection(self, widget):
        if not self.selectchild:
            self.selectparent = False
            self.selectchild = True
            self.set_interface_lock(True)
        else:
            self.selectparent = False
            self.selectchild = False
            self.set_interface_lock(False)


    def set_interface_lock(self, lock):
        if lock:
            self.projectproperties.set_sensitive(False)
            self.actions.set_sensitive(False)
            self.navbox.set_sensitive(False)
        else:
            self.projectproperties.set_sensitive(True)
            self.actions.set_sensitive(True)
            self.navbox.set_sensitive(True)

    def get_selection_strings(self, selection):
        strings = []
        (model, rownrs) = selection.get_selected_rows()
        for row in rownrs:
            iter = model.get_iter(row)
            strings.append(model.get_value(iter, 0))
        return strings

    def convert_action_to_task(self, widget):
        if self.pid is not None and self.aid is not None:
            actiondata = DBConnection.get_data("action", self.aid)
            DBConnection.add_task(self.pid, actiondata[1], "available", "1901-01-01")
            self.remove_action(widget)

    def cascade(self, tid, trace = None):
        if trace is None:
            trace = []
        if tid not in trace:
            trace.append(tid)
            for child in DBConnection.get_childs(tid):
                parent_status = DBConnection.get_task_status(tid)
                child_status = DBConnection.get_task_status(child)
                if child_status == hold and parent_status == release_trigger :
                    valid_update = True
                    for status in DBConnection.get_status_all_parents(child):
                        if DBConnection.get_task_status(status) != done:
                            valid_update = False
                    if valid_update:
                        DBConnection.update_table("task", "status = '%(status)s'" % {"status":released}, child)
                        self.cascade(child, trace)
                elif child_status not in (ignore, done) and parent_status != release_trigger :
                    DBConnection.update_table("task", "status = '%(status)s'" % {"status":hold}, child)
                    self.cascade(child, trace)

if __name__ == "__main__":
    window = MyDotWindow()
    window.set_title("Explicator")
    window.connect('destroy', gtk.main_quit)
    gtk.main()