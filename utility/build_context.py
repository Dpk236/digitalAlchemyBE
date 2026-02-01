from utility.time_to_seconds import seconds_to_hhmmss

def build_context(docs, max_chars=12000):
    context_blocks = []
    total_chars = 0

    for d in docs:
        text = d.page_content.strip()
        if not text:
            continue
        start_raw = d.metadata.get('start_time')
        end_raw = d.metadata.get('end_time')

        if start_raw is not None and end_raw is not None:
            start = seconds_to_hhmmss(start_raw)
            end = seconds_to_hhmmss(end_raw)
            block = f"[{start}–{end}]\n{text}"
        else:
            block = text

        if total_chars + len(block) > max_chars:
            break

        context_blocks.append(block)
        total_chars += len(block)

    return "\n\n".join(context_blocks)
