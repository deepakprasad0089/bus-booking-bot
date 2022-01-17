import json
import os
import requests
import csv
import re
import time
import random
import string
import uuid
import mysql.connector
import pickle
from requests.auth import HTTPBasicAuth
from datetime import datetime, date, timezone, timedelta
from itertools import chain 
mydb=mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="ridebus"
)

mycursor=mydb.cursor()
class Bot():
    def __init__(self, json):
        
        self.json = json
        self.dict_messages = self.json['messages']
        self.APIUrl = 'https://eu208.chat-api.com/instance<Instance id>/'
        self.token = '<Token>'

    def send_requests(self, method, data):
        
        url = f"{self.APIUrl}{method}?token={self.token}"
        headers = {'Content-type': 'application/json'}
        response = requests.post(url, data=json.dumps(data), headers=headers)
        print(response.json())
        return response.json()

    def send_message(self, chatID, text):
        
        data = {
            'chatId': chatID,
            'body': text
        }
        answer = self.send_requests('sendMessage', data)
        return answer
    
    

    def generate_payment_link(self, reference_id, amount):
        
        reference_id = reference_id
        data = {
            "amount": amount,
            "currency": "INR",
            "description": "Testing",
            "reference_id": reference_id,
            "callback_url": "https://571a-2409-4050-e15-c6a4-e5c2-f926-777e-d4ea.ngrok.io/payments/",
            "callback_method": "get"
        }
        data = json.dumps(data)
        headers = {
            'Content-type': 'application/json'
        }
        res = requests.post(url="https://api.razorpay.com/v1/payment_links/", headers=headers, data=data,
                            auth=HTTPBasicAuth('<Username>', '<password>')).json()
        print(res)
        return res

    def welcome_user(self, chatID, text):
        return self.send_message(chatID, text)

    def ask_next_question(self, chatID, text):
        return self.send_message(chatID, text)
   
    
    def ticket_order(self, chatID, string):
        path = 'C:/Users/jmdee/Downloads/bus-booking-bot-main/bus-booking-bot-main/bus-booking-bot/orders/'+chatID+'_ongoing.json'
        with open(path, mode='r') as f:
            user = json.load(f)
            
        text = f"""Here is your ticket :\n\n*Ticket No.-*{user.get('ticket_no.')}\n*Bus No.- *{user.get('bus_no')}\n*Bus company -*{user.get('bus')}\n*From -*{user.get('from')}\n*To -*{user.get('to')}\n*Seat No -*{user.get('book_seat')}\n*Seat Type -*{user.get('seat')}\n*Name -*{user.get('name')}\n*Age -*{user.get('age')}\n*Gender -*{user.get('gender')}\n*Contact details of operator -*{user.get('contact')}"""
        if string:
            text = string + text
        return self.send_message(chatID, text)
    def cal_cost(self, quantity, cost_per_quantity):
        return quantity * cost_per_quantity
    def calculate_ticket_cost(self,amount,book_seat):
        return amount*book_seat
    
    
    def processing(self):
        
        t=''
        a=''
        #li=[]
        
        print('hii')                                   
        if self.dict_messages:
            print('Hi')
            for message in self.dict_messages:
                text = message['body']
                id = message['chatId']
                if not message['fromMe']:
                    if '@g.us' in str(id):
                        continue
                    question_dict = {}
                    with open("C:/Users/jmdee/Downloads/bus-booking-bot-main/bus-booking-bot-main/bus-booking-bot/Questions/questions.csv", mode='r',encoding="utf-8") as f:
                        reader = csv.reader(f)
                        question_dict = {rows[0]: rows[1].replace(
                            '\\n', '\n') for rows in reader}
                    keys = list(question_dict.keys())
                    path = 'C:/Users/jmdee/Downloads/bus-booking-bot-main/bus-booking-bot-main/bus-booking-bot/orders/' + id + '_ongoing.json'
                    state_dict = {}
                    phone_number = id[:12]
                    if not os.path.isfile(path):
                        state_dict['id'] = id
                        state_dict['reference_id'] = str(
                            get_random_string(10)) + id
                        state_dict['phone_number'] = '+' + phone_number
                        state_dict['state'] = keys[1]
                        with open(path, mode='w+') as f:
                            json.dump(state_dict, f)
                        return self.welcome_user(id, question_dict[keys[1]])

                    else:
                        with open(path, mode='r+') as f:
                            state_dict = json.load(f)
                        state = state_dict.get('state')

                        if text.lower() == 'reset':
                            os.remove(path)
                            return self.welcome_user(id,question_dict[keys[1]])

                        try:
                            index_of_key = keys.index(state)
                        except:
                            pass
                        if state == 'wlcm_msg': 
                            mycursor.execute("SELECT from_ FROM ridebus")
                            myresult=mycursor.fetchall()
                            myresult=set(myresult)
                            myresult=list(myresult)
                            a='\n'.join([str(v+1) +". "+ str(x)for v,l in enumerate(myresult) for x in l])
                            t=a
                            li= list(chain(*myresult))
                            with open("text.txt","wb") as fp:
                                pickle.dump(li,fp)
                            
                            print(f"list{li}")
                            if text.lower() not in ['yes', 'no']:
                                err_msg = "Please reply with Yes or No\n\n" + \
                                    question_dict[keys[1]]
                                return self.send_message(id, err_msg)
                            elif text.lower() == 'no':
                                os.remove(path)
                                return self.send_goodbye(id)

                        if state == 'address':
                            if len(text.split('\n')) < 3:
                                err_msg = 'Entered information was not in valid format\n\n' + \
                                    question_dict[keys[index_of_key]]
                                return self.send_message(id, err_msg)

                        if state == 'location':
                            temp = text.split(';')
                            try:
                                temp[0] = float(temp[0])
                                temp[1] = float(temp[1])
                                text = tuple(temp)
                            except:
                                err_msg = 'Sent information was not a valid location\n\n' + \
                                    question_dict[keys[index_of_key]]
                                return self.send_message(id, err_msg)
                            location_regex = re.compile(
                                r'^(\()([-+]?)([\d]{1,2})(((\.)(\d+)(,)))(\s*)(([-+]?)([\d]{1,3})((\.)(\d+))?(\)))$')
                            if not re.match(location_regex, str(text)):
                                err_msg = 'Sent information was not a valid location\n\n' + \
                                    question_dict[keys[index_of_key]]
                                return self.send_message(id, err_msg)
                        
                        elif state=='name':
                            try:
                              if len(text) <3:
                                 raise ValueError
                            except:
                               err_msg = '*Proper name needed*\n\n'+ \
                                    question_dict[keys[index_of_key]]
                               return self.send_message(id, err_msg)
                            state_dict[state]=text
                        elif state=='age':
                            try:
                              if int(text) <8 or int(text)>100:
                                 raise ValueError
                            except:
                               err_msg = '*No with that age can travel*\n\n'+ \
                                    question_dict[keys[index_of_key]]
                               return self.send_message(id, err_msg)
                            state_dict[state]=text
                        elif state=='gender':
                            
                            try:
                              if text !='M' and text !='F' and text !='O':
                                 raise ValueError
                            except:
                               err_msg = '*Wrong Gender*\n\n'+ \
                                    question_dict[keys[index_of_key]]
                               return self.send_message(id, err_msg)
                            u=''.join(random.choice(string.digits) for i in range(10))
                            ticket_no={"ticket_no.":u}
                            mycursor.execute(f"SELECT bus_no,contact FROM ridebus where from_ = '{state_dict['from']}'  and to_ ='{state_dict['to']}'and bus='{state_dict['bus']}' ")
                            print(f"cursor{mycursor}")

                            myresult=mycursor.fetchall()
                            print(myresult)
                            myresult=set(myresult)
                            myresult=list(myresult)
                            myresult=list(myresult[0])
                            print(f'ticket {myresult}')
                            print(f'bus{myresult[0]}')
                            bus_no={"bus_no":myresult[0]}
                            contact={"contact":str(myresult[1])}
                            with open( 'C:/Users/jmdee/Downloads/bus-booking-bot-main/bus-booking-bot-main/bus-booking-bot/orders/' + id + '_ongoing.json', mode='r') as j:
                                 data=json.load(j)    
                            print(f'data={data}')                        
                            data.update(ticket_no)
                            data.update(bus_no)
                            data.update(contact)
                            data.update({'gender':text})
                            print(f"datais {data}")
                            with open( 'C:/Users/jmdee/Downloads/bus-booking-bot-main/bus-booking-bot-main/bus-booking-bot/orders/' + id + '_ongoing.json', mode='w+') as o:
                              print(f"datadump {data}")
                              json.dump(data,o)
                            #state_dict[state]=text
                            self.ticket_order(id,'')
                        elif state=='pay':
                            try:
                              if(state_dict['payment']=="paid"):
                                self.send_message(id,"")
                                
                            except:
                                self.send_message(id,"You haven't made the payment .\nPlease pay the amount in the above link to proceed") 
                            

                            
                           
                            
                        elif state=='from':
                            #if len(text) not in range(1, 4):
                            
                            #for x in myresult:
                               # a=' \n'.join(x)
                            with open("text.txt","rb") as fp:
                                li=pickle.load(fp)
                            print(f"from {li}")
                            i=int(text)
                            
                            length=len(li)
                            a='\n'.join([str(v+1) +". "+ str(l)for v,l in enumerate(li)])
                            t=a
                            #li.clear()
                            try:
                              if int(text) not in range(1, length+1):
                                 raise ValueError
                            except:
                               err_msg = 'choose valid option \n\n  '  + \
                                    question_dict[keys[index_of_key]]+t
                               return self.send_message(id, err_msg)
                            '''i=int(text)
                            state_dict[state]=li[i-1]
                            li.clear()'''
                            state_dict[state]=li[i-1]
                            li.clear()
                            x=state_dict['from']
                            mycursor.execute(f"SELECT to_ FROM ridebus where from_ = '{x}'")
                            myresult=mycursor.fetchall()
                            myresult=set(myresult)
                            myresult=list(myresult)
                            a='\n'.join([str(v+1) +". "+ str(x)for v,l in enumerate(myresult) for x in l])
                            t=a
                            #mycursor.execute("SELECT from_ FROM ridebus")
                            #myresult=mycursor.fetchall()
                            myresult=set(myresult)
                            myresult=list(myresult)
                            #a='\n'.join([str(v+1) +". "+ str(x)for v,l in enumerate(myresult) for x in l])
                            #li=list(chain(*myresult))
                            print(f"{text}")
                            '''i=int(text)
                            state_dict[state]=li[i-1]
                            li.clear()'''
                            li=list(chain(*myresult))
                            with open("text.txt","wb") as fp:
                                pickle.dump(li,fp)
                            #i=int(text)
                            #state_dict[state]=li[i-1]
                        elif state=='to':
                            with open("text.txt","rb") as fp:
                                li=pickle.load(fp)
                            print(f"from {li}")
                            i=int(text)
                           
                            length=len(li)
                            #li.clear()
                            a='\n'.join([str(v+1) +". "+ str(l)for v,l in enumerate(li)])
                            t=a
                            try:
                              if int(text) not in range(1, length+1):
                                 raise ValueError
                            except:
                               err_msg = 'choose valid option \n\n  '  + \
                                    question_dict[keys[index_of_key]]+t
                               return self.send_message(id, err_msg)
                            state_dict[state]=li[i-1]
                            li.clear()
                            x=state_dict['to']
                            mycursor.execute(f"SELECT bus FROM ridebus where from_ = '{state_dict['from']}' and to_ ='{state_dict['to']}'")
                            myresult=mycursor.fetchall()
                            myresult=set(myresult)
                            myresult=list(myresult)
                            print(f"bus{myresult}")
                            a='\n'.join([str(v+1) +". "+ str(x)for v,l in enumerate(myresult) for x in l])
                            t=a
                            #mycursor.execute("SELECT from_ FROM ridebus")
                            #myresult=mycursor.fetchall()
                            myresult=set(myresult)
                            myresult=list(myresult)
                            #a='\n'.join([str(v+1) +". "+ str(x)for v,l in enumerate(myresult) for x in l])
                            #li=list(chain(*myresult))
                            print(f"{text}")
                            '''i=int(text)
                            state_dict[state]=li[i-1]
                            li.clear()'''
                            li=list(chain(*myresult))
                            with open("text.txt","wb") as fp:
                                pickle.dump(li,fp)
                        elif state=='bus':
                            with open("text.txt","rb") as fp:
                                li=pickle.load(fp)
                            print(f"from {li}")
                            i=int(text)
                            length=len(li)
                            a='\n'.join([str(v+1) +". "+ str(l)for v,l in enumerate(li)])
                            t=a
                         
                            try:
                              if int(text) not in range(1, length +1):
                                 raise ValueError
                            except:
                               err_msg = 'choose valid option \n\n  '  + \
                                    question_dict[keys[index_of_key]]+t
                               return self.send_message(id, err_msg)
                            
                            state_dict[state]=li[i-1]
                            length=len(li)
                            li.clear()
                            x=state_dict['to']
                            mycursor.execute(f"SELECT seat FROM ridebus where from_ = '{state_dict['from']}'  and to_ ='{x}'and bus='{state_dict['bus']}' ")
                            myresult=mycursor.fetchall()
                            myresult=set(myresult)
                            myresult=list(myresult)
                            #myresult=list(myresult[0])
                           
                            myresult=list(myresult[0])
                            print(myresult)
                            myresult=myresult[0].split(",")
                            a='\n'.join([str(v+1) +". "+ str(l)for v,l in enumerate(myresult)])
                            '''com1=a.find(',')
                            print(f"first comma {com1}")
                            a.replace(',','\n2.',1)
                            print(a)
                            com2=a.find(',',com1+1,-1)
                            print(f"first comma {com2}")
                            print(a)
                            a[com2:].replace(',','\n3.',1)
                            com3=a.find(',',com2+1,-1)
                            print(f"first comma {com3}")
                            a[com3:].replace(',','\n4.',1)'''
                            t=a
                            #mycursor.execute("SELECT from_ FROM ridebus")
                            #myresult=mycursor.fetchall()
                           # myresult=set(myresult)
                           # myresult=list(myresult)
                           # myresult=list(myresult[0])
                           # print(myresult)
                           # myresult=myresult[0].split(",")
                           # print(myresult)
                           # print('\n'.join([str(v+1) +". "+ str(l)for v,l in enumerate(myresult) ]))
                            #a='\n'.join([str(v+1) +". "+ str(x)for v,l in enumerate(myresult) for x in l])
                            #li=list(chain(*myresult))
                           # print(f"{text}")
                            '''i=int(text)
                            state_dict[state]=li[i-1]
                            li.clear()'''
                            li=myresult
                            with open("text.txt","wb") as fp:
                                pickle.dump(li,fp)

                        elif state=='seat':
                            with open("text.txt","rb") as fp:
                                li=pickle.load(fp)
                            print(f"from {li}")
                            i=int(text)
                            
                            length=len(li)
                            a='\n'.join([str(v+1) +". "+ str(l)for v,l in enumerate(li)])
                            m=a
                            try:
                              if int(text) not in range(1, length+1):
                                 raise ValueError
                            except:
                               err_msg = 'choose valid option \n\n  '  + \
                                    question_dict[keys[index_of_key]]+m
                               return self.send_message(id, err_msg)
                            state_dict[state]=li[i-1]
                            li.clear()
                            t=''
                            a=''
                            print(f"inside of seat {t}")

                        elif state=='book_seat':
                            try:
                              if text.isdigit()=='False':
                                 raise ValueError
                            except:
                               err_msg = 'Enter a number \n\n  '  + \
                                    question_dict[keys[index_of_key]]+t
                               return self.send_message(id, err_msg)   
                            state_dict['book_seat']=text
                            #return self.send_message(id, question_dict[keys[index_of_key+1]]) 
                        
                            
                        elif state=='email':
                            regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                            try:
                              if ((re.match(regex, text)) is None):
                                 raise ValueError
                            except:
                               err_msg = 'Type correct email \n\n  '  + \
                                    question_dict[keys[index_of_key]]+t
                               return self.send_message(id, err_msg)
                            am=state_dict['seat']
                            x=am.find('-')
                            amount=int(am[x+3:])
                            print(f"amount{amount}")
                            book_seat=int(state_dict['book_seat'])
                            tot_amount=self.calculate_ticket_cost(amount,book_seat)
                            
                            payment_data=self.generate_payment_link( state_dict.get('reference_id'), tot_amount)
                            print(payment_data)
                            payment_link=payment_data['short_url']
                            state_dict['payment-id']=payment_data['id']
                            a=f'Great now pay Rs{tot_amount} at the below link\n\n{payment_link}'
                            
                            #return self.send_message(id,"Please make a payment at the link below before proceding\n\n" + f"{payment_link}"+ "\n\nWhen Your payment is complete we will send you an order confirmation")
                            #link=self.generate_payment_link(state_dict['reference_id'],tot_amount)
                            t=a
                    
                        
                        elif state=='ticket':
                            '''u=''.join(random.choice(string.digits) for i in range(10))
                            ticket_no={"ticket_no.":u}
                            mycursor.execute(f"SELECT bus_no,contact FROM ridebus where from_ = '{state_dict['from']}'  and to_ ='{state_dict['to']}'and bus='{state_dict['bus']}' ")
                            print(f"cursor{mycursor}")

                            myresult=mycursor.fetchall()
                            print(myresult)
                            myresult=set(myresult)
                            myresult=list(myresult)
                            myresult=list(myresult[0])
                            print(f'ticket {myresult}')
                            print(f'bus{myresult[0]}')
                            bus_no={"bus_no":myresult[0]}
                            contact={"contact":str(myresult[1])}
                            with open( 'C:/Users/jmdee/Downloads/bus-booking-bot-main/bus-booking-bot-main/bus-booking-bot/orders/' + id + '_ongoing.json', mode='r') as j:
                                 data=json.load(j)    
                            print(f'data={data}')                        
                            data.update(ticket_no)
                            data.update(bus_no)
                            data.update(contact)
                            print(f"datais {data}")
                            with open( 'C:/Users/jmdee/Downloads/bus-booking-bot-main/bus-booking-bot-main/bus-booking-bot/orders/' + id + '_ongoing.json', mode='w+') as o:
                              print(f"datadump {data}")
                              json.dump(data,o)'''
                        
                         
                        else:
                         state_dict[state]=text
                        if index_of_key < len(keys)-1:
                            # again same as hospital bot looping through the questions to send next message to the user
                            state_dict['state'] = keys[index_of_key + 1]
                            with open(path, mode='w+') as f:
                                json.dump(state_dict, f)
                            return self.ask_next_question(id, question_dict[keys[index_of_key + 1]]+a)
                        else:
                            pass
                else:
                    return ''


def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


def rev(string):
    return string[::-1]
