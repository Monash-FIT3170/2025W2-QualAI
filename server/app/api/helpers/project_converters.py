def project_row_to_dict(row_id: int, row: tuple) -> dict:
    # row: (name, description, created_at)
    return {
        "project_id": row_id,
        "name": row[0],
        "description": row[1],
        "created_at": row[2],
    }


def project_full_row_to_dict(row: tuple) -> dict:
    # row: (project_id, name, description, created_at)
    return {
        "project_id": row[0],
        "name": row[1],
        "description": row[2],
        "created_at": row[3],
    }
