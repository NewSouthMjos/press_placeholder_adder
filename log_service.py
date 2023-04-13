import csv
from pathlib import Path

from models import Post


class LogHandler:
    def __init__(self, log_path: str) -> None:
        self.path = log_path
        self.already_edited_posts_ids = set()
        self._log_was_opened = False

    def get_already_edited_posts_ids(self) -> set:
        """Возвращает множество IDшников уже обработанных статей"""
        if not self._log_was_opened:
            raise Exception('Call the open_log() func first!')
        return self.already_edited_posts_ids

    def add_post(self, post: Post) -> None:
        """Добавляет обработанную статью в лог файл"""
        if not self._log_was_opened:
            raise Exception('Call the open_log() func first!')
        with open(self.path, mode="a", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([post.id, "нет", post.title, post.date_str, "0", "0", "0"])

    def open_log(self) -> None:
        file_path = Path(self.path)
        if not file_path.exists():
            with open(self.path, mode="w", newline="", encoding="utf-8") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(["ID статьи", "Была обработана", "Заголовок",
                                 "Дата и время",
                                 "Исходное количество символов",
                                 "Количество добавленных символов",
                                 "Количество символов в результате", ])
            self._log_was_opened = True
            return
        with open(self.path, 'r', encoding="utf-8") as log:
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
