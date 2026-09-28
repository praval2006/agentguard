# Notification preferences

Add an API to update a user's notification preferences. Accept email_enabled and
push_enabled as optional boolean values, with at least one provided. Reject other
primitive types, null, unknown fields, and empty updates. Validate the complete
update before saving so an invalid value cannot leave a partial change.

Store the supplied choices, preserving any omitted channel's current value. Return
the resulting preferences, including the unchanged daily_digest_hour, an existing
integer setting that this operation must not edit. Explicit false is a choice and
must not be treated as an omitted value.

Use a caller-supplied local current-user preference record for this small application.
Document initial state, ownership, the update interface and its response shape.
No notification delivery service or authentication framework is part of this task.
