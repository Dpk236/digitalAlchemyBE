from store.openai_client import get_openai_client
import os
model = os.getenv("model", "gpt-4o")
def summarize_chunk(chunk: dict) -> dict:
    client = get_openai_client()

    system_prompt = """
    You are an NCERT-based teaching assistant.

    Rules:
    - Use ONLY the provided text
    - Do NOT add external knowledge
    - Do NOT hallucinate
    - Keep it simple and student-friendly
    - Use NCERT terminology
    - Do NOT mention anything not present in the text

    Return 1–2 short bullet points.
    """

    user_prompt = f"""
    Lecture Segment:
    Start Time: {chunk["start_time"]}
    End Time: {chunk["end_time"]}

    Text:
    {chunk["text"]}
    """

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    summary_text = response.choices[0].message.content.strip()

    return {
        "video_id": chunk["video_id"],
        "start_time": chunk["start_time"],
        "end_time": chunk["end_time"],
        "summary": summary_text
    }

def summarize_video_chunks(chunks):
    """
    Summarizes all transcript chunks of a video.
    Expects LangChain Document objects.
    """
    print("Summarizing video chunks...", len(chunks))
    summarized_chunks = []

    for idx, doc in enumerate(chunks):
        start_time = doc.metadata.get("start_time")
        end_time = doc.metadata.get("end_time")

        print(
            f"Summarizing chunk {idx + 1}/{len(chunks)} "
            f"({start_time}–{end_time})"
        )
        print("Chunk Text", doc, doc.page_content)
        summary = summarize_chunk({
            "video_id": doc.metadata.get("video_id"),
            "start_time": start_time,
            "end_time": end_time,
            "text": doc.page_content
        })

        summarized_chunks.append(summary)

    return summarized_chunks
