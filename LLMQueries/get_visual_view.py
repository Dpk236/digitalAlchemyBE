from store.openai_client import get_openai_client
from typing import Any
import os
model = os.getenv("model", "gpt-4o")
client = get_openai_client()
from pathlib import Path
OUTPUT_FILE = "480989616.html"

# ---------------- PROMPT ---------------- #

def build_canvas_prompt(video_summary: str) -> str:
    return f"""
You are an expert educational product designer and frontend developer.

This is the summary of the video lecture:
\"\"\"
{video_summary}
\"\"\"

TASK:
Help me digest the information.

Create a REAL-LIFE SIMULATOR WEB APP that:
1. Explains each concept visually and interactively
2. Uses real-life analogies
3. Has sliders, buttons, toggles, or small simulations
4. Gives instant visual feedback
5. Is suitable for students
6. Make 3d model images to explain the topic, it should looks 3d model
7. When the user clicks on the topic, there will be 3d images

STRICT RULES:
- Output ONLY a SINGLE HTML FILE
- Use ONLY HTML, CSS, and basic JavaScript
- No external libraries
- All CSS inside <style>
- All JS inside <script>
- Clean UI
- Beginner-friendly explanations
- Mobile responsive
- Add comments explaining logic
 CSS COLORS:
- Use soft, pastel colors
- Avoid bright, harsh colors
- Use colors to enhance understanding
- Use colors consistently for the same concepts
- Use accessible color contrasts
OUTPUT FORMAT:
Return ONLY valid HTML code.
NO markdown.
NO explanations outside the HTML.
"""

# ---------------- GEMINI CALL ---------------- #

def generate_simulator(video_summary: str) -> str:
    result_llm = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": build_canvas_prompt(video_summary)},
            {"role": "user", "content": "Generate the simulator HTML file."}
        ]
    )

    raw_data = result_llm.choices[0].message.content
    print("Raw LLM Data generated.")
    return raw_data


# ---------------- SAVE FILE ---------------- #

def save_html(content: str):
    Path(OUTPUT_FILE).write_text(content, encoding="utf-8")
    print(f"✅ Simulator generated: {OUTPUT_FILE}")


# ---------------- MAIN ---------------- #

def get_visual_view_query(summary: str) -> str:
    print("\n⏳ Generating interactive simulator...\n")
    html_output = generate_simulator(summary)

    save_html(html_output)
    return html_output
