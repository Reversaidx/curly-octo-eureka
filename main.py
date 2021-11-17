# -*- coding: utf-8 -*-
from flask import Flask, request, Response
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages.text_message import TextMessage
from viberbot.api.viber_requests import ViberConversationStartedRequest
from viberbot.api.viber_requests import ViberFailedRequest
from viberbot.api.viber_requests import ViberMessageRequest
from viberbot.api.viber_requests import ViberSubscribedRequest
from viberbot.api.viber_requests import ViberUnsubscribedRequest

import time
import logging
import sched
import threading
import mysql.connector

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

app = Flask(__name__)
viber = Api(BotConfiguration(
    name = "ДР Хлебсоль" ,
    avatar='https://cs12.pikabu.ru/post_img/big/2021/11/16/5/1637044848151875496.jpg',
    auth_token='4e45394a1227dded-f7463d21e7b569c3-226bab802efd7b4a'
))

@app.route('/', methods=['POST'])
def incoming():
    logger.debug("received request. post data: {0}".format(request.get_data()))

    viber_request = viber.parse_request(request.get_data().decode('utf8'))

    if isinstance(viber_request, ViberMessageRequest):
        message = viber_request.message
        name=mysqlquery(message,connection)
        if name!=-1:
            viber.send_messages(viber_request.sender.id, [
                f'Вы выйграли {name}'
            ])
        else:
            viber.send_messages(viber_request.sender.id, [
                f'Идите нахуй'
            ])
    elif isinstance(viber_request, ViberConversationStartedRequest) \
            or isinstance(viber_request, ViberSubscribedRequest) \
            or isinstance(viber_request, ViberUnsubscribedRequest):
        viber.send_messages(viber_request.sender.id, [
            TextMessage(None, None, viber_request.get_event_type())
        ])
    elif isinstance(viber_request, ViberFailedRequest):
        logger.warn("client failed receiving message. failure: {0}".format(viber_request))

    return Response(status=200)

def set_webhook(viber):
        #viber.unset_webhook()
        viber.set_webhook('https://omnomnommnom.com/')


def mysqlquery(id,connect):
    query=f'select * from promo where id={id} and status is not null;'
    cursor = connect.cursor()
    cursor.execute(query)
    if len(cursor)==0:
        result=-1
    else:
        result=cursor[0]

    query2=f'update promo set status=true where id={id} and status is not null'
    cursor.execute(query2)

    cursor.close()
    return result

if __name__ == "__main__":
    scheduler = sched.scheduler(time.time, time.sleep)
    global connection
    connection = mysql.connector.connect(host='localhost',
                                         database='electronics',
                                         user='pynative',
                                         password='pynative@#29'
                                         )
    scheduler.enter(5, 11, set_webhook, (viber,))
    t = threading.Thread(target=scheduler.run)
    t.start()

    app.run(host='0.0.0.0', port=81, debug=True)