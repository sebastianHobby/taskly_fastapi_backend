def generate_multi_get_description(model_name) -> str:
    description: str = (
        f"Read multiple {model_name} rows from the database.\n\n"
        f"**Pagination Options:**\n"
        f"- Use `page` & `itemsPerPage` for paginated results\n"
        f"- Use `offset` & `limit` for specific ranges\n\n"
        f"**Response Format:**\n"
        f"- Returns paginated response when using page/itemsPerPage\n"
        f"- Returns simple list response when using offset/limit"
    )
    return description
