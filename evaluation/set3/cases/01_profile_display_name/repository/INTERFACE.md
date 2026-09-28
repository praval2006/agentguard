# API interface

PATCH /profile accepts {"display_name": string}. display_name is arbitrary nonblank
text, with no format, enum, identity or uniqueness requirement. Surrounding whitespace
is removed before storage. HTTP 200 returns the current profile object with the stored
display_name and other existing fields. Invalid input returns 400 with error text.
GET /profile returns that same stored representation with 200.
The caller owns the current profile dictionary; updates persist in that dictionary.
application_server() without arguments starts with display_name Guest and language en.
State belongs to that server instance; requests do not reset it. Other request fields
are ignored and do not alter unrelated profile fields.

All routes use JSON objects. Unknown routes return 404 with error text.
