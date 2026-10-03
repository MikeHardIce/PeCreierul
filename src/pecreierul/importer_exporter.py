from datetime import datetime
import os
import csv
from typing import Dict, List
from sqlalchemy.orm import Session

from pecreierul.database import Lesson, LessonTerm, Tag, Term
from pecreierul.lesson_repository import LessonRepository


class ImporterExporter:

    @staticmethod
    def import_lesson(lesson: Lesson, tags: Dict[str,Tag], lesson_path: str):
        if os.path.isfile(lesson_path):
            with open(lesson_path, mode="r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                keys = set(["question", "answers", "tag_question", "tag_answers"])
                duplicate_catcher = set()
                for row in reader:
                    if keys.issubset(row.keys()):
                        entry = (row["question"], row["tag_question"], row["answers"], row["tag_answers"])
                        if entry not in duplicate_catcher:
                            tag_question = row["tag_question"].strip()
                            tag_answer = row["tag_answers"].strip()
                            tag1 = tags[tag_question] if tag_question in tags else Tag(name=tag_question)
                            tag2 = tags[tag_answer] if tag_answer in tags else Tag(name=tag_answer)
                            lesson_term = LessonTerm()
                            lesson_term.term1 = Term(value = row["question"].strip(), tag = tag1)
                            lesson_term.term2 = Term(value = row["answers"].strip(), tag = tag2)
                            lesson.lesson_terms.append(lesson_term)

                            duplicate_catcher.add(entry)
        

    @staticmethod
    def export_lesson(lesson: Lesson, lesson_path: str) -> str:
        """
            Exports the current lesson to the given path. If a file with that name already exists,
            a date will be added after the file name and before the file extension
        """
        file_split = lesson_path.split(".")
        *all, file_ext = file_split
        file_path = ".".join(all)

        if os.path.exists(f"{file_path}.{file_ext}"):
            lesson_path = f"{file_path}{datetime.now().strftime("%Y%m%d%H%M%S")}.{file_ext}"

        with open(lesson_path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["question", "tag_question", "answers", "tag_answers"])
            for lesson_term in lesson.lesson_terms:
                writer.writerow([lesson_term.term1.value.strip(), lesson_term.term1.tag.name
                                 , lesson_term.term2.value.strip(), lesson_term.term2.tag.name])

        return lesson_path