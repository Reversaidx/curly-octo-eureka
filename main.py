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
		viber.send_messages(viber_request.sender.id, [
			message
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
        viber.unset_webhook()
        viber.set_webhook('https://drxs.ru/')

def mysqlquery(id):
	try:
		connection = mysql.connector.connect(host='localhost',
											 database='electronics',
											 user='pynative',
											 password='pynative@#29')

		sql_select_Query = "select * from Laptop"
		cursor = connection.cursor()
		cursor.execute(sql_select_Query)
		# get all records
		records = cursor.fetchall()
		print("Total number of rows in table: ", cursor.rowcount)

		print("\nPrinting each row")
		for row in records:
			print("Id = ", row[0], )
			print("Name = ", row[1])
			print("Price  = ", row[2])
			print("Purchase date  = ", row[3], "\n")

	except mysql.connector.Error as e:
		print("Error reading data from MySQL table", e)
	finally:
		if connection.is_connected():
			connection.close()
			cursor.close()
			print("MySQL connection is closed")

if __name__ == "__main__":
	scheduler = sched.scheduler(time.time, time.sleep)
	scheduler.enter(5, 11, set_webhook, (viber,))
	t = threading.Thread(target=scheduler.run)
    t.start()

    context = ('server.crt', 'server.key')
	app.run(host='0.0.0.0', port=81, debug=True)