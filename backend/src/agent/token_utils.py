"""Token management utilities for OpenAI models."""

import logging
from typing import List, Optional, Tuple
import tiktoken
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Token limits for different OpenAI models
TOKEN_LIMITS = {
    "o3": 200000,
    "o4-mini": 200000,
    "gpt-4.1": None,  # No token limit splitting for gpt-4.1
}

# Models that require token counting and splitting
MODELS_REQUIRING_SPLITTING = {"o3", "o4-mini"}

# Default tiktoken encodings for OpenAI models
MODEL_ENCODINGS = {
    "o3": "o200k_base",
    "o4-mini": "o200k_base", 
    "gpt-4.1": "cl100k_base",
}


def get_model_encoding(model_name: str) -> str:
    """Get the appropriate tiktoken encoding for a model."""
    return MODEL_ENCODINGS.get(model_name, "cl100k_base")


def count_tokens(text: str, model_name: str) -> int:
    """Count tokens in text using tiktoken for the specified model.
    
    Args:
        text: The text to count tokens for
        model_name: The OpenAI model name to get encoding for
        
    Returns:
        Number of tokens in the text
    """
    try:
        encoding_name = get_model_encoding(model_name)
        encoding = tiktoken.get_encoding(encoding_name)
        tokens = encoding.encode(text)
        return len(tokens)
    except Exception as e:
        logging.warning(f"Error counting tokens for model {model_name}: {e}")
        # Fallback estimation: roughly 4 characters per token
        return len(text) // 4


def needs_token_splitting(model_name: str, text: str) -> bool:
    """Check if text needs to be split based on model token limits.
    
    Args:
        model_name: The model name to check limits for
        text: The text to check
        
    Returns:
        True if text exceeds model token limit and needs splitting
    """
    if model_name not in MODELS_REQUIRING_SPLITTING:
        return False
        
    token_limit = TOKEN_LIMITS.get(model_name)
    if token_limit is None:
        return False
        
    token_count = count_tokens(text, model_name)
    logging.debug(f"Token count for {model_name}: {token_count}/{token_limit}")
    
    return token_count > token_limit


def split_text_by_tokens(text: str, model_name: str, chunk_overlap: int = 200) -> List[str]:
    """Split text into chunks that respect token limits.
    
    Args:
        text: The text to split
        model_name: The model name to get token limits for
        chunk_overlap: Number of tokens to overlap between chunks
        
    Returns:
        List of text chunks that fit within token limits
    """
    token_limit = TOKEN_LIMITS.get(model_name)
    if token_limit is None:
        return [text]
    
    # Reserve some tokens for the response and system overhead
    max_chunk_tokens = int(token_limit * 0.8)  # Use 80% of limit for safety
    
    try:
        # Create a text splitter that works with tokens
        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            encoding_name=get_model_encoding(model_name),
            chunk_size=max_chunk_tokens,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", "! ", "? ", "; ", ", ", " ", ""],
        )
        
        chunks = text_splitter.split_text(text)
        
        # Log splitting information
        total_tokens = count_tokens(text, model_name)
        chunk_tokens = [count_tokens(chunk, model_name) for chunk in chunks]
        logging.info(f"Split text with {total_tokens} tokens into {len(chunks)} chunks with tokens: {chunk_tokens}")
        
        return chunks
        
    except Exception as e:
        logging.error(f"Error splitting text for model {model_name}: {e}")
        # Fallback: split by character count estimation
        chunk_size = max_chunk_tokens * 4  # Rough estimation
        chunks = []
        for i in range(0, len(text), chunk_size):
            chunks.append(text[i:i + chunk_size])
        return chunks


def split_prompt_for_model(prompt: str, model_name: str) -> Tuple[List[str], bool]:
    """Split a prompt if it exceeds the model's token limits.
    
    Args:
        prompt: The prompt to potentially split
        model_name: The model name to check limits for
        
    Returns:
        Tuple of (list of prompt chunks, was_split_flag)
    """
    if not needs_token_splitting(model_name, prompt):
        return [prompt], False
    
    logging.info(f"Splitting prompt for model {model_name} due to token limit")
    chunks = split_text_by_tokens(prompt, model_name)
    return chunks, True


def aggregate_responses(responses: List[str]) -> str:
    """Aggregate multiple responses from split prompts into a coherent result.
    
    Args:
        responses: List of responses from each prompt chunk
        
    Returns:
        Aggregated response
    """
    if len(responses) == 1:
        return responses[0]
    
    # For now, concatenate responses with separators
    # More sophisticated aggregation logic could be added here
    aggregated = "\n\n---\n\n".join(responses)
    
    logging.info(f"Aggregated {len(responses)} responses into single result")
    return aggregated


def log_token_usage(model_name: str, prompt: str, response: str = "") -> None:
    """Log token usage statistics for debugging.
    
    Args:
        model_name: The model name
        prompt: The input prompt
        response: The model response (optional)
    """
    prompt_tokens = count_tokens(prompt, model_name)
    response_tokens = count_tokens(response, model_name) if response else 0
    total_tokens = prompt_tokens + response_tokens
    
    limit = TOKEN_LIMITS.get(model_name, "No limit")
    
    logging.debug(f"Token usage for {model_name}: {prompt_tokens} prompt + {response_tokens} response = {total_tokens} total (limit: {limit})")