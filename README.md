# Universal Operational Efficiency Scoring System

An AI-powered system that analyzes **any type of business operation**, detects bottlenecks, provides improvement recommendations, and predicts future performance.

Works with 6 built-in operation types or your own custom pipeline.

## Built-in Operation Types

| Type | Pipeline | Steps |
|------|----------|-------|
| `order-fulfillment` | E-commerce order processing | 7 |
| `customer-service` | Support ticket lifecycle | 7 |
| `manufacturing` | Production line workflow | 8 |
| `hr-onboarding` | New employee onboarding | 8 |
| `it-incident` | IT incident response | 9 |
| `procurement` | Purchase order processing | 8 |
| `custom` | Your own pipeline (JSON config) | Any |

## What It Does

1. **Efficiency Scoring** - Scores each process step (0-100) based on cycle time, wait time, error rate, and rework rate
2. **Bottleneck Detection** - Identifies which steps are slowing down the entire pipeline
3. **Visualizations** - Creates 6 charts showing performance patterns
4. **AI Recommendations** - Uses Google Gemini (free) to suggest process improvements
5. **Performance Prediction** - Forecasts future performance using Machine Learning (Random Forest)
6. **PDF Report** - Generates a professional report with all findings

## Setup

```bash
git clone https://github.com/Leo-emp/universal-ops-scorer.git
cd universal-ops-scorer
pip install -r requirements.txt
```

## Usage

### Step 1: Generate Data

```bash
# See all available operation types
python generate_data.py --list

# Generate data for any type
python generate_data.py --type order-fulfillment
python generate_data.py --type customer-service
python generate_data.py --type manufacturing
python generate_data.py --type hr-onboarding
python generate_data.py --type it-incident
python generate_data.py --type procurement

# Custom number of cases
python generate_data.py --type manufacturing --orders 5000
```

### Step 2: Run Analysis

```bash
# Basic analysis (no AI)
python main.py

# With AI recommendations (needs free Gemini API key)
export GEMINI_API_KEY=your-key-here
python main.py --with-ai

# Custom output path
python main.py -o my_report.pdf
```

### Custom Pipeline

Define your own operation in a JSON file:

```bash
# Generate an example config to customize
python generate_data.py --example-config

# Edit example_pipeline.json with your process steps, then:
python generate_data.py --type custom --config my_pipeline.json
python main.py
```

Example JSON config:
```json
{
  "name": "My Custom Pipeline",
  "description": "Description of your operation",
  "steps": [
    {
      "name": "Step 1 Name",
      "department": "Department",
      "avg_cycle": 30,
      "cycle_std": 10,
      "avg_wait": 15,
      "wait_std": 5,
      "error_rate": 0.05,
      "rework_rate": 0.03
    }
  ],
  "employees": {
    "Department": ["EMP_01", "EMP_02"]
  }
}
```

## Output

```
universal-ops-scorer/
├── data/
│   ├── operations_data.csv          # Generated dataset
│   └── pipeline_meta.json           # Pipeline type metadata
├── charts/
│   ├── 1_efficiency_scores.png      # Scores per step
│   ├── 2_cycle_vs_wait.png          # Time breakdown
│   ├── 3_error_rework_rates.png     # Quality metrics
│   ├── 4_monthly_trend.png          # Seasonal patterns
│   ├── 5_department_heatmap.png     # Department comparison
│   └── 6_prediction_analysis.png    # ML predictions
└── reports/
    └── operational_efficiency_report.pdf
```

## Scoring Methodology

Each process step is scored on 4 dimensions:

| Factor | Weight | Measures |
|--------|--------|----------|
| Cycle Time | 30% | How fast is the step? |
| Wait Time | 30% | How long do cases wait? |
| Error Rate | 25% | How many errors occur? |
| Rework Rate | 15% | How often is rework needed? |

Grades: A (80+), B (65-79), C (50-64), D (35-49), F (below 35)

## Tech Stack

- **Python** - Core language
- **pandas** - Data analysis
- **matplotlib / seaborn** - Visualizations
- **scikit-learn** - Machine learning predictions
- **Google Gemini API** - AI-powered recommendations (free tier)
- **fpdf2** - PDF report generation

## Cost

**Free.** Everything runs locally except AI recommendations (optional, uses Gemini free tier).

## License

MIT
