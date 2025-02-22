from enum import StrEnum
from rich.markdown import Markdown
from textual import on
from textual.app import App, ComposeResult
from textual.screen import Screen, ModalScreen
from textual.containers import (
    HorizontalScroll,
    VerticalScroll,
    Horizontal,
    Vertical,
    Container,
)
from textual.css.query import NoMatches
from textual.reactive import reactive
from textual.events import Key, Click
from textual.widget import Widget
from textual.widgets import (
    Header,
    Button,
    Footer,
    Static,
    Input,
    Select,
    Log,
    Label,
    SelectionList,
    ListItem,
    ListView,
    HelpPanel,
)
from textual_fspicker import SelectDirectory
from rich.cells import cell_len
from typing import Optional
import sys
from pathlib import Path
from app import constants, logger
import app.services.ffmpeg_converter.ffmpeg_converter as ffmpeg_converter
import threading
import time
import re
from .src import CSS, LICENSE_TEXT, ABOUT_TEXT

# LICENSE_TEXT = Path("LICENSE").read_text(encoding="utf-8")
# ABOUT_TEXT = Path("ABOUT.md").read_text(encoding="utf-8")

probed_cache: dict[str, str] = {}
# Define the About text using Markdown


def sanitize_string(s: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]", "", s)


class AllIds(StrEnum):
    MyStores = "MyStores"
    VideoFilePicker = "VideoFilePicker"
    output_path = "output_path"
    input_path = "input_path"
    video_path = "video_path"
    video_info = "video_info"
    threshold = "threshold"
    threshold_preset = "threshold_preset"
    start_button = "start_button"
    queue_button = "queue_button"
    open_output_path = "open_output_path"
    all_files = "all_files"
    rendered_file_list_view = "rendered_file_list_view"
    rendered_video_status = "rendered_video_status"


class MyStores(Widget):
    threads: list[tuple[threading.Thread, str]] = []

    def on_mount(self) -> None:
        # Assign values to the reactive list
        pass

    def set_value(self, id: str, value: str | Path):
        if not hasattr(self, id):
            setattr(self, id, reactive(""))
        setattr(self, id, value)

    def get_value(self, id: str):
        if hasattr(self, id):
            return getattr(self, id)
        return None

    pass


class MyModal(ModalScreen):
    """A modal screen that displays the About page."""

    def __init__(self, content: str, key: str) -> None:
        super().__init__()
        self.content = content
        self.key = key

    def on_mount(self) -> None:
        self.query_one(MyScrollFocusable).focus()

    def compose(self) -> ComposeResult:
        # Display the about text in a styled Static widget.
        yield MyScrollFocusable(
            Static(
                Markdown(self.content),
            ),
            classes="ScrollAuto HoverBorder MyModalContent",
        )

        # Static(Markdown(ABOUT_TEXT), id="MyModalContent", classes="ScrollAuto")

    def on_key(self, event: Key) -> None:
        # Allow closing the modal with Escape or Ctrl+A.
        event.stop()
        if event.key in ("escape", f"ctrl+{self.key}"):
            self.dismiss()

    def on_click(self, event: Click) -> None:
        """Close the modal if the click is outside the Static widget."""
        event.stop()
        if not self.query_one(MyScrollFocusable).region.contains(event.x, event.y):
            self.dismiss()


class LayoutApp(App):
    BINDINGS = [
        ("ctrl+c", "toggle_key_panel", "Keys"),
        ("ctrl+t", "toggle_theme", "Theme"),
        ("ctrl+a", f"toggle_modal('about', 'a')", "About"),
        ("ctrl+l", f"toggle_modal('license', 'l')", "License"),
        ("ctrl+q", "quit", "Quit"),
    ]

    def action_toggle_key_panel(self) -> None:
        """Show the keys panel."""
        try:
            self.query_one(HelpPanel).remove()
        except NoMatches:
            self.mount(HelpPanel())

    def action_toggle_theme(self) -> None:
        self.dark = not self.dark

    def action_toggle_modal(self, option: str, key: str) -> None:
        """Toggle the About modal dialog."""
        match option:
            case "about":
                content = ABOUT_TEXT
            case "license":
                content = LICENSE_TEXT
            case _:
                return
        self.push_screen(MyModal(content, key))

    # Track whether the About modal is currently shown.
    about_open: bool = False
    # CSS_PATH = "style.css"
    CSS = CSS
    _batch_counter = reactive(0)
    TITLE = constants.APP_NAME
    SUB_TITLE = "Auto Silence Remover"
    ENABLE_COMMAND_PALETTE = False

    def on_ready(self) -> None:
        self.push_screen(MainScreen())

    def on_mount(self) -> None:
        pass

    def set_input_path(self, selected_path: Path | None) -> None:
        """Set the input path to the selected directory.

        Args:
            to_show: The file to show.
        """
        if selected_path is None:
            return
        self.query_one("#" + AllIds.input_path).value = str(selected_path)  # type: ignore

    def set_video_info(self, video_file: Path) -> None:
        if probed_cache.get(video_file) is None:
            probed_cache[video_file] = {
                "Video Path": str(video_file),
                "Duration": ffmpeg_converter._convert_seconds_to_timestamp(
                    ffmpeg_converter.probe_duration(video_file)
                ),
                "Encode": ffmpeg_converter.probe_encoding(video_file),
            }
        video_info = probed_cache.get(video_file)
        formatted_info = "  \n".join(f"**{key}**: `{value}`" for key, value in video_info.items())  # type: ignore
        self.query_one("#" + AllIds.video_info).update(Markdown(formatted_info))  # type: ignore

    @on(Input.Changed, "*")
    def on_input_changed(
        self, event: Input.Changed, selected_id=AllIds.output_path
    ) -> None:
        # event.input: the Input widget that triggered the event.
        # event.value: the new value of the input.
        my_stores = self.query_one(AllIds.MyStores)
        selected_id = event.input.id
        value = event.value
        my_stores.set_value(selected_id, value)  # type: ignore
        logger.info(f"Changed {selected_id} to {getattr(my_stores, selected_id)}")  # type: ignore
        if selected_id == AllIds.input_path and Path(value).is_dir():
            video_files: list[Path] = [
                video
                for video in Path(value).glob("*")  # type: ignore
                if video.suffix.lstrip(".") in ffmpeg_converter.VideoSuffix
            ]
            my_stores.set_value(AllIds.all_files, video_files)  # type: ignore
            logger.info(f"Selectable : {video_files}")
            self.query_one("#" + AllIds.VideoFilePicker).clear_options()  # type: ignore
            self.query_one("#" + AllIds.VideoFilePicker).add_options(  # type: ignore
                [(video.name, str(video), True) for video in video_files]
            )
            self.query_one("#" + AllIds.video_info).update("")  # type: ignore
            logger.info(f"{video_files = }")
            if len(video_files) > 0:
                self.query_one("#" + AllIds.output_path).value = value + r"\Rendered"  # type: ignore
                self.set_video_info(video_files[0])

    @on(SelectionList.SelectedChanged, "#" + AllIds.VideoFilePicker)
    def update_selected_videos(self) -> None:
        VideoFilePicker = self.query_one("#" + AllIds.VideoFilePicker)
        video_files = VideoFilePicker.selected  # type: ignore
        my_stores: MyStores = self.query_one(AllIds.MyStores)  # type: ignore
        my_stores.set_value(AllIds.VideoFilePicker, video_files)  # type: ignore
        logger.info(f"Selected {my_stores.get_value(AllIds.VideoFilePicker)}")  # type: ignore

    @on(SelectionList.SelectionHighlighted, "#" + AllIds.VideoFilePicker)
    def update_video_info(self) -> None:
        my_stores: Widget = self.query_one(AllIds.MyStores)
        VideoFilePicker: SelectionList[str] = self.query_one("#" + AllIds.VideoFilePicker)  # type: ignore
        video_file = my_stores.get_value(AllIds.all_files)[VideoFilePicker.highlighted]  # type: ignore
        logger.info(f"highlighted {video_file}")  # type: ignore
        self.set_video_info(video_file)

    @on(Select.Changed, "#" + AllIds.threshold_preset)
    def on_threshold_preset_changed(self, event: Select.Changed) -> None:
        # event.value holds the newly selected option's value.
        # You can also access the sender (the widget that emitted the event)
        my_stores = self.query_one(AllIds.MyStores)
        value = event.value
        if Select.BLANK == value:
            logger.info("Please select a threshold preset or input a custom value")
            return
        self.query_one("#" + AllIds.threshold).value = value  # type: ignore

    @on(Button.Pressed, "#" + AllIds.open_output_path)
    def select_directory(self) -> None:
        my_stores: Widget = self.query_one(AllIds.MyStores)
        input_path = my_stores.get_value(AllIds.input_path)  # type: ignore
        if not Path(input_path).is_dir():
            input_path = constants.AppPaths.USERPROFILE / "Downloads"
        """show the `SelectDirectory` dialog when the button is pushed."""
        self.push_screen(
            SelectDirectory(location=input_path, show_files=True),
            callback=self.set_input_path,
        )

    @on(Button.Pressed, "#" + AllIds.queue_button)
    def put_in_queue(self, event: Button.Pressed) -> None:
        my_stores: MyStores = self.query_one(AllIds.MyStores)  # type: ignore
        videos = my_stores.get_value(AllIds.VideoFilePicker)
        if videos is None or len(videos) == 0:
            logger.error("No video selected")
            return
        for video in videos:
            video = Path(video)
            threshold: str = my_stores.get_value(AllIds.threshold)  # type: ignore
            output_path = Path(my_stores.get_value(AllIds.output_path))  # type: ignore
            output_path.mkdir(parents=True, exist_ok=True)
            output_path = output_path / (
                video.stem + "_rendered_" + threshold + video.suffix
            )
            _id: str = sanitize_string(
                "Render_" + str(self._batch_counter) + "_" + str(output_path.stem)
            )
            file_list_view: ListView = self.query_one("#" + AllIds.rendered_file_list_view)  # type: ignore
            file_list_view.append(  # type: ignore
                RenderedFile(
                    file_name=video.name,
                    output_path=str(output_path),
                    _batch=self._batch_counter,
                    id=_id,
                )
            )
            if not file_list_view.is_vertical_scrollbar_grabbed:
                file_list_view.scroll_end(animate=False)
            self._batch_counter += 1
            # Run without blocking the main thread
            my_stores.threads.append(
                (
                    threading.Thread(
                        target=ffmpeg_converter.cut_silence,
                        args=(video, output_path, threshold),
                        daemon=True,
                    ),
                    _id,
                )
            )

    @on(Button.Pressed, "#" + AllIds.start_button)
    def start_render(self, event: Button.Pressed) -> None:
        def start_all():
            my_stores: MyStores = self.query_one(AllIds.MyStores)  # type: ignore
            button: Button = self.query_one("#" + AllIds.start_button)  # type: ignore
            button.disabled = True
            button.label = "Rendering..."

            for thread in my_stores.threads:
                _label = self.query_one("#" + thread[1])  # type: ignore
                if _label.status == "Done":  # type: ignore
                    continue
                _label.status = "Rendering"  # type: ignore
                _label.add_class("Rendering")
                _label.query_one(Static).update(_label.status + " : " + _label.file_name + " to " + _label.output_path)  # type: ignore
                thread[0].start()
                while thread[0].is_alive():
                    time.sleep(2)
                _label.status = "Done"  # type: ignore
                _label.remove_class("Rendering")
                _label.add_class("Done")
                _label.query_one(Static).update(_label.status + " : " + _label.file_name + " to " + _label.output_path)  # type: ignore

            logger.info(f"All selected videos rendered")
            button.disabled = False
            button.label = "Render"

        start_render_thread = threading.Thread(target=start_all, daemon=True)
        start_render_thread.start()


class MainScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Vertical(
            Header(show_clock=True),
            MainContainer(id="MainContainer"),
            Footer(show_command_palette=False),
            MyStores(id=AllIds.MyStores, classes="Hidden"),
        )


class MyFooter(Footer):
    def on_mount(self) -> None:
        self.show_command_palette = False

    # def compose(self) -> ComposeResult:
    #     # yield Action()
    #     pass

    pass


class MainContainer(Container):
    def compose(self) -> ComposeResult:
        with Horizontal():
            # yield Sidebar(id="Sidebar", classes="H_One_FR")
            yield MainContent(id="MainContent", classes="H_Eight_FR")


class Sidebar(Container):
    def compose(self) -> ComposeResult:
        yield VerticalScroll(
            Label("Auto Silence Remover", id="Cut_Silence", classes="Action Center_All")
        )


class MainContent(Vertical):

    def compose(self) -> ComposeResult:
        yield Vertical(
            VideoPanel(classes="V_Custom_FR Border_Panel"),
            ParameterPanel(id="ParameterPanel", classes="V_One_FR Border_Panel"),
            ProgressPanel(classes="V_One_Half_FR Border_Panel"),
        )


class VideoPanel(Container):
    selections_videos: reactive[list[tuple[str, str, Optional[bool]]] | None] = (
        reactive([])
    )

    def on_mount(self) -> None:
        self.query_one(SelectionList).border_title = "Select Video Files"  # type: ignore
        self.query_one("#" + "Video_Info").border_title = "Video Info"  # type: ignore

    def compose(self) -> ComposeResult:
        yield VerticalScroll(
            Horizontal(
                Button(
                    label="Input Videos Directory",
                    id=AllIds.open_output_path,
                    tooltip="Select the directory containing the input videos",
                    classes="H_One_FR",
                ),
                Input(
                    placeholder="Selected input videos's directory path",
                    id=AllIds.input_path,
                    value=str(constants.AppPaths.USERPROFILE / "Downloads"),
                    classes="H_Two_FR",
                ),
                classes="Height_Three Margin_One_Down",
            ),
            Horizontal(
                SelectionList[str](
                    *self.selections_videos,  # type: ignore
                    id=AllIds.VideoFilePicker,
                    classes="H_One_FR V_One_FR ScrollAuto HoverBorder",
                ),
                MyScrollFocusable(
                    Static(
                        id=AllIds.video_info,
                    ),
                    classes="H_Two_FR V_One_FR ScrollAuto HoverBorder",
                    id="Video_Info",
                ),
                classes="MinHeight_Five",
            ),
        )


class MyScrollFocusable(Widget, can_focus=True):
    pass


class ParameterPanel(Container):
    def compose(self) -> ComposeResult:
        yield VerticalScroll(
            Parameter_Output(
                id=f"Parameter_Output", classes="Height_Three Margin_One_Down"
            ),
            Parameter_Threshold(id="Parameter_Threshold", classes="Height_Three"),
        )


class Parameter_Output(Container):
    def compose(self) -> ComposeResult:
        yield Horizontal(
            Static(
                "Output Directory",
                classes="Parameter_Label H_One_FR V_One_FR Center_All",
            ),
            Input(
                placeholder="Output Path",
                value=str(constants.AppPaths.USERPROFILE / "Downloads" / "Rendered"),
                id=AllIds.output_path,
                classes="Parameter_detail H_Three_FR Center_All",
                tooltip="This directory will be created if it does not exist, default in the same directory as the input videos",
            ),
        )


class Parameter_Threshold(Container):

    def compose(self) -> ComposeResult:
        yield Horizontal(
            Static(
                "Silence Threshold",
                id="Label_Threshold",
                classes="Parameter_Label H_One_FR V_One_FR Center_All",
            ),
            Parameter_Threshold_wrapper(
                id="Threshold_wrapper", classes="Parameter_detail H_Three_FR"
            ),
        )


class Parameter_Threshold_wrapper(Container):

    def compose(self) -> ComposeResult:
        yield Horizontal(
            Select(
                prompt="Select dB threshold preset",
                options=[("High", "-15"), ("Medium", "-21"), ("Low", "-30")],
                value="-21",
                id=AllIds.threshold_preset,
                classes="H_One_FR V_One_FR Center_All",
                tooltip="Higher threshold value removes more silence",
            ),
            Input(
                placeholder="dB",
                id=AllIds.threshold,
                classes="H_One_FR V_One_FR Center_All",
                type="number",
                tooltip="The smaller the number(unit -dB), the more silence will be removed",
            ),
        )


class ProgressPanel(Container):
    def on_mount(self) -> None:
        self.query_one(ListView).border_title = "Render Queue"  # type: ignore
        pass

    def compose(self) -> ComposeResult:
        with VerticalScroll():
            yield Horizontal(
                Button(
                    label="Queue",
                    id=AllIds.queue_button,
                    classes="H_One_FR ButtonA",
                ),
                Button(
                    label="Render",
                    id=AllIds.start_button,
                    classes="H_One_FR ButtonB",
                ),
                classes="Height_Three Margin_One_Down",
            )
            yield HorizontalScroll(
                ListView(
                    id=AllIds.rendered_file_list_view,
                    classes="H_One_FR V_One_FR HoverBorder ScrollAuto",
                ),
                LogView(id="LogView", classes="H_One_FR V_One_FR"),
                classes="MinHeight_Five",
            )


class RenderedFile(ListItem):
    """List item with a reactive counter."""

    _batch: reactive[int] = reactive(0)  # Reactive attribute
    file_name: reactive[str] = reactive("")  # Reactive attribute
    output_path: reactive[str] = reactive("")  # Reactive attribute
    status: reactive[str] = reactive("")  # Reactive attribute
    shown_content: reactive[str] = reactive("")  # Reactive attribute

    def __init__(
        self,
        file_name: str,
        output_path: str,
        _batch: int,
        id: str,
        status: str = "Ready",
    ) -> None:
        super().__init__()
        self.file_name = file_name
        self.output_path = output_path
        self._batch = _batch
        self.id = id
        self.status = status
        self.shown_content = (
            self.status + " : " + self.file_name + " to " + self.output_path
        )

    def on_mount(self):
        self.styles.width = cell_len(self.shown_content)

    def compose(self) -> ComposeResult:
        yield Static(self.shown_content)


class LogView(Container):
    _logger = Log

    def compose(self) -> ComposeResult:
        self.log_output = self._logger(classes="Log HoverBorder")
        yield self.log_output

    def on_mount(self) -> None:
        global logger
        sys.stdout = self
        sys.stderr = self
        logger.handlers[0].setStream(self)  # type: ignore
        self.query_one(self._logger).border_title = "Log"  # type: ignore

    def write(self, message: str) -> None:
        self.log_output.write(message)

    def flush(self) -> None:
        pass


if __name__ == "__main__":
    app = LayoutApp()
    app.run()
