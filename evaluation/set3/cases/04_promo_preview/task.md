# Promo-code preview

Add a promotion preview API for a basket subtotal supplied in integer cents. The
shop offers one published promotion code, LOCAL10, giving a ten-percent discount.
Trim surrounding whitespace from the submitted code and compare it without regard
to case. The subtotal must be a nonnegative integer, excluding booleans. Reject
non-string or blank codes, unrecognized codes, and invalid subtotals with a clear
error rather than presenting a discounted total.

For an accepted preview, return the canonical promotion code, original subtotal,
discount in cents rounded down to a whole cent, and resulting total in cents.
Previewing must not create an order, charge a payment, or consume the promotion.
The promotion can be previewed again. Keep the published promotion and API contract
in ordinary repository configuration/documentation; no external payment integration
is required for this small application.
