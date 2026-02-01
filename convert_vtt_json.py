import re


def vtt_to_segments(vtt_file_path):
    print(f"Converting VTT file: {vtt_file_path} to JSON segments")
    segments = []

    def time_to_seconds(time_str):
        """
        Converts HH:MM:SS.mmm or MM:SS.mmm to seconds
        """
        parts = time_str.split(":")
        if len(parts) == 3:
            h, m, s = parts
            return int(h) * 3600 + int(m) * 60 + float(s)
        else:
            m, s = parts
            return int(m) * 60 + float(s)

    with open(vtt_file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Match timestamp line
        if "-->" in line:
            start, end = line.split(" --> ")
            start_time = int(time_to_seconds(start))
            end_time = int(time_to_seconds(end))

            i += 1
            text_lines = []

            # Collect subtitle text
            while i < len(lines) and lines[i].strip() != "":
                text_lines.append(lines[i].strip())
                i += 1

            segments.append({
                "video_id": "1002990",
                "subject": "Bialogy",
                "chapter": "Bacteria and Virus",
                "topic": "Staphylococcus of Parabola",
                "sub_topic": "Staphylococcus and Directrix",
                "difficulty": "Easy",
                "start_time": start_time,
                "end_time": end_time,
                "text_original": " ".join(text_lines)
            })

        i += 1

    return segments
