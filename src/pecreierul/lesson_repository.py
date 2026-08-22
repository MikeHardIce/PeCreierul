from collections import deque
import random
from typing import Dict, List, Tuple
from dataclasses import dataclass
from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

from pecreierul.database import Lesson, LessonTerm, Tag, Term

@dataclass
class Paging:
    page_from: int = 0
    page_to: int = 10

class LessonRepository:

    def delete_lessons(self, session: Session, lessons: List[Lesson]):
        for lesson in lessons:
            session.delete(lesson)
            
    def load_all_lessons(self, session: Session, paging: Paging = Paging(0, 100)) -> List[Lesson]:
        return list(session.scalars(select(Lesson).offset(paging.page_from).limit(paging.page_to - paging.page_from)).all())
    
    def load_lesson_by_id(self, session: Session, id: int) -> Lesson:
        return session.scalar(select(Lesson).where(Lesson.id == id))

    def load_all_terms(self, session: Session, paging: Paging = Paging(0, 100)) -> List[Term]:
        return list(session.scalars(select(Term).offset(paging.page_from).limit(paging.page_to - paging.page_from)).unique())

    def load_all_tags(self, session: Session, paging: Paging = Paging(0, 100)) -> List[Tag]:
        return list(session.scalars(select(Tag).offset(paging.page_from).limit(paging.page_to - paging.page_from)).unique())

    def save_lessons(self, session: Session, lessons: List[Lesson]):
        session.add_all(lessons)

    def save_tag(self, session: Session, tag: Tag) -> None:
        session.add(tag)

    def delete_tag_by_id(self, session: Session, id: int) -> None:
        tag = session.scalar(select(Tag).where(Tag.id == id))
        session.delete(tag)
        
    def attach_to_lesson(self, lesson: Lesson, term1_str: str, tag1_str: str, term2_str: str, tag2_str: str) -> None:
        lesson.lesson_terms.append(LessonTerm(term1=Term(value= term1_str, tag= Tag(name=tag1_str)), term2= Term(value= term2_str, tag= Tag(name=tag2_str))))