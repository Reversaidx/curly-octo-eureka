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
import json

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

app = Flask(__name__)
viber = Api(BotConfiguration(
    name="ДР Хлебсоль",
    avatar='https://cs12.pikabu.ru/post_img/big/2021/11/16/5/1637044848151875496.jpg',
    auth_token=''
))


@app.route('/', methods=['POST'])
def incoming():
    logger.debug("received request. post data: {0}".format(request.get_data()))
    tmp = request.get_data().decode('utf8')
    viber_request = viber.parse_request(tmp)
    data = json.loads(tmp)
    if isinstance(viber_request, ViberMessageRequest):
        print(data["message"]["text"])
        request_dict = json.loads(tmp)
        message = viber_request.from_dict(request_dict)
        id = data["message"]["text"]
        name = mysqlquery(id, connection)
        if name != -1:
            viber.send_messages(viber_request.sender.id, [
                TextMessage(text=  f'Вы выйграли {name}')

            ])
        else:
            viber.send_messages(viber_request.sender.id, [
               TextMessage(text=f'Идите нахуй')
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
    # viber.unset_webhook()
    viber.set_webhook('https://omnomnommnom.com/')


def mysqlquery(id, connect):
    query = f'select name from promo where id={id} and status is  null;'
    print(query.encode('ascii', 'ignore'))
    cursor = connect.cursor()
    cursor.execute(query)
    try:
        result = [  row for  row in cursor ]
    except:
        return -1

    if len(result)==0:
        return -1
    query2 = f'update promo set status=true where id={id}'
    cursor.execute(query2)


    cursor.close()
    connect.commit()
    return result[0]


if __name__ == "__main__":
    scheduler = sched.scheduler(time.time, time.sleep)
    global connection
    connection = mysql.connector.connect(host='localhost',
                                         database='promocode',
                                         user='root',
                                         password=''
                                         )
    scheduler.enter(5, 11, set_webhook, (viber,))
    t = threading.Thread(target=scheduler.run)
    t.start()

    app.run(host='0.0.0.0', port=81, debug=True)
