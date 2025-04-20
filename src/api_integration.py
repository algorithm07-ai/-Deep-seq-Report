"""
API Integration for DeepSeq-Report

This module handles integration with the DeepSeek API for report generation.
"""

import os
import requests
import logging
import json
import time
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# API Configuration
API_KEY = os.getenv("DEEPSEEK_API_KEY")
API_URL = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/v1/")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))


def validate_api_key() -> None:
    """
    Validate that API key is available.
    
    Raises:
        ValueError: If API key is not configured
    """
    if not API_KEY:
        raise ValueError(
            "DeepSeek API key not found. Please set DEEPSEEK_API_KEY "
            "environment variable or in .env file."
        )


def construct_prompt(data: Dict[str, Any]) -> str:
    """
    Construct a prompt for the DeepSeek API based on protein data.
    
    Args:
        data: Protein prediction data
        
    Returns:
        str: Formatted prompt for the API
    """
    protein_id = data.get("protein_id", "Unknown")
    go_term = data.get("predicted_go_term", "Unknown")
    go_term_name = data.get("go_term_name", "Unknown")
    confidence = data.get("confidence_score", 0)
    
    prompt = f"""
Analyze the following protein function prediction:

Protein ID: {protein_id}
GO Term: {go_term}
GO Term Name: {go_term_name}
Confidence Score: {confidence}

Please provide:
1. A brief explanation of this protein's predicted function
2. The significance of this function in biological context
3. Relevant biochemical pathways this protein might be involved in
4. Any notable structural domains that might contribute to this function
"""
    
    return prompt.strip()


def get_api_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get a response from the DeepSeek API for protein analysis.
    
    Args:
        data: Protein prediction data
        
    Returns:
        Dict: API response data
        
    Raises:
        ValueError: For API authentication or validation errors
        TimeoutError: For API timeout issues
        ConnectionError: For network issues
    """
    validate_api_key()
    
    # Construct API request
    prompt = construct_prompt(data)
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    # Make API request with retry logic
    max_retries = 3
    retry_delay = 2  # seconds
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Making API request for protein {data.get('protein_id', 'Unknown')}")
            response = requests.post(
                f"{API_URL.rstrip('/')}/chat/completions",
                headers=headers,
                json=payload,
                timeout=REQUEST_TIMEOUT
            )
            
            # Check for successful response
            if response.status_code == 200:
                response_data = response.json()
                return {
                    "protein_id": data.get("protein_id", "Unknown"),
                    "analysis": response_data["choices"][0]["message"]["content"],
                    "go_term": data.get("predicted_go_term", "Unknown"),
                    "confidence": data.get("confidence_score", 0)
                }
            
            # Handle authentication errors
            elif response.status_code == 401:
                error_msg = response.json().get("error", {}).get("message", "Authentication failed")
                raise ValueError(f"Authentication failed: {error_msg}")
            
            # Handle rate limiting
            elif response.status_code == 429:
                if attempt < max_retries - 1:
                    retry_after = int(response.headers.get("Retry-After", retry_delay))
                    logger.warning(f"Rate limited. Retrying after {retry_after} seconds.")
                    time.sleep(retry_after)
                    continue
                else:
                    raise ValueError("API rate limit exceeded. Please try again later.")
            
            # Handle other API errors
            else:
                error_msg = response.json().get("error", {}).get("message", "Unknown API error")
                raise ValueError(f"API error: {error_msg}")
                
        except requests.exceptions.Timeout:
            logger.warning(f"API request timed out (attempt {attempt+1}/{max_retries})")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
                continue
            raise TimeoutError("API request timed out after multiple attempts")
            
        except requests.exceptions.ConnectionError:
            logger.warning(f"Connection error (attempt {attempt+1}/{max_retries})")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
                continue
            raise ConnectionError("Failed to connect to API after multiple attempts")
            
    # This line should not be reached due to the raises inside the loop
    raise RuntimeError("Unexpected error in API request handling") 