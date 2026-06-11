from typing import List

def is_new_recipient(recipient_alias: str, known_recipients: List[str]) -> bool:
    """
    Returns True if the recipient has never been transacted with before.
    """
    if not recipient_alias:
        return True
    return recipient_alias not in known_recipients