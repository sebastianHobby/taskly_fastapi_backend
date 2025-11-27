def generate_multi_get_description(model_name) -> str:
    description: str = (
        f"Read multiple {model_name} rows from the database.\n\n"
        f"**Pagination Options:**\n"
        f"- Use `page` & `itemsPerPage` for paginated results\n"
    )
    return description
