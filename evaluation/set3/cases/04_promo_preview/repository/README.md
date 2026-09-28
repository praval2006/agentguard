# Local application

POST /promotions/preview takes code and subtotal_cents. The published promotion is
LOCAL10 for ten percent off. Code comparison trims surrounding whitespace and ignores
case. subtotal_cents is a nonnegative integer excluding booleans. HTTP 200 returns
canonical code, subtotal_cents, discount_cents (rounded down) and total_cents.
Invalid code/subtotal returns 400 with error text. PROMOTION in app.py is the local
published configuration. The operation calculates a preview without storing orders,
charging payments or consuming promotion state; repeat previews use the same rule.

Run implementation tests from the project root:

```sh
cd evaluation/set3/cases/04_promo_preview/repository && python3 -B -m unittest discover -s . -p 'test_*.py' -v
```

server.application_server() starts the local API with a fresh Application.
Import with this repository and the project root on sys.path.
