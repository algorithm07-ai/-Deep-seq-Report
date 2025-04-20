import pytest
import json
import os
from unittest.mock import patch, MagicMock
import sys
sys.path.append('../')  # Add parent directory to path

from src.report_generator import generate_report
from src.protein_analysis import analyze_sequence
from src.api_integration import get_api_response


class TestErrorHandling:
    """Test suite for error handling in DeepSeq-Report."""
    
    def setup_method(self):
        """Setup test environment before each test."""
        # Create test data
        self.valid_data = {
            "metadata": {
                "input_file": "test.fasta",
                "evo2_model": "v2.0",
                "analysis_type": "full",
                "timestamp": "2023-10-15T12:30:45",
                "confidence_threshold": 0.7
            },
            "predictions": [
                {
                    "protein_id": "P12345",
                    "predicted_go_term": "GO:0003700",
                    "go_term_name": "DNA binding",
                    "confidence_score": 0.85,
                    "notes": "High confidence"
                }
            ]
        }
        
        # Create test file paths
        self.input_file = "test_input.json"
        self.output_file = "test_output.md"
    
    def teardown_method(self):
        """Cleanup after each test."""
        # Remove test files if they exist
        for file in [self.input_file, self.output_file]:
            if os.path.exists(file):
                os.remove(file)
    
    def test_invalid_json_format(self):
        """Test handling of invalid JSON format."""
        # Create invalid JSON file
        with open(self.input_file, 'w') as f:
            f.write("{invalid json")
        
        # Test generate_report with invalid JSON
        with pytest.raises(json.JSONDecodeError):
            generate_report(self.input_file, self.output_file)
    
    def test_missing_required_fields(self):
        """Test handling of missing required fields in input data."""
        # Create data with missing fields
        invalid_data = {
            "metadata": {
                "input_file": "test.fasta"
                # Missing other required fields
            },
            "predictions": []
        }
        
        with open(self.input_file, 'w') as f:
            json.dump(invalid_data, f)
        
        # Test generate_report with missing fields
        with pytest.raises(ValueError, match="Missing required metadata fields"):
            generate_report(self.input_file, self.output_file)
    
    def test_empty_predictions(self):
        """Test handling of empty predictions list."""
        # Create data with empty predictions
        data_empty_predictions = {
            "metadata": self.valid_data["metadata"],
            "predictions": []
        }
        
        with open(self.input_file, 'w') as f:
            json.dump(data_empty_predictions, f)
        
        # Test generate_report with empty predictions
        # This should not raise an error but generate a warning in the report
        generate_report(self.input_file, self.output_file)
        
        # Verify output contains warning
        with open(self.output_file, 'r') as f:
            content = f.read()
            assert "No predictions found" in content
    
    def test_invalid_confidence_score(self):
        """Test handling of invalid confidence scores."""
        # Create data with invalid confidence score
        invalid_data = self.valid_data.copy()
        invalid_data["predictions"][0]["confidence_score"] = "invalid"
        
        with open(self.input_file, 'w') as f:
            json.dump(invalid_data, f)
        
        # Test generate_report with invalid confidence score
        with pytest.raises(TypeError, match="Confidence score must be a number"):
            generate_report(self.input_file, self.output_file)
    
    def test_file_permissions(self):
        """Test handling of file permission errors."""
        # Mock os.access to simulate permission denied
        with patch('os.access', return_value=False):
            with pytest.raises(PermissionError):
                generate_report(self.input_file, self.output_file)
    
    def test_api_timeout(self):
        """Test handling of API timeout."""
        # Create valid input file
        with open(self.input_file, 'w') as f:
            json.dump(self.valid_data, f)
        
        # Mock API call to simulate timeout
        with patch('src.api_integration.get_api_response', 
                   side_effect=TimeoutError("API request timed out")):
            with pytest.raises(TimeoutError, match="API request timed out"):
                generate_report(self.input_file, self.output_file)
    
    def test_api_authentication_error(self):
        """Test handling of API authentication errors."""
        # Create valid input file
        with open(self.input_file, 'w') as f:
            json.dump(self.valid_data, f)
        
        # Mock API call to simulate authentication error
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"error": "Invalid API key"}
        
        with patch('src.api_integration.requests.post', return_value=mock_response):
            with pytest.raises(ValueError, match="Authentication failed: Invalid API key"):
                generate_report(self.input_file, self.output_file)
    
    def test_encoding_errors(self):
        """Test handling of encoding errors."""
        # Create test data with special characters
        special_data = self.valid_data.copy()
        special_data["predictions"][0]["go_term_name"] = "特殊字符测试"
        
        with open(self.input_file, 'w', encoding='utf-8') as f:
            json.dump(special_data, f)
        
        # Test with incorrect encoding detection
        with patch('src.utils.file_io.detect_encoding', return_value='ascii'):
            # Should fall back to utf-8
            generate_report(self.input_file, self.output_file)
            
            # Verify file was created
            assert os.path.exists(self.output_file)
    
    def test_invalid_sequence_format(self):
        """Test handling of invalid protein sequence formats."""
        # Create invalid sequence
        invalid_sequence = "ABC123XYZ"  # Invalid amino acid codes
        
        # Test sequence analysis with invalid sequence
        with pytest.raises(ValueError, match="Invalid protein sequence format"):
            analyze_sequence(invalid_sequence)
    
    def test_recovery_from_partial_failure(self):
        """Test recovery mechanisms when some operations fail."""
        # Create valid input file
        with open(self.input_file, 'w') as f:
            json.dump(self.valid_data, f)
        
        # Mock API to fail for one prediction but succeed for others
        original_api_function = get_api_response
        
        def mock_api_call(data):
            if data["protein_id"] == "P12345":
                raise ConnectionError("Network error")
            return original_api_function(data)
        
        with patch('src.api_integration.get_api_response', side_effect=mock_api_call):
            # This should complete with warnings
            generate_report(self.input_file, self.output_file)
            
            # Verify output contains warning
            with open(self.output_file, 'r') as f:
                content = f.read()
                assert "Some predictions could not be processed" in content


if __name__ == "__main__":
    pytest.main(["-v", "test_error_handling.py"]) 