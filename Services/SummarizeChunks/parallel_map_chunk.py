
from store.openai_client import get_openai_client
from LLMQueries.get_summary_of_chunk import get_summary
from typing import List, Dict, Any
import os
client = get_openai_client()
model = os.getenv("model", "gpt-4o")

# -------------------------------------------------------------
#   CONFIG - You can tune these
# -------------------------------------------------------------
CHUNKS_PER_GROUP_LEVEL1 = 5       # Merge 5 chunk summaries → 1 section
CHUNKS_PER_GROUP_LEVEL2 = 4       # Merge 4 sections → 1 bigger unit/chapter
# Use stronger model only for the very last summary
USE_STRONG_LLM_FOR_FINAL = True

# -------------------------------------------------------------
#   Helper: Call your LLM (replace with your actual client)
# -------------------------------------------------------------


def call_llm(prompt: str) -> str:
    """
    Replace this with your actual LLM call.
    Returns only the cleaned text response.
    """
    # Example placeholder - implement your real call here
    messages = [
    {
        "role": "system",
        "content": "You must strictly follow formatting rules. Output only Markdown."
    },
    {
        "role": "user",
        "content": prompt
    }
]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
    )
    return response.choices[0].message.content.strip()


# -------------------------------------------------------------
#   Merge prompt templates (very important!)
# -------------------------------------------------------------
MERGE_PROMPT_TEMPLATE = """
You are an expert NCERT tutor creating structured academic notes.

TASK:
Combine the following summaries into ONE coherent, well-organized summary.

TIMESTAMP RULES (MANDATORY):
- Preserve ALL timestamps provided in the input summaries
- Timestamps must appear in square brackets: [MM:SS]
- Place timestamps ONLY at the end of a sentence or bullet point
- Do NOT invent new timestamps
- Do NOT modify existing timestamps
- If multiple timestamps apply to one point, keep the earliest one

STRICT FORMAT RULES:
- Output MUST be in MARKDOWN format only
- Use ## for ONE section heading
- Use bullet points (-) where helpful
- Use **bold** for key terms, definitions, formulas
- Use *italics* for examples or scientific names
- Do NOT use HTML tags
- Do NOT use markdown code blocks
- Do NOT add any information not present in input
- Remove redundancy while preserving meaning
- Maintain NCERT terminology

STYLE:
- Short paragraphs
- Teacher-like revision tone
- Exam-oriented phrasing

INPUT SUMMARIES (in order):
{chunk_summaries_text}

OUTPUT:
- Markdown only
"""

FINAL_GLOBAL_PROMPT = """
You are creating the FINAL complete summary of the entire lecture.

TASK:
Merge all section summaries into a single, exam-ready Markdown document.

TIMESTAMP RULES (STRICT):
- Use timestamps ONLY if present in section summaries
- Format must be exactly: [MM:SS]
- Place timestamps at the END of headings, bullet points, or sentences
- Never place timestamps mid-sentence
- Do NOT fabricate or interpolate timestamps
- If a section covers multiple timestamps, use the earliest relevant one

STRICT FORMAT RULES:
- Output ONLY Markdown
- No explanations, no extra text
- Use # for main title
- Use ## for major sections
- Use ### for subsections if required
- Use bullet lists (-)
- Use **bold** for key concepts, definitions, formulas
- Use *italics* for examples or scientific terms
- Do NOT use HTML
- Do NOT use markdown code blocks
- Do NOT add new information
- One idea per line
- Clean spacing between sections

DOCUMENT STRUCTURE (MANDATORY):
1. # Topic Overview  
   - 1–2 sentences describing lecture purpose

2. ## Key Concepts Covered  
   - Bullet points with brief explanations

3. ## Important Definitions & Concepts  
   - High-yield exam points only

4. ## Examples Mentioned  
   - Include ONLY if present in summaries

5. ## Most Important for Exams  
   - 3–5 bullet points (highest weightage)

SECTION SUMMARIES:
{section_summaries_text}

OUTPUT:
- Markdown only
"""



def hierarchical_merge(
    chunk_summaries: List[Dict[str, Any]],
    merge_prompt_template: str = MERGE_PROMPT_TEMPLATE,
    final_prompt: str = FINAL_GLOBAL_PROMPT,
    level1_group_size: int = CHUNKS_PER_GROUP_LEVEL1,
    level2_group_size: int = CHUNKS_PER_GROUP_LEVEL2
) -> Dict[str, Any]:
    """
    Performs hierarchical merge of chunk summaries.

    Input: list of dicts like:
        [{"range": "00:00-05:30", "summary": "...", "key_points": [...], ...}, ...]

    Returns dict with:
        - level1_summaries
        - level2_summaries
        - final_summary (if enough content)
    """
    if not chunk_summaries:
        return {"final_summary": "No content available"}

    # --------------------------------------------------
    # Level 1: Merge small groups of chunk summaries
    # --------------------------------------------------
    level1_summaries = []

    for i in range(0, len(chunk_summaries), level1_group_size):
        group = chunk_summaries[i:i + level1_group_size]

        # Prepare text for prompt
        summaries_text = ""
        for item in group:
            r = item["range"]
            s = item.get("summary", "").strip()
            summaries_text += f"[{r}]\n{s}\n\n"

        prompt = merge_prompt_template.format(
            chunk_summaries_text=summaries_text)

        merged = call_llm(prompt)  # cheap model here

        level1_summaries.append({
            "level": 1,
            "range_start": group[0]["range"].split("-")[0],
            "range_end": group[-1]["range"].split("-")[-1],
            "summary": merged,
            "source_chunks": len(group)
        })

    # --------------------------------------------------
    # Level 2: Merge sections into bigger units
    # --------------------------------------------------
    if len(level1_summaries) <= 3:
        # Too few → skip to final
        level2_summaries = level1_summaries
    else:
        level2_summaries = []
        for i in range(0, len(level1_summaries), level2_group_size):
            group = level1_summaries[i:i + level2_group_size]

            summaries_text = ""
            for item in group:
                summaries_text += f"{item['summary']}\n\n---\n\n"

            prompt = merge_prompt_template.format(
                chunk_summaries_text=summaries_text)
            merged = call_llm(prompt)

            level2_summaries.append({
                "level": 2,
                "summary": merged,
                "source_sections": len(group)
            })

    # --------------------------------------------------
    # Level 3: Final global summary (optional but recommended)
    # --------------------------------------------------
    final_summary = None

    if len(level2_summaries) >= 1:
        summaries_text = ""
        for item in level2_summaries:
            summaries_text += f"{item['summary']}\n\n============\n\n"

        model_for_final = "claude-3-5-sonnet" if USE_STRONG_LLM_FOR_FINAL else "gpt-4o-mini"

        prompt = final_prompt.format(section_summaries_text=summaries_text)
        final_summary = call_llm(prompt)

    # --------------------------------------------------
    # Return everything
    # --------------------------------------------------
    return {
        "level1_summaries": level1_summaries,
        "level2_summaries": level2_summaries,
        "final_summary": final_summary,
        "total_original_chunks": len(chunk_summaries)
    }


def summarize_video_chunks(chunks):
    """
    Summarizes all transcript chunks of a video.
    Expects LangChain Document objects.
    """
    print("Summarizing video chunks...", len(chunks))
    summarized_chunks = []

    for idx, chunk in enumerate(chunks):
        # Handle both dicts and LangChain Doc objects
        if hasattr(chunk, 'metadata'):
            start_time = chunk.metadata.get("start_time", 0)
            end_time = chunk.metadata.get("end_time", 0)
            content = chunk.page_content
        else:
            start_time = chunk.get("start", 0)
            end_time = chunk.get("end", 0)
            content = str(chunk)
            
        res = get_summary(content)
        summary = {"range": f"{start_time}-{end_time}", "summary": res}
        summarized_chunks.append(summary)

    return summarized_chunks


def ParallelMapChunk(
        video_id: str,
        chunks: list[str],
):
    res = summarize_video_chunks(chunks)
    # with open(f"{video_id}_chunk_summaries.json", "r") as f: // reading the chunk
    #     import json
    #     res = json.load(f)
    #     print("Summary of first chunk:", len(res))
    with open(f"{video_id}_chunk_summaries.json", "w") as f: # writing the chunk
        import json
        json.dump(res, f, indent=4)
        result = hierarchical_merge(res)
        with open(f"{video_id}_hierarchical_summary.json", "w") as f2:
            json.dump(result, f2, indent=4)
            print("level1_summaries:", len(result["level1_summaries"]))
            print("level2_summaries:",len(result["level2_summaries"]))
            print("final_summary:", len(result["final_summary"]))
            print("total_original_chunks:", result["total_original_chunks"])

            print("Final summary length:", len(result["final_summary"]) if result["final_summary"] else 0)    
        

    # chunk = chunks[0]
    # start_time = chunk["start"]
    # end_time = chunk["end"]
    # chunk_def = {"range": f"{start_time}-{end_time}", "summary": "Introduction to sets..."}
    # fake_chunk_summaries = [
    #     {"range": "00:00-05:00", "summary": "Introduction to sets..."},
    #     # ... imagine 25 more
    # ] * 25

    # result = hierarchical_merge(fake_chunk_summaries)
    # print("level1_summaries:", len(result["level1_summaries"]), result["level1_summaries"])
    # print("level2_summaries:",len(result["level2_summaries"]), result["level2_summaries"])
    # print("final_summary:", len(result["final_summary"]), result["final_summary"])
    # print("total_original_chunks:", result["total_original_chunks"])

    # print("Final summary length:", len(result["final_summary"]) if result["final_summary"] else 0)
    pass
