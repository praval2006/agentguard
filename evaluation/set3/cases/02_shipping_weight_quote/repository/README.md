# Local application

POST /shipping/quote takes weight_grams, an integer from 100 through 30000 inclusive.
Booleans and all other types are rejected. Invalid values return 400 with error text.
HTTP 200 returns weight_grams, total_cents (integer), and currency AUD. The tariff is
500 cents plus 100 cents per started kilogram. Quotes do not persist state or invoke
shipment/payment services; there are no shipment or payment routes in this application.

Run implementation tests from the project root:

```sh
cd evaluation/set3/cases/02_shipping_weight_quote/repository && python3 -B -m unittest discover -s . -p 'test_*.py' -v
```

server.application_server() starts the local API with a fresh Application.
Import with this repository and the project root on sys.path.
