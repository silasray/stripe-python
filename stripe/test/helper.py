import datetime
import os
import random
import re
import string
import sys
import unittest2

from mock import patch, Mock

import stripe

NOW = datetime.datetime.now()

DUMMY_CARD = {
    'number': '4242424242424242',
    'exp_month': NOW.month,
    'exp_year': NOW.year + 4
}
DUMMY_DEBIT_CARD = {
    'number': '4000056655665556',
    'exp_month': NOW.month,
    'exp_year': NOW.year + 4
}
DUMMY_CHARGE = {
    'amount': 100,
    'currency': 'usd',
    'card': DUMMY_CARD
}

DUMMY_DISPUTE = {
    'status': 'needs_response',
    'currency': 'usd',
    'metadata': {}
}

DUMMY_PLAN = {
    'amount': 2000,
    'interval': 'month',
    'name': 'Amazing Gold Plan',
    'currency': 'usd',
    'id': ('stripe-test-gold-' +
           ''.join(random.choice(string.ascii_lowercase) for x in range(10)))
}

DUMMY_COUPON = {
    'percent_off': 25,
    'duration': 'repeating',
    'duration_in_months': 5,
    'metadata': {}
}

DUMMY_RECIPIENT = {
    'name': 'John Doe',
    'type': 'individual'
}

DUMMY_TRANSFER = {
    'amount': 400,
    'currency': 'usd',
    'recipient': 'self'
}

DUMMY_INVOICE_ITEM = {
    'amount': 456,
    'currency': 'usd',
}

SAMPLE_INVOICE = stripe.util.json.loads("""
{
  "amount_due": 1305,
  "attempt_count": 0,
  "attempted": true,
  "charge": "ch_wajkQ5aDTzFs5v",
  "closed": true,
  "customer": "cus_osllUe2f1BzrRT",
  "date": 1338238728,
  "discount": null,
  "ending_balance": 0,
  "id": "in_t9mHb2hpK7mml1",
  "livemode": false,
  "next_payment_attempt": null,
  "object": "invoice",
  "paid": true,
  "period_end": 1338238728,
  "period_start": 1338238716,
  "starting_balance": -8695,
  "subtotal": 10000,
  "total": 10000,
  "lines": {
    "invoiceitems": [],
    "prorations": [],
    "subscriptions": [
      {
        "plan": {
          "interval": "month",
          "object": "plan",
          "identifier": "expensive",
          "currency": "usd",
          "livemode": false,
          "amount": 10000,
          "name": "Expensive Plan",
          "trial_period_days": null,
          "id": "expensive"
        },
        "period": {
          "end": 1340917128,
          "start": 1338238728
        },
        "amount": 10000
      }
    ]
  }
}
""")

SAMPLE_EVENT_PAYLOAD = """{
  "api_version": "2016-03-07",
  "created": 1460636017,
  "data": {
    "object": {
      "amount": 200,
      "amount_refunded": 0,
      "application_fee": null,
      "balance_transaction": "txn_000000000000000000000000",
      "captured": true,
      "created": 1460636017,
      "currency": "usd",
      "customer": null,
      "description": null,
      "destination": null,
      "dispute": null,
      "failure_code": null,
      "failure_message": null,
      "fraud_details": {},
      "id": "ch_000000000000000000000000",
      "invoice": null,
      "livemode": false,
      "metadata": {},
      "object": "charge",
      "order": null,
      "paid": true,
      "receipt_email": null,
      "receipt_number": null,
      "refunded": false,
      "refunds": {
        "data": [],
        "has_more": false,
        "object": "list",
        "total_count": 0,
        "url": "/v1/charges/ch_000000000000000000000000/refunds"
      },
      "shipping": null,
      "source": {
        "address_city": null,
        "address_country": null,
        "address_line1": null,
        "address_line1_check": null,
        "address_line2": null,
        "address_state": null,
        "address_zip": null,
        "address_zip_check": null,
        "brand": "Visa",
        "country": "US",
        "customer": null,
        "cvc_check": "pass",
        "dynamic_last4": null,
        "exp_month": 4,
        "exp_year": 2017,
        "fingerprint": "NrVafqTONZfbLkQK",
        "funding": "credit",
        "id": "card_000000000000000000000000",
        "last4": "4242",
        "metadata": {},
        "name": null,
        "object": "card",
        "tokenization_method": null
      },
      "source_transfer": null,
      "statement_descriptor": null,
      "status": "succeeded"
    }
  },
  "id": "evt_000000000000000000000000",
  "livemode": false,
  "object": "event",
  "pending_webhooks": 0,
  "request": "req_00000000000000",
  "type": "charge.succeeded"
}"""

SAMPLE_EVENT_DEAUTH_PAYLOAD = """{
  "api_version": null,
  "created": 1448270796,
  "data": {
    "object": {
      "id": "ca_00000000000000000000000000000000",
      "name": "Sample Connect Application",
      "object": "application"
    }
  },
  "id": "evt_000000000000000000000000",
  "livemode": true,
  "object": "event",
  "pending_webhooks": 0,
  "request": null,
  "stripe_user_id": "acct_0000000000000000",
  "type": "account.application.deauthorized"
}"""


class StripeTestCase(unittest2.TestCase):
    RESTORE_ATTRIBUTES = ('api_version', 'api_key')

    def setUp(self):
        super(StripeTestCase, self).setUp()

        self._stripe_original_attributes = {}

        for attr in self.RESTORE_ATTRIBUTES:
            self._stripe_original_attributes[attr] = getattr(stripe, attr)

        api_base = os.environ.get('STRIPE_API_BASE')
        if api_base:
            stripe.api_base = api_base
        stripe.api_key = os.environ.get(
            'STRIPE_API_KEY', 'tGN0bIwXnHdwOa85VABjPdSn8nWY7G7I')

    def tearDown(self):
        super(StripeTestCase, self).tearDown()

        for attr in self.RESTORE_ATTRIBUTES:
            setattr(stripe, attr, self._stripe_original_attributes[attr])

    # Python < 2.7 compatibility
    def assertRaisesRegexp(self, exception, regexp, callable, *args, **kwargs):
        try:
            callable(*args, **kwargs)
        except exception as err:
            if regexp is None:
                return True

            if isinstance(regexp, basestring):
                regexp = re.compile(regexp)
            if not regexp.search(str(err)):
                raise self.failureException('"%s" does not match "%s"' %
                                            (regexp.pattern, str(err)))
        else:
            raise self.failureException(
                '%s was not raised' % (exception.__name__,))


class StripeUnitTestCase(StripeTestCase):
    REQUEST_LIBRARIES = ['urlfetch', 'requests', 'pycurl']

    if sys.version_info >= (3, 0):
        REQUEST_LIBRARIES.append('urllib.request')
    else:
        REQUEST_LIBRARIES.append('urllib2')

    def setUp(self):
        super(StripeUnitTestCase, self).setUp()

        self.request_patchers = {}
        self.request_mocks = {}
        for lib in self.REQUEST_LIBRARIES:
            patcher = patch("stripe.http_client.%s" % (lib,))

            self.request_mocks[lib] = patcher.start()
            self.request_patchers[lib] = patcher

    def tearDown(self):
        super(StripeUnitTestCase, self).tearDown()

        for patcher in self.request_patchers.itervalues():
            patcher.stop()


class StripeApiTestCase(StripeTestCase):

    def setUp(self):
        super(StripeApiTestCase, self).setUp()

        self.requestor_patcher = patch('stripe.api_requestor.APIRequestor')
        requestor_class_mock = self.requestor_patcher.start()
        self.requestor_mock = requestor_class_mock.return_value

    def tearDown(self):
        super(StripeApiTestCase, self).tearDown()

        self.requestor_patcher.stop()

    def mock_response(self, res):
        self.requestor_mock.request = Mock(return_value=(res, 'reskey'))


class StripeResourceTest(StripeApiTestCase):

    def setUp(self):
        super(StripeResourceTest, self).setUp()
        self.mock_response({})


class MyResource(stripe.resource.APIResource):
    pass


class MySingleton(stripe.resource.SingletonAPIResource):
    pass


class MyListable(stripe.resource.ListableAPIResource):
    pass


class MyCreatable(stripe.resource.CreateableAPIResource):
    pass


class MyUpdateable(stripe.resource.UpdateableAPIResource):
    pass


class MyDeletable(stripe.resource.DeletableAPIResource):
    pass


class MyComposite(stripe.resource.ListableAPIResource,
                  stripe.resource.CreateableAPIResource,
                  stripe.resource.UpdateableAPIResource,
                  stripe.resource.DeletableAPIResource):
    pass
