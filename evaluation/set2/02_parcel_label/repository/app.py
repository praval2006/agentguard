def dispatch(method, path, data):
    if (method, path) != ("POST", "/labels/preview"):
        return 404, {"error": "Unknown route"}
    recipient, postal = data.get("recipient"), data.get("postal_code")
    if not isinstance(recipient, str) or not isinstance(postal, str) or not recipient.strip() or not postal.strip():
        return 400, {"error": "Recipient and postal code required"}
    return 200, {"label": {"recipient": recipient.strip(), "postal_code": postal.strip().upper(), "service": "standard"}}
