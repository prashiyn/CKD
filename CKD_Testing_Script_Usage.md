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

### Command Line Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--scenario` | string | Auto-generated | Patient description for testing |
| `--response_type` | choice | `yes_no_maybe` | Type of responses (`text` or `yes_no_maybe`) |
| `--llm_provider` | choice | `groq` | LLM provider (`groq` or `openai`) |
| `--model` | choice | `llama` | Groq model (`llama`, `deepseek`, `mistral`) |
| `--output_dir` | string | `output` | Directory to save results |

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

### Sample Output Structure
```markdown
# CKD Assessment Report

## Test Scenario
**Patient Description:** 25 year old male with high blood pressure
**Assessment Date:** 2024-01-15T10:30:45
**Processing Time:** 45.2 seconds

## Configuration
- **LLM Provider:** groq
- **Total Agents:** 5

## Patient Responses Summary
| Question | Patient Response |
|----------|------------------|
| What is your gender? | male |
| What is your current age? | 25 |
| Do you have high blood pressure? | yes |
...

## Assessment Results
[Complete formatted assessment from presentation agent]
```

## Testing Workflow

The script follows this automated workflow:

1. **Scenario Input** → Patient description provided
2. **Question Parsing** → Extracts questions from `propmpts.py`
3. **Response Generation** → LLM generates patient answers
4. **Agent Pipeline** → Runs 5-agent assessment workflow:
   - QnA Agent: Validates responses
   - Diagnostic Agent: Analyzes symptoms
   - Research Agent: Calculates risk factors
   - Critique Agent: Reviews assessment
   - Presentation Agent: Creates final report
5. **Export** → Saves markdown report to output directory

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

### Integration with CI/CD

The script can be integrated into automated testing pipelines:

```bash
#!/bin/bash
# test_scenarios.sh

scenarios=(
    "25 year old with hypertension"
    "45 year old diabetic female"
    "65 year old with multiple conditions"
)

for scenario in "${scenarios[@]}"; do
    python scripts.py --scenario "$scenario" --output_dir "ci_results"
    if [ $? -ne 0 ]; then
        echo "Test failed for: $scenario"
        exit 1
    fi
done

echo "All tests passed!"
```

## Performance Considerations

- **Processing Time**: Each assessment takes 30-60 seconds depending on LLM provider
- **API Costs**: Consider rate limits and costs when running multiple tests
- **Memory Usage**: Vector store initialization requires ~500MB RAM
- **File Storage**: Each report is typically 5-20KB

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