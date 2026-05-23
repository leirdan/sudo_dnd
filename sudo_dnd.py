import requests
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, TabbedContent, TabPane, MarkdownViewer

START_MARKDOWN = """
# SUDO DND

O Sudo DND é uma iniciativa de intersecção entre os nerds de RPG e os nerds da computação.
"""


class SudoDNDApp(App):
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("1", "show_tab('start')", "Start"),
        ("2", "show_tab('races')", "Races"),
        ("3", "show_tab('classes')", "Classes"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with TabbedContent():
            with TabPane("Start", id="start"):
                yield MarkdownViewer(START_MARKDOWN, show_table_of_contents=False)
            with TabPane("Races", id="races"):
                yield MarkdownViewer("# Hello! \n ## Olá!", show_table_of_contents=True)
            with TabPane("Classes", id="classes"):
                yield MarkdownViewer("# Hello! \n ## Olá!", show_table_of_contents=True)
            # with TabPane("Equipment"):
            #     yield MarkdownViewer("# Hello! \n ## Olá!", show_table_of_contents=True)
        yield Footer()

    def action_toggle_dark(self) -> None:
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    def action_show_tab(self, target: str) -> None:
        self.get_child_by_type(TabbedContent).active = target


def main():
    app = SudoDNDApp()
    app.run()


if __name__ == "__main__":
    main()
