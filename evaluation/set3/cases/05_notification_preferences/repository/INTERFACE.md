# API interface

PATCH /preferences accepts optional email_enabled and push_enabled, each strictly
boolean; at least one is required. Other fields and other types are rejected with
400 and error text. The complete update is validated before storing changes.
HTTP 200 returns email_enabled, push_enabled and daily_digest_hour. Omitted channel
values and daily_digest_hour retain their stored values. GET /preferences returns
the stored object with 200. The caller owns the current-user preference dictionary;
the application does not resolve users from request input. Default state for a new
server is email_enabled true, push_enabled false, daily_digest_hour 9. Updates persist
for that server instance. No notification delivery is performed by this API.

All routes use JSON objects. Unknown routes return 404 with error text.
