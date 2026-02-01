import json

from store import redis_connection
redis_client = redis_connection.return_redis_client()

SUMMARY_TTL_SECONDS = 24 * 60 * 60  # 24 hours (optional)


def cache_video_summaries(video_id: str, summaries: list[dict]):
    key = f"video_summary:{video_id}"

    redis_client.set(
        key,
        json.dumps(summaries)
    )

    # Optional TTL
    redis_client.expire(key, SUMMARY_TTL_SECONDS)

    print(f"Cached {len(summaries)} summaries for video {video_id}")


def get_cached_video_summaries(video_id: str) -> list[dict] | None:
    key = f"video_summary:{video_id}"

    data = redis_client.get(key)
    if not data:
        return None

    return json.loads(data)

def get_cached_video_notes(video_id: str) -> list[dict] | None:
    key = f"video_notes:{video_id}"

    data = redis_client.get(key)
    if not data:
        return None

    return json.loads(data)
def cache_video_notes(video_id: str, notes: list[dict]):
    key = f"video_notes:{video_id}"

    redis_client.set(
        key,
        json.dumps(notes)
    )

    # Optional TTL
    redis_client.expire(key, SUMMARY_TTL_SECONDS)

    print(f"Cached {len(notes)} notes for video {video_id}")

