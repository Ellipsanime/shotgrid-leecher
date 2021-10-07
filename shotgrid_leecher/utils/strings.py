def format_path(path: str) -> str:
    return f",{','.join([x for x in path.split('/') if x])},"
