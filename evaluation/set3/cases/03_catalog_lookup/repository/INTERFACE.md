# API interface

POST /catalog/search takes term as nonblank text, trims it, and matches product-name
substrings case-insensitively. HTTP 200 returns items, an array of objects with code,
name, unit_price_cents and available; objects are ordered by code. No matches returns
items as an empty array. Invalid term input returns 400 with error text. The local
stationery catalog is defined in app.py; search does not update it. Each application
owns a copy of its catalog. No remote service is used.

All routes use JSON objects. Unknown routes return 404 with error text.
