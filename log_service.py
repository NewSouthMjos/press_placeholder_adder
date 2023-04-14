import csv
from pathlib import Path


TITLE_ROW = [
    "ID статьи",
    "Была обработана",
    "Подлежит обработке",
    "Заголовок",
    "Ссылка",
    "Дата и время",
    "Исходное количество символов (с пробелами, без заголовка) — должно примерно как в предыдущих отчетах",
    "Исходное количество символов (без пробелов, с заголовком)",
    "Компенсируемая разница",
    "Количество добавленных символов (без пробелов)",
    "Итоговое количество символов в статье (без пробелов)",
]


class ResultLogRow:
    def __init__(
        self,
        post_id: int,
        was_edited: str,
        should_be_edited: str,
        title: str,
        link: str,
        datetime: str,
        initial_syms_count_with_spaces: int,  # (с пробелами, без заголовка)
        initial_syms_count_without_spaces: int,  # (без пробелов, с заголовком)
        diff: int,
        added_syms_count: int,
        finish_syms_count: int,
    ) -> None:
        self.post_id = post_id
        self.was_edited = was_edited
        self.should_be_edited = should_be_edited
        self.title = title
        self.link = link
        self.datetime = datetime
        self.initial_syms_count_with_spaces = initial_syms_count_with_spaces
        self.initial_syms_count_without_spaces = (
            initial_syms_count_without_spaces
        )
        self.diff = diff
        self.added_syms_count = added_syms_count
        self.finish_syms_count = finish_syms_count

    def __iter__(self):
        yield self.post_id
        yield self.was_edited
        yield self.should_be_edited
        yield self.title
        yield self.link
        yield self.datetime
        yield self.initial_syms_count_with_spaces
        yield self.initial_syms_count_without_spaces
        yield self.diff
        yield self.added_syms_count
        yield self.finish_syms_count


class LogHandler:
    def __init__(self, log_path: str) -> None:
        self.path = log_path
        self.already_edited_posts_ids = set()
        self._log_was_opened = False

    def get_already_edited_posts_ids(self) -> set:
        """Возвращает множество IDшников уже обработанных статей"""
        if not self._log_was_opened:
            raise Exception("Call the open_log() func first!")
        return self.already_edited_posts_ids

    def add_log_row(self, log_row: ResultLogRow) -> None:
        """Добавляет обработанную статью в лог файл"""
        if not self._log_was_opened:
            raise Exception("Call the open_log() func first!")
        with open(
            self.path, mode="a", newline="", encoding="utf-8"
        ) as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(log_row)

    def open_log(self) -> None:
        file_path = Path(self.path)
        if not file_path.exists():
            with open(
                self.path, mode="w", newline="", encoding="utf-8"
            ) as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(TITLE_ROW)
            self._log_was_opened = True
            return
        with open(self.path, "r", encoding="utf-8") as log:
            csv_reader = csv.reader(log)
            for row in csv_reader:
                try:
                    id_int = int(row[0])
                    if row[1] == "да":
                        self.already_edited_posts_ids.add(id_int)
                except Exception:
                    continue
        self._log_was_opened = True
        return


if __name__ == "__main__":
    a = ResultLogRow(
        1323,
        "да",
        "да",
        "В Самаре завершился лыжный марафон «Сокольи горы»",
        "sdsds",
        "Опубликовано 31.01.2022 в 20:31",
        8000,
        7000,
        1000,
        1017,
        8017,
    )
    for col in a:
        print(col)
