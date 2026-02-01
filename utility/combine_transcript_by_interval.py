from typing import List, Dict
import math

def combine_transcript_by_interval(
    segments: List[Dict],
    interval_seconds: int = 180
) -> List[Dict]:
    """
    Combines transcript segments into fixed time intervals (default: 3 minutes).

    Args:
        segments (List[Dict]): List of transcript objects with start, end, text.
        interval_seconds (int): Interval duration in seconds (default 180).

    Returns:
        List[Dict]: Combined transcript per interval.
    """

    combined = {}

    for seg in segments:
        # Determine which interval this segment belongs to
        interval_index = math.floor(seg["start"] / interval_seconds)
        interval_start = interval_index * interval_seconds
        interval_end = interval_start + interval_seconds

        if interval_index not in combined:
            combined[interval_index] = {
                "start": interval_start,
                "end": interval_end,
                "text": []
            }

        combined[interval_index]["text"].append(seg["text"])

        # Extend end time if needed
        combined[interval_index]["end"] = max(
            combined[interval_index]["end"],
            seg["end"]
        )

    # Convert to list and join text
    result = []
    for interval in sorted(combined.keys()):
        result.append({
            "start": round(combined[interval]["start"], 2),
            "end": round(combined[interval]["end"], 2),
            "text": " ".join(combined[interval]["text"]).strip()
        })

    return result
