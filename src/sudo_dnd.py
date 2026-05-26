import asyncio
from textual.app import App, ComposeResult
from httpx import AsyncClient
from textual.widgets import Footer, Header, TabbedContent, TabPane, MarkdownViewer

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


# TODO: vai ficar muito complexo computacionalmente se formos puxar as features
# async def fetch_features(feats: list) -> str:
#     pass


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
                markdown += f"##### {data["name"]}\n"
                markdown += f"Kind: {data["subclass_flavor"]}\n"
                markdown += f"{data["desc"]}\n"
    return markdown


async def fetch_classes() -> str:
    base_url = URL_PREFIX + "/api/2014/classes/"
    classes: list = [
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
    markdown: str = CLASSES_MARKDOWN

    headers = {"Accept": "application/json"}

    async with AsyncClient(headers=headers) as client:
        requests = [client.get(base_url + c) for c in classes]
        responses = await asyncio.gather(*requests)
        for response in responses:
            if response.status_code == 200:
                data = response.json()
                markdown += f"## {data['name']}\n"
                markdown += f"### General Stats\n"
                markdown += f"- Hit Dice: d{data['hit_die']}\n"
                if data["class_levels"]:
                    markdown += f"#### Levels\n"
                    markdown += await fetch_class_levels(data["class_levels"])

                if data["subclasses"]:
                    markdown += f"### Subclasses\n"
                    markdown += await fetch_subclasses(
                        [sub["url"] for sub in data["subclasses"]]
                    )

    return markdown


class SudoDNDApp(App):
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("s", "show_tab('start_tab')", "Start"),
        ("r", "show_tab('races_tab')", "Races"),
        ("c", "show_tab('classes_tab')", "Classes"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with TabbedContent():
            with TabPane("Start", id="start_tab"):
                yield MarkdownViewer(START_MARKDOWN, show_table_of_contents=False)
            with TabPane("Races", id="races_tab"):
                pass
            with TabPane("Classes", id="classes_tab"):
                pass
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
        markdown_viewer = MarkdownViewer(races_data, show_table_of_contents=False)
        await races_tab.mount(markdown_viewer)

        classes_data = await fetch_classes()
        classes_tab = self.query_one("#classes_tab", TabPane)
        markdown_viewer = MarkdownViewer(classes_data, show_table_of_contents=False)
        await classes_tab.mount(markdown_viewer)
