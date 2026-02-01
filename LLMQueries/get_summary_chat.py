from store.openai_client import get_openai_client
import os
client = get_openai_client()
model = os.getenv("model", "gpt-4o-mini")
def summarize_messages(existing_summary, old_messages):
    try:
        conversation = "\n".join(
            f"{m['role']}: {m['content']}" for m in old_messages
        )

        prompt = f"""
        You are summarizing a conversation between a student and a teacher.

        Existing summary:
        {existing_summary}

        New conversation to summarize:
        {conversation}

        Rules:
        - Keep it short (3–5 lines)
        - Preserve important concepts discussed
        - Do NOT add new information
        - Do NOT mention timestamps
        - Write in neutral teaching tone

        Return ONLY the updated summary.
        """

        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": prompt}, {"role":"user","content":"You are summarizing a conversation between a student and a teacher."}]
        )
        result = response.choices[0].message.content.strip()
        print("resultresult==", result)
        return result
    except ValueError as e:
        print("error occure", e)
        return e
