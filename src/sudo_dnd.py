import asyncio
from textual.app import App, ComposeResult
from textual.containers import Horizontal, HorizontalGroup
from httpx import AsyncClient
from textual.widgets import (
    DataTable,
    Footer,
    Header,
    OptionList,
    TabbedContent,
    TabPane,
    MarkdownViewer,
)

from textual.widgets.option_list import Option

from error_modal import ErrorScreen

START_MARKDOWN = """
# SUDO DND

Sudo DND is an initiative that brings together RPG nerds and computer nerds. Browse the pages to explore the content.
"""

RACES_MARKDOWN = """
# RACES 

Come explore all the diversity D&D has to offer on this page!
"""

CLASSES_MARKDOWN = """
# CLASSES

Come see all the amazing possibilities you can become in D&D.
"""

URL_PREFIX = "https://www.dnd5eapi.co"

CLASSES: list = [
    "barbarian",
    "bard",
    "cleric",
    "druid",
    "fighter",
    "monk",
    "paladin",
    "ranger",
    "rogue",
    "sorcerer",
    "warlock",
    "wizard",
]


async def fetch_traits(traits: list) -> str:
    headers = {"Accept": "application/json"}
    markdown = "## Traits\n"
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
                markdown += f"# {data['name']}\n"
                markdown += f"## Race Description\n"
                markdown += f"- Alignment: {data['alignment']}\n"
                markdown += f"- Size: {data['size_description']}\n"
                markdown += f"- Languages: {data['language_desc']}\n"

                markdown += f"## General Stats\n"
                markdown += f"- Speed: {data['speed']}ft\n"
                markdown += f"- Abilities bonuses: \n"
                for ability_bonus in data["ability_bonuses"]:
                    markdown += f"  - {ability_bonus['ability_score']['name']} (+{ability_bonus['bonus']})\n"
                # if data["traits"]:
                #     markdown += await fetch_traits(
                #         [item["url"] for item in data["traits"]]
                #     )
    return markdown


async def fetch_class_levels(c) -> str:
    url = URL_PREFIX + c
    markdown: str = ""
    headers = {"Accept": "application/json"}

    async with AsyncClient(headers=headers) as client:
        response = await client.get(url)
        if response.status_code == 200:
            data = response.json()
            for element in data:
                markdown += f"##### Level {element["level"]}\n"
                markdown += f"Proficience bonus: (+{element["prof_bonus"]})\n"
                markdown += f"Features: "
                for f in element["features"]:
                    markdown += f"{f["name"]}; "
                markdown += "\n"
    return markdown


async def fetch_subclasses(subclasses_url: list) -> str:
    markdown: str = ""
    headers = {"Accept": "application/json"}
    async with AsyncClient(headers=headers) as client:
        requests = [client.get(URL_PREFIX + sub) for sub in subclasses_url]
        responses = await asyncio.gather(*requests)
        for response in responses:
            if response.status_code == 200:
                data = response.json()
                markdown += f"#### {data["name"]}\n"
                markdown += f"Kind: {data["subclass_flavor"]}\n"
                markdown += f"{data["desc"]}\n"
    return markdown


async def fetch_classes() -> str:
    base_url = URL_PREFIX + "/api/2014/classes/"
    markdown: str = CLASSES_MARKDOWN

    headers = {"Accept": "application/json"}

    async with AsyncClient(headers=headers) as client:
        requests = [client.get(base_url + c) for c in CLASSES]
        responses = await asyncio.gather(*requests)
        for response in responses:
            if response.status_code == 200:
                data = response.json()
                markdown += f"# {data['name']}\n"
                markdown += f"## General Stats\n"
                markdown += f"- Hit Dice: d{data['hit_die']}\n"
                # if data["class_levels"]:
                #     markdown += f"### Levels\n"
                #     markdown += await fetch_class_levels(data["class_levels"])

                # if data["subclasses"]:
                #     markdown += f"## Subclasses\n"
                #     markdown += await fetch_subclasses(
                #         [sub["url"] for sub in data["subclasses"]]
                #     )

    return markdown


async def fetch_spells_by_class(c: str) -> list[(str, str)]:
    list: list[(str, str)] = []
    base_url = URL_PREFIX + "/api/2014/classes/" + c + "/spells"
    headers = {"Accept": "application/json"}
    async with AsyncClient(headers=headers) as client:
        response = await client.get(base_url)
        if response.status_code == 200:
            data = response.json()
            if data["count"] > 0:
                list.extend([(s["name"], s["level"]) for s in data["results"]])
                # list.append({data["results"]["name"]}, {data["results"]["level"]})

    return list


class SudoDNDApp(App):
    BINDINGS = [
        ("s", "show_tab('start_tab')", "Start"),
        ("r", "show_tab('races_tab')", "Races"),
        ("c", "show_tab('classes_tab')", "Classes"),
        ("g", "show_tab('spells_tab')", "Grimoire"),
    ]

    CSS_PATH = "styles.tcss"

    def compose(self) -> ComposeResult:
        yield Header()
        with TabbedContent():
            with TabPane("Start", id="start_tab"):
                yield MarkdownViewer(START_MARKDOWN, show_table_of_contents=False)
            with TabPane("Races", id="races_tab"):
                pass
            with TabPane("Classes", id="classes_tab"):
                pass
            with TabPane("Grimoire", id="spells_tab"):
                with Horizontal(id="spells_container"):
                    yield OptionList(
                        *(Option(c.capitalize(), id=c) for c in CLASSES),
                        id="spell_class_list",
                    )
                    yield DataTable(id="spell_table")
        yield Footer()

    def action_toggle_dark(self) -> None:
        self.theme = "ansi-dark" if self.theme == "ansi-light" else "ansi-light"

    def action_show_tab(self, target: str) -> None:
        self.get_child_by_type(TabbedContent).active = target

    async def on_option_list_option_selected(
        self, target: OptionList.OptionSelected
    ) -> None:
        value = target.option.id
        list = await fetch_spells_by_class(value)
        self.show_spells_result(list)

    def show_spells_result(self, list: list[(str, str)]) -> None:
        spells_table = self.query_one("#spell_table", DataTable)
        spells_table.clear(columns=True)

        if len(list) == 0:
            self.push_screen(ErrorScreen("This class has no spells available"))
            pass

        spells_table.add_columns("Name", "Level")
        for name, level in list:
            spells_table.add_row(name, str(level))

    async def on_mount(self) -> None:
        self.theme = "ansi-dark"
        races_data = await fetch_races()
        races_tab = self.query_one("#races_tab", TabPane)
        markdown_viewer = MarkdownViewer(races_data, show_table_of_contents=True)
        await races_tab.mount(markdown_viewer)

        classes_data = await fetch_classes()
        classes_tab = self.query_one("#classes_tab", TabPane)
        markdown_viewer = MarkdownViewer(classes_data, show_table_of_contents=True)
        await classes_tab.mount(markdown_viewer)
