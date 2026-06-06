from typing import List
from sqlalchemy import func
from sqlalchemy import String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship, mapped_column, Mapped

Base = declarative_base()

class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(Integer, primary_key= True, autoincrement= True)
    name: Mapped[str] = mapped_column(String, nullable= False)
    description: Mapped[str] = mapped_column(String)
    created: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    modified: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

    lesson_terms: Mapped[List["LessonTerm"]] = relationship("LessonTerm", back_populates= "lesson", cascade="all, delete-orphan", single_parent=True)

    def __repr__(self) -> str:
        return f"id:{self.id} name: {self.name} description: {self.description} created: {self.created} modified: {self.modified} \n" \
                + "-->" + "".join([l.__repr__() for l in self.lesson_terms])

class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key= True, autoincrement= True)
    name: Mapped[str] = mapped_column(String, nullable= False, unique=True)

    linked_terms: Mapped[List["Term"]] = relationship("Term", back_populates= "tag")

class Term(Base):
    __tablename__ = "terms"

    id: Mapped[int] = mapped_column(Integer, primary_key= True, autoincrement= True)
    value: Mapped[str] = mapped_column(String, nullable= False)
    created: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    modified: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    tag_id: Mapped[int] = mapped_column(Integer, ForeignKey("tags.id"))
    
    
    tag: Mapped[Tag] = relationship("Tag", back_populates="linked_terms")

    def __repr__(self) -> str:
        return f"id: {self.id} value: {self.value} ({self.tag.name})  created: {self.created} modified: {self.modified}"


class LessonTerm(Base):
    __tablename__ = "lessons_terms"

    id: Mapped[int] = mapped_column(Integer, primary_key= True, autoincrement= True)
    lesson_id: Mapped[int] = mapped_column(Integer, ForeignKey("lessons.id"))
    lesson: Mapped[Lesson] = relationship("Lesson", back_populates= "lesson_terms")

    term1_id: Mapped[int] = mapped_column(Integer, ForeignKey("terms.id"))
    term2_id: Mapped[int] = mapped_column(Integer, ForeignKey("terms.id"))

    term1: Mapped[Term] = relationship("Term", foreign_keys="LessonTerm.term1_id", cascade="all, delete-orphan", single_parent=True)
    term2: Mapped[Term] = relationship("Term", foreign_keys="LessonTerm.term2_id", cascade="all, delete-orphan", single_parent=True)

    def __repr__(self) -> str:
        return f"id: {self.id} term1: {self.term1.value} ({self.term1.tag.name}) term2: {self.term2.value} ({self.term2.tag.name})"