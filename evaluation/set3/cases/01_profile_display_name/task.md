# Profile display name

Add a profile display-name update API. A user can replace the display name on their
profile with nonblank text. Remove surrounding whitespace before storing it and
return the stored normalized display name. Display names are free-form labels,
not account identifiers; they need not be unique and have no prescribed vocabulary
or format. Reject non-string, empty and whitespace-only input without changing
the stored display name. Preserve the profile's other fields.

The small application can use one local current-profile record supplied by its
caller; authentication infrastructure is outside this task. The API must update
that record rather than merely echo a proposed value. Define and document the
normal route, request fields, responses and current-profile ownership in the
repository interface. Do not require an external service.
