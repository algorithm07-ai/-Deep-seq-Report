#!/bin/bash
# Script to run the DeepSeq-Report Singularity container

# Check if the API key is set
if [ -z "$DEEPSEEK_API_KEY" ]; then
    echo "Error: DEEPSEEK_API_KEY environment variable is not set"
    echo "Please set the API key with: export DEEPSEEK_API_KEY=your_api_key"
    exit 1
fi

# Check if input and output files are provided
if [ "$#" -lt 2 ]; then
    echo "Usage: $0 <input_file> <output_file>"
    echo "Example: $0 /path/to/input.json /path/to/output.md"
    exit 1
fi

# Get absolute paths
INPUT_FILE=$(readlink -f "$1")
OUTPUT_FILE=$(readlink -f "$2")
OUTPUT_DIR=$(dirname "$OUTPUT_FILE")

# Check if input file exists
if [ ! -f "$INPUT_FILE" ]; then
    echo "Error: Input file '$INPUT_FILE' does not exist"
    exit 1
fi

# Create output directory if it doesn't exist
if [ ! -d "$OUTPUT_DIR" ]; then
    echo "Creating output directory: $OUTPUT_DIR"
    mkdir -p "$OUTPUT_DIR"
fi

# Find the latest Singularity image
LATEST_IMAGE=$(ls -t deep-seq-report_*.sif 2>/dev/null | head -1)

if [ -z "$LATEST_IMAGE" ]; then
    echo "Error: No DeepSeq-Report Singularity image found"
    echo "Please run singularity-build.sh first to create the image"
    exit 1
fi

echo "Using Singularity image: $LATEST_IMAGE"
echo "Input file: $INPUT_FILE"
echo "Output file: $OUTPUT_FILE"

# Run the Singularity container
echo "Running DeepSeq-Report Singularity container..."
DEEPSEEK_API_KEY=$DEEPSEEK_API_KEY singularity run \
    --bind $(dirname "$INPUT_FILE"):/input \
    --bind "$OUTPUT_DIR":/output \
    $LATEST_IMAGE \
    /input/$(basename "$INPUT_FILE") \
    /output/$(basename "$OUTPUT_FILE")

echo "DeepSeq-Report analysis complete. Results saved to: $OUTPUT_FILE" 