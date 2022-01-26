"""Script to seed the trivia database."""

import os
import json
from random import choice, randint

import crud
import model
import server

from tests import RobotTestsDatabase

# Purge old databases:
db_name = "trivia"
os.system(f"dropdb {db_name}")

os.system(f"createdb {db_name}")

model.connect_to_db(server.app)
model.db.create_all()

NUM_SEED_ANSWERS = 20

test_params = RobotTestsDatabase()
test_params.make_users()
test_params.make_questions()

possible_answers = crud.compile_possible_answers()
for _ in range(NUM_SEED_ANSWERS):    
    for user_instance in crud.get_users():
        random_answer_given = choice(possible_answers)
        # unique_question = crud.get_unique_question(user_instance.user_id)
        unique_question = crud.get_random_question()
        if unique_question:
            one_user_answer_instance = crud.create_user_answer(
                user_id=user_instance.user_id, 
                question_id=unique_question.question_id, 
                answer_given = random_answer_given)