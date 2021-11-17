package main

import (
	_"fmt"
	"log"
	"net/http"
	"time"

	"github.com/mileusna/viber"
)

func main() {
	v := &viber.Viber{
		AppKey: "4e4b961433e7dd2a-1a75da9575db2e68-6f2fa13f46af23f2",
		Sender: viber.Sender{
			Name:   "Нахуй иди",
			Avatar: "https://cs12.pikabu.ru/post_img/big/2021/11/16/5/1637044848151875496.jpg",
		},
		Message:   myMsgReceivedFunc,  // your function for handling messages
		Delivered: myDeliveredFunc,    // your function for delivery report
	}
	v.Seen = mySeenFunc   // or assign events after declaration
	v.SetWebhook("https://drxs.ru:81", nil)
	// this have to be your webhook, pass it your viber app as http handler
	http.Handle("/viber/webhook/", v)
	http.ListenAndServe(":81", nil)
}

// myMsgReceivedFunc will be called everytime when user send us a message
func myMsgReceivedFunc(v *viber.Viber, u viber.User, m viber.Message, token uint64, t time.Time) {
	switch m.(type) {

	case *viber.TextMessage:
		v.SendTextMessage(u.ID, "Thank you for your message")
		txt := m.(*viber.TextMessage).Text
		v.SendTextMessage(u.ID, "This is the text you have sent to me "+txt)

	case *viber.URLMessage:
		url := m.(*viber.URLMessage).Media
		v.SendTextMessage(u.ID, "You have sent me an interesting link "+url)

	case *viber.PictureMessage:
		v.SendTextMessage(u.ID, "Nice pic!")

	}
}

func myDeliveredFunc(v *viber.Viber, userID string, token uint64, t time.Time) {
	log.Println("Message ID", token, "delivered to user ID", userID)
}

func mySeenFunc(v *viber.Viber, userID string, token uint64, t time.Time) {
	log.Println("Message ID", token, "seen by user ID", userID)
}