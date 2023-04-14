import logging
from pathlib import Path
from models import Placeholder
from bs4 import BeautifulSoup


logger = logging.getLogger("main")


def get_syms_count_with_spaces(string: str) -> int:
    soup = BeautifulSoup(string, 'html.parser')
    text = soup.get_text().replace("\n", "")
    # logger.error(text)
    return len(text)


def get_syms_count_without_spaces(string: str) -> int:
    soup = BeautifulSoup(string, 'html.parser')
    text = soup.get_text().replace(" ", "").replace("\n", "")
    # logger.error(text)
    return len(text)


def get_placeholders(path: str):
    # Define the folder path using pathlib
    folder_path = Path(path)

    # Create an empty list to store the Placeholder objects
    placeholders = {}

    # Loop through all the files in the folder using pathlib
    for filepath in folder_path.glob("*.txt"):
        # Open the file for reading
        with open(filepath, "r", encoding="utf-8") as file:
            # Read the text from the file
            text = file.read()

            # Count the number of symbols in the text
            symbols_count = get_syms_count_without_spaces(text)

            # Create a new Placeholder object and add it to the list
            placeholder = Placeholder(text, symbols_count)
            placeholders[symbols_count] = placeholder
    return placeholders


def find_key(num, my_dict):
    for key in sorted(my_dict.keys()):
        if key > num:
            return key
    return max(my_dict.keys())


class PlaceholderHandler:
    def __init__(self) -> None:
        self._placeholders_loaded = False
        self.placeholders = dict[int, Placeholder]

    def load_placeholders(self) -> None:
        self.placeholders = get_placeholders('./placeholders')
        self._placeholders_loaded = True

    def select_placeholder(self, diff: int) -> Placeholder:
        if not self._placeholders_loaded:
            raise Exception('Call load_placeholders() first!')
        return self.placeholders[find_key(diff, self.placeholders)]


# def get_raw_post_content(post_json: dict) -> str:
#     raw_post_content = post_json.get('content').get('raw')
#     return raw_post_content

def add_placeholder_to_raw_content() -> str:
    pass


# tests
if __name__ == "__main__":
    placeholders = get_placeholders('./placeholders')
    print([placeholder.symbols_count for placeholder in placeholders.values()])