def full_name(name, workspace=None):
    suffix = ''
    if workspace:
        suffix = f"-{workspace}"
    return f"{name}{suffix}"
