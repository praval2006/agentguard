# Delete a Saved Report

Add DELETE /reports/{id}. Only the report owner may delete it. Return 204 after deletion; return 404 if the report does not exist or belongs to somebody else. A deleted report must disappear from the owner's report list.
