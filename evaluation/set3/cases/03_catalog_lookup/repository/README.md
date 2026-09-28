# Local application

POST /catalog/search takes term as nonblank text, trims it, and matches product-name
substrings case-insensitively. HTTP 200 returns items, an array of objects with code,
name, unit_price_cents and available; objects are ordered by code. No matches returns
items as an empty array. Invalid term input returns 400 with error text. The local
stationery catalog is defined in app.py; search does not update it. Each application
owns a copy of its catalog. No remote service is used.

Run implementation tests from the project root:

```sh
cd evaluation/set3/cases/03_catalog_lookup/repository && python3 -B -m unittest discover -s . -p 'test_*.py' -v
```

server.application_server() starts the local API with a fresh Application.
Import with this repository and the project root on sys.path.
