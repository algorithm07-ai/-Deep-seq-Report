"""
Protein Analysis Module for DeepSeq-Report

This module provides functions for analyzing protein sequences.
"""

import re
import logging
from typing import Dict, Any, List, Tuple, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Amino acid properties
AA_PROPERTIES = {
    'A': {'hydrophobic': True, 'charge': 0, 'molecular_weight': 89.09},
    'R': {'hydrophobic': False, 'charge': 1, 'molecular_weight': 174.20},
    'N': {'hydrophobic': False, 'charge': 0, 'molecular_weight': 132.12},
    'D': {'hydrophobic': False, 'charge': -1, 'molecular_weight': 133.10},
    'C': {'hydrophobic': True, 'charge': 0, 'molecular_weight': 121.15},
    'E': {'hydrophobic': False, 'charge': -1, 'molecular_weight': 147.13},
    'Q': {'hydrophobic': False, 'charge': 0, 'molecular_weight': 146.15},
    'G': {'hydrophobic': True, 'charge': 0, 'molecular_weight': 75.07},
    'H': {'hydrophobic': False, 'charge': 0.1, 'molecular_weight': 155.16},
    'I': {'hydrophobic': True, 'charge': 0, 'molecular_weight': 131.17},
    'L': {'hydrophobic': True, 'charge': 0, 'molecular_weight': 131.17},
    'K': {'hydrophobic': False, 'charge': 1, 'molecular_weight': 146.19},
    'M': {'hydrophobic': True, 'charge': 0, 'molecular_weight': 149.21},
    'F': {'hydrophobic': True, 'charge': 0, 'molecular_weight': 165.19},
    'P': {'hydrophobic': True, 'charge': 0, 'molecular_weight': 115.13},
    'S': {'hydrophobic': False, 'charge': 0, 'molecular_weight': 105.09},
    'T': {'hydrophobic': False, 'charge': 0, 'molecular_weight': 119.12},
    'W': {'hydrophobic': True, 'charge': 0, 'molecular_weight': 204.23},
    'Y': {'hydrophobic': False, 'charge': 0, 'molecular_weight': 181.19},
    'V': {'hydrophobic': True, 'charge': 0, 'molecular_weight': 117.15},
}

# Regular expression for valid protein sequence
VALID_PROTEIN_REGEX = re.compile(r'^[ACDEFGHIKLMNPQRSTVWY]+$')


def validate_sequence(sequence: str) -> str:
    """
    Validate a protein sequence.
    
    Args:
        sequence: Protein sequence string
        
    Returns:
        str: Validated sequence (upper case)
        
    Raises:
        ValueError: If sequence is invalid
    """
    if not sequence:
        raise ValueError("Empty sequence provided")
    
    # Convert to uppercase and remove whitespace
    sequence = re.sub(r'\s', '', sequence.upper())
    
    # Validate characters
    if not VALID_PROTEIN_REGEX.match(sequence):
        raise ValueError("Invalid protein sequence format. Sequence must contain only standard amino acid codes (ACDEFGHIKLMNPQRSTVWY).")
    
    return sequence


def calculate_molecular_weight(sequence: str) -> float:
    """
    Calculate the molecular weight of a protein sequence.
    
    Args:
        sequence: Validated protein sequence
        
    Returns:
        float: Molecular weight in Daltons
    """
    # Add water molecule (H2O)
    mw = 18.01528
    
    for aa in sequence:
        mw += AA_PROPERTIES[aa]['molecular_weight']
    
    return round(mw, 2)


def analyze_amino_acid_composition(sequence: str) -> Dict[str, float]:
    """
    Analyze the amino acid composition of a sequence.
    
    Args:
        sequence: Validated protein sequence
        
    Returns:
        Dict: Amino acid composition as percentages
    """
    total_length = len(sequence)
    composition = {}
    
    for aa in AA_PROPERTIES.keys():
        count = sequence.count(aa)
        composition[aa] = round((count / total_length) * 100, 2)
    
    return composition


def analyze_physicochemical_properties(sequence: str) -> Dict[str, Any]:
    """
    Analyze physicochemical properties of a protein sequence.
    
    Args:
        sequence: Validated protein sequence
        
    Returns:
        Dict: Physicochemical properties
    """
    # Count hydrophobic and charged amino acids
    hydrophobic_count = sum(1 for aa in sequence if AA_PROPERTIES[aa]['hydrophobic'])
    positive_charge_count = sum(1 for aa in sequence if AA_PROPERTIES[aa]['charge'] > 0)
    negative_charge_count = sum(1 for aa in sequence if AA_PROPERTIES[aa]['charge'] < 0)
    
    # Calculate percentages
    total_length = len(sequence)
    hydrophobic_percent = (hydrophobic_count / total_length) * 100
    
    # Calculate net charge
    net_charge = positive_charge_count - negative_charge_count
    
    # Isoelectric point estimation (simplified)
    isoelectric_point = 7.0 + (0.5 * net_charge)
    
    # Aromaticity (F, Y, W content)
    aromatic_count = sequence.count('F') + sequence.count('Y') + sequence.count('W')
    aromaticity = (aromatic_count / total_length) * 100
    
    return {
        'hydrophobic_percent': round(hydrophobic_percent, 2),
        'positive_charge_count': positive_charge_count,
        'negative_charge_count': negative_charge_count,
        'net_charge': net_charge,
        'estimated_isoelectric_point': round(isoelectric_point, 2),
        'aromaticity': round(aromaticity, 2)
    }


def identify_regions(sequence: str, window_size: int = 7) -> Dict[str, List[Dict[str, Any]]]:
    """
    Identify hydrophobic and charged regions in a protein sequence.
    
    Args:
        sequence: Validated protein sequence
        window_size: Window size for region analysis
        
    Returns:
        Dict: Identified regions
    """
    regions = {
        'hydrophobic_regions': [],
        'charged_regions': []
    }
    
    if len(sequence) < window_size:
        return regions
    
    # Scan for hydrophobic regions
    for i in range(len(sequence) - window_size + 1):
        window = sequence[i:i+window_size]
        
        # Count hydrophobic residues in window
        hydrophobic_count = sum(1 for aa in window if AA_PROPERTIES[aa]['hydrophobic'])
        
        # If >70% of the window is hydrophobic, consider it a hydrophobic region
        if (hydrophobic_count / window_size) > 0.7:
            # Check if this extends an existing region
            if (regions['hydrophobic_regions'] and 
                regions['hydrophobic_regions'][-1]['end'] == i):
                regions['hydrophobic_regions'][-1]['end'] = i + window_size
                regions['hydrophobic_regions'][-1]['sequence'] = sequence[
                    regions['hydrophobic_regions'][-1]['start']:
                    regions['hydrophobic_regions'][-1]['end']
                ]
            else:
                regions['hydrophobic_regions'].append({
                    'start': i,
                    'end': i + window_size,
                    'sequence': window
                })
    
    # Scan for charged regions
    for i in range(len(sequence) - window_size + 1):
        window = sequence[i:i+window_size]
        
        # Count charged residues in window
        charged_count = sum(1 for aa in window if AA_PROPERTIES[aa]['charge'] != 0)
        
        # If >50% of the window is charged, consider it a charged region
        if (charged_count / window_size) > 0.5:
            # Check if this extends an existing region
            if (regions['charged_regions'] and 
                regions['charged_regions'][-1]['end'] == i):
                regions['charged_regions'][-1]['end'] = i + window_size
                regions['charged_regions'][-1]['sequence'] = sequence[
                    regions['charged_regions'][-1]['start']:
                    regions['charged_regions'][-1]['end']
                ]
            else:
                # Calculate the net charge
                net_charge = sum(AA_PROPERTIES[aa]['charge'] for aa in window)
                
                regions['charged_regions'].append({
                    'start': i,
                    'end': i + window_size,
                    'sequence': window,
                    'net_charge': net_charge
                })
    
    return regions


def predict_secondary_structure(sequence: str, method: str = 'simple') -> Dict[str, Any]:
    """
    Predict secondary structure elements (very simplified).
    
    Args:
        sequence: Validated protein sequence
        method: Prediction method ('simple' is currently the only option)
        
    Returns:
        Dict: Secondary structure prediction results
    """
    # This is a very simplified prediction method based on amino acid propensities
    # A real implementation would use more sophisticated algorithms
    
    if method != 'simple':
        raise ValueError(f"Unsupported prediction method: {method}")
    
    # Simple propensities for secondary structures
    helix_propensity = {
        'A': 1.4, 'R': 1.0, 'N': 0.8, 'D': 0.9, 'C': 0.6, 'Q': 1.2, 'E': 1.5, 
        'G': 0.4, 'H': 1.0, 'I': 1.0, 'L': 1.2, 'K': 1.1, 'M': 1.4, 'F': 1.0, 
        'P': 0.5, 'S': 0.7, 'T': 0.8, 'W': 1.1, 'Y': 0.7, 'V': 0.9
    }
    
    sheet_propensity = {
        'A': 0.7, 'R': 0.9, 'N': 0.5, 'D': 0.4, 'C': 1.0, 'Q': 0.8, 'E': 0.6, 
        'G': 0.6, 'H': 0.9, 'I': 1.5, 'L': 1.2, 'K': 0.7, 'M': 1.0, 'F': 1.2, 
        'P': 0.4, 'S': 0.8, 'T': 1.2, 'W': 1.2, 'Y': 1.3, 'V': 1.7
    }
    
    turn_propensity = {
        'A': 0.7, 'R': 1.0, 'N': 1.5, 'D': 1.5, 'C': 0.9, 'Q': 1.0, 'E': 0.7, 
        'G': 1.6, 'H': 1.0, 'I': 0.6, 'L': 0.6, 'K': 1.2, 'M': 0.6, 'F': 0.6, 
        'P': 1.5, 'S': 1.2, 'T': 0.9, 'W': 0.7, 'Y': 1.0, 'V': 0.6
    }
    
    # Calculate propensities
    helix_score = sum(helix_propensity[aa] for aa in sequence) / len(sequence)
    sheet_score = sum(sheet_propensity[aa] for aa in sequence) / len(sequence)
    turn_score = sum(turn_propensity[aa] for aa in sequence) / len(sequence)
    
    # Normalize scores
    total = helix_score + sheet_score + turn_score
    helix_fraction = helix_score / total
    sheet_fraction = sheet_score / total
    turn_fraction = turn_score / total
    
    return {
        'helix_fraction': round(helix_fraction, 2),
        'sheet_fraction': round(sheet_fraction, 2),
        'turn_fraction': round(turn_fraction, 2),
        'prediction_method': method,
        'note': "This is a simplified prediction and should not be used for scientific purposes."
    }


def analyze_sequence(sequence: str) -> Dict[str, Any]:
    """
    Analyze a protein sequence.
    
    Args:
        sequence: Protein sequence string
        
    Returns:
        Dict: Analysis results
        
    Raises:
        ValueError: If sequence is invalid
    """
    try:
        # Validate sequence
        validated_sequence = validate_sequence(sequence)
        
        # Perform analyses
        molecular_weight = calculate_molecular_weight(validated_sequence)
        aa_composition = analyze_amino_acid_composition(validated_sequence)
        physicochemical = analyze_physicochemical_properties(validated_sequence)
        regions = identify_regions(validated_sequence)
        secondary_structure = predict_secondary_structure(validated_sequence)
        
        # Compile results
        results = {
            'sequence_length': len(validated_sequence),
            'molecular_weight': molecular_weight,
            'amino_acid_composition': aa_composition,
            'physicochemical_properties': physicochemical,
            'regions': regions,
            'secondary_structure': secondary_structure
        }
        
        return results
        
    except Exception as e:
        logger.error(f"Error analyzing sequence: {str(e)}")
        raise


if __name__ == "__main__":
    # Example usage
    test_sequence = "MKCPECGKSFSQRANLQRHQRTHTGEK"
    try:
        results = analyze_sequence(test_sequence)
        print(f"Sequence length: {results['sequence_length']}")
        print(f"Molecular weight: {results['molecular_weight']} Da")
        print(f"Hydrophobic content: {results['physicochemical_properties']['hydrophobic_percent']}%")
        print(f"Secondary structure prediction: Helix {results['secondary_structure']['helix_fraction'] * 100:.1f}%")
    except ValueError as e:
        print(f"Error: {e}") 