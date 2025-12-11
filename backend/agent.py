from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from backend.settings import settings
from typing import Awaitable  # For async type hint

async def get_response(user_input: str) -> Awaitable[str]:
    """
    Generate a response from the LLM based on user input.

    Args:
        user_input (str): The user's message.

    Returns:
        Awaitable[str]: The LLM's response content.

    Notes:
        - Uses async for potential streaming/future scalability.
        - Personality injected via system prompt.
    """
    # Initialize LLM with config settings
    llm = ChatOllama(
        model=settings['ollama']['model'],
        base_url=settings['ollama']['host'],
        temperature=settings['ollama']['temperature'],
        stream=False  # Non-streaming for simplicity; enable for real-time output
    )
    
    # Define prompt template with personality traits
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are Freya: warm, emotionally intelligent, friendly with witty sarcasm, truth-seeking, honest, admits uncertainty, family-safe."),
        ("user", "{input}")
    ])
    
    # Chain prompt to LLM
    chain = prompt | llm
    
    # Invoke async and extract content
    response = await chain.ainvoke({"input": user_input})
    return response.content