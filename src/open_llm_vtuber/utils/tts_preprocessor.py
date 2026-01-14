import re
import unicodedata
from loguru import logger
from ..translate.translate_interface import TranslateInterface


def tts_filter(
    text: str,
    remove_special_char: bool,
    ignore_brackets: bool,
    ignore_parentheses: bool,
    ignore_asterisks: bool,
    ignore_angle_brackets: bool,
    translator: TranslateInterface | None = None,
) -> str:
    """
    Filter or do anything to the text before TTS generates the audio.
    Changes here do not affect subtitles or LLM's memory. The generated audio is
    the only affected thing.

    Args:
        text (str): The text to filter.
        remove_special_char (bool): Whether to remove special characters.
        ignore_brackets (bool): Whether to ignore text within brackets.
        ignore_parentheses (bool): Whether to ignore text within parentheses.
        ignore_asterisks (bool): Whether to ignore text within asterisks.
        translator (TranslateInterface, optional):
            The translator to use. If None, we'll skip the translation. Defaults to None.

    Returns:
        str: The filtered text.
    """
    if ignore_asterisks:
        try:
            text = filter_asterisks(text)
        except Exception as e:
            logger.warning(f"Error ignoring asterisks: {e}")
            logger.warning(f"Text: {text}")
            logger.warning("Skipping...")

    if ignore_brackets:
        try:
            text = filter_brackets(text)
        except Exception as e:
            logger.warning(f"Error ignoring brackets: {e}")
            logger.warning(f"Text: {text}")
            logger.warning("Skipping...")
    if ignore_parentheses:
        try:
            text = filter_parentheses(text)
        except Exception as e:
            logger.warning(f"Error ignoring parentheses: {e}")
            logger.warning(f"Text: {text}")
            logger.warning("Skipping...")
    if ignore_angle_brackets:
        try:
            text = filter_angle_brackets(text)
        except Exception as e:
            logger.warning(f"Error ignoring angle brackets: {e}")
            logger.warning(f"Text: {text}")
            logger.warning("Skipping...")
    if remove_special_char:
        try:
            text = remove_special_characters(text)
        except Exception as e:
            logger.warning(f"Error removing special characters: {e}")
            logger.warning(f"Text: {text}")
            logger.warning("Skipping...")
    if translator:
        try:
            logger.info("Translating...")
            text = translator.translate(text)
            logger.info(f"Translated: {text}")
        except Exception as e:
            logger.critical(f"Error translating: {e}")
            logger.critical(f"Text: {text}")
            logger.warning("Skipping...")

    logger.debug(f"Filtered text: {text}")
    return text


def remove_special_characters(text: str) -> str:
    """
    Filter text to remove all non-letter, non-number, and non-punctuation characters.

    Args:
        text (str): The text to filter.

    Returns:
        str: The filtered text.
    """
    normalized_text = unicodedata.normalize("NFKC", text)

    def is_valid_char(char: str) -> bool:
        category = unicodedata.category(char)
        return (
            category.startswith("L")
            or category.startswith("N")
            or category.startswith("P")
            or char.isspace()
        )

    filtered_text = "".join(char for char in normalized_text if is_valid_char(char))
    return filtered_text


def _filter_nested(text: str, left: str, right: str) -> str:
    """
    Generic function to handle nested symbols.

    Args:
        text (str): The text to filter.
        left (str): The left symbol (e.g. '[' or '(').
        right (str): The right symbol (e.g. ']' or ')').

    Returns:
        str: The filtered text.
    """
    if not isinstance(text, str):
        raise TypeError("Input must be a string")
    if not text:
        return text

    result = []
    depth = 0
    for char in text:
        if char == left:
            depth += 1
        elif char == right:
            if depth > 0:
                depth -= 1
        else:
            if depth == 0:
                result.append(char)
    filtered_text = "".join(result)
    filtered_text = re.sub(r"\s+", " ", filtered_text).strip()
    return filtered_text


def filter_brackets(text: str) -> str:
    """
    Filter text to remove all text within brackets, handling nested cases.

    Args:
        text (str): The text to filter.

    Returns:
        str: The filtered text.
    """
    return _filter_nested(text, "[", "]")


def filter_parentheses(text: str) -> str:
    """
    Filter text to remove all text within parentheses, handling nested cases.

    Args:
        text (str): The text to filter.

    Returns:
        str: The filtered text.
    """
    return _filter_nested(text, "(", ")")


def filter_angle_brackets(text: str) -> str:
    """
    Filter text to remove all text within angle brackets, handling nested cases.

    Args:
        text (str): The text to filter.

    Returns:
        str: The filtered text.
    """
    return _filter_nested(text, "<", ">")


def filter_asterisks(text: str) -> str:
    """
    Removes text enclosed within asterisks of any length (*, **, ***, etc.) from a string.

    Args:
        text: The input string.

    Returns:
        The string with asterisk-enclosed text removed.
    """
    # Handle asterisks of any length (*, **, ***, etc.)
    filtered_text = re.sub(r"\*{1,}((?!\*).)*?\*{1,}", "", text)

    # Clean up any extra spaces
    filtered_text = re.sub(r"\s+", " ", filtered_text).strip()

    return filtered_text


def filter_numbered_lists(text: str) -> str:
    """
    Remove numbered list patterns (e.g., "1. ", "2. ", "1)", "2)", etc.) from text.

    Args:
        text: The input string.

    Returns:
        The string with numbered list markers removed.
    """
    # Normalize common numbered list markers at the start of lines or segments.
    # Examples handled:
    #   "1. xxx", "2．xxx", "3。xxx", "4) xxx", "5、xxx", "(6) xxx", "（7）xxx"
    # We only target markers at the beginning of a line to avoid over-stripping.
    filtered_text = text

    # Patterns like "1. " / "2．" / "3。"
    filtered_text = re.sub(
        r"(?m)^\s*\d+[\.．。]\s*",
        "",
        filtered_text,
    )
    # Patterns like "1) " / "2） " and "1、 "
    filtered_text = re.sub(
        r"(?m)^\s*\d+[)、]\s*",
        "",
        filtered_text,
    )
    # Patterns like "(1) " / "（2） "
    filtered_text = re.sub(
        r"(?m)^\s*[（(]\d+[）)]\s*",
        "",
        filtered_text,
    )
    # Clean up any extra spaces
    filtered_text = re.sub(r"\s+", " ", filtered_text).strip()
    return filtered_text


def filter_special_formatting(text: str) -> str:
    """
    Remove common markdown and formatting symbols that shouldn't appear in spoken text.
    This function preserves Live2D expression keywords in brackets.

    Args:
        text: The input string.

    Returns:
        The string with formatting symbols removed.
    """
    # Protect Live2D expressions [expression] patterns first
    protected_patterns = []
    protected_counter = 0

    def protect_live2d(match):
        nonlocal protected_counter
        placeholder = f"__LIVE2D_PROTECT_{protected_counter}__"
        protected_patterns.append((placeholder, match.group(0)))
        protected_counter += 1
        return placeholder

    # Protect [expression] patterns (Live2D expressions)
    text = re.sub(r"\[[^\]]+\]", protect_live2d, text)

    # Remove standalone asterisks used for emphasis (single or multiple, but not in brackets)
    # This removes patterns like *text*, **text**, ***text*** etc.
    text = re.sub(r"\*{1,}((?!\*).)*?\*{1,}", "", text)
    # Also remove standalone asterisks not in pairs
    text = re.sub(r"(?<!\*)\*(?!\*)", "", text)

    # Remove markdown headers (#, ##, ###)
    text = re.sub(r"#{1,6}\s+", "", text)
    # Remove markdown list markers at line start (-, +)
    text = re.sub(r"^[-+]\s+", "", text, flags=re.MULTILINE)

    # Restore protected Live2D patterns
    for placeholder, original in protected_patterns:
        text = text.replace(placeholder, original)

    # Clean up extra spaces
    text = re.sub(r"\s+", " ", text).strip()
    return text
