"""
File I/O utilities for DeepSeq-Report

This module provides functions for file operations with encoding support.
"""

import json
import os
import chardet
from typing import Dict, Any, Union, Optional


def detect_encoding(file_path: str) -> str:
    """
    Detect the encoding of a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        str: Detected encoding, defaults to utf-8 if detection fails
    """
    # Read a sample of the file to detect encoding
    with open(file_path, 'rb') as f:
        sample = f.read(4096)
    
    # Detect encoding
    result = chardet.detect(sample)
    encoding = result['encoding'] if result['encoding'] else 'utf-8'
    
    # Default to utf-8 for common cases or GBK for Chinese Windows
    if encoding.lower() in ('ascii', 'iso-8859-1'):
        # If detected as ASCII but contains non-ASCII chars, use utf-8 or GBK
        try:
            sample.decode('ascii')
            return encoding
        except UnicodeDecodeError:
            # Try UTF-8 first, then GBK if on Windows
            try:
                sample.decode('utf-8')
                return 'utf-8'
            except UnicodeDecodeError:
                if os.name == 'nt':  # Windows
                    try:
                        sample.decode('gbk')
                        return 'gbk'
                    except UnicodeDecodeError:
                        pass
                return 'utf-8'  # Default to utf-8
    
    return encoding


def read_json_file(file_path: str) -> Dict[str, Any]:
    """
    Read and parse a JSON file with encoding detection.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Dict: Parsed JSON data
        
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If JSON is invalid
        UnicodeDecodeError: If encoding issues occur
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Detect encoding
    encoding = detect_encoding(file_path)
    
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            data = json.load(f)
        return data
    except UnicodeDecodeError:
        # Fallback to utf-8 if encoding detection fails
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except json.JSONDecodeError as e:
        # Re-raise with more context
        raise json.JSONDecodeError(
            f"Invalid JSON in {file_path}: {str(e)}", 
            e.doc, 
            e.pos
        )


def write_markdown_file(file_path: str, content: str, encoding: str = 'utf-8') -> None:
    """
    Write content to a markdown file.
    
    Args:
        file_path: Path to write the markdown file
        content: Content to write
        encoding: Encoding to use, defaults to utf-8
        
    Raises:
        PermissionError: If write permission is denied
        OSError: For other I/O errors
    """
    # Ensure the directory exists
    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
    
    try:
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
    except UnicodeEncodeError:
        # If utf-8 fails, try with system default encoding
        with open(file_path, 'w', encoding=detect_encoding(file_path) if os.path.exists(file_path) else 'utf-8') as f:
            f.write(content)
    except PermissionError:
        raise PermissionError(f"Permission denied when writing to {file_path}")
    except OSError as e:
        raise OSError(f"Error writing to {file_path}: {str(e)}")


def ensure_directory(directory_path: str) -> None:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory_path: Path to the directory
        
    Raises:
        PermissionError: If directory cannot be created due to permissions
    """
    if not os.path.exists(directory_path):
        try:
            os.makedirs(directory_path, exist_ok=True)
        except PermissionError:
            raise PermissionError(f"Permission denied when creating directory {directory_path}")
        except OSError as e:
            raise OSError(f"Error creating directory {directory_path}: {str(e)}")


def is_file_readable(file_path: str) -> bool:
    """
    Check if a file exists and is readable.
    
    Args:
        file_path: Path to the file
        
    Returns:
        bool: True if file exists and is readable, False otherwise
    """
    return os.path.isfile(file_path) and os.access(file_path, os.R_OK)


def is_directory_writable(directory_path: str) -> bool:
    """
    Check if a directory exists and is writable.
    
    Args:
        directory_path: Path to the directory
        
    Returns:
        bool: True if directory exists and is writable, False otherwise
    """
    return os.path.isdir(directory_path) and os.access(directory_path, os.W_OK) 