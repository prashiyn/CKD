#!/usr/bin/env python3
"""
CKD Simulation Analysis Module

This module provides functions to load, combine, and analyze results from multiple
CKD assessment simulations. It uses pandas for data manipulation and analysis.

Features:
- Load individual CSV files into pandas DataFrames
- Combine multiple CSVs into a single analysis table
- Basic statistical analysis of simulation results
- Extensible structure for adding more analysis functions

Usage:
    python analyze.py --input_dir output --scenario "60 year old female with high blood pressure"
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import pandas as pd
import numpy as np
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SimulationAnalyzer:
    """Analyze results from multiple CKD assessment simulations"""
    
    def __init__(self, input_dir: str = "output"):
        self.input_dir = Path(input_dir)
        logger.info(f"Initialized analyzer with input directory: {self.input_dir.absolute()}")
    
    def find_simulation_files(self, scenario: str) -> Dict[str, Path]:
        """Find CSV files for a given scenario"""
        scenario_clean = self._clean_filename(scenario)
        files = {}
        
        for file in self.input_dir.glob(f"consolidated_{scenario_clean}_*"):
            if file.suffix == '.csv':
                if 'responses' in file.name:
                    files['responses'] = file
                elif 'risk_factors' in file.name:
                    files['risk_factors'] = file
                elif 'risk_scores' in file.name:
                    files['risk_scores'] = file
        
        if not files:
            raise FileNotFoundError(f"No simulation files found for scenario: {scenario}")
        
        return files
    
    def load_data(self, files: Dict[str, Path]) -> Dict[str, pd.DataFrame]:
        """Load CSV files into pandas DataFrames"""
        data = {}
        
        for key, file in files.items():
            logger.info(f"Loading {key} data from: {file}")
            data[key] = pd.read_csv(file)
        
        return data
    
    def combine_data(self, data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Combine multiple DataFrames into a single analysis table"""
        # Start with risk scores as base
        combined = data['risk_scores'].copy()
        
        # Add risk factors
        risk_factors = data['risk_factors'].pivot(
            index='simulation_number',
            columns='risk_factor',
            values='percentage'
        ).reset_index()
        combined = combined.merge(risk_factors, on='simulation_number', how='left')
        
        # Add responses
        responses = data['responses'].pivot(
            index='simulation_number',
            columns='question',
            values='response'
        ).reset_index()
        combined = combined.merge(responses, on='simulation_number', how='left')
        
        return combined
    
    def analyze_results(self, combined_data: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Perform basic analysis on combined data"""
        analysis = {}
        
        # Risk score statistics
        analysis['risk_score_stats'] = pd.DataFrame({
            'metric': ['mean', 'std', 'min', 'max', 'median'],
            'risk_score': [
                combined_data['risk_score'].mean(),
                combined_data['risk_score'].std(),
                combined_data['risk_score'].min(),
                combined_data['risk_score'].max(),
                combined_data['risk_score'].median()
            ],
            'confidence': [
                combined_data['confidence_percentage'].mean(),
                combined_data['confidence_percentage'].std(),
                combined_data['confidence_percentage'].min(),
                combined_data['confidence_percentage'].max(),
                combined_data['confidence_percentage'].median()
            ]
        })
        
        # Risk factor analysis
        risk_factor_cols = [col for col in combined_data.columns 
                          if col not in ['simulation_number', 'risk_score', 'confidence_percentage'] 
                          and not col.startswith('What is your')]
        
        analysis['risk_factor_stats'] = combined_data[risk_factor_cols].describe()
        
        # Response analysis
        response_cols = [col for col in combined_data.columns 
                        if col.startswith('What is your')]
        analysis['response_stats'] = combined_data[response_cols].describe()
        
        return analysis
    
    def export_analysis(self, analysis: Dict[str, pd.DataFrame], scenario: str) -> Dict[str, str]:
        """Export analysis results to CSV files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        scenario_clean = self._clean_filename(scenario)
        base_filename = f"analysis_{scenario_clean}_{timestamp}"
        
        output_files = {}
        for key, df in analysis.items():
            filename = f"{base_filename}_{key}.csv"
            filepath = self.input_dir / filename
            df.to_csv(filepath, index=False)
            output_files[key] = str(filepath)
        
        return output_files
    
    def _clean_filename(self, text: str) -> str:
        """Clean text for use in filename"""
        import re
        clean = re.sub(r'[^\w\s-]', '', text)
        clean = re.sub(r'[-\s]+', '_', clean)
        return clean[:50].strip('_')

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="CKD Simulation Analysis Script")
    
    parser.add_argument('--input_dir', type=str, default='output',
                       help='Directory containing simulation CSV files')
    parser.add_argument('--scenario', type=str, required=True,
                       help='Scenario to analyze (must match simulation files)')
    
    return parser.parse_args()

def main():
    """Main execution function"""
    args = parse_args()
    
    try:
        # Initialize analyzer
        analyzer = SimulationAnalyzer(args.input_dir)
        
        # Find and load simulation files
        files = analyzer.find_simulation_files(args.scenario)
        data = analyzer.load_data(files)
        
        # Combine data
        combined_data = analyzer.combine_data(data)
        
        # Analyze results
        analysis = analyzer.analyze_results(combined_data)
        
        # Export analysis
        output_files = analyzer.export_analysis(analysis, args.scenario)
        
        logger.info("Analysis completed successfully!")
        logger.info(f"Analysis files generated: {output_files}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main()) 