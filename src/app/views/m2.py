import sys
from io import StringIO
from pathlib import Path
from textual import on
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import (
    Button,
    Header,
    Footer,
    Static,
    Input,
    Select,
    ProgressBar,
    Log,
    Label,
)

# Language support structure
LANGUAGES = {
    "en": {
        "title": "Video Silence Remover",
        "nav_home": "Home",
        "nav_about": "About",
        # ... other strings
    },
    # Add other languages
}


class LanguageManager:
    def __init__(self):
        self.current_lang = "en"

    def get(self, key: str) -> str:
        return LANGUAGES[self.current_lang].get(key, key)


class RedirectedOutput:
    def __init__(self, log_widget: Log):
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        self.log_widget = log_widget
        self.buffer = StringIO()

    def write(self, text: str):
        self.buffer.write(text)
        self.log_widget.write(text)

    def flush(self):
        self.buffer.flush()


class Sidebar(Vertical):
    def compose(self) -> ComposeResult:
        yield Button("Home", id="nav-home")
        yield Button("About", id="nav-about")
        yield Button("Settings", id="nav-settings")
        yield Button("Settings2", id="nav-settings2")


class VideoArea(Container):
    def compose(self) -> ComposeResult:
        yield Label("Drag & Drop Video Here", id="drop-zone")
        yield Static("No video selected", id="video-info")


class ProcessingForm(Container):
    def compose(self) -> ComposeResult:
        yield Input(placeholder="dB Threshold", id="threshold")
        yield Select(
            [("Loud", "loud"), ("Medium", "medium"), ("Silent", "silent")], id="preset"
        )
        yield Input(placeholder="Output Path", id="output-path")


class MainContent(Container):
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def compose(self) -> ComposeResult:
        yield VideoArea()
        yield ProcessingForm()
        yield Button("Process Video", id="process-btn")


class SettingsScreen(Container):
    def compose(self) -> ComposeResult:
        yield Select(
            [("English", "en"), ("中文", "zh")],
            prompt="Select Language",
            id="lang-select",
        )


class VideoProcessorApp(App):
    TITLE = "Video Silence Remover"

    def __init__(self):
        super().__init__()
        self.lang = LanguageManager()
        self.redirected_output = None

    def compose(self) -> ComposeResult:
        self.redirected_output = RedirectedOutput(Log())
        sys.stdout = self.redirected_output
        sys.stderr = self.redirected_output

        yield Header()
        yield Horizontal(
            Sidebar(),
            Vertical(
                MainContent(id="main-content"),
                ProgressBar(show_eta=False, id="progress"),
                self.redirected_output.log_widget,
            ),
        )
        yield Footer()

    @on(Button.Pressed, "#nav-home")
    def show_home(self):
        print(123)
        # self.query_one("#main-content").remove()
        # self.mount(MainContent(id="main-content"))

    @on(Button.Pressed, "#nav-settings")
    def show_settings(self):
        self.query_one("#main-content").replace(SettingsScreen())

    @on(Select.Changed, "#preset")
    def handle_preset_change(self, event: Select.Changed):
        presets = {"loud": -30, "medium": -21, "silent": -15}
        self.query_one("#threshold").value = str(presets.get(event.value, -40))

    @on(Button.Pressed, "#process-btn")
    def start_processing(self):
        progress_bar = self.query_one(ProgressBar)
        # Connect to your existing processing logic here
        for percent in range(101):
            self.call_from_thread(progress_bar.update, progress=percent)


if __name__ == "__main__":
    app = VideoProcessorApp()
    app.run()
