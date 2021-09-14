def update_json(json, **kwargs):
    for key, value in kwargs.items():
        json[key] = value

    return json
