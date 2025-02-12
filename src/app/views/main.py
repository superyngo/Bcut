from ast import List
from asyncio import threads
from enum import StrEnum
from math import e
from textual import on
from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.containers import (
    Grid,
    HorizontalScroll,
    VerticalScroll,
    Horizontal,
    Vertical,
    Container,
)
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import (
    Placeholder,
    Button,
    Header,
    Footer,
    Static,
    Input,
    Select,
    ProgressBar,
    Log,
    Label,
    SelectionList,
    ListItem,
    ListView,
)
from textual_fspicker import FileOpen, FileSave, Filters, SelectDirectory
from textual.events import Mount
from typing import ItemsView, Optional
import sys
from io import StringIO
from pathlib import Path
from app import constants, logger
import app.services.ffmpeg_converter.ffmpeg_converter as ffmpeg_converter
import threading
import time

probed_cache = {}


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
    open_output_path = "open_output_path"
    all_files = "all_files"
    rendered_file_list_view = "rendered_file_list_view"
    rendered_video_status = "rendered_video_status"


class MyStores(Widget):

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


class LayoutApp(App):
    # BINDINGS = [("s", "start", "Start")]
    CSS_PATH = "style.css"
    _batch_counter = reactive(0)

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
                [(video.stem, str(video), True) for video in video_files]
            )
            self.query_one("#" + AllIds.video_info).update("")  # type: ignore
            logger.info(f"{video_files = }")
            if len(video_files) > 0:
                self.query_one("#" + AllIds.output_path).value = value + r"\Rendered"  # type: ignore
                video_file = video_files[0]
                if probed_cache.get(video_file) is None:
                    probed_cache[video_file] = {
                        "Video Path": str(video_file),
                        "Duration": ffmpeg_converter._convert_seconds_to_timestamp(
                            ffmpeg_converter.probe_duration(video_file)
                        ),
                        "Encode": ffmpeg_converter.probe_encoding(video_file),
                    }
                video_info = probed_cache.get(video_file)
                formatted_info = "\n".join(f"{key}: {value}" for key, value in video_info.items())  # type: ignore
                self.query_one("#" + AllIds.video_info).update(formatted_info)  # type: ignore

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
        if probed_cache.get(video_file) is None:
            probed_cache[video_file] = {
                "Video Path": str(video_file),
                "Duration": ffmpeg_converter._convert_seconds_to_timestamp(
                    ffmpeg_converter.probe_duration(video_file)
                ),
                "Encode": ffmpeg_converter.probe_encoding(video_file),
            }
        video_info = probed_cache.get(video_file)
        formatted_info = "\n".join(f"{key}: {value}" for key, value in video_info.items())  # type: ignore
        self.query_one("#" + AllIds.video_info).update(formatted_info)  # type: ignore

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

    @on(ListView.Highlighted, "#" + AllIds.rendered_file_list_view)
    def list_highlight_changed(self, event: ListView.Highlighted) -> None:
        """Handle highlight changes only for the list with id='my-list'"""
        highlighted_child = self.query_one("#" + AllIds.rendered_file_list_view).highlighted_child  # type: ignore
        show_rendered_video_status = self.query_one("#" + AllIds.rendered_video_status)  # type: ignore
        show_rendered_video_status.update(highlighted_child.status + " to " + highlighted_child.output_path)  # type: ignore

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

    @on(Button.Pressed, "#" + AllIds.start_button)
    def start_render(self, event: Button.Pressed) -> None:
        my_stores: MyStores = self.query_one(AllIds.MyStores)  # type: ignore
        videos = my_stores.get_value(AllIds.VideoFilePicker)
        if videos is None or len(videos) == 0:
            logger.error("No video selected")
            return
        button: Button = self.query_one("#" + AllIds.start_button)  # type: ignore
        button.disabled = True
        button.label = "Rendering..."
        threads: list[tuple[threading.Thread, str]] = [None] * len(videos)  # type: ignore
        for i, video in enumerate(videos):
            video = Path(video)
            threshold: str = my_stores.get_value(AllIds.threshold)  # type: ignore
            output_path = Path(my_stores.get_value(AllIds.output_path))  # type: ignore
            output_path.mkdir(parents=True, exist_ok=True)
            output_path = output_path / (
                video.stem + "_rendered_" + threshold + video.suffix
            )
            _id: str = (
                "Render_" + str(self._batch_counter) + "_" + str(output_path.stem)
            )
            self.query_one("#" + AllIds.rendered_file_list_view).append(  # type: ignore
                RenderedFile(
                    file_name=video.stem,
                    output_path=str(output_path),
                    _batch=self._batch_counter,
                    id=_id,
                )
            )
            self._batch_counter += 1
            # Run without blocking the main thread
            threads[i] = (
                threading.Thread(
                    target=ffmpeg_converter.cut_silence,
                    args=(video, output_path, threshold),
                    daemon=True,
                ),
                _id,
            )
            threads[i][0].start()

        def check_all():
            for thread in threads:
                while thread[0].is_alive():
                    time.sleep(2)
                self.query_one("#" + thread[1]).status = "Done"  # type: ignore
            threads.clear()
            logger.info(f"All selected videos rendered")
            button.disabled = False
            button.label = "Start render"

        checker_all = threading.Thread(target=check_all, daemon=True)
        checker_all.start()

        # self.progress_timer.resume()


class MainScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Vertical(
            MyHeader(id="Header"),
            MainContainer(id="MainContainer"),
            MyFooter(id="Footer"),
            MyStores(id=AllIds.MyStores, classes="Hidden"),
        )


class MyHeader(Header):
    pass


class MyFooter(Footer):
    # def compose(self) -> ComposeResult:
    #     # yield Action()
    #     pass

    pass


class MainContainer(Container):
    def compose(self) -> ComposeResult:
        yield Horizontal(
            Sidebar(id="Sidebar", classes="H_One_FR"),
            MainContent(id="MainContent", classes="H_Four_FR"),
        )


class Sidebar(Container):
    def compose(self) -> ComposeResult:
        yield VerticalScroll(
            Button(label="Cut Silence", id="Cut_Silence", classes="Action")
        )


class MainContent(Vertical):

    def compose(self) -> ComposeResult:
        yield Vertical(
            VideoPanel(classes="V_Two_FR"),
            ParameterPanel(id="ParameterPanel", classes="V_Two_FR"),
            ProgressPanel(classes="V_Half_FR H_One_FR"),
            LogView(id="LogView", classes="V_One_FR"),
        )


class ProgressPanel(Container):
    def compose(self) -> ComposeResult:
        yield HorizontalScroll(
            Button(label="Start render", id=AllIds.start_button, classes="H_One_FR"),
            ListView(
                id=AllIds.rendered_file_list_view,
                classes="H_One_FR V_One_FR Center_All",
            ),
            Static(
                "Please select a video file to check its status",
                id=AllIds.rendered_video_status,
                classes="H_One_FR V_One_FR Center_All",
            ),
        )


class RenderedFile(ListItem):
    """List item with a reactive counter."""

    _batch: reactive[int] = reactive(0)  # Reactive attribute
    file_name: reactive[str] = reactive("")  # Reactive attribute
    output_path: reactive[str] = reactive("")  # Reactive attribute
    status: reactive[str] = reactive("")  # Reactive attribute

    def __init__(
        self,
        file_name: str,
        output_path: str,
        _batch: int,
        id: str,
        status: str = "rendering",
    ) -> None:
        super().__init__()
        self.file_name = file_name
        self.output_path = output_path
        self._batch = _batch
        self.id = id
        self.status = status

    def compose(self) -> ComposeResult:
        yield Label(self.file_name)


class VideoPanel(Container):
    selections_videos: reactive[list[tuple[str, str, Optional[bool]]] | None] = (
        reactive([])
    )

    def on_mount(self) -> None:
        self.query_one(SelectionList).border_title = "Select Video Files"  # type: ignore
        self.query_one("#" + AllIds.video_info).border_title = "Video Info"  # type: ignore

    def compose(self) -> ComposeResult:
        yield Horizontal(
            Vertical(
                Button(
                    label="Select Directory",
                    id=AllIds.open_output_path,
                    classes="H_One_FR",
                ),
                SelectionList[str](
                    *self.selections_videos,  # type: ignore
                    classes="V_One_FR VerticalScroll",
                    id=AllIds.VideoFilePicker,
                ),
                classes="H_One_FR",
            ),
            VerticalScroll(
                Input(
                    placeholder="Selected input videos's directory path",
                    id=AllIds.input_path,  # , classes="V_One_FR"
                    value=str(constants.AppPaths.USERPROFILE / "Downloads"),
                ),
                Static("", id=AllIds.video_info, classes="V_One_FR HoverBorder"),
                classes="H_Two_FR",
            ),
        )


class ParameterPanel(Container):
    def compose(self) -> ComposeResult:
        yield VerticalScroll(
            Parameter_Output(id=f"Parameter_Output", classes="Parameter"),
            Parameter_Threshold(id="Parameter_Threshold", classes="Parameter"),
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
                options=[("Loud", "-15"), ("Medium", "-21"), ("Silent", "-30")],
                value="-21",
                id=AllIds.threshold_preset,
                classes="H_One_FR V_One_FR Center_All",
            ),
            Input(
                placeholder="dB",
                id=AllIds.threshold,
                classes="H_One_FR V_One_FR Center_All",
                type="number",
            ),
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
            ),
        )


class LogView(Container):

    def compose(self) -> ComposeResult:
        self.log_output = Log(classes="Log HoverBorder")
        yield self.log_output

    def on_mount(self) -> None:
        global logger
        sys.stdout = self
        sys.stderr = self
        logger.handlers[0].setStream(self)  # type: ignore
        self.query_one(Log).border_title = "Log"  # type: ignore

    def write(self, message: str) -> None:
        self.log_output.write(message)

    def flush(self) -> None:
        pass


if __name__ == "__main__":
    app = LayoutApp()
    app.run()
