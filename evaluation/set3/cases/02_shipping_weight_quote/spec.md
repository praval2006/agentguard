# Shipping weight quote

Add a domestic parcel shipping quote API using whole grams. Accept parcel weights
from 100 grams through 30,000 grams, including both limits. Reject non-integer
values, including booleans, and weights outside this range with a clear validation
error. Do not silently round or clamp weights.

The service charges 500 cents plus 100 cents per started kilogram of parcel weight.
Return a quote containing the submitted weight in grams, the total charge in integer
cents, and currency AUD. A quote is informational and must not create a shipment
or payment. Document the route and request/response shapes as ordinary API details.
