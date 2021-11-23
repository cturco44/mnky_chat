
def custom_time_sort(a, b):
    a = a["recent_message_timestamp"]
    b = b["recent_message_timestamp"]
    if not a and not b:
        return 0
    elif not a:
        return -1
    elif not b:
        return 1
    elif a > b:
        return 1
    elif a == b:
        return 0
    else:
        return -1