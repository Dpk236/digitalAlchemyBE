from utility.time_to_seconds import seconds_to_hhmmss

def build_context(docs, max_chars=12000):
    context_blocks = []
    total_chars = 0

    for d in docs:
        text = d.page_content.strip()
        if not text:
            continue
        start = seconds_to_hhmmss(d.metadata['start_time'])
        end = seconds_to_hhmmss(d.metadata['end_time'])
        block = f"[{start}–{end}]\n{text}"

        if total_chars + len(block) > max_chars:
            break

        context_blocks.append(block)
        total_chars += len(block)

    return "\n\n".join(context_blocks)
