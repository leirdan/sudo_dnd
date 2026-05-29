from textual.screen import ModalScreen
from textual.widgets import Button, Label


class ErrorScreen(ModalScreen):
    CSS_PATH = "styles.tcss"

    def __init__(self, error_message: str, **kwargs):
        super().__init__(**kwargs)
        self.error_message = error_message

    def compose(self):
        yield Label("ERROR", id="error_dialog")
        yield Label(self.error_message, id="error_message")
        yield Button("OK", id="ok_btn", variant="error")

    def on_button_pressed(self, event: Button.Pressed):
        self.dismiss()
