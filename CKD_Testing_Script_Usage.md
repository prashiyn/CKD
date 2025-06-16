# CKD Assessment Testing Script - Usage Guide

## Overview

The `scripts.py` file is a comprehensive testing tool for the Chronic Kidney Disease (CKD) assessment system. It automates the process of generating patient scenarios, running them through the agentic workflow, and exporting detailed reports.

## Features

- **Automated Scenario Generation**: Uses LLM to generate realistic patient responses based on input scenarios
- **Multiple Response Types**: Supports both natural text responses and structured yes/no/maybe answers  
- **Complete Workflow Testing**: Runs the full 5-agent assessment pipeline (QnA → Research → Diagnostic → Critique → Presentation)
- **Markdown Export**: Automatically exports results as formatted markdown reports
- **Configurable LLM Providers**: Supports both Groq and OpenAI models
- **Comprehensive Logging**: Detailed logging for debugging and monitoring

## Installation & Setup

### Prerequisites

Ensure you have all dependencies installed:
```bash
pip install -r requirements.txt
```

### Environment Variables

Make sure your `.env` file contains the necessary API keys:
```env
GROQ_API_KEY=your_groq_api_key_here
OPENAI_API_KEY=your_openai_api_key_here  # if using OpenAI
```

### Directory Structure

The script expects this structure:
```
ckd/
├── scripts.py
├── main.py
├── propmpts.py
├── data/
│   ├── past_patient_responses.json
│   ├── present_patient_responses.json
│   └── *.pdf, *.txt (medical documents)
└── output/ (created automatically)
```

## Usage

### Basic Usage

**Simple scenario testing:**
```bash
python scripts.py --scenario "25 year old male with high blood pressure"
```

**With specific response type:**
```bash
python scripts.py --scenario "45 year old female with diabetes" --response_type text
```

**Using OpenAI instead of Groq:**
```bash
python scripts.py --scenario "60 year old with kidney problems" --llm_provider openai
```

**Custom output directory:**
```bash
python scripts.py --scenario "30 year old with chest pain" --output_dir "test_results"
```
For number of simulations add --num_simulations 10

### Command Line Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--scenario` | string | Auto-generated | Patient description for testing |
| `--response_type` | choice | `yes_no_maybe` | Type of responses (`text` or `yes_no_maybe`) |
| `--llm_provider` | choice | `groq` | LLM provider (`groq` or `openai`) |
| `--model` | choice | `llama` | Groq model (`llama`, `deepseek`, `mistral`) |
| `--output_dir` | string | `output` | Directory to save results |
| `--num_simulations` | integer | `1` | Number of simulations to run |
| `--analyze` | flag | `False` | Run analysis on consolidated results |

### Response Types

**1. `yes_no_maybe` (Structured):**
- Generates standardized yes/no/maybe responses
- Better for consistent testing and comparison
- Faster processing
- Example: "Do you have high blood pressure?" → "yes"

**2. `text` (Natural):**
- Generates conversational, human-like responses
- More realistic patient interactions
- Provides richer context
- Example: "Do you have high blood pressure?" → "Yes, I've been on medication for it for about 2 years"

## Example Scenarios

### Medical Conditions
```bash
# Diabetes patient
python scripts.py --scenario "45 year old female with type 2 diabetes and occasional swelling in feet"

# Hypertension patient  
python scripts.py --scenario "55 year old male with high blood pressure and family history of kidney disease"

# Multiple conditions
python scripts.py --scenario "65 year old with diabetes, hypertension, and recent weight loss"
```

### Age-Based Testing
```bash
# Young adult
python scripts.py --scenario "22 year old college student with recent fatigue and decreased appetite"

# Middle-aged
python scripts.py --scenario "40 year old office worker with stress and irregular eating habits"

# Elderly
python scripts.py --scenario "70 year old retiree with multiple medications and mobility issues"
```

### Symptom-Focused Testing
```bash
# Kidney-specific symptoms
python scripts.py --scenario "35 year old with blood in urine and flank pain"

# Systemic symptoms
python scripts.py --scenario "50 year old with persistent fatigue, nausea, and metallic taste"

# Early-stage symptoms
python scripts.py --scenario "30 year old with mild swelling and occasional night urination"
```

## Output Files

### Individual Assessment Reports

Each test generates a markdown file with this structure:

**Filename Format:** `ckd_assessment_{scenario}_{timestamp}.md`

**Content Sections:**
1. **Test Scenario** - Input description and metadata
2. **Configuration** - LLM settings and agent counts
3. **Patient Responses Summary** - QnA table with all questions and answers
4. **Assessment Results** - Complete output from the presentation agent

### Consolidated Analysis Reports

When running multiple simulations with `--analyze`, the script generates three CSV files:

**Filename Format:** `analysis_{scenario}_{timestamp}_{type}.csv`

**File Types:**
1. **Risk Score Statistics** (`*_risk_score_stats.csv`)
   - Mean, standard deviation, min, max, median of risk scores
   - Confidence level statistics

2. **Risk Factor Analysis** (`*_risk_factor_stats.csv`)
   - Distribution of risk factors across simulations
   - Percentage breakdown of contributing factors

3. **Response Analysis** (`*_response_stats.csv`)
   - Statistical analysis of patient responses
   - Response patterns and correlations

**Sample Usage:**
```bash
# Run 5 simulations with analysis
python scripts.py --scenario "60 year old female" --num_simulations 5 --analyze
```

**Output Structure:**
```
output/
├── ckd_assessment_*.md           # Individual reports
├── consolidated_*.csv           # Raw simulation data
└── analysis_*.csv               # Analysis results
```

## Testing Workflow

The script follows this automated workflow:

1. **Scenario Input** → Patient description provided
2. **Question Parsing** → Extracts questions from `propmpts.py`
3. **Response Generation** → LLM generates patient answers
4. **Agent Pipeline** → Runs 5-agent assessment workflow
5. **Export** → Saves markdown report to output directory
6. **Analysis** → (if `--analyze`) Generates statistical analysis of results

## Error Handling

### Common Issues & Solutions

**1. Missing API Keys**
```
Error: LLM provider authentication failed
Solution: Check .env file has correct API keys
```

**2. Import Errors**
```
Error: No module named 'propmpts'
Solution: Run from correct directory, ensure files exist
```

**3. JSON Parsing Errors**
```
Warning: Using fallback response generation
Solution: LLM response was malformed, fallback responses used automatically
```

**4. Assessment Workflow Errors**
```
Error in assessment workflow: [specific error]
Solution: Check data files exist, vector store is initialized
```

### Error Output Files

Failed assessments still generate reports with error details:
```markdown
# CKD Assessment Report - ERROR

## Test Scenario
**Patient Description:** [scenario]
**Assessment Date:** [timestamp]

## Error Details
```
[error message and stack trace]
```
```

## Advanced Usage

### Custom Scenarios for Specific Testing

**Risk Level Testing:**
```bash
# Low risk
python scripts.py --scenario "20 year old healthy athlete with no symptoms"

# Medium risk  
python scripts.py --scenario "45 year old with borderline blood pressure and family history"

# High risk
python scripts.py --scenario "65 year old diabetic with kidney symptoms and hypertension"
```

**Edge Case Testing:**
```bash
# Unclear symptoms
python scripts.py --scenario "patient with vague fatigue and occasional nausea"

# Multiple comorbidities
python scripts.py --scenario "complex patient with diabetes, heart disease, and kidney stones"

# Young person with serious symptoms
python scripts.py --scenario "25 year old with severe symptoms suggesting advanced kidney disease"
```

### Multiple Simulations with Analysis

**Basic Analysis:**
```bash
# Run 10 simulations with analysis
python scripts.py --scenario "45 year old diabetic" --num_simulations 10 --analyze
```

**Custom Output Directory:**
```bash
# Run analysis in custom directory
python scripts.py --scenario "60 year old with hypertension" --num_simulations 5 --analyze --output_dir "analysis_results"
```

**Integration with CI/CD:**
```bash
#!/bin/bash
# test_scenarios.sh

scenarios=(
    "25 year old with hypertension"
    "45 year old diabetic female"
    "65 year old with multiple conditions"
)

for scenario in "${scenarios[@]}"; do
    python scripts.py --scenario "$scenario" --num_simulations 5 --analyze --output_dir "ci_results"
    if [ $? -ne 0 ]; then
        echo "Test failed for: $scenario"
        exit 1
    fi
done

echo "All tests completed with analysis!"
```

## Performance Considerations

- **Processing Time**: Each assessment takes 30-60 seconds depending on LLM provider
- **Analysis Time**: Additional 5-10 seconds per simulation batch
- **API Costs**: Consider rate limits and costs when running multiple tests
- **Memory Usage**: Vector store initialization requires ~500MB RAM
- **File Storage**: Each report is typically 5-20KB, analysis files ~1-5KB

## Troubleshooting

### Debug Mode
Add debug logging by modifying the script:
```python
logging.basicConfig(level=logging.DEBUG)
```

### Manual Verification
Compare generated responses with expected medical logic:
1. Check patient responses make sense for the scenario
2. Verify risk assessment aligns with medical guidelines
3. Ensure presentation format is consistent

### Performance Optimization
- Use Groq for faster processing
- Run tests during off-peak hours for better API response times
- Use `yes_no_maybe` response type for faster generation

## Contributing

When adding new test scenarios or modifying the script:

1. Test with multiple response types
2. Verify output format consistency  
3. Check error handling works properly
4. Update documentation for new features

## Support

For issues or questions:
1. Check the logs in `scripts_testing.log`
2. Verify all dependencies are installed
3. Ensure API keys are valid and have sufficient credits
4. Review this documentation for common solutions 

## Scenario Testing Script Usage

The `scenario_testing.py` script extends the testing capabilities by running multiple simulations across predefined scenarios from a CSV file. This is particularly useful for systematic testing of different patient profiles and risk levels.

### Features

- **CSV-based Scenario Management**: Loads test scenarios from a structured CSV file
- **Multiple Simulations per Scenario**: Runs configurable number of simulations while maintaining core parameters
- **Scenario-specific Output Organization**: Creates separate directories for each scenario's results
- **Comprehensive Analysis**: Generates consolidated reports and statistical analysis for each scenario
- **Metadata-rich Outputs**: Includes scenario parameters in all analysis files

### Directory Structure

The script expects this structure:
```
ckd/
├── scenario_testing.py
├── scripts.py
├── scenarios/
│   └── ckd_scenarios.csv
└── output/
    └── scenarios/
        ├── scenario_1/
        │   ├── ckd_assessment_*.md
        │   ├── consolidated_*.csv
        │   └── analysis_*.csv
        ├── scenario_2/
        │   └── ...
        └── ...
```

### CSV Scenario Format

The scenarios CSV file should have these columns:
- `bucket`: Risk category (e.g., "low", "medium", "high")
- `risk_level`: Numeric risk level
- `age`: Patient age
- `gender`: Patient gender
- `t1d`: Type 1 diabetes (boolean)
- `t2d`: Type 2 diabetes (boolean)
- `hypertension`: Hypertension status (boolean)
- `cardiovascular`: Cardiovascular condition (boolean)
- `fatigue`: Fatigue symptoms (boolean)
- `pedal_edema`: Pedal edema symptoms (boolean)
- `scenario_desc`: Detailed scenario description

### Usage

**Basic Usage:**
```bash
python scenario_testing.py --llm_provider groq --model llama --num_simulations 5
```

**Using OpenAI:**
```bash
python scenario_testing.py --llm_provider openai --num_simulations 3
```

**Custom Scenarios File:**
```bash
python scenario_testing.py --scenarios_file "custom_scenarios.csv" --num_simulations 5
```

**Custom Output Directory:**
```bash
python scenario_testing.py --output_dir "test_results/scenarios" --num_simulations 5
```

### Command Line Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--llm_provider` | choice | `groq` | LLM provider (`groq` or `openai`) |
| `--model` | choice | `llama` | Groq model (`llama`, `deepseek`, `mistral`) |
| `--num_simulations` | integer | `5` | Number of simulations per scenario |
| `--output_dir` | string | `output/scenarios` | Directory to save results |
| `--scenarios_file` | string | `scenarios/ckd_scenarios.csv` | Path to scenarios CSV file |

### Output Files

For each scenario, the script generates:

1. **Individual Assessment Reports**
   - Filename: `ckd_assessment_{scenario}_{timestamp}.md`
   - Location: `output/scenarios/scenario_{N}/`
   - Contains: Complete assessment results for each simulation

2. **Consolidated CSV Files**
   - Base filename: `consolidated_{scenario}_{timestamp}_{type}.csv`
   - Types:
     - `*_responses.csv`: All QnA responses with scenario metadata
     - `*_risk_factors.csv`: Risk factor analysis with percentages
     - `*_risk_scores.csv`: Risk scores and confidence levels

3. **Analysis Reports**
   - Generated in each scenario directory
   - Includes statistical analysis of all simulations
   - Contains scenario-specific insights and trends

### Performance Considerations

- **Processing Time**: 
  - Each scenario: 2-3 minutes (5 simulations)
  - Analysis: Additional 5-10 seconds per scenario
- **Storage**: 
  - Each scenario directory: ~100-200KB
  - Total size depends on number of scenarios and simulations
- **Memory Usage**: 
  - Similar to scripts.py
  - Additional memory for scenario data management

### Error Handling

The script includes comprehensive error handling:
- Validates CSV format and required columns
- Creates output directories if they don't exist
- Logs all operations to `scenario_testing.log`
- Continues processing remaining scenarios if one fails

### Example Integration

```bash
#!/bin/bash
# run_scenario_tests.sh

# Run tests with different configurations
python scenario_testing.py --llm_provider groq --model llama --num_simulations 1
python scenario_testing.py --llm_provider openai --num_simulations 3

# Check for errors
if [ $? -ne 0 ]; then
    echo "Scenario testing failed"
    exit 1
fi

echo "All scenario tests completed successfully!"
``` 