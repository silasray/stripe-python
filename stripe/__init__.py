# Stripe Python bindings
# API docs at http://stripe.com/docs/api
# Authors:
# Patrick Collison <patrick@stripe.com>
# Greg Brockman <gdb@stripe.com>
# Andrew Metcalf <andrew@stripe.com>

# Configuration variables

api_key = None
client_id = None
api_base = 'https://api.stripe.com'
connect_api_base = 'https://connect.stripe.com'
upload_api_base = 'https://uploads.stripe.com'
api_version = None
verify_ssl_certs = True
proxy = None
default_http_client = None

# Set to either 'debug' or 'info', controls console logging
log = None

# Resource
from stripe.resource import (  # noqa
    Account,
    AlipayAccount,
    ApplePayDomain,
    ApplicationFee,
    Balance,
    BalanceTransaction,
    BankAccount,
    BitcoinReceiver,
    BitcoinTransaction,
    Card,
    Charge,
    CountrySpec,
    Coupon,
    Customer,
    Dispute,
    Event,
    FileUpload,
    Invoice,
    InvoiceItem,
    Order,
    OrderReturn,
    Payout,
    Plan,
    Product,
    Recipient,
    RecipientTransfer,
    Refund,
    SKU,
    Source,
    Subscription,
    SubscriptionItem,
    ThreeDSecure,
    Token,
    Transfer)

# OAuth
from stripe.oauth import OAuth  # noqa

# Error imports.  Note that we may want to move these out of the root
# namespace in the future and you should prefer to access them via
# the fully qualified `stripe.error` module.

from stripe.error import (  # noqa
    APIConnectionError,
    APIError,
    AuthenticationError,
    PermissionError,
    RateLimitError,
    CardError,
    InvalidRequestError,
    OAuthError,
    StripeError)

# DEPRECATED: These imports will be moved out of the root stripe namespace
# in version 2.0

from stripe.version import VERSION  # noqa
from stripe.api_requestor import APIRequestor  # noqa
from stripe.resource import (  # noqa
    APIResource,
    CreateableAPIResource,
    DeletableAPIResource,
    ListObject,
    ListableAPIResource,
    SingletonAPIResource,
    StripeObject,
    StripeObjectEncoder,
    UpdateableAPIResource,
    convert_to_stripe_object)
from stripe.util import json, logger  # noqa
