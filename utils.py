# Utility functions for managing global state.
# These wrap basic dictionary/list operations to make the main app.py file cleaner.

def save_offer(data_store, payload):
    data_store.clear()
    data_store.update(payload)

def get_offer(data_store):
    return data_store if data_store else None

def save_leads(data_store, leads):
    data_store.clear()
    data_store.extend(leads)

def get_leads(data_store):
    return data_store if data_store else None