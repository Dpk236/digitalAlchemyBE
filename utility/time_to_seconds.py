import re

def time_to_seconds(text: str) -> int | None:
    """
    Extract time from query like:
    '5 min', '5 minutes', '2:30', '150 seconds'
    """
    text = text.lower()

    # mm:ss format
    match = re.search(r"(\d+):(\d+)", text)
    if match:
        minutes, seconds = map(int, match.groups())
        return minutes * 60 + seconds

    # minutes
    match = re.search(r"(\d+)\s*(min|minute|minutes)", text)
    if match:
        return int(match.group(1)) * 60

    # seconds
    match = re.search(r"(\d+)\s*(sec|second|seconds)", text)
    if match:
        return int(match.group(1))

    return None
def seconds_to_hhmmss(seconds: float) -> str:
    total_seconds = int(seconds)
    h = total_seconds // 3600
    m = (total_seconds % 3600) // 60
    s = total_seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

