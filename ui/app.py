import chainlit as cl
from backend.agent import get_response

@cl.on_message
async def main(message: cl.Message):
    """
    Chainlit message handler: Process user input and send response.

    Args:
        message (cl.Message): Incoming user message.

    Notes:
        - Async to handle potential delays in LLM calls.
        - Debug: Add logging here for production (e.g., structlog).
    """
    # Get LLM response
    response = await get_response(message.content)
    
    # Send back to UI
    await cl.Message(content=response).send()