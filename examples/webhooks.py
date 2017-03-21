from __future__ import print_function

import os

import stripe
from flask import Flask, request

stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
webhook_secret = os.environ.get('WEBHOOK_SECRET')

app = Flask(__name__)


@app.route('/webhooks', methods=['POST'])
def webhooks():
    payload = request.data
    received_sig = request.headers.get('Stripe-Signature', None)

    # try:
    event = stripe.Event.from_payload(payload, received_sig, webhook_secret)

    print("Received event: id={id}, type={type}".format(id=event.id, type=event.type))
    #except Exception as e:
    #    print("Something happened :(")
    #    print(e.message)
    #    return '', 400

    return '', 200


if __name__ == '__main__':
    app.run(port=int(os.environ.get('PORT', 5000)))
