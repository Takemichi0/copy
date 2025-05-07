# ref: https://firebase.google.com/docs/firestore/best-practices
FORBIDDEN_CHARACTERS = ['.', '/', '\\', '`', '*', '[', ']']

def sanitize_for_firestore(text: str) -> str:
    for char in FORBIDDEN_CHARACTERS:
        text = text.replace(char, '-')

    return text
