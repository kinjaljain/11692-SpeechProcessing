import logging
from random import randint
from flask import Flask, render_template
from flask_ask import Ask, statement, question, session

app = Flask(__name__)
ask = Ask(app, "/")
logging.getLogger("flask_ask").setLevel(logging.DEBUG)
num_dict = {
    1: "first",
    2: "second",
    3: "third",
    4: "fourth"
}
PIZZA_TOPPINGS = ["sausage", "pepperoni", "bacon", "ham", "meatball", "meatballs", "mushroom", "mushrooms", "onion",
                  "onions", "olive", "olives", "capsicum",  "capsicums", "jalapeno", "jalapenos", "tomatoes", "tomato",
                  "corn", "spinach", "broccoli", "cheese", "steak", "shrimp", "shrimps", "paneer", "tofu"]
UNUSUAL_TOPPPINGS = ["pineapple", "pineapples", "watermelon", "watermelons", "apple", "apples", "kiwi", "kiwis",
                     "cashew", "cashews", "fries", "chocolate", "raisin", "raisins"]
DRINKS = ["coke", "lemonade"]
SIZES = ["regular", "medium", "large"]
CRUSTS = ["focaccia", "thin", "thick", "cheese"]

@ask.launch
def welcome_ask():
    index = randint(1, 4)
    welcome_msg = render_template('welcome_{}'.format(index))
    session.attributes['state'] = ['welcome']
    return question(welcome_msg).reprompt("I am waiting for your response")


@ask.intent("FetchSizeIntent", convert={'size': str})
def ask_crust(size):
    num_current_pizza = session.attributes.get('number', 0)
    if size not in SIZES:
        msg = render_template('out_of_options_size')
        return question(msg).reprompt("I am waiting for your response")

    if num_current_pizza > 1:
        session.attributes['pizza'][str(num_current_pizza)] = {"size": size}
        msg = render_template('ask_crust_multiple')
        session.attributes['state'].append(['added_size'])
        return question(msg).reprompt("I am waiting for your response")

    index = randint(1, 2)
    session.attributes['pizza'][str(num_current_pizza)] = {"size": size}
    msg = render_template('ask_crust_{}'.format(index))
    session.attributes['state'].append(['added_size'])
    return question(msg).reprompt("I am waiting for your response")


@ask.intent("FetchCrustIntent", convert={'crust': str})
def ask_toppings(crust):
    num_current_pizza = session.attributes.get('number', 0)
    if crust not in CRUSTS:
        msg = render_template('out_of_options_crust')
        return question(msg).reprompt("I am waiting for your response")

    current_pizza_details = session.attributes['pizza'][str(num_current_pizza)]
    current_pizza_details.update({"crust": crust})
    session.attributes['pizza'][str(num_current_pizza)] = current_pizza_details
    msg = render_template('want_toppings_or_not')
    session.attributes['state'].append('added_crust')
    return question(msg).reprompt("I am waiting for your response")


@ask.intent("AskToppingsIntent")
def tell_and_ask_toppings():
    msg = render_template('possible_toppings')
    session.attributes['state'].append('ask_toppings')
    return question(msg).reprompt("I am waiting for your response")


@ask.intent("FetchToppingsIntent", convert={'first': str, 'second': str, 'third': str, 'fourth': str})
def ask_order_details(first, second, third, fourth):
    toppings = []
    msg = ""
    if first:
        first_toppings = first.split()
        for i in range(len(first_toppings)):
            toppings.append(first_toppings[i])
    if second:
        second_toppings = second.split()
        for i in range(len(second_toppings)):
            toppings.append(second_toppings[i])
    if third:
        third_toppings = third.split()
        for i in range(len(third_toppings)):
            toppings.append(third_toppings[i])
    if fourth:
        fourth_toppings = fourth.split()
        for i in range(len(fourth_toppings)):
            toppings.append(fourth_toppings[i])
    if len(toppings) > 4:
        msg = render_template('more_than_4_topping')
        return question(msg)
    print(toppings)
    total_toppings = PIZZA_TOPPINGS + UNUSUAL_TOPPPINGS
    for topping in toppings:
        if topping not in total_toppings:
            msg = render_template('out_of_options_topping', toppings=topping)
            return question(msg).reprompt("I am waiting for your response")
    num_current_pizza = session.attributes.get('number', 0)
    current_pizza_details = session.attributes['pizza'][str(num_current_pizza)]
    current_pizza_details.update({'toppings': toppings})
    current_pizza_details.update({'plain': False})
    session.attributes['pizza'][str(num_current_pizza)] = current_pizza_details
    session.attributes['state'].append('added_toppings')
    print session.attributes['pizza']
    for topping in toppings:
        if topping in UNUSUAL_TOPPPINGS:
            msg += render_template('unusual_topping_remark', unusual_topping=topping)
            break
    msg += render_template('confirm_order')
    session.attributes['state'].append('confirm_details')
    return question(msg).reprompt("I am waiting for your response")

@ask.intent("FetchDrinkIntent", convert={'drink': str, 'number': int})
def end(drink, number):
    if drink not in DRINKS:
        msg = render_template('out_of_options_drink')
        return question(msg).reprompt("I am waiting for your response")
    state = session.attributes['state']
    if state[-1] == 'ask_drink':
        msg = render_template('drink_yes_intent')
        session.attributes['drink'] = drink
        if number:
            msg += render_template('confirm_drink_glasses', number=number, drink=drink)
        else:
            msg += render_template('confirm_drink', drink=drink)
        msg += render_template('end_with_drink')
        session.attributes['state'].append('end_with_drink')
        return statement(msg)

@ask.intent("YesIntent")
def yes():
    state = session.attributes['state']
    number_of_pizzas = session.attributes.get('number', 0)
    if state[-1] == "welcome":
        index = randint(1, 2)
        number_of_pizzas = session.attributes.get('number', 0)
        if number_of_pizzas == 0:
            number_of_pizzas = 1
        session.attributes['number'] = number_of_pizzas
        session.attributes['pizza'] = {str(number_of_pizzas): {}}
        msg = render_template('ask_size_{}'.format(index))
        session.attributes['state'].append('start_order')
        return question(msg).reprompt("I am waiting for your response")

    elif state[-1] == "confirm_details":
        if number_of_pizzas == 1:
            msg = render_template('confirm_order_details_1', number=session.attributes['number'])
            pizza_details = session.attributes['pizza'][str(1)]
            is_plain = pizza_details['plain']
            if is_plain:
                msg += render_template('confirm_order_without_topping_1', size=pizza_details['size'],
                                       crust=pizza_details['crust'])
            else:
                msg += render_template('confirm_order_in_detail', size=pizza_details['size'],
                                       crust=pizza_details['crust'], toppings=pizza_details['toppings'])
        else:
            print number_of_pizzas
            msg = render_template('confirm_order_details_many', number=session.attributes['number'])
            for i in range(1, number_of_pizzas+1):
                print i
                print session.attributes['pizza']
                pizza_details = session.attributes['pizza'][str(i)]
                is_plain = pizza_details['plain']
                if is_plain:
                    msg += render_template('confirm_order_without_topping_many', i=num_dict[i],
                                           size=pizza_details['size'], crust=pizza_details['crust'])
                else:
                    msg += render_template('confirm_order_many_in_detail', i=num_dict[i], size=pizza_details['size'],
                                           crust=pizza_details['crust'], toppings=pizza_details['toppings'])

        index = randint(1, 2)
        session.attributes['state'].append('order_more')
        msg += render_template('order_more_{}'.format(index))
        return question(msg).reprompt("I am waiting for your response")

    elif state[-1] == "added_crust":
        index = randint(1, 2)
        msg = render_template('ask_toppings_{}'.format(index))
        session.attributes['state'].append('ask_toppings')
        return question(msg).reprompt("I am waiting for your response")

    elif state[-1] == 'ask_drink':
        msg = render_template('drink_yes')
        session.attributes['state'].append('ask_drink')
        return question(msg).reprompt("I am waiting for your response")

    elif state[-1] == "order_more":
        msg = render_template('ask_if_same_as_previous')
        session.attributes['number'] += 1
        session.attributes['pizza'][str(session.attributes['number'])] = {}
        session.attributes['state'].append('asking_next_order_same_or_not')
        return question(msg).reprompt("I am waiting for your response")

    elif state[-1] == "asking_next_order_same_or_not":
        pizza_2 = session.attributes['pizza'][str(number_of_pizzas-1)]
        session.attributes['pizza'].update({str(number_of_pizzas): pizza_2})
        msg = render_template('confirm_added_another_pizza')
        session.attributes['state'].append('added_pizza')
        msg += render_template('confirm_order')
        session.attributes['state'].append('confirm_details')
        return question(msg).reprompt("I am waiting for your response")

@ask.intent("NoIntent")
def no():
    state = session.attributes['state']
    if state[-1] == "welcome":
        msg = render_template('no_pizza_order')
        session.attributes['state'].append('no_pizza_order')
        return statement(msg)

    elif state[-1] == "added_crust":
        session.attributes['plain'] = True
        num_current_pizza = session.attributes.get('number', 0)
        current_pizza_details = session.attributes['pizza'][str(num_current_pizza)]
        current_pizza_details.update({'toppings': []})
        current_pizza_details.update({'plain': True})
        session.attributes['pizza'][str(num_current_pizza)] = current_pizza_details
        print session.attributes['pizza']
        msg = render_template('confirm_order')
        session.attributes['state'].append('confirm_details')
        return question(msg).reprompt("I am waiting for your response")

    elif state[-1] == 'confirm_details':
        index = randint(1, 2)
        msg = render_template('order_more_{}'.format(index))
        session.attributes['state'].append('order_more')
        return question(msg).reprompt("I am waiting for your response")

    elif state[-1] == 'order_more':
        msg = render_template('ask_drink')
        session.attributes['state'].append('ask_drink')
        return question(msg).reprompt("I am waiting for your response")

    elif state[-1] == "asking_next_order_same_or_not":
        number_of_pizzas = session.attributes.get('number', 0) + 1
        if number_of_pizzas > 1:
            msg = render_template('ask_size_multiple')
            session.attributes['state'].append('start_order')
            return question(msg).reprompt("I am waiting for your response")

    elif state[-1] == 'ask_drink':
        msg = render_template('end_no_drink')
        session.attributes['state'].append('no_drink')
        return statement(msg)


if __name__ == '__main__':
    app.run()
