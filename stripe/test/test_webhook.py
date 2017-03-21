import time

import stripe
from stripe.test.helper import StripeUnitTestCase, SAMPLE_WEBHOOK_PAYLOAD, SAMPLE_WEBHOOK_SECRET


class WebhookTests(StripeUnitTestCase):

    def test_create_event_from_payload(self):
        event = stripe.Webhook.create_event_from_payload(SAMPLE_WEBHOOK_PAYLOAD)
        self.assertTrue(isinstance(event, stripe.Event))
        self.assertEquals('evt_test_webhook', event.id)

    def test_raise_on_json_error(self):
        with self.assertRaises(ValueError):
            stripe.Webhook.create_event_from_payload("this is not valid JSON")

    def test_create_event_from_payload_and_header(self):
        header = WebhookSignatureTests.generate_header()
        event = stripe.Webhook.create_event_from_payload(SAMPLE_WEBHOOK_PAYLOAD, header, SAMPLE_WEBHOOK_SECRET)
        self.assertTrue(isinstance(event, stripe.Event))

    def test_raise_on_invalid_header(self):
        header = "bad_header"
        with self.assertRaises(stripe.error.SignatureVerificationError):
            stripe.Webhook.create_event_from_payload(SAMPLE_WEBHOOK_PAYLOAD, header, SAMPLE_WEBHOOK_SECRET)


class WebhookSignatureTests(StripeUnitTestCase):
    @staticmethod
    def generate_header(**kwargs):
        timestamp = kwargs.get('timestamp', int(time.time()))
        payload = kwargs.get('payload', SAMPLE_WEBHOOK_PAYLOAD)
        secret = kwargs.get('secret', SAMPLE_WEBHOOK_SECRET)
        scheme = kwargs.get('scheme', stripe.WebhookSignature.EXPECTED_SCHEME)
        signature = kwargs.get('signature', None)
        if signature is None:
            payload_to_sign = "{}.{}".format(timestamp, payload)
            signature = stripe.WebhookSignature.compute_signature(payload_to_sign, secret)
        header = "t={},{}={}".format(timestamp, scheme, signature)
        return header

    def test_raise_on_malformed_header(self):
        header = "i'm not even a real signature header"
        with self.assertRaises(stripe.error.SignatureVerificationError) as e:
            stripe.WebhookSignature.verify_header(SAMPLE_WEBHOOK_PAYLOAD, header, SAMPLE_WEBHOOK_SECRET)
            self.assertEqual("Unable to extract timestamp and signatures from header", e.message)

    def test_raise_on_no_signatures_with_expected_scheme(self):
        header = self.generate_header(scheme='v0')
        with self.assertRaises(stripe.error.SignatureVerificationError) as e:
            stripe.WebhookSignature.verify_header(SAMPLE_WEBHOOK_PAYLOAD, header, SAMPLE_WEBHOOK_SECRET)
            self.assertEqual("No signatures found with expected scheme v1", e.message)

    def test_raise_on_no_valid_signatures_for_payload(self):
        header = self.generate_header(signature='bad_signature')
        with self.assertRaises(stripe.error.SignatureVerificationError) as e:
            stripe.WebhookSignature.verify_header(SAMPLE_WEBHOOK_PAYLOAD, header, SAMPLE_WEBHOOK_SECRET)
            self.assertEqual("No signatures found matching the expected signature for payload", e.message)

    def test_raise_on_timestamp_outside_tolerance(self):
        header = self.generate_header(timestamp=int(time.time()) - 15)
        with self.assertRaises(stripe.error.SignatureVerificationError) as e:
            stripe.WebhookSignature.verify_header(SAMPLE_WEBHOOK_PAYLOAD, header, SAMPLE_WEBHOOK_SECRET, 10)
            self.assertEqual("Timestamp outside the tolerance zone", e.message)
