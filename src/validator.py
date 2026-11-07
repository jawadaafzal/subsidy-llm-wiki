from pydantic import ValidationError
from src.schema import WikiPage


def validate_wiki_page(data: dict):
    try:
        page = WikiPage(**data)
        return True, page
    except ValidationError as error:
        return False, error