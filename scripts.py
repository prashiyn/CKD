#!/usr/bin/env python3
"""
CKD Assessment Testing Script

This script generates test scenarios for the Chronic Kidney Disease (CKD) assessment 
system using LLM-generated responses and evaluates the agentic workflow.

Features:
- Generate realistic patient scenarios using LLM
- Support for different response types (text/yes_no_maybe)
- Automated testing of the complete agentic workflow
- Export results as markdown files

Usage:
    python scripts.py --scenario "25 year old with high blood pressure" --response_type yes_no_maybe
    python scripts.py --scenario "45 year old female with diabetes" --output_dir results
"""

import os
import sys
import json
import argparse
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import time
import random

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from crewai.llm import LLM

# Import from main application
from propmpts import (
    questions_list, qna_agent_prompt, research_agent_prompt, 
    diagnostic_agent_prompt, critique_agent_prompt, presentation_agent_prompt
)
from main import (
    get_llm, load_patient_data, search_medical_knowledge
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scripts_testing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CKDTestScenarioGenerator:
    """Generate test scenarios for CKD assessment using LLM"""
    
    def __init__(self, llm_provider="groq", model="llama"):
        self.llm = get_llm(llm_provider, model)
        self.questions = self._parse_questions()
        logger.info(f"Initialized scenario generator with {llm_provider}/{model}")
        logger.info(f"Loaded {len(self.questions)} questions for testing")
    
    def _parse_questions(self) -> List[str]:
        """Parse questions from questions_list"""
        questions = []
        for line in questions_list.strip().split('\n'):
            line = line.strip()
            if line and not line.startswith('"""') and line[0].isdigit():
                # Remove question number and clean up
                question = line.split('.', 1)[1].strip()
                questions.append(question)
        return questions
    
    def generate_responses(self, scenario: str, response_type: str = "text") -> Dict[str, Any]:
        """Generate responses to questions based on patient scenario"""
        logger.info(f"Generating {response_type} responses for scenario: {scenario}")
        
        if response_type == "yes_no_maybe":
            prompt = self._create_structured_prompt(scenario)
        else:
            prompt = self._create_text_prompt(scenario)
        
        try:
            # Generate responses using CrewAI LLM - use call method
            response = self.llm.call(prompt)
            
            # Extract response content
            response_text = str(response)
            logger.info(f"Generated response length: {len(response_text)} characters")
            
            # Parse the response into structured format
            return self._parse_llm_response(response_text, scenario)
            
        except Exception as e:
            logger.error(f"Error generating responses: {str(e)}")
            return self._generate_fallback_responses(scenario, response_type)
    
    def _create_structured_prompt(self, scenario: str) -> str:
        """Create prompt for yes/no/maybe responses"""
        questions_formatted = "\n".join([f"{i+1}. {q}" for i, q in enumerate(self.questions)])
        
        return f"""You are a medical AI assistant generating realistic patient responses.

PATIENT SCENARIO: {scenario}

Answer these questions as the patient would:

{questions_formatted}

Return a JSON array with this format:
[
    {{"question": "What is your gender?", "answer": "male"}},
    {{"question": "What is your current age?", "answer": "25"}}
]

Be realistic and consistent with the scenario."""
    
    def _create_text_prompt(self, scenario: str) -> str:
        """Create prompt for natural text responses"""
        questions_formatted = "\n".join([f"{i+1}. {q}" for i, q in enumerate(self.questions)])
        
        return f"""Roleplay as a patient: {scenario}

Answer these questions naturally:

{questions_formatted}

Return JSON array format:
[
    {{"question": "What is your gender?", "answer": "I am male"}},
    {{"question": "What is your current age?", "answer": "I'm 25 years old"}}
]"""
    
    def _parse_llm_response(self, response_text: str, scenario: str) -> Dict[str, Any]:
        """Parse LLM response into structured format"""
        try:
            # Try to extract JSON from response
            start_idx = response_text.find('[')
            end_idx = response_text.rfind(']') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                responses = json.loads(json_str)
            else:
                responses = json.loads(response_text)
            
            # Convert to QnA format
            qna_responses = []
            for resp in responses:
                qna_responses.append({
                    "question": resp.get("question", ""),
                    "answer": resp.get("answer", "")
                })
            
            result = {
                "scenario": scenario,
                "timestamp": datetime.now().isoformat(),
                "qna_responses": qna_responses,
                "total_questions": len(qna_responses)
            }
            
            logger.info(f"Successfully parsed {len(qna_responses)} responses")
            return result
            
        except Exception as e:
            logger.error(f"Error parsing LLM response: {str(e)}")
            return self._generate_fallback_responses(scenario, "text")
    
    def _generate_fallback_responses(self, scenario: str, response_type: str) -> Dict[str, Any]:
        """Generate fallback responses if LLM fails"""
        logger.warning("Using fallback response generation")
        
        # Extract basic info from scenario
        scenario_lower = scenario.lower()
        
        # Extract age from scenario
        age = "unknown"
        import re
        age_match = re.search(r'(\d+)\s*year', scenario_lower)
        if age_match:
            age = age_match.group(1)
        
        # Extract gender from scenario  
        gender = "unknown"
        if "male" in scenario_lower and "female" not in scenario_lower:
            gender = "male"
        elif "female" in scenario_lower:
            gender = "female"
        
        qna_responses = []
        for i, question in enumerate(self.questions):
            if "age" in question.lower():
                answer = age
            elif "gender" in question.lower():
                answer = gender
            elif any(condition in scenario_lower for condition in ["diabetes", "diabetic"]) and "diabetes" in question.lower():
                answer = "yes"
            elif any(condition in scenario_lower for condition in ["blood pressure", "hypertension"]) and "blood pressure" in question.lower():
                answer = "yes"
            elif any(condition in scenario_lower for condition in ["swelling", "swollen", "edema"]) and ("swelling" in question.lower() or "edema" in question.lower()):
                answer = "yes"
            elif any(condition in scenario_lower for condition in ["fatigue", "tired", "weakness"]) and ("fatigue" in question.lower() or "tired" in question.lower()):
                answer = "yes"
            elif response_type == "yes_no_maybe":
                answer = random.choice(["yes", "no", "maybe"])
            else:
                answer = "I'm not sure"
            
            qna_responses.append({
                "question": question,
                "answer": answer
            })
        
        return {
            "scenario": scenario,
            "timestamp": datetime.now().isoformat(),
            "qna_responses": qna_responses,
            "total_questions": len(qna_responses),
            "fallback_used": True
        }

class CKDAgentWorkflowTester:
    """Test the CKD assessment agentic workflow"""
    
    def __init__(self, llm_provider="groq", model="llama"):
        self.llm = get_llm(llm_provider, model)
        self.provider = llm_provider
        self.model = model
        
        # Configure embeddings to match LLM provider
        if llm_provider == "groq":
            # Use local HuggingFace embeddings (no API calls)
            self.embedder_config = {
                "provider": "huggingface",
                "config": {
                    "model": "sentence-transformers/all-MiniLM-L6-v2",
                    "local": True  # Use local model to avoid API URL issues
                }
            }
        else:  # openai
            self.embedder_config = {
                "provider": "openai",
                "config": {
                    "model": "text-embedding-3-small"
                }
            }
        
        logger.info(f"Initialized workflow tester with {llm_provider}/{model}")
        logger.info(f"Using embedder: {self.embedder_config['provider']}")
    
    def run_assessment(self, qna_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run the complete CKD assessment workflow"""
        start_time = time.time()
        logger.info(f"Starting assessment for scenario: {qna_data['scenario']}")
        
        try:
            # Prepare collected answers
            collected_answers_json = json.dumps(qna_data['qna_responses'], indent=2)
            
            # Create agents and tasks
            agents = self._create_agents(collected_answers_json)
            tasks = self._create_tasks(*agents, collected_answers_json)
            
            # Create and run crew with matching embedder
            crew = Crew(
                agents=agents,
                tasks=tasks,
                verbose=False,
                process=Process.sequential,
                memory=False if self.provider == "groq" else True,  # Disable memory for Groq to avoid embedding issues
                embedder=self.embedder_config if self.provider != "groq" else None  # Only use embedder for OpenAI
            )
            
            logger.info("Running CrewAI workflow...")
            result = crew.kickoff()
            
            # Extract result content
            if hasattr(result, 'raw'):
                result_content = str(result.raw)
            else:
                result_content = str(result)
            
            duration = time.time() - start_time
            
            assessment_result = {
                "scenario": qna_data['scenario'],
                "timestamp": datetime.now().isoformat(),
                "qna_responses": qna_data['qna_responses'],
                "assessment_result": result_content,
                "processing_time_seconds": round(duration, 2),
                "agent_config": {
                    "llm_provider": self.provider,
                    "llm_model": self.model,
                    "total_agents": len(agents),
                    "total_tasks": len(tasks)
                }
            }
            
            logger.info(f"Assessment completed in {duration:.2f} seconds")
            return assessment_result
            
        except Exception as e:
            logger.error(f"Error in assessment workflow: {str(e)}")
            return {
                "scenario": qna_data['scenario'],
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "processing_time_seconds": time.time() - start_time
            }
    
    def _create_agents(self, collected_patient_data: str):
        """Create agents for workflow"""
        # Load patient data
        past_patient_qna, present_patient_qna = load_patient_data()
        
        # Create agents
        qna_agent = Agent(
            role="QnA Agent",
            goal="Process and validate collected patient questionnaire responses",
            backstory=qna_agent_prompt.format(questions_list=questions_list),
            verbose=False,
            llm=self.llm
        )
        
        research_agent = Agent(
            role="Research Agent",
            goal="Research CKD and assess risk percentage based on patient responses",
            backstory=research_agent_prompt.format(
                past_patient_qna=past_patient_qna, 
                present_patient_qna=present_patient_qna,
                current_patient_responses=collected_patient_data
            ),
            verbose=False,
            llm=self.llm,
            tools=[search_medical_knowledge]
        )
        
        diagnostic_agent = Agent(
            role="Diagnostic Agent",
            goal="Analyze patient data to predict CKD and assess severity",
            backstory=diagnostic_agent_prompt,
            verbose=False,
            llm=self.llm
        )
        
        critique_agent = Agent(
            role="Critique Agent",
            goal="Ensure accuracy of CKD risk assessment",
            backstory=critique_agent_prompt,
            verbose=False,
            llm=self.llm
        )
        
        presentation_agent = Agent(
            role="Presentation Agent",
            goal="Present clear, user-friendly CKD assessment",
            backstory=presentation_agent_prompt,
            verbose=False,
            llm=self.llm
        )
        
        return qna_agent, research_agent, diagnostic_agent, critique_agent, presentation_agent
    
    def _create_tasks(self, qna_agent, research_agent, diagnostic_agent, critique_agent, presentation_agent, collected_patient_data):
        """Create tasks for workflow"""
        
        collect_info_task = Task(
            description=f"Process and validate patient responses: {collected_patient_data}",
            agent=qna_agent,
            expected_output="Structured patient questionnaire responses"
        )
        
        diagnostic_task = Task(
            description="Analyze patient responses for kidney issues",
            agent=diagnostic_agent,
            dependencies=[collect_info_task],
            expected_output="Diagnostic analysis of patient data"
        )
        
        research_task = Task(
            description="Conduct comprehensive CKD risk assessment with factor analysis",
            agent=research_agent,
            dependencies=[collect_info_task, diagnostic_task],
            expected_output="CKD risk assessment with detailed factors"
        )
        
        critique_task = Task(
            description="Review CKD risk assessment for accuracy",
            agent=critique_agent,
            dependencies=[research_task],
            expected_output="Verified CKD assessment"
        )
        
        presentation_task = Task(
            description="Create patient-friendly CKD assessment report",
            agent=presentation_agent,
            dependencies=[critique_task],
            expected_output="User-friendly CKD assessment report"
        )
        
        return [collect_info_task, diagnostic_task, research_task, critique_task, presentation_task]

class ResultsExporter:
    """Export testing results to markdown files"""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        logger.info(f"Results will be exported to: {self.output_dir.absolute()}")
    
    def export_assessment(self, assessment_result: Dict[str, Any]) -> str:
        """Export single assessment result to markdown"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        scenario_clean = self._clean_filename(assessment_result['scenario'])
        sim_num = assessment_result.get('simulation_number', 1)
        filename = f"ckd_assessment_{scenario_clean}_sim{sim_num:03d}_{timestamp}.md"
        filepath = self.output_dir / filename
        
        markdown_content = self._generate_markdown(assessment_result)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        logger.info(f"Exported assessment to: {filepath}")
        return str(filepath)
    
    def _clean_filename(self, text: str) -> str:
        """Clean text for use in filename"""
        import re
        clean = re.sub(r'[^\w\s-]', '', text)
        clean = re.sub(r'[-\s]+', '_', clean)
        return clean[:50].strip('_')
    
    def _generate_markdown(self, assessment_result: Dict[str, Any]) -> str:
        """Generate markdown content for single assessment"""
        if 'error' in assessment_result:
            return f"""# CKD Assessment Report - ERROR

## Test Scenario
**Patient Description:** {assessment_result['scenario']}
**Assessment Date:** {assessment_result['timestamp']}
**Simulation Number:** {assessment_result.get('simulation_number', 1)}

## Error Details
```
{assessment_result['error']}
```
"""
        
        return f"""# CKD Assessment Report

## Test Scenario
**Patient Description:** {assessment_result['scenario']}
**Assessment Date:** {assessment_result['timestamp']}
**Simulation Number:** {assessment_result.get('simulation_number', 1)}
**Processing Time:** {assessment_result['processing_time_seconds']} seconds

## Configuration
- **LLM Provider:** {assessment_result['agent_config']['llm_provider']}
- **LLM Model:** {assessment_result['agent_config']['llm_model']}
- **Total Agents:** {assessment_result['agent_config']['total_agents']}

## Patient Responses Summary

| Question | Patient Response |
|----------|------------------|
{self._format_qna_table(assessment_result['qna_responses'])}

## Assessment Results

{assessment_result['assessment_result']}

---
*Report generated by CKD Assessment Testing Script*
"""
    
    def _format_qna_table(self, qna_responses: List[Dict[str, Any]]) -> str:
        """Format QnA responses as markdown table"""
        rows = []
        for resp in qna_responses:
            question = resp['question'][:60] + "..." if len(resp['question']) > 60 else resp['question']
            answer = resp['answer'][:40] + "..." if len(resp['answer']) > 40 else resp['answer']
            rows.append(f"| {question} | {answer} |")
        return "\n".join(rows)

class SimulationResultsAggregator:
    """Aggregate results from multiple simulations into CSV reports"""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        logger.info(f"Consolidated reports will be exported to: {self.output_dir.absolute()}")
    
    def aggregate_results(self, assessment_results: List[Dict[str, Any]], scenario: str) -> Dict[str, str]:
        """Aggregate results from multiple simulations into CSV files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        scenario_clean = self._clean_filename(scenario)
        base_filename = f"consolidated_{scenario_clean}_{timestamp}"
        
        # Generate CSV files
        responses_csv = self._generate_responses_csv(assessment_results, base_filename)
        risk_factors_csv = self._generate_risk_factors_csv(assessment_results, base_filename)
        risk_scores_csv = self._generate_risk_scores_csv(assessment_results, base_filename)
        
        return {
            "responses": responses_csv,
            "risk_factors": risk_factors_csv,
            "risk_scores": risk_scores_csv
        }
    
    def _clean_filename(self, text: str) -> str:
        """Clean text for use in filename"""
        import re
        clean = re.sub(r'[^\w\s-]', '', text)
        clean = re.sub(r'[-\s]+', '_', clean)
        return clean[:50].strip('_')
    
    def _generate_responses_csv(self, assessment_results: List[Dict[str, Any]], base_filename: str) -> str:
        """Generate CSV of question responses across simulations"""
        import csv
        
        # Get all unique questions
        all_questions = set()
        for result in assessment_results:
            for qna in result['qna_responses']:
                all_questions.add(qna['question'])
        
        # Create CSV with simulation number and responses
        filename = f"{base_filename}_responses.csv"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            header = ['simulation_number', 'question_number', 'question', 'response']
            writer.writerow(header)
            
            # Write data
            for result in assessment_results:
                sim_num = result['simulation_number']
                for i, qna in enumerate(result['qna_responses'], 1):
                    writer.writerow([sim_num, i, qna['question'], qna['answer']])
        
        return str(filepath)
    
    def _generate_risk_factors_csv(self, assessment_results: List[Dict[str, Any]], base_filename: str) -> str:
        """Generate CSV of risk factors across simulations"""
        import csv
        import re
        
        filename = f"{base_filename}_risk_factors.csv"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            header = ['simulation_number', 'risk_factor', 'percentage']
            writer.writerow(header)
            
            # Write data
            for result in assessment_results:
                sim_num = result['simulation_number']
                content = result['assessment_result']
                
                # Extract risk factors using regex
                risk_pattern = r"(\d+)%\s*-\s*([^:]+):"
                risk_factors = re.findall(risk_pattern, content)
                
                for percentage, factor in risk_factors:
                    writer.writerow([sim_num, factor.strip(), percentage])
        
        return str(filepath)
    
    def _generate_risk_scores_csv(self, assessment_results: List[Dict[str, Any]], base_filename: str) -> str:
        """Generate CSV of final risk scores across simulations"""
        import csv
        import re
        
        filename = f"{base_filename}_risk_scores.csv"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            header = ['simulation_number', 'risk_score', 'confidence_percentage']
            writer.writerow(header)
            
            # Write data
            for result in assessment_results:
                sim_num = result['simulation_number']
                content = result['assessment_result']
                
                # Extract risk score and confidence
                risk_score_match = re.search(r"(\d+)%", content)
                confidence_match = re.search(r"(\d+)% confidence", content)
                
                risk_score = risk_score_match.group(1) if risk_score_match else "N/A"
                confidence = confidence_match.group(1) if confidence_match else "N/A"
                
                writer.writerow([sim_num, risk_score, confidence])
        
        return str(filepath)

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="CKD Assessment Testing Script")
    
    parser.add_argument('--scenario', type=str, help='Patient scenario description')
    parser.add_argument('--response_type', choices=['text', 'yes_no_maybe'], 
                       default='yes_no_maybe', help='Type of responses to generate')
    parser.add_argument('--llm_provider', choices=['groq', 'openai'], 
                       default='groq', help='LLM provider to use')
    parser.add_argument('--model', choices=['llama', 'deepseek', 'mistral'], 
                       default='llama', help='Groq model to use')
    parser.add_argument('--output_dir', type=str, default='output', 
                       help='Directory to save results')
    parser.add_argument('--num_simulations', type=int, default=1,
                       help='Number of simulations to run with different responses')
    parser.add_argument('--analyze', action='store_true',
                       help='Run analysis after generating results')
    
    return parser.parse_args()

def main():
    """Main execution function"""
    args = parse_args()
    
    logger.info("Starting CKD Assessment Testing Script")
    
    # Use default scenario if none provided
    if not args.scenario:
        args.scenario = "25 year old male with high blood pressure and occasional chest pain"
        logger.info(f"Using default scenario: {args.scenario}")
    
    try:
        # Initialize components
        generator = CKDTestScenarioGenerator(args.llm_provider, args.model)
        tester = CKDAgentWorkflowTester(args.llm_provider, args.model)
        exporter = ResultsExporter(args.output_dir)
        aggregator = SimulationResultsAggregator(args.output_dir)
        
        # Store all assessment results
        all_assessment_results = []
        
        # Run multiple simulations
        for sim_num in range(args.num_simulations):
            logger.info(f"Running simulation {sim_num + 1}/{args.num_simulations}")
            
            # Generate responses
            logger.info("Generating patient responses...")
            qna_data = generator.generate_responses(args.scenario, args.response_type)
            
            # Run assessment
            logger.info("Running CKD assessment...")
            assessment_result = tester.run_assessment(qna_data)
            
            # Add simulation number to result
            assessment_result['simulation_number'] = sim_num + 1
            
            # Export individual results
            logger.info("Exporting results...")
            output_file = exporter.export_assessment(assessment_result)
            
            # Store result for aggregation
            all_assessment_results.append(assessment_result)
            
            logger.info(f"Simulation {sim_num + 1} completed. Results saved to: {output_file}")
        
        # Generate consolidated reports
        if args.num_simulations > 1:
            logger.info("Generating consolidated reports...")
            csv_files = aggregator.aggregate_results(all_assessment_results, args.scenario)
            logger.info(f"Consolidated reports generated: {csv_files}")
            
            # Run analysis if requested
            if args.analyze:
                logger.info("Running analysis on consolidated results...")
                from analyze import SimulationAnalyzer
                analyzer = SimulationAnalyzer(args.output_dir)
                analysis = analyzer.analyze_results(analyzer.combine_data(analyzer.load_data(csv_files)))
                analyzer.export_analysis(analysis, args.scenario)
                logger.info("Analysis completed and exported")
        
        logger.info(f"All {args.num_simulations} simulations completed successfully!")
        return 0
        
    except Exception as e:
        logger.error(f"Testing failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main()) 