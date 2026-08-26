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
                            tag1 = tags[row["tag_question"]] if row["tag_question"] in tags else Tag(name=row["tag_question"])
                            tag2 = tags[row["tag_answers"]] if row["tag_answers"] in tags else Tag(name=row["tag_answers"])
                            lesson_term = LessonTerm()
                            lesson_term.term1 = Term(value = row["question"].strip(), tag = tag1)
                            lesson_term.term2 = Term(value = row["answers"].strip(), tag = tag2)
                            lesson.lesson_terms.append(lesson_term)

                            duplicate_catcher.add(entry)
        

    @staticmethod
    def export_lesson(lesson: Lesson, lesson_path: str):
        with open(lesson_path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["question", "answers", "tag_question", "tag_answers"])
            for lesson_term in lesson.lesson_terms:
                writer.writerow([lesson_term.term1.value.strip(), lesson_term.term1.tag.name
                                 , lesson_term.term2.value.strip(), lesson_term.term2.tag.name])