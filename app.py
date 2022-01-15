from flask import Flask, request, jsonify
from bot import Bot, get_random_string
import json
import os
import requests

app = Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
def home():
    if request.method == 'POST':
        bot = Bot(request.json)
        return bot.processing()
    return "Processing..."


@app.route('/payments/')
def payments():
    
    if request.args:
        print(request.args)
        arguments = request.args
        payment_id = arguments.get('razorpay_payment_id')
        payment_status = arguments.get('razorpay_payment_link_status')
        reference_id = arguments.get('razorpay_payment_link_reference_id')
        print(payment_status)
        chatID = reference_id[10:]
        print(chatID)
        path = 'C:/Users/jmdee/Downloads/bus-booking-bot-main/bus-booking-bot-main/bus-booking-bot/orders/' + chatID + '_ongoing.json'
        with open(path, mode='r+') as f:
            state_dict = json.load(f)
        state_dict['payment_id'] = payment_id
        with open(path, mode='w+') as f:
            json.dump(state_dict, f)
        if payment_status == 'paid':

            state_dict['payment'] = 'paid'
            state_dict['payment_id'] = payment_id
            text = f"""Your payment was successful\n\n*_Congratulations_*\nYour seat has been booked """
            APIUrl = 'https://eu208.chat-api.com/instance<Instance id>/'
            token = '<Token>'
            data = {
                'chatId' : chatID,
                'body' : text
            }
            url = f"{APIUrl}sendMessage?token={token}"
            headers = {'Content-type': 'application/json'}
            res = requests.post(url=url, data=json.dumps(data), headers=headers)
            print(res.json())
            # same as hospital bot
            
            with open(path, mode='w+') as f:
                json.dump(state_dict, f)
            
            return "<h1>Payment Was Successful</h1>"
        else:
            return "<h1>Payment Was Not Successful</h1>"
    return ''


if __name__ == '__main__':
    app.run()
