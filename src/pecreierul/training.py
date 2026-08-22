from collections import deque
from dataclasses import dataclass
import random
from typing import Dict, List

class TrainingUnit:
    question: str
    answer: str
    occurence: int = 0
    fake_answers: List[str] = []

    def __init__(self, question: str, answer: str):
        self.question = question
        self.answer = answer

class TrainingSession:

    stacks: List[deque[TrainingUnit]]
    all_answers: List[str]
    current_unit: TrainingUnit | None
    current_stack: int = 0
    number_of_fake_answers: int = 0

    def __init__(self, question_answers: Dict[str, str], number_of_stacks: int = 5, number_of_fake_answers: int = 4):
        """
            Args:
                question_answers - dictionary consisting of question answer pairs to be trained
                number_of_stacks - number of how many stacks need each unit pass
                number_of_fake_answers - number of fake answers that will get returned with each unit (fake answers 
                will be assigned new each time a unit is returned)
        """
        units = [TrainingUnit(question = k, answer = v) for k,v in question_answers.items()]

        self.all_answers = [u.answer for u in units]
        self.stacks = [deque(units)] + [deque() for _ in range(0, number_of_stacks - 1)]

        self.number_of_fake_answers = number_of_fake_answers

    def get_next(self) -> TrainingUnit | None:
        """
            Gets the next unit from a random stack which isn't the last stack.

            Return:
                The next unit or None if all units are located on the last stack. 
                Then the training is complete.
        """
        dist = self.get_current_distribution()

        available_stacks: List[int] = []
        for index, u  in enumerate(dist):
            if u > 0 and index < (len(dist) - 1):
                available_stacks.append(index)

        if len(available_stacks) > 0:
            self.current_stack = random.choice(available_stacks)
        else:
            return None

        self.current_unit = self.stacks[self.current_stack].popleft()

        fake_answers = list(set(self.all_answers).difference(set([self.current_unit.answer])))
        self.current_unit.fake_answers = random.choices(fake_answers, k=self.number_of_fake_answers) \
                                         if self.number_of_fake_answers > 0 else []
        
        return self.current_unit

    def submit_answer(self, answer: str) -> bool:
        """
            Checks if the answer is correct. If it is wrong, the unit goes to the previous stack. 
            If correct, the unit moves to the next stack.
            Args:
                answer (str): answer to the current units question

            Return:
                True - answer was correct
                False - answer was wrong
        """
        if self.current_unit is None:
            return False

        is_answer_correct = self.current_unit.answer.lower().strip() == answer.lower().strip()

        if is_answer_correct:
            self.current_stack += 1
        else:
            self.current_stack -= 0 if self.current_stack == 0 else 1

        self.stacks[self.current_stack].append(self.current_unit)
        self.current_unit = None

        return is_answer_correct

    def get_current_distribution(self) -> List[int]:
        return [len(x) for x in self.stacks]