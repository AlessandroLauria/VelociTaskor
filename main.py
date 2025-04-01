from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.colorpicker import ColorPicker
from kivy.properties import (ColorProperty, BooleanProperty,
                             StringProperty, ObjectProperty)
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout

import os
import sys
import json
from datetime import datetime
from pathlib import Path

version = "1.0.0"

data = {
    "tabs": {
        1: {
            "title": "Tab 1",
            "color": [0.9, 0.43, 0.31, 1],
            "tasks": {
                1: {
                    "PROJECT": "project name",
                    "TASK": "task definition",
                    "OWNER": "myself",
                    "STATUS": "DONE",
                    "DATE": "2025-03-26",
                    "NOTE": "usefull notes"
                }
            }
        }
    }
}

class PathHandler():

    def __init__(self):
        pass

    @classmethod
    def get_resource_path(cls, relative_path):
        """Ottiene il percorso corretto per file inclusi nell'eseguibile."""
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.dirname(__file__), relative_path)

    @classmethod
    def get_data_path(cls, relative_path):
        """Restituisce il percorso della cartella in cui salvare i dati dell'app."""
        if sys.platform == "win32":  # Windows
            base_path = Path(os.getenv("LOCALAPPDATA", os.path.expanduser("~\\AppData\\Local\\VelociTaskor\\")))
        elif sys.platform == "darwin":  # macOS
            base_path = Path(os.path.expanduser("~/Library/Application Support/VelociTaskor/"))
        else:  # Linux (se necessario)
            base_path = Path(os.path.expanduser("~/.local/share/VelociTaskor/"))

        base_path.mkdir(parents=True, exist_ok=True)  # Crea la cartella se non esiste
        app_path = os.path.join(base_path, relative_path)
        return app_path

    @classmethod
    def icon_path(cls):
        return cls.get_resource_path(os.path.join("images", "VelociTaskorIcon.png")) #os.path.join(os.path.dirname(__file__), "images", "VelociTaskorIcon.png")

    @classmethod
    def save_path(cls):
        return cls.get_data_path("velocitaskor_data.json")#os.path.join(os.path.dirname(__file__), "velocitaskor_data.json")


class Save():

    def __init__(self):
        pass

    @classmethod
    def find_missing(cls, lst):
        lst = [int(x) for x in lst]
        if len(lst) < 2:
            return []
        return sorted(set(range(lst[0], lst[-1])) - set(lst))

    @classmethod
    def get_unique_tab_id(cls):
        missing_ids = cls.find_missing(list(data["tabs"].keys()))
        max_id = len(data["tabs"].keys()) + 1
        new_id = missing_ids[0] if len(missing_ids) > 0 else max_id
        return new_id

    @classmethod
    def get_unique_row_id(cls, tab_id):
        tasks = list(data["tabs"][tab_id]["tasks"].keys())
        missing_ids = cls.find_missing(tasks)
        max_id = len(tasks) + 1
        new_id = missing_ids[0] if len(missing_ids) > 0 else max_id
        return new_id

    @classmethod
    def save_tab(cls, tab_id: int, tab_info):
        if tab_id in data["tabs"].keys():
            tasks = data["tabs"][tab_id]["tasks"]
            data["tabs"][tab_id] = tab_info
            data["tabs"][tab_id]["tasks"] = tasks
        else:
            data["tabs"][tab_id] = tab_info
        cls.save_data()

    @classmethod
    def save_row(cls, tab_id: int, row_id: int, row_info: str):
        tasks = data["tabs"][tab_id]["tasks"]
        tasks[row_id] = row_info
        cls.save_data()

    @classmethod
    def delete_tab(cls, tab_id):
        data["tabs"].pop(tab_id)
        cls.save_data()

    @classmethod
    def delete_row(cls, tab_id, row_id):
        data["tabs"][tab_id]["tasks"].pop(row_id)
        cls.save_data()

    @classmethod
    def load_data(cls):
        save_path = PathHandler.save_path()
        if os.path.isfile(save_path):
            with open(save_path, "r", encoding="utf-8") as file:
                global data
                data = json.load(file)

    @classmethod
    def save_data(cls):
        save_path = PathHandler.save_path()
        with open(save_path, "w", encoding="utf-8") as file:
            global data
            json.dump(data, file, indent=4)


class CustomTab(TabbedPanelItem):
    tab_color = ColorProperty([1, 1, 1, 1])
    background_color = tab_color
    original_text = StringProperty()
    preview_content = ObjectProperty(None)

    def __init__(self, id=-1, **kwargs):
        super().__init__(**kwargs)
        self.original_text = self.text
        self.preview_content = Label(
            text="Nessuna cella selezionata",
            halign="left",
            valign="top"
        )
        self.bind(on_touch_down=self.on_double_tap)
        self.last_tap_time = 0
        self.id = id

    def get_id(self):
        return self.id

    def on_double_tap(self, instance, touch):
        if self.collide_point(*touch.pos):
            current_time = Clock.get_time()
            if (current_time - self.last_tap_time) < 0.3:
                self.show_edit_popup()
                return True
            self.last_tap_time = current_time
        return False

    def show_edit_popup(self):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        name_input = TextInput(text=self.original_text)
        content.add_widget(name_input)

        color_picker = ColorPicker()
        color_picker.color = self.tab_color
        content.add_widget(color_picker)

        btn_layout = BoxLayout(size_hint_y=0.2, spacing=10)
        ok_btn = Button(text="OK")
        cancel_btn = Button(text="Cancel")

        def apply_changes(instance):
            self.original_text = name_input.text
            self.text = name_input.text
            self.tab_color = color_picker.color
            tab_info = {
                "title": self.text,
                "color": self.tab_color,
                "tasks": data["tabs"][self.id]["tasks"]
            }
            Save.save_tab(self.id, tab_info)
            popup.dismiss()

        ok_btn.bind(on_press=apply_changes)
        cancel_btn.bind(on_press=lambda x: popup.dismiss())

        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(ok_btn)
        content.add_widget(btn_layout)

        popup = Popup(title="Edit Tab", content=content, size_hint=(0.9, 0.9))
        popup.open()


class TableRow(GridLayout):
    selected = BooleanProperty(False)

    def __init__(self,
                 tab_id=-1,
                 id=-1,
                 project="",
                 task="",
                 owner="",
                 status="",
                 date="",
                 note="",
                 **kwargs):
        super().__init__(**kwargs)
        self.tab_id = tab_id
        self.id = id
        self.pjt = project
        self.tsk = task
        self.ownr = owner
        self.stat = status
        self.dt = date
        self.nt = note

        self.cols = 6
        self.size_hint_y = None
        self.height = dp(40)
        self.spacing = dp(2)
        self.status_value = "BACKLOG"
        self.create_widgets()
        self.bind(
            selected=self.update_selection,
            pos=self.update_graphics,
            size=self.update_graphics
        )

    def save_row(self, instance, value):
        row_info = {
            "PROJECT": self.project.text,
            "TASK": self.task.text,
            "OWNER": self.owner.text,
            "STATUS": self.status.text,
            "DATE": self.date.text,
            "NOTE": self.note.text
        }
        Save.save_row(self.tab_id, self.id, row_info)

    def create_widgets(self):
        self.project = TextInput(multiline=False)
        self.project.text = self.pjt
        self.project.bind(focus=self.on_cell_focus)
        self.project.bind(text=self.save_row)
        self.add_widget(self.project)

        self.task = TextInput(multiline=False)
        self.task.text = self.tsk
        self.task.bind(focus=self.on_cell_focus)
        self.task.bind(text=self.save_row)
        self.add_widget(self.task)

        self.owner = TextInput(multiline=False)
        self.owner.text = self.ownr
        self.owner.bind(focus=self.on_cell_focus)
        self.owner.bind(text=self.save_row)
        self.add_widget(self.owner)

        self.status = Spinner(
            text=self.stat,
            values=["BACKLOG", "IN PROGRESS", "DONE", "BLOCKED"],
            background_color=(0.8, 0.8, 0.8, 1)
        )
        self.status.bind(text=self.update_status)
        self.add_widget(self.status)

        self.date = Label(text=self.dt) #datetime.now().strftime("%Y-%m-%d"))
        self.add_widget(self.date)

        self.note = TextInput(multiline=False)
        self.note.text = self.nt
        self.note.bind(focus=self.on_cell_focus)
        self.note.bind(text=self.save_row)
        self.add_widget(self.note)

    def on_cell_focus(self, instance, value):
        if value:
            main_panel = App.get_running_app().root
            if hasattr(main_panel, 'current_tab') and isinstance(main_panel.current_tab, CustomTab):
                tab = main_panel.current_tab
                tab.preview_content.text = instance.text
                instance.bind(text=lambda x, t: setattr(tab.preview_content, 'text', t))

    def update_status(self, instance, value):
        self.status_value = value
        self.update_graphics()
        self.save_row(instance, value)

    def update_graphics(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            colors = {
                "BACKLOG": (0.8, 0.8, 0.8, 1),
                "IN PROGRESS": (0.91, 0.76, 0.41, 1),
                "DONE": (0.16, 0.6, 0.56, 1),
                "BLOCKED": (0.9, 0.43, 0.31, 1)
            }
            Color(*colors.get(self.status_value, (1, 1, 1, 1)))
            Rectangle(pos=self.pos, size=self.size)

    def update_selection(self, instance, value):
        self.canvas.after.clear()
        if value:
            with self.canvas.after:
                Color(0, 0, 1, 0.3)
                Rectangle(pos=self.pos, size=self.size)


class TableView(BoxLayout):
    selected_row = ObjectProperty(None, allownone=True)

    def __init__(self, id=-1, tasks={}, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(5)

        # Intestazione fissa
        self.header = GridLayout(cols=6, size_hint_y=None, height=dp(40), spacing=dp(2))
        headers = ["PROJECT", "TASK", "OWNER", "STATUS", "DATE", "NOTE"]
        for header in headers:
            btn = Button(text=header)
            btn.bind(on_press=lambda x, h=header: self.sort_by_column(h))
            self.header.add_widget(btn)
        self.add_widget(self.header)

        # Scrollview per le righe
        self.scroll_view = ScrollView()
        self.rows_layout = GridLayout(cols=1, size_hint_y=None, spacing=dp(5))
        self.rows_layout.bind(minimum_height=self.rows_layout.setter('height'))
        self.scroll_view.add_widget(self.rows_layout)
        self.add_widget(self.scroll_view)

        self.sort_reverse = False

        self.id = id
        self.tasks = tasks
        self.load_data()

    def load_data(self):
        for task_key in self.tasks.keys():
            task = self.tasks[task_key]
            self.add_row(task_key, task["PROJECT"], task["TASK"], task["OWNER"], task["STATUS"], task["DATE"], task["NOTE"])

    def on_touch_down(self, touch):
        if not self.rows_layout.collide_point(*touch.pos):
            if self.selected_row:
                self.selected_row.selected = False
                self.selected_row = None
        return super().on_touch_down(touch)

    def add_row(self, id=-1, project="", task="", owner="", status="BACKLOG", date=datetime.now().strftime("%Y-%m-%d"), note=""):
        new_row = TableRow(self.id, id, project, task, owner, status, date, note)
        new_row.bind(on_touch_down=lambda instance, t: self.select_row(instance, t))
        self.rows_layout.add_widget(new_row)
        new_row.update_status(None, status)
        new_row.save_row(None, None)

    def select_row(self, instance, touch):
        if instance.collide_point(*touch.pos):
            if self.selected_row:
                self.selected_row.selected = False
            instance.selected = True
            self.selected_row = instance
        else:
            if self.selected_row:
                self.selected_row.selected = False
                self.selected_row = None

    def sort_by_column(self, column_name):
        col_index = ["PROJECT", "TASK", "OWNER", "STATUS", "DATE", "NOTE"].index(column_name)
        rows = self.rows_layout.children.copy()

        def get_key(row):
            widget = row.children[5 - col_index]
            if isinstance(widget, Spinner):
                return widget.text
            elif isinstance(widget, TextInput):
                return widget.text.lower()
            return widget.text.lower()

        rows.sort(key=get_key, reverse=self.sort_reverse)
        self.rows_layout.clear_widgets()
        for row in rows:
            self.rows_layout.add_widget(row)

        self.sort_reverse = not self.sort_reverse


class MainPanel(TabbedPanel):
    bg_color = ColorProperty([1, 1, 1, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.default_tab_text = "Home"
        self.bg_color = [1, 1, 1, 1]
        self.do_default_tab = False
        self.show_home_screen()
        self.load_data()
        #self.add_widget(self.create_tab())
        self.bind(current_tab=self.update_bg_color)

    def load_data(self):
        tabs = data["tabs"]
        for tab_key in tabs.keys():
            tab = tabs[tab_key]
            self.add_widget(self.create_tab(tab_key, tab["title"], tab["color"], tab["tasks"]))

    def show_home_screen(self):
        """Mostra la schermata iniziale con icona, testo e pulsante centrati."""
        home_tab = TabbedPanelItem(text="Home")

        # Layout principale che permette il posizionamento libero
        layout = FloatLayout()

        # Icona 512x512 centrata
        icon = Image(source=PathHandler.icon_path(), size_hint=(None, None), size=(512, 512))
        icon.pos_hint = {'center_x': 0.5, 'center_y': 0.7}
        layout.add_widget(icon)

        # Testo introduttivo sotto l'icona
        intro_label = Label(
            text="""
                    Welcome to VelociTaskor!
                    Create and manage your tasks with ease.
                 """,
            halign="left",
            valign="middle",
            size_hint=(None, None),
            size=(900, 150)
        )
        intro_label.pos_hint = {'center_x': 0.5, 'center_y': 0.45}
        layout.add_widget(intro_label)

        intro_label = Label(
            text="""
                    Some tips:
                    - Double click on Tab name to edit it
                    - Every time you edit something it will automatically save it
                    - Click on column name to sort table rows
                 """,
            halign="left",
            valign="middle",
            size_hint=(None, None),
            size=(900, 150)
        )
        intro_label.pos_hint = {'center_x': 0.5, 'center_y': 0.3}
        layout.add_widget(intro_label)

        # Pulsante sotto il testo
        new_tab_button = Button(text="Create New Tab", size_hint=(None, None), size=(350, 90))
        new_tab_button.pos_hint = {'center_x': 0.5, 'center_y': 0.18}
        new_tab_button.bind(on_press=self.add_tab)
        layout.add_widget(new_tab_button)

        version_label = Label(
            text=f"Version {version}",
            font_size=18,
            size_hint_y=None,  # Altezza fissa
            height=30,
            valign='top'
        )
        version_label.pos_hint = {'center_x': 0.5, 'center_y': 0.1}

        layout.add_widget(version_label)

        # Aggiunge il layout alla tab principale
        home_tab.content = layout
        self.add_widget(home_tab)

        self.default_tab = home_tab

    def create_tab(self, id, title, color, tasks):
        tab = CustomTab(id=id, text=title)
        tab.tab_color = color
        layout = BoxLayout(orientation="vertical")

        tab.table = TableView(id, tasks)
        layout.add_widget(tab.table)

        buttons = self.create_control_buttons(tab.table)
        layout.add_widget(buttons)

        # Preview Panel
        preview_layout = BoxLayout(size_hint_y=0.2)
        preview_label = Label(text="Content:", size_hint_x=0.15)
        scroll = ScrollView()
        scroll.add_widget(tab.preview_content)
        preview_layout.add_widget(preview_label)
        preview_layout.add_widget(scroll)
        layout.add_widget(preview_layout)

        tab.content = layout
        return tab

    def create_control_buttons(self, table):
        buttons = BoxLayout(size_hint_y=None, height=dp(50))

        new_task_btn = Button(text="New Task", on_press=lambda x: table.add_row(Save.get_unique_row_id(table.id)))
        buttons.add_widget(new_task_btn)

        delete_task_btn = Button(text="Delete Task", disabled=True)
        delete_task_btn.bind(on_press=lambda x: self.delete_task(table))

        table.bind(selected_row=lambda instance, value: setattr(
            delete_task_btn, 'disabled', value is None
        ))
        buttons.add_widget(delete_task_btn)

        buttons.add_widget(Button(text="New Tab", on_press=self.add_tab, background_color=(0.16, 0.6, 0.56, 1)))
        buttons.add_widget(Button(text="Delete Tab", on_press=lambda x: self.delete_tab(table.id), background_color=(0.16, 0.6, 0.56, 1)))

        return buttons

    def add_tab(self, instance):
        tab_name = f"Tab {len(self.tab_list) + 1}"
        tab_id = Save.get_unique_tab_id()
        new_tab = CustomTab(id=tab_id, text=tab_name)
        new_tab.tab_color = [0.1, 0.1, 0.1, 1]
        layout = BoxLayout(orientation="vertical")
        tab_info = {
            "title": new_tab.text,
            "color": new_tab.tab_color,
            "tasks": {}
        }
        Save.save_tab(new_tab.id, tab_info)

        new_tab.table = TableView(tab_id)
        layout.add_widget(new_tab.table)

        buttons = self.create_control_buttons(new_tab.table)
        layout.add_widget(buttons)

        # Preview Panel per nuovo tab
        preview_layout = BoxLayout(size_hint_y=0.2)
        preview_label = Label(text="Anteprima:", size_hint_x=0.15)
        scroll = ScrollView()
        scroll.add_widget(new_tab.preview_content)
        preview_layout.add_widget(preview_label)
        preview_layout.add_widget(scroll)
        layout.add_widget(preview_layout)

        new_tab.content = layout
        self.add_widget(new_tab)
        self.switch_to(self.tab_list[0])

    def delete_tab(self, tab_id):
        if len(self.tab_list) > 1:
            self.show_confirmation_popup(tab_id)
        else:
            self.show_error_popup("Cannot delete last tab!")

    def delete_task(self, table):
        if table.selected_row:
            table.rows_layout.remove_widget(table.selected_row)
            Save.delete_row(table.id, table.selected_row.id)
            table.selected_row = None

    def update_bg_color(self, instance, value):
        if value and hasattr(value, 'tab_color'):
            self.bg_color = value.tab_color
            with self.canvas.before:
                Color(*self.bg_color)
                Rectangle(pos=self.pos, size=self.size)

    def show_confirmation_popup(self, tab_id):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text="Delete this tab?"))

        btn_layout = BoxLayout(size_hint_y=0.3, spacing=10)
        yes_btn = Button(text="Yes")
        no_btn = Button(text="No")

        popup = Popup(title="Confirm", content=content, size_hint=(0.6, 0.4))
        yes_btn.bind(on_press=lambda x: [self.remove_widget(self.current_tab),
                                         self.switch_to(self.tab_list[0]),
                                         Save.delete_tab(tab_id),
                                         popup.dismiss()]
                     )
        no_btn.bind(on_press=popup.dismiss)

        btn_layout.add_widget(no_btn)
        btn_layout.add_widget(yes_btn)
        content.add_widget(btn_layout)
        popup.open()

    def show_error_popup(self, message):
        content = BoxLayout(orientation='vertical', padding=10)
        content.add_widget(Label(text=message))
        ok_btn = Button(text="OK", size_hint=(1, 0.3))
        popup = Popup(title="Error", content=content, size_hint=(0.6, 0.3))
        ok_btn.bind(on_press=popup.dismiss)
        content.add_widget(ok_btn)
        popup.open()


class VelociTaskorApp(App):
    def build(self):
        Window.set_icon(PathHandler.icon_path())
        Save.load_data()
        return MainPanel()


if __name__ == "__main__":
    VelociTaskorApp().run()