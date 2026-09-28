# API interface

POST /shipping/quote takes weight_grams, an integer from 100 through 30000 inclusive.
Booleans and all other types are rejected. Invalid values return 400 with error text.
HTTP 200 returns weight_grams, total_cents (integer), and currency AUD. The tariff is
500 cents plus 100 cents per started kilogram. Quotes do not persist state or invoke
shipment/payment services; there are no shipment or payment routes in this application.

All routes use JSON objects. Unknown routes return 404 with error text.
