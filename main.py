from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Line
import sqlite3
from kivy.utils import platform

#  importing android specific modules
if platform == 'android':
    from android.permissions import request_permissions, Permission
    from android.storage import primary_external_storage_path

class BorderedLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.after:
            Color(1, 1, 1, 1)
            self.line = Line(rectangle=(self.x, self.y, self.width, self.height), width=1)

    def on_size(self, *args):
        self.line.rectangle = (self.x, self.y, self.width, self.height)

    def on_pos(self, *args):
        self.line.rectangle = (self.x, self.y, self.width, self.height)

class EDMApp(App):
    def build(self):
        self.title = "LevelLog"
        self.icon = "level.PNG"

        self.layout = BoxLayout(orientation='vertical', padding=10)
        self.init_project_details()
        return self.layout

    def init_project_details(self):
        self.layout.clear_widgets()

        project_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        title_label = Label(text="Project Details", size_hint_y=None, height=40, font_size=20)
        project_layout.add_widget(title_label)

        self.project_title = TextInput(hint_text="Project Title", multiline=False, size_hint_y=None, height=40)
        self.description = TextInput(hint_text="Description", multiline=False, size_hint_y=None, height=40)
        self.area_of_study = TextInput(hint_text="Area of Study", multiline=False, size_hint_y=None, height=40)
        self.carried_by = TextInput(hint_text="Carried By", multiline=False, size_hint_y=None, height=40)
        self.date_of_study = TextInput(hint_text="Date of Study", multiline=False, size_hint_y=None, height=40)

        labels = ["Project Title", "Description", "Area of Study", "Carried By", "Date "]
        inputs = [self.project_title, self.description, self.area_of_study, self.carried_by, self.date_of_study]

        for label_text, text_input in zip(labels, inputs):
            label = Label(text=label_text, size_hint_y=None, height=30)
            project_layout.add_widget(label)
            project_layout.add_widget(text_input)

        submit_button = Button(text="Submit Project Details", on_press=self.submit_project_details, size_hint_y=None, height=40)
        project_layout.add_widget(submit_button)

        self.layout.add_widget(project_layout)

    def submit_project_details(self, instance):
        self.project_details = {
            'title': self.project_title.text.strip(),
            'description': self.description.text.strip(),
            'area_of_study': self.area_of_study.text.strip(),
            'carried_by': self.carried_by.text.strip(),
            'date_of_study': self.date_of_study.text.strip()
        }

        if any(self.project_details.values()):
            self.init_db()
            self.init_main_layout()

    def init_db(self):
        self.project_table = f"levels_{self.project_details['title'].replace(' ', '_')}_{self.project_details['date_of_study'].replace('/', '_')}"
        conn = sqlite3.connect('entries.db')
        cursor = conn.cursor()
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {self.project_table} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                back_sight REAL,
                intermediate REAL,
                fore_sight REAL,
                rise REAL,
                fall REAL,
                reduced_level REAL,
                distance REAL,
                remarks TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def init_main_layout(self):
        self.layout.clear_widgets()

        self.recorded_levels = GridLayout(cols=8, size_hint_y=None)
        self.recorded_levels.bind(minimum_height=self.recorded_levels.setter('height'))

        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_view.add_widget(self.recorded_levels)

        self.layout.add_widget(scroll_view)

        headers = ["Back Sight", "Intermediate", "Fore Sight", "Rise", "Fall", "Reduced Level", "Distance", "Remarks"]
        for header in headers:
            self.recorded_levels.add_widget(BorderedLabel(text=header))

        input_layout = BoxLayout(size_hint_y=None, height=100, orientation='vertical')

        input_row1 = BoxLayout(size_hint_y=None, height=50, orientation='horizontal')
        self.back_sight = TextInput(hint_text="BS", multiline=False)
        self.intermediate = TextInput(hint_text="IS", multiline=False)
        self.fore_sight = TextInput(hint_text="FS", multiline=False)
        input_row1.add_widget(self.back_sight)
        input_row1.add_widget(self.intermediate)
        input_row1.add_widget(self.fore_sight)

        input_row2 = BoxLayout(size_hint_y=None, height=50, orientation='horizontal')
        self.reduced_level = TextInput(hint_text="RL", multiline=False)
        self.distance = TextInput(hint_text="D", multiline=False)
        self.comments = TextInput(hint_text="Remarks", multiline=False)
        input_row2.add_widget(self.reduced_level)
        input_row2.add_widget(self.distance)
        input_row2.add_widget(self.comments)

        input_layout.add_widget(input_row1)
        input_layout.add_widget(input_row2)

        button_layout = BoxLayout(size_hint_y=None, height=50, orientation='horizontal')
        self.add_button = Button(text="Add Entry", on_press=self.add_entry, background_color=(0.1, 0.5, 0.8, 1))
        self.clear_button = Button(text="Clear Data", on_press=self.clear_data, background_color=(0.8, 0.1, 0.1, 1))
        self.submit_button = Button(text="Submit Project", on_press=self.submit_project, background_color=(0.1, 0.8, 0.1, 1))
        self.check_button = Button(text="Perform Checks", on_press=self.perform_checks, background_color=(0, 1, 1, 1))  # Cyan color
        button_layout.add_widget(self.add_button)
        button_layout.add_widget(self.clear_button)
        button_layout.add_widget(self.submit_button)
        button_layout.add_widget(self.check_button)
        input_layout.add_widget(button_layout)

        self.layout.add_widget(input_layout)

        # Initialize readings list
        self.readings = []
        self.check_results = None

    def add_entry(self, instance):
        entry = {
            'back_sight': round(float(self.back_sight.text.strip() or 0), 3),
            'intermediate': round(float(self.intermediate.text.strip() or 0), 3),
            'fore_sight': round(float(self.fore_sight.text.strip() or 0), 3),
            'rise': 0,
            'fall': 0,
            'reduced_level': round(float(self.reduced_level.text.strip() or 0), 3),
            'distance': round(float(self.distance.text.strip() or 0), 3),
            'remarks': self.comments.text.strip()
        }
        # computing rise and fall values
        if len(self.readings) > 0:
            prev_entry = self.readings[-1]

            if entry['intermediate'] != 0:
                if prev_entry['back_sight'] != 0 and prev_entry['fore_sight'] != 0:
                    difference = prev_entry['back_sight'] - entry['intermediate']
                else:
                    prev_is = next((e['intermediate'] for e in reversed(self.readings) if e['intermediate'] != 0), None)
                    prev_bs = next((e['back_sight'] for e in reversed(self.readings) if e['back_sight'] != 0), None)
                    if prev_is is not None:
                        difference = prev_is - entry['intermediate']
                    elif prev_bs is not None:
                        difference = prev_bs - entry['intermediate']
                    else:
                        difference = 0
            elif entry['fore_sight'] != 0:
                prev_is = next((e['intermediate'] for e in reversed(self.readings) if e['intermediate'] != 0), None)
                if prev_is is not None:
                    difference = prev_is - entry['fore_sight']
                else:
                    difference = 0
            else:
                difference = 0

            if difference > 0:
                entry['rise'] = round(difference, 3)
            elif difference < 0:
                entry['fall'] = round(-difference, 3)

            # Calculate the reduced level
            if entry['rise'] != 0:
                entry['reduced_level'] = round(prev_entry['reduced_level'] + entry['rise'], 3)
            elif entry['fall'] != 0:
                entry['reduced_level'] = round(prev_entry['reduced_level'] - entry['fall'], 3)
            else:
                entry['reduced_level'] = prev_entry['reduced_level']
        else:
            entry['reduced_level'] = entry['reduced_level']

        self.readings.append(entry)

        if any([entry['back_sight'], entry['intermediate'], entry['fore_sight']]):
            self.display_entry(entry)
            self.save_entry(entry)
            self.clear_inputs()

    def save_entry(self, entry):
        conn = sqlite3.connect('entries.db')
        cursor = conn.cursor()
        cursor.execute(f'''
            INSERT INTO {self.project_table} (back_sight, intermediate, fore_sight, rise, fall, reduced_level, distance, remarks)
            VALUES (:back_sight, :intermediate, :fore_sight, :rise, :fall, :reduced_level, :distance, :remarks)
        ''', entry)
        conn.commit()
        conn.close()

    def display_entry(self, entry):
        self.recorded_levels.add_widget(BorderedLabel(text=str(entry['back_sight'])))
        self.recorded_levels.add_widget(BorderedLabel(text=str(entry['intermediate'])))
        self.recorded_levels.add_widget(BorderedLabel(text=str(entry['fore_sight'])))
        self.recorded_levels.add_widget(BorderedLabel(text=str(entry['rise'])))
        self.recorded_levels.add_widget(BorderedLabel(text=str(entry['fall'])))
        self.recorded_levels.add_widget(BorderedLabel(text=str(entry['reduced_level'])))
        self.recorded_levels.add_widget(BorderedLabel(text=str(entry['distance'])))
        self.recorded_levels.add_widget(BorderedLabel(text=str(entry['remarks'])))

    def clear_inputs(self):
        self.back_sight.text = ''
        self.intermediate.text = ''
        self.fore_sight.text = ''
        self.reduced_level.text = ''
        self.distance.text = ''
        self.comments.text = ''

    def clear_data(self, instance):
        self.readings = []
        self.recorded_levels.clear_widgets()
        headers = ["Back Sight", "Intermediate", "Fore Sight", "Rise", "Fall", "Reduced Level", "Distance", "Remarks"]
        for header in headers:
            self.recorded_levels.add_widget(BorderedLabel(text=header))
        conn = sqlite3.connect('entries.db')
        cursor = conn.cursor()
        cursor.execute(f'DROP TABLE IF EXISTS {self.project_table}')
        conn.commit()
        conn.close()
        self.init_db()

        # Clear check results
        if self.check_results:
            self.layout.remove_widget(self.check_results)
            self.check_results = None

    def submit_project(self, instance):
        pass  # No need to export to CSV, just submit to database

    def perform_checks(self, instance):
        if not self.readings:
            return

        sum_bs = round(sum(entry['back_sight'] for entry in self.readings), 3)
        sum_fs = round(sum(entry['fore_sight'] for entry in self.readings), 3)
        sum_rise = round(sum(entry['rise'] for entry in self.readings), 3)
        sum_fall = round(sum(entry['fall'] for entry in self.readings), 3)

        # Calculating the check values
        self.check_fs_bs = round(sum_bs - sum_fs, 3)
        self.check_rise_fall = round(sum_rise - sum_fall, 3)
        self.rl_difference = round(self.readings[-1]['reduced_level'] - self.readings[0]['reduced_level'], 3)

        self.recorded_levels.add_widget(BorderedLabel(text=""))
        self.recorded_levels.add_widget(BorderedLabel(text=""))
        self.recorded_levels.add_widget(BorderedLabel(text=""))
        self.recorded_levels.add_widget(BorderedLabel(text="Summation"))
        self.recorded_levels.add_widget(BorderedLabel(text=str(sum_bs)))
        self.recorded_levels.add_widget(BorderedLabel(text=str(sum_fs)))
        self.recorded_levels.add_widget(BorderedLabel(text=str(sum_rise)))
        self.recorded_levels.add_widget(BorderedLabel(text=str(sum_fall)))

        if self.check_results:
            self.layout.remove_widget(self.check_results)

        self.check_results = BoxLayout(orientation='vertical', padding=10, spacing=10)
        check_label = Label(text="Check Results", size_hint_y=None, height=40, font_size=20)
        self.check_results.add_widget(check_label)

        check_bs_fs_label = Label(text=f"BS - FS: {self.check_fs_bs}", size_hint_y=None, height=30)
        self.check_results.add_widget(check_bs_fs_label)

        check_rise_fall_label = Label(text=f"Rise - Fall: {self.check_rise_fall}", size_hint_y=None, height=30)
        self.check_results.add_widget(check_rise_fall_label)

        check_rl_label = Label(text=f"RL Last - RL First: {self.rl_difference}", size_hint_y=None, height=30)
        self.check_results.add_widget(check_rl_label)

        self.check_passed = self.check_fs_bs == self.check_rise_fall == self.rl_difference

        check_result = "Check Passed" if self.check_passed else "Check Failed"
        
        if check_result == "Check Passed":
            check_result_label = Label(text=f"[color=00FF00]✔ Check Result: {check_result}[/color]", size_hint_y=None, height=30, markup=True)
        else:
            check_result_label = Label(text=f"[color=FF0000]✘ Check Result: {check_result}[/color]", size_hint_y=None, height=30, markup=True)
        
        self.check_results.add_widget(check_result_label)

        self.layout.add_widget(self.check_results)

if __name__ == '__main__':
    EDMApp().run()













































