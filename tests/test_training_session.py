
from src.pecreierul.training import TrainingSession, TrainingUnit

def test_basic_training():

    question_answers = {"q1":"a1", "q2":"a2", "q3":"a3", "q4":"a4"}

    session = TrainingSession({"q1":"a1", "q2":"a2", "q3":"a3", "q4":"a4"}, 3, 3)

    unit = session.get_next()

    assert unit is not None
    assert unit.answer == question_answers[unit.question]
    assert len(unit.fake_answers) == 3
    assert unit.fake_answers[0] in question_answers.values()
    assert unit.fake_answers[1] in question_answers.values()
    assert unit.fake_answers[2] in question_answers.values()

    i = 0
    while unit is not None and session.submit_answer(unit.answer):
        unit = session.get_next()
        i += 1

    assert i == 8
    assert session.get_next() is None
    dist = session.get_current_distribution()
    exp = [0, 0, 4]

    for i in range(0, 3):
        assert dist[i] == exp[i]

def test_incorrect_answers():
    question_answers = {"q1":"a1", "q2":"a2", "q3":"a3", "q4":"a4"}
    
    session = TrainingSession({"q1":"a1", "q2":"a2", "q3":"a3", "q4":"a4"}, 3, 3)

    unit = session.get_next()

    for i in range(0,6):
        if unit is not None:
            session.submit_answer(unit.answer)
            unit = session.get_next()

    assert unit is not None
    assert session.submit_answer("bla") == False
