def update_event_property(
    events, propertyForEquality, valueForEquality, property, value
):
    if isinstance(events["data"], list):
        updated_event_cb = (
            lambda _event: _event
            if (_event[propertyForEquality] != valueForEquality)
            else {**_event, property: value}
        )
        updated_events_iterator = map(updated_event_cb, events["data"])
        events["data"] = list(updated_events_iterator)
