import asyncio
from textual.app import App, ComposeResult
from httpx import AsyncClient
from textual.widgets import Footer, Header, TabbedContent, TabPane, MarkdownViewer

START_MARKDOWN = """
# SUDO DND

O Sudo DND é uma iniciativa de intersecção entre os nerds de RPG e os nerds da computação.
"""

RACES_MARKDOWN = """
# RACES 

Here, you will know the main characteristics of each race present in Dungeons & Dragons.
"""

URL_PREFIX = "https://www.dnd5eapi.co"


async def fetch_traits(traits: list) -> str:
    headers = {"Accept": "application/json"}
    markdown = "#### Traits\n"
    async with AsyncClient(headers=headers) as client:
        requests = [client.get(URL_PREFIX + trait_route) for trait_route in traits]
        responses = await asyncio.gather(*requests)
        for response in responses:
            if response.status_code == 200:
                data = response.json()
                markdown += f"  - {data["name"]}: {data["desc"]}\n"
    return markdown


async def fetch_races() -> str:
    base_url = URL_PREFIX + "/api/2014/races/"
    races: list = [
        "dragonborn",
        "dwarf",
        "elf",
        "gnome",
        "half-elf",
        "half-orc",
        "halfling",
        "human",
        "tiefling",
    ]
    markdown: str = RACES_MARKDOWN

    headers = {"Accept": "application/json"}

    async with AsyncClient(headers=headers) as client:
        requests = [client.get(base_url + race) for race in races]
        responses = await asyncio.gather(*requests)
        for response in responses:
            if response.status_code == 200:
                data = response.json()
                markdown += f"## {data['name']}\n"
                markdown += f"### Race Description\n"
                markdown += f"- Alignment: {data['alignment']}\n"
                markdown += f"- Size: {data['size_description']}\n"
                markdown += f"- Languages: {data['language_desc']}\n"

                markdown += f"### General Stats\n"
                markdown += f"- Speed: {data['speed']}ft\n"
                markdown += f"- Abilities bonuses: \n"
                for ability_bonus in data["ability_bonuses"]:
                    markdown += f"  - {ability_bonus['ability_score']['name']} (+{ability_bonus['bonus']})\n"
                if data["traits"]:
                    markdown += await fetch_traits(
                        [item["url"] for item in data["traits"]]
                    )
    return markdown


class SudoDNDApp(App):
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("1", "show_tab('start_tab')", "Start"),
        ("2", "show_tab('races_tab')", "Races"),
        ("3", "show_tab('classes_tab')", "Classes"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with TabbedContent():
            with TabPane("Start", id="start_tab"):
                yield MarkdownViewer(START_MARKDOWN, show_table_of_contents=False)
            with TabPane("Races", id="races_tab"):
                pass
            with TabPane("Classes", id="classes_tab"):
                yield MarkdownViewer("# Hello! \n ## Olá!", show_table_of_contents=True)
        yield Footer()

    def action_toggle_dark(self) -> None:
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    def action_show_tab(self, target: str) -> None:
        self.get_child_by_type(TabbedContent).active = target

    async def on_mount(self) -> None:
        races_data = await fetch_races()
        races_tab = self.query_one("#races_tab", TabPane)
        markdown_viewer = MarkdownViewer(races_data)
        await races_tab.mount(markdown_viewer)
