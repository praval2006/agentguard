# Catalog lookup

Add a catalog search API for product names. Accept a text search term, trim its
surrounding whitespace, and find products whose names contain that term without
regard to letter case. Reject an empty or whitespace-only term and non-string input.
Return all matches in a collection ordered by product code. If there are no matches,
return an empty collection rather than an error.

Each match must preserve its product code, display name, unit price in integer cents,
and availability flag from the catalog. Searching must not modify the catalog.
The repository should contain a small stable local catalog with ordinary product
records representing the shop's inventory, and document its search interface.
No remote catalog or purchasing service is required.
