import hmac
import time
from hashlib import sha256

import stripe
from stripe import error, util


class Webhook(object):
    @staticmethod
    def create_event_from_payload(payload, sig_header=None, secret=None,
                                  tolerance=30.0):
        data = util.json.loads(payload)
        event = stripe.Event.construct_from(data, stripe.api_key)

        if sig_header:
            if not secret:
                raise ValueError(
                    "You must pass a secret in order to verify signatures")

            WebhookSignature.verify_header(payload, sig_header, secret,
                                           tolerance)

        return event


class WebhookSignature(object):
    EXPECTED_SCHEME = 'v1'

    @staticmethod
    def compute_signature(payload, secret):
        mac = hmac.new(util.utf8(secret), msg=util.utf8(payload),
                       digestmod=sha256)
        return mac.hexdigest()

    @staticmethod
    def get_timestamp_and_signatures(header, scheme):
        list_items = map(lambda i: i.split('=', 2), header.split(','))
        timestamp = int([i[1] for i in list_items if i[0] == 't'][0])
        signatures = [i[1] for i in list_items if i[0] == scheme]
        return timestamp, signatures

    @classmethod
    def verify_header(cls, payload, header, secret, tolerance=None):
        try:
            timestamp, signatures = cls.get_timestamp_and_signatures(
                header, cls.EXPECTED_SCHEME)
        except:
            raise error.SignatureVerificationError(
                "Unable to extract timestamp and signatures from header",
                header, payload)

        if len(signatures) == 0:
            raise error.SignatureVerificationError(
                "No signatures found with expected scheme {scheme}".format(
                    scheme=cls.EXPECTED_SCHEME),
                header, payload)

        signed_payload = "{timestamp}.{payload}".format(timestamp=timestamp,
                                                        payload=payload)
        expected_sig = cls.compute_signature(signed_payload, secret)
        if not any(util.secure_compare(expected_sig, s) for s in signatures):
            raise error.SignatureVerificationError(
                "No signatures found matching the expected signature for "
                "payload",
                header, payload)

        if tolerance and timestamp < time.time() - tolerance:
            raise error.SignatureVerificationError(
                "Timestamp outside the tolerance zone ({time})".format(
                    time=0),
                header, payload)

        return True
