from typing import Dict, Tuple

def transcription_meta_row_to_dict(row: tuple) -> Dict:
    # row: (transcription_id, name, processed_at)
    return {
        "transcription_id": row[0],
        "name": row[1],
        "processed_at": row[2],
    }

def transcription_full_row_to_dict(project_id: int, row: tuple) -> Dict:
    return {
        "project_id": project_id,
        "name": row[1],
        "text": row[2],
        "processed_at": row[3],
    }
