from textual.widget import Widget
from textual.reactive import Reactive


class Navigator(Widget):
    def render(self):
        return "Navigator: 功能選擇"


class VideoArea(Widget):
    def render(self):
        return "Video Area: 選擇或拖入視頻"


class InputArea(Widget):
    def render(self):
        return "Input Area: 設置參數"


class ProgressBar(Widget):
    progress: Reactive[int] = Reactive(0)

    def render(self):
        return f"Progress: {self.progress}%"


class ConsoleMessage(Widget):
    def render(self):
        return "Console Message: 顯示標準輸出/錯誤消息"
