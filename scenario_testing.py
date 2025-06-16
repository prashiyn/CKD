#!/usr/bin/env python3
"""
CKD Scenario Testing Script

This script runs multiple simulations for each scenario defined in ckd_scenarios.csv.
Each simulation maintains core scenario parameters while varying other responses.

Usage:
    python scenario_testing.py --llm_provider groq --model llama --num_simulations 5
"""

import os
import sys
import json
import argparse
import logging
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Tuple
import time

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from scripts import (
    CKDTestScenarioGenerator, CKDAgentWorkflowTester,
    ResultsExporter, SimulationResultsAggregator
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scenario_testing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ScenarioManager:
    """Manages loading and processing of scenarios from CSV"""
    
    def __init__(self, scenarios_file: str = "scenarios/ckd_scenarios.csv"):
        self.scenarios_file = Path(scenarios_file)
        self.scenarios_df = self._load_scenarios()
        logger.info(f"Loaded {len(self.scenarios_df)} scenarios from {scenarios_file}")
    
    def _load_scenarios(self) -> pd.DataFrame:
        """Load scenarios from CSV file"""
        if not self.scenarios_file.exists():
            raise FileNotFoundError(f"Scenarios file not found: {self.scenarios_file}")
        
        return pd.read_csv(self.scenarios_file)
    
    def get_scenario_params(self, row: pd.Series) -> Dict[str, Any]:
        """Extract core parameters from scenario row"""
        return {
            "bucket": row["bucket"],
            "risk_level": row["risk_level"],
            "age": row["age"],
            "gender": row["gender"],
            "t1d": row["t1d"],
            "t2d": row["t2d"],
            "hypertension": row["hypertension"],
            "cardiovascular": row["cardiovascular"],
            "fatigue": row["fatigue"],
            "pedal_edema": row["pedal_edema"],
            "scenario_desc": row["scenario_desc"]
        }

class ScenarioResultsAggregator(SimulationResultsAggregator):
    """Extends SimulationResultsAggregator to include scenario metadata"""
    
    def aggregate_results(self, assessment_results: List[Dict[str, Any]], scenario_params: Dict[str, Any]) -> Dict[str, str]:
        """Aggregate results with scenario metadata"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        scenario_clean = self._clean_filename(scenario_params["scenario_desc"])
        base_filename = f"consolidated_{scenario_clean}_{timestamp}"
        
        # Generate CSV files with scenario metadata
        responses_csv = self._generate_responses_csv(assessment_results, base_filename, scenario_params)
        risk_factors_csv = self._generate_risk_factors_csv(assessment_results, base_filename, scenario_params)
        risk_scores_csv = self._generate_risk_scores_csv(assessment_results, base_filename, scenario_params)
        
        return {
            "responses": responses_csv,
            "risk_factors": risk_factors_csv,
            "risk_scores": risk_scores_csv
        }
    
    def _generate_responses_csv(self, assessment_results: List[Dict[str, Any]], base_filename: str, scenario_params: Dict[str, Any]) -> str:
        """Generate CSV of question responses with scenario metadata"""
        import csv
        
        filename = f"{base_filename}_responses.csv"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header with scenario metadata
            header = [
                'bucket', 'risk_level', 'scenario_desc',
                'simulation_number', 'question_number', 'question', 'response'
            ]
            writer.writerow(header)
            
            # Write data
            for result in assessment_results:
                sim_num = result['simulation_number']
                for i, qna in enumerate(result['qna_responses'], 1):
                    writer.writerow([
                        scenario_params["bucket"],
                        scenario_params["risk_level"],
                        scenario_params["scenario_desc"],
                        sim_num, i, qna['question'], qna['answer']
                    ])
        
        return str(filepath)
    
    def _generate_risk_factors_csv(self, assessment_results: List[Dict[str, Any]], base_filename: str, scenario_params: Dict[str, Any]) -> str:
        """Generate CSV of risk factors with scenario metadata"""
        import csv
        import re
        
        filename = f"{base_filename}_risk_factors.csv"
        filepath = self.output_dir / filename
        
        # Track unique combinations to avoid duplicates
        seen_combinations = set()
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header with scenario metadata
            header = [
                'bucket', 'risk_level', 'scenario_desc',
                'simulation_number', 'risk_factor', 'percentage'
            ]
            writer.writerow(header)
            
            # Write data
            for result in assessment_results:
                sim_num = result['simulation_number']
                content = result['assessment_result']
                
                risk_pattern = r"(\d+)%\s*-\s*([^:]+):"
                risk_factors = re.findall(risk_pattern, content)
                
                for percentage, factor in risk_factors:
                    # Create unique key for this combination
                    key = f"{sim_num}_{factor.strip()}_{percentage}"
                    if key not in seen_combinations:
                        seen_combinations.add(key)
                        writer.writerow([
                            scenario_params["bucket"],
                            scenario_params["risk_level"],
                            scenario_params["scenario_desc"],
                            sim_num, factor.strip(), percentage
                        ])
        
        return str(filepath)
    
    def _generate_risk_scores_csv(self, assessment_results: List[Dict[str, Any]], base_filename: str, scenario_params: Dict[str, Any]) -> str:
        """Generate CSV of risk scores with scenario metadata"""
        import csv
        import re
        
        filename = f"{base_filename}_risk_scores.csv"
        filepath = self.output_dir / filename
        
        # Track unique combinations to avoid duplicates
        seen_combinations = set()
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header with scenario metadata
            header = [
                'bucket', 'risk_level', 'scenario_desc',
                'simulation_number', 'risk_score', 'confidence_percentage'
            ]
            writer.writerow(header)
            
            # Write data
            for result in assessment_results:
                sim_num = result['simulation_number']
                content = result['assessment_result']
                
                risk_score_match = re.search(r"(\d+)%", content)
                confidence_match = re.search(r"(\d+)% confidence", content)
                
                risk_score = risk_score_match.group(1) if risk_score_match else "N/A"
                confidence = confidence_match.group(1) if confidence_match else "N/A"
                
                # Create unique key for this combination
                key = f"{sim_num}_{risk_score}_{confidence}"
                if key not in seen_combinations:
                    seen_combinations.add(key)
                    writer.writerow([
                        scenario_params["bucket"],
                        scenario_params["risk_level"],
                        scenario_params["scenario_desc"],
                        sim_num, risk_score, confidence
                    ])
        
        return str(filepath)

    def _analyze_scenario_results(self, scenario_params: Dict[str, Any], assessment_results: List[Dict[str, Any]]) -> None:
        """Analyze results for a single scenario"""
        try:
            # Generate consolidated CSVs
            base_filename = f"consolidated_{scenario_params['bucket']}_{scenario_params['scenario_desc']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Generate all CSV files
            responses_file = self._generate_responses_csv(assessment_results, base_filename, scenario_params)
            risk_factors_file = self._generate_risk_factors_csv(assessment_results, base_filename, scenario_params)
            risk_scores_file = self._generate_risk_scores_csv(assessment_results, base_filename, scenario_params)
            
            # Load data for analysis
            risk_factors_df = pd.read_csv(risk_factors_file)
            risk_scores_df = pd.read_csv(risk_scores_file)
            
            # Ensure unique entries by dropping duplicates
            risk_factors_df = risk_factors_df.drop_duplicates(subset=['simulation_number', 'risk_factor', 'percentage'])
            risk_scores_df = risk_scores_df.drop_duplicates(subset=['simulation_number', 'risk_score', 'confidence_percentage'])
            
            # Create pivot tables with proper index handling
            risk_factors_pivot = risk_factors_df.pivot_table(
                index='simulation_number',
                columns='risk_factor',
                values='percentage',
                aggfunc='first'  # Use first occurrence if duplicates exist
            ).fillna(0)
            
            risk_scores_pivot = risk_scores_df.pivot_table(
                index='simulation_number',
                columns='risk_score',
                values='confidence_percentage',
                aggfunc='first'  # Use first occurrence if duplicates exist
            ).fillna(0)
            
            # Calculate statistics
            risk_factors_stats = risk_factors_pivot.describe()
            risk_scores_stats = risk_scores_pivot.describe()
            
            # Save analysis results
            analysis_file = self.output_dir / f"analysis_{scenario_params['bucket']}_{scenario_params['scenario_desc']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            with open(analysis_file, 'w', newline='', encoding='utf-8') as f:
                f.write("Risk Factors Analysis\n")
                f.write("===================\n\n")
                f.write(risk_factors_stats.to_string())
                f.write("\n\nRisk Scores Analysis\n")
                f.write("===================\n\n")
                f.write(risk_scores_stats.to_string())
            
            logger.info(f"Analysis saved to {analysis_file}")
            
        except Exception as e:
            logger.error(f"Error analyzing scenario results: {str(e)}")
            raise

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="CKD Scenario Testing Script")
    
    parser.add_argument('--llm_provider', choices=['groq', 'openai'], 
                       default='groq', help='LLM provider to use')
    parser.add_argument('--model', choices=['llama', 'deepseek', 'mistral'], 
                       default='llama', help='Groq model to use')
    parser.add_argument('--num_simulations', type=int, default=5,
                       help='Number of simulations to run per scenario')
    parser.add_argument('--output_dir', type=str, default='output/scenarios',
                       help='Directory to save results')
    parser.add_argument('--scenarios_file', type=str, default='scenarios/ckd_scenarios.csv',
                       help='Path to scenarios CSV file')
    
    return parser.parse_args()

def main():
    """Main execution function"""
    args = parse_args()
    
    logger.info("Starting CKD Scenario Testing Script")
    
    try:
        # Create output directory structure
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        scenario_manager = ScenarioManager(args.scenarios_file)
        generator = CKDTestScenarioGenerator(args.llm_provider, args.model)
        tester = CKDAgentWorkflowTester(args.llm_provider, args.model)
        exporter = ResultsExporter(str(output_dir))
        aggregator = ScenarioResultsAggregator(str(output_dir))
        
        # Process each scenario
        for idx, row in scenario_manager.scenarios_df.iterrows():
            scenario_params = scenario_manager.get_scenario_params(row)
            logger.info(f"Processing scenario {idx + 1}: {scenario_params['scenario_desc']}")
            
            # Create scenario-specific directory
            scenario_dir = output_dir / f"scenario_{idx + 1}"
            scenario_dir.mkdir(exist_ok=True)
            
            # Update exporter and aggregator for this scenario
            exporter.output_dir = scenario_dir
            aggregator.output_dir = scenario_dir
            
            # Store all assessment results for this scenario
            all_assessment_results = []
            
            # Run multiple simulations
            for sim_num in range(args.num_simulations):
                logger.info(f"Running simulation {sim_num + 1}/{args.num_simulations}")
                
                # Generate responses
                logger.info("Generating patient responses...")
                qna_data = generator.generate_responses(scenario_params['scenario_desc'])
                
                # Run assessment
                logger.info("Running CKD assessment...")
                assessment_result = tester.run_assessment(qna_data)
                
                # Add simulation number and scenario metadata
                assessment_result['simulation_number'] = sim_num + 1
                assessment_result.update(scenario_params)
                
                # Export individual results
                logger.info("Exporting results...")
                output_file = exporter.export_assessment(assessment_result)
                
                # Store result for aggregation
                all_assessment_results.append(assessment_result)
                
                logger.info(f"Simulation {sim_num + 1} completed. Results saved to: {output_file}")
            
            # Generate consolidated reports
            logger.info("Generating consolidated reports...")
            csv_files = aggregator.aggregate_results(all_assessment_results, scenario_params)
            logger.info(f"Consolidated reports generated: {csv_files}")
            
            # Run analysis
            logger.info("Running analysis on consolidated results...")
            aggregator._analyze_scenario_results(scenario_params, all_assessment_results)
            logger.info("Analysis completed and exported")
        
        logger.info("All scenarios processed successfully!")
        return 0
        
    except Exception as e:
        logger.error(f"Testing failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main()) 