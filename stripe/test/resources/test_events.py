import stripe
from stripe.test.helper import (
    StripeResourceTest, SAMPLE_EVENT_PAYLOAD, SAMPLE_EVENT_DEAUTH_PAYLOAD
)


class EventTest(StripeResourceTest):

    def test_event_verify(self):
        stripe.Event.verify(SAMPLE_EVENT_PAYLOAD)

        self.requestor_mock.request.assert_called_with(
            'get',
            '/v1/events/evt_000000000000000000000000',
            {},
            None
        )

    def test_event_verify_connected_account(self):
        # Add a stripe_user_id key to the payload
        event_dict = stripe.util.json.loads(SAMPLE_EVENT_PAYLOAD)
        event_dict['stripe_user_id'] = 'acct_0000000000000000'
        event_payload = stripe.util.json.dumps(event_dict)

        event = stripe.Event.verify(event_payload)

        self.requestor_mock.request.assert_called_with(
            'get',
            '/v1/events/evt_000000000000000000000000',
            {},
            None
        )
        self.assertEqual('acct_0000000000000000', event.stripe_account)

    def test_event_verify_deauth(self):
        self.assertRaises(stripe.error.EventVerificationError,
                          stripe.Event.verify, SAMPLE_EVENT_DEAUTH_PAYLOAD)

        self.requestor_mock.request.assert_called_with(
            'get',
            '/v1/accounts/acct_0000000000000000',
            {},
            None
        )
