from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.graphics import Color, RoundedRectangle
from plyer import tts

Window.clearcolor = get_color_from_hex('#121212')

class RoundedButton(Button):
    def __init__(self, btn_color='#0055FF', **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.btn_color = get_color_from_hex(btn_color)
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(rgba=self.btn_color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[10,])

class CompactPlanner(App):
    def build(self):
        self.queue = []
        self.is_running = False
        
        # Основной контейнер без боковых отступов
        root = BoxLayout(orientation='vertical', padding=0, spacing=15)

        root.add_widget(Label(
            text="ПЛАНЕР", font_size='32sp', bold=True,
            color=get_color_from_hex('#38BDF8'), size_hint_y=None, height=60
        ))

        # ПОЛЯ ВВОДА: Максимально широкие
        input_container = BoxLayout(orientation='vertical', spacing=2, size_hint_y=None, height=180)
        
        self.task_in = TextInput(
            hint_text="Что нужно сделать?", 
            multiline=False, font_size='26sp',
            background_color=(1, 1, 1, 1), foreground_color=(0, 0, 0, 1),
            padding=[20, 20, 20, 20], size_hint_x=1
        )
        
        self.time_in = TextInput(
            hint_text="Минуты", 
            multiline=False, input_filter='int', font_size='26sp',
            background_color=(1, 1, 1, 1), foreground_color=(0, 0, 0, 1),
            padding=[20, 20, 20, 20], size_hint_x=1
        )
        
        input_container.add_widget(self.task_in)
        input_container.add_widget(self.time_in)
        root.add_widget(input_container)

        # Кнопка добавить (с небольшим отступом для красоты)
        btn_wrap = BoxLayout(padding=[10, 0, 10, 0], size_hint_y=None, height=70)
        self.add_btn = RoundedButton(
            text="ДОБАВИТЬ", btn_color='#1E40AF',
            font_size='22sp', bold=True
        )
        self.add_btn.bind(on_press=self.add_to_list)
        btn_wrap.add_widget(self.add_btn)
        root.add_widget(btn_wrap)

        # СПИСОК: Пункты теперь меньше и компактнее
        self.scroll = ScrollView()
        self.task_list_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5)
        self.task_list_layout.bind(minimum_height=self.task_list_layout.setter('height'))
        self.scroll.add_widget(self.task_list_layout)
        root.add_widget(self.scroll)

        # Нижняя панель
        footer = BoxLayout(orientation='vertical', padding=10, spacing=5, size_hint_y=None, height=130)
        self.start_btn = RoundedButton(
            text="ЗАПУСТИТЬ", btn_color='#10B981',
            font_size='26sp', bold=True, size_hint_y=None, height=80
        )
        self.start_btn.bind(on_press=self.start_schedule)
        footer.add_widget(self.start_btn)

        self.status_label = Label(text="Ожидание...", font_size='18sp', color=(0.6, 0.6, 0.6, 1))
        footer.add_widget(self.status_label)
        root.add_widget(footer)

        return root

    def add_to_list(self, instance):
        task = self.task_in.text
        minutes = self.time_in.text
        if task and minutes:
            self.queue.append({"task": task, "time": int(minutes)})
            # Создаем компактный пункт списка
            item = Label(
                text=f"• {task} ({minutes} м)", 
                font_size='20sp', size_hint_y=None, height=40,
                color=(1, 1, 1, 0.9)
            )
            self.task_list_layout.add_widget(item)
            self.task_in.text = ""
            self.time_in.text = ""

    def start_schedule(self, instance):
        if self.queue and not self.is_running:
            self.is_running = True
            self.start_btn.disabled = True
            self.run_next_task()

    def run_next_task(self):
        if self.queue:
            current = self.queue.pop(0)
            self.current_task_name = current['task']
            self.seconds_left = current['time'] * 60
            tts.speak(f"Начинайте {self.current_task_name}")
            if self.task_list_layout.children:
                self.task_list_layout.remove_widget(self.task_list_layout.children[-1])
            Clock.schedule_interval(self.update_timer, 1)
        else:
            self.status_label.text = "Все готово!"
            tts.speak("Все задачи выполнены!")
            self.is_running = False
            self.start_btn.disabled = False

    def update_timer(self, dt):
        self.seconds_left -= 1
        mins, secs = divmod(self.seconds_left, 60)
        self.status_label.text = f"{self.current_task_name}: {mins:02}:{secs:02}"
        if self.seconds_left <= 0:
            Clock.unschedule(self.update_timer)
            tts.speak(f"Время вышло для {self.current_task_name}")
            self.run_next_task()

if __name__ == "__main__":
    CompactPlanner().run()
