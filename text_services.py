from pathlib import Path
from models import Placeholder


def get_symbols_count(text: str):
    """Как в Word: без знаков пробелов, но со всеми
    знаками препинания и другими символами"""
    cutted_text = text.replace(" ", "").replace("\n", "")
    print(cutted_text)
    return len(cutted_text)


def get_placeholders(path: str):
    # Define the folder path using pathlib
    folder_path = Path(path)

    # Create an empty list to store the Placeholder objects
    placeholders = []

    # Loop through all the files in the folder using pathlib
    for filepath in folder_path.glob("*.txt"):
        # Open the file for reading
        with open(filepath, "r", encoding="utf-8") as file:
            # Read the text from the file
            text = file.read()

            # Count the number of symbols in the text
            symbols_count = get_symbols_count(text)

            # Create a new Placeholder object and add it to the list
            placeholder = Placeholder(text, symbols_count)
            placeholders.append(placeholder)
    return placeholders


# tests
if __name__ == "__main__":
    placeholders = get_placeholders('./placeholders')
    print([placeholder.symbols_count for placeholder in placeholders])