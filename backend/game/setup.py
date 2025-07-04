import json

def _json_encoder_default(self, obj):
    if hasattr(obj, '__json__'):
        return obj.__json__()
    return json.JSONEncoder().default(obj)


# Only patch the encoder if it hasn't been patched already
if not hasattr(json.JSONEncoder, '_is_patched'):
    json.JSONEncoder.default = _json_encoder_default
    json.JSONEncoder._is_patched = True  # Prevent multiple patches

