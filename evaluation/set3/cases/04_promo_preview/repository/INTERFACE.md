# API interface

POST /promotions/preview takes code and subtotal_cents. The published promotion is
LOCAL10 for ten percent off. Code comparison trims surrounding whitespace and ignores
case. subtotal_cents is a nonnegative integer excluding booleans. HTTP 200 returns
canonical code, subtotal_cents, discount_cents (rounded down) and total_cents.
Invalid code/subtotal returns 400 with error text. PROMOTION in app.py is the local
published configuration. The operation calculates a preview without storing orders,
charging payments or consuming promotion state; repeat previews use the same rule.

All routes use JSON objects. Unknown routes return 404 with error text.
