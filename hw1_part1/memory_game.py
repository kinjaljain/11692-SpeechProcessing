import logging
from random import randint
from flask import Flask, render_template
from flask_ask import Ask, statement, question, session

app = Flask(__name__)
ask = Ask(app, "/")
logging.getLogger("flask_ask").setLevel(logging.DEBUG)

@ask.launch
def new_game():
    welcome_msg = render_template('welcome')
    return question(welcome_msg)

@ask.intent("YesIntent")
def next_round():
    index = randint(1, 3)
    numbers = [randint(0, 9) for _ in range(3)]
    round_msg = render_template('ask_question_{}'.format(index), numbers=numbers)
    print round_msg
    session.attributes['numbers'] = numbers[::-1]  # reverse
    return question(round_msg)

@ask.intent("AnswerIntent", convert={'first': int, 'second': int, 'third': int})
def answer(first, second, third):
    index = randint(1, 3)
    winning_numbers = session.attributes['numbers']
    if [first, second, third] == winning_numbers:
        msg = render_template('win_{}'.format(index))
        return question(msg)
    else:
        msg = render_template('lose_{}'.format(index))
        return question(msg)
    # return statement(msg)

@ask.intent("NoIntent")
def end_game():
    msg = render_template('end')
    return statement(msg)

if __name__ == '__main__':
    app.run()
