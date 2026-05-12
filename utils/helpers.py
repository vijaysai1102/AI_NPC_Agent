from datetime import datetime


def ts_to_display(ts_str: str) -> str:
    try:
        dt = datetime.fromisoformat(ts_str)
        return dt.strftime("%b %d, %H:%M")
    except Exception:
        return ts_str


def truncate(text: str, max_len: int = 80) -> str:
    return text if len(text) <= max_len else text[:max_len - 3] + "..."
