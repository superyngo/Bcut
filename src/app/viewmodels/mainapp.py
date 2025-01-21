from pathlib import Path
import json
import os
from urllib.parse import urlparse
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.filechooser import FileChooserListView
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.uix.behaviors import DragBehavior

class DragDropBox(DragBehavior, BoxLayout):
    pass

class SessionManager:
    def __init__(self):
        self.base_dir = Path.home() / "AppData" / "Roaming" / "mideoToGPhoto"
        self.config_path = self.base_dir / "config.conf"
        self.sessions_dir = self.base_dir / "sessions"
        
        # Create directories if they don't exist
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.sessions_dir.mkdir(exist_ok=True)
        
        # Initialize or load config
        self.load_config()

    def load_config(self):
        if not self.config_path.exists():
            self.config = [{
                "session_name": "anonymous",
                "cookie": "",
                "action": []
            }]
            self.save_config()
        else:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)

    def save_config(self):
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)

class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10
        
        self.session_manager = SessionManager()
        
        # Session selection
        self.session_box = BoxLayout(size_hint_y=None, height=30)
        self.session_spinner = Spinner(
            text='anonymous',
            values=[s['session_name'] for s in self.session_manager.config] + ['New Session'],
            size_hint_x=0.8
        )
        self.session_spinner.bind(text=self.on_session_select)
        
        self.edit_button = Button(
            text='✎',
            size_hint_x=0.2
        )
        self.edit_button.bind(on_press=self.edit_session_name)
        
        self.session_box.add_widget(self.session_spinner)
        self.session_box.add_widget(self.edit_button)
        self.add_widget(self.session_box)
        
        # action list
        self.tasks_box = BoxLayout(orientation='vertical')
        self.refresh_tasks()
        self.add_widget(self.tasks_box)
        
        # Add task button
        self.add_widget(Button(
            text='Add Task',
            size_hint_y=None,
            height=40,
            on_press=self.add_task
        ))

    def refresh_tasks(self):
        self.tasks_box.clear_widgets()
        current_session = next(
            (s for s in self.session_manager.config if s['session_name'] == self.session_spinner.text),
            self.session_manager.config[0]
        )
        
        for task in current_session['action']:
            task_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
            
            # Local folder selection
            folder_input = TextInput(
                text=task['local_album_folder'],
                multiline=False,
                size_hint_x=0.4
            )
            folder_input.bind(text=lambda instance, value: self.update_task(
                task, 'local_album_folder', value
            ))
            
            # URL input
            url_input = TextInput(
                text=task['google_photo_url'],
                multiline=False,
                size_hint_x=0.4
            )
            url_input.bind(text=lambda instance, value: self.update_task(
                task, 'google_photo_url', value
            ))
            
            browse_button = Button(
                text='Browse',
                size_hint_x=0.2,
                on_press=lambda x: self.show_folder_dialog(folder_input)
            )
            
            task_box.add_widget(folder_input)
            task_box.add_widget(url_input)
            task_box.add_widget(browse_button)
            
            self.tasks_box.add_widget(task_box)

    def update_task(self, task, key, value):
        task[key] = value
        self.session_manager.save_config()

    def on_session_select(self, instance, value):
        if value == 'New Session':
            self.create_new_session()
        self.refresh_tasks()

    def create_new_session(self):
        new_session = {
            "session_name": f"Session_{len(self.session_manager.config)}",
            "cookie": "",
            "action": []
        }
        self.session_manager.config.append(new_session)
        self.session_manager.save_config()
        self.session_spinner.values = [s['session_name'] for s in self.session_manager.config] + ['New Session']
        self.session_spinner.text = new_session['session_name']

    def edit_session_name(self, instance):
        content = BoxLayout(orientation='vertical')
        input_field = TextInput(text=self.session_spinner.text, multiline=False)
        
        def save_name(instance):
            session = next(s for s in self.session_manager.config if s['session_name'] == self.session_spinner.text)
            session['session_name'] = input_field.text
            self.session_manager.save_config()
            self.session_spinner.values = [s['session_name'] for s in self.session_manager.config] + ['New Session']
            self.session_spinner.text = input_field.text
            popup.dismiss()
            
        content.add_widget(input_field)
        content.add_widget(Button(text='Save', on_press=save_name))
        
        popup = Popup(title='Edit Session Name',
                     content=content,
                     size_hint=(None, None), size=(400, 200))
        popup.open()

    def show_folder_dialog(self, input_widget):
        content = BoxLayout(orientation='vertical')
        file_chooser = FileChooserListView(path=os.path.expanduser("~"))
        
        def select_folder(instance):
            input_widget.text = file_chooser.path
            popup.dismiss()
            
        content.add_widget(file_chooser)
        content.add_widget(Button(text='Select', on_press=select_folder, size_hint_y=None, height=40))
        
        popup = Popup(title='Select Folder',
                     content=content,
                     size_hint=(0.9, 0.9))
        popup.open()

    def add_task(self, instance):
        current_session = next(
            s for s in self.session_manager.config if s['session_name'] == self.session_spinner.text
        )
        current_session['action'].append({
            'local_album_folder': '',
            'google_photo_url': ''
        })
        self.session_manager.save_config()
        self.refresh_tasks()

class MideoToGPhotoApp(App):
    def build(self):
        return MainLayout()

if __name__ == '__main__':
    MideoToGPhotoApp().run()