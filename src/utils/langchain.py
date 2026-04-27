from typing import Any
from langchain_core.messages import HumanMessage, AIMessage, ContentBlock


def extract_text_from_content_blocks(content_blocks: list[ContentBlock]) -> str:
    """Extracts and concatenates content from a list of content blocks.

    Args:
        content_blocks (list[ContentBlock]): A list of content blocks, where each block is a ContentBlock instance.

    Returns:
        str: A single string containing the concatenated content from all blocks.
    """
    contents = []
    for block in content_blocks:
        if block.get("type") != "text":
            continue  # Skip non-text blocks for now, but could be extended to handle other types (e.g., images, tables) in the future.
        content = block.get("text")
        if content:
            contents.append(content)
    return "\n".join(contents)


# NOTE: TBD what the heck I do here.
def get_final_response(response: dict[str, Any]) -> str:
    """Extracts the final response text from the agent's output.

    Args:
        response (dict): The raw response from the agent.

    Returns:
        str: The extracted final response text.
    """
    messages: list[HumanMessage | AIMessage] = response.get("messages", [])
    for message in reversed(messages):
        if isinstance(message, AIMessage):
            return extract_text_from_content_blocks(
                content_blocks=message.content_blocks
            )
    return "No valid response found."
