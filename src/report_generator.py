"""
Report Generator for DeepSeq-Report

This module handles the generation of protein function prediction reports
based on evo2 toolkit analysis results.
"""

import json
import os
from typing import Dict, Any, List, Union
import logging

# Local imports
from .utils.file_io import read_json_file, write_markdown_file, detect_encoding
from .api_integration import get_api_response

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def validate_input_data(data: Dict[str, Any]) -> None:
    """
    Validate input data structure and content.
    
    Args:
        data: The input data dictionary
        
    Raises:
        ValueError: If required fields are missing
        TypeError: If data types are incorrect
    """
    # Check required metadata fields
    required_metadata = ["input_file", "evo2_model", "analysis_type", "timestamp", "confidence_threshold"]
    if "metadata" not in data:
        raise ValueError("Missing metadata section in input data")
    
    missing_fields = [field for field in required_metadata if field not in data["metadata"]]
    if missing_fields:
        raise ValueError(f"Missing required metadata fields: {', '.join(missing_fields)}")
    
    # Check predictions structure
    if "predictions" not in data:
        raise ValueError("Missing predictions section in input data")
    
    # Validate prediction data types if any predictions exist
    if data["predictions"]:
        for prediction in data["predictions"]:
            if "confidence_score" in prediction and not isinstance(prediction["confidence_score"], (int, float)):
                raise TypeError("Confidence score must be a number")


def generate_executive_summary(data: Dict[str, Any]) -> str:
    """
    Generate an executive summary from the prediction data.
    
    Args:
        data: The input data dictionary
        
    Returns:
        str: Executive summary text
    """
    metadata = data["metadata"]
    predictions = data["predictions"]
    
    # Count predictions by confidence level
    high_confidence = sum(1 for p in predictions if p.get("confidence_score", 0) >= 0.8)
    medium_confidence = sum(1 for p in predictions if 0.5 <= p.get("confidence_score", 0) < 0.8)
    low_confidence = sum(1 for p in predictions if p.get("confidence_score", 0) < 0.5)
    
    # Create summary text
    summary = (
        f"Analysis of {len(predictions)} protein sequences was performed using evo2 model "
        f"{metadata['evo2_model']} on {metadata['timestamp']}. "
        f"The analysis identified {high_confidence} high-confidence predictions, "
        f"{medium_confidence} medium-confidence predictions, and {low_confidence} low-confidence predictions. "
        f"All predictions were filtered using a confidence threshold of {metadata['confidence_threshold']}."
    )
    
    return summary


def format_predictions(predictions: List[Dict[str, Any]], min_confidence: float = 0.7) -> str:
    """
    Format high-confidence predictions section.
    
    Args:
        predictions: List of prediction data
        min_confidence: Minimum confidence score for high confidence predictions
        
    Returns:
        str: Formatted predictions text
    """
    if not predictions:
        return "No predictions found in the analysis data."
    
    # Filter high confidence predictions
    high_confidence = [p for p in predictions if p.get("confidence_score", 0) >= min_confidence]
    
    if not high_confidence:
        return "No high-confidence predictions found."
    
    # Format predictions
    result = ""
    for prediction in high_confidence:
        result += (
            f"- **{prediction.get('protein_id', 'Unknown')}:** "
            f"{prediction.get('go_term_name', 'Unknown function')} "
            f"({prediction.get('predicted_go_term', 'No GO term')}, "
            f"confidence: {prediction.get('confidence_score', 0):.2f})\n"
        )
    
    return result


def format_low_confidence(predictions: List[Dict[str, Any]], max_confidence: float = 0.7) -> str:
    """
    Format low/medium confidence predictions section.
    
    Args:
        predictions: List of prediction data
        max_confidence: Maximum confidence score for low/medium confidence predictions
        
    Returns:
        str: Formatted low confidence predictions text
    """
    if not predictions:
        return "No predictions found in the analysis data."
    
    # Filter low/medium confidence predictions
    low_confidence = [p for p in predictions if p.get("confidence_score", 0) < max_confidence]
    
    if not low_confidence:
        return "No low/medium-confidence predictions found."
    
    # Format predictions
    result = ""
    for prediction in low_confidence:
        result += (
            f"- **{prediction.get('protein_id', 'Unknown')}:** "
            f"{prediction.get('go_term_name', 'Unknown function')} "
            f"({prediction.get('predicted_go_term', 'No GO term')}, "
            f"confidence: {prediction.get('confidence_score', 0):.2f})"
        )
        if prediction.get("notes"):
            result += f" - Note: {prediction.get('notes')}"
        result += "\n"
    
    return result


def format_methodology(data: Dict[str, Any]) -> str:
    """
    Format methodology section.
    
    Args:
        data: The input data dictionary
        
    Returns:
        str: Formatted methodology text
    """
    metadata = data["metadata"]
    
    methodology = (
        f"- Analysis performed using evo2 toolkit version {metadata.get('evo2_model', 'Unknown')}\n"
        f"- Analysis type: {metadata.get('analysis_type', 'Unknown')}\n"
        f"- Confidence threshold: {metadata.get('confidence_threshold', 0)}\n"
        f"- Input data from: {metadata.get('input_file', 'Unknown')}\n"
        f"- Timestamp: {metadata.get('timestamp', 'Unknown')}\n"
    )
    
    return methodology


def generate_report_content(data: Dict[str, Any]) -> str:
    """
    Generate full report content from the input data.
    
    Args:
        data: The input data dictionary
        
    Returns:
        str: Complete report content in markdown format
    """
    # Generate report sections
    executive_summary = generate_executive_summary(data)
    key_predictions = format_predictions(data["predictions"])
    low_confidence_notes = format_low_confidence(data["predictions"])
    methodology = format_methodology(data)
    
    # Compile full report
    report = f"""# evo2 Protein Function Prediction Summary Report

## Executive Summary
{executive_summary}

## Key Predictions
{key_predictions}

## Moderate/Low Confidence Notes
{low_confidence_notes}

## Methodology
{methodology}
"""
    
    return report


def generate_report(input_file: str, output_file: str) -> None:
    """
    Main function to generate report from input file.
    
    Args:
        input_file: Path to the input JSON file
        output_file: Path to output the markdown report
        
    Raises:
        Various exceptions based on input validation and file operations
    """
    logger.info(f"Starting report generation from {input_file}")
    
    # Check input file existence
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file not found: {input_file}")
    
    # Check file permissions
    if not os.access(os.path.dirname(os.path.abspath(output_file)), os.W_OK):
        raise PermissionError(f"No write permission for output directory: {os.path.dirname(output_file)}")
    
    try:
        # Read and parse input file
        data = read_json_file(input_file)
        
        # Validate data structure
        validate_input_data(data)
        
        # Handle empty predictions
        if not data["predictions"]:
            logger.warning("No predictions found in input data")
            # Create a warning report
            report_content = """# evo2 Protein Function Prediction Summary Report

## Warning
No predictions found in the analysis data. Please check the input file and analysis parameters.
"""
            write_markdown_file(output_file, report_content)
            logger.info(f"Warning report written to {output_file}")
            return
        
        # Generate report content
        report_content = generate_report_content(data)
        
        # Write output file
        write_markdown_file(output_file, report_content)
        
        logger.info(f"Report successfully generated at {output_file}")
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON format in input file: {e}")
        raise
    except ValueError as e:
        logger.error(f"Input validation error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during report generation: {e}")
        raise


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python report_generator.py <input_json_file> <output_markdown_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    try:
        generate_report(input_file, output_file)
        print(f"Report generated successfully: {output_file}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1) 