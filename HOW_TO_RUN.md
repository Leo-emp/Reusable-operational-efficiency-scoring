# How to Run the Script - Complete Guide

This guide covers everything you need to run the Operational Efficiency Scoring System,
whether you're using synthetic data or real-world data from your workplace.

---

## QUICK START (Test with Synthetic Data)

Open your terminal and run:

```bash
cd C:\Users\User\universal-ops-scorer
python generate_data.py --type order-fulfillment
python main.py
```

That's it. Check the results in:
- `reports/operational_efficiency_report.pdf` (PDF report)
- `reports/operational_efficiency_report.pptx` (PowerPoint presentation)
- `charts/` folder (6 PNG charts)

---

## STEP 1: Choose Your Operation Type

### Option A: Use a Built-in Template

See all available templates:

```bash
python generate_data.py --list
```

Available types:

| Command | Operation | Steps |
|---------|-----------|-------|
| `python generate_data.py --type order-fulfillment` | E-commerce order processing | 7 |
| `python generate_data.py --type customer-service` | Support ticket lifecycle | 7 |
| `python generate_data.py --type manufacturing` | Production line workflow | 8 |
| `python generate_data.py --type hr-onboarding` | New employee onboarding | 8 |
| `python generate_data.py --type it-incident` | IT incident response | 9 |
| `python generate_data.py --type procurement` | Purchase order processing | 8 |

You can also change the number of cases:

```bash
python generate_data.py --type manufacturing --orders 5000
```

### Option B: Use Your Own Real Data

See STEP 3 below.

### Option C: Define a Custom Pipeline from Scratch

Generate an example JSON config:

```bash
python generate_data.py --example-config
```

This creates `example_pipeline.json`. Edit it with your own process steps:

```json
{
    "name": "My Company Operations",
    "description": "Our internal process",
    "steps": [
        {
            "name": "Step 1 Name",
            "department": "Department Name",
            "avg_cycle": 30,
            "cycle_std": 10,
            "avg_wait": 15,
            "wait_std": 5,
            "error_rate": 0.05,
            "rework_rate": 0.03
        }
    ],
    "employees": {
        "Department Name": ["EMP_01", "EMP_02"]
    }
}
```

Then generate data from your config:

```bash
python generate_data.py --type custom --config example_pipeline.json
```

---

## STEP 2: Run the Analysis

### Basic Analysis (no AI, works offline):

```bash
python main.py
```

### With AI Recommendations (needs free Gemini API key):

Get a free key at: https://aistudio.google.com/apikey

```bash
export GEMINI_API_KEY=your-key-here
python main.py --with-ai
```

### Custom PDF Output Path:

```bash
python main.py -o my_custom_report.pdf
```

---

## STEP 3: Using Real-World Data

This is the most important section if you want to analyze your actual workplace data.

### What Data Do You Need?

You need a CSV or Excel file where each row represents ONE process step for ONE case.

Example: If you have 100 orders and each order goes through 5 steps,
you need 500 rows (100 orders x 5 steps).

### Method 1: Use the Data Preparation Helper (Easiest)

If your data has columns with common names like `order_id`, `ticket_id`,
`processing_time`, `duration`, etc., the helper will auto-map them:

```bash
python prepare_data.py your_data.csv
python main.py
```

Or with Excel:

```bash
python prepare_data.py your_data.xlsx --name "My Company Operations"
python main.py
```

Preview first without saving:

```bash
python prepare_data.py your_data.csv --preview
```

The helper auto-maps these common column names:

| Your Column Name | Maps To |
|-----------------|---------|
| `order_id`, `ticket_id`, `incident_id`, `po_number`, `request_id` | `case_id` |
| `order_date`, `date`, `created_date`, `ticket_date` | `case_date` |
| `step`, `step_name`, `stage`, `phase`, `activity` | `process_step` |
| `dept`, `team`, `group`, `unit` | `department` |
| `employee`, `agent`, `worker`, `assigned_to`, `handler` | `employee_id` |
| `wait_time`, `waiting_time`, `queue_time` | `wait_time_min` |
| `cycle_time`, `processing_time`, `duration` | `cycle_time_min` |
| `value`, `order_value`, `amount`, `cost` | `case_value` |

Columns that are missing will be auto-filled with sensible defaults.

### Method 2: Format Your CSV Manually

If you want full control, format your CSV with these exact column names:

```
case_id,case_date,process_step,step_number,department,employee_id,priority,complexity,case_value,wait_time_min,cycle_time_min,total_time_min,start_time,end_time,error_count,rework_count,month,day_of_week
```

See `data/template.csv` for an example with sample data.

Required columns (MUST have):
- `case_id` — Unique ID for each case/order/ticket
- `case_date` — Date (YYYY-MM-DD format)
- `process_step` — Name of the step
- `step_number` — Order of the step (1, 2, 3...)
- `department` — Which team handles this step
- `cycle_time_min` — How long the step took (in minutes)
- `wait_time_min` — How long the case waited before this step (in minutes)
- `total_time_min` — wait_time + cycle_time
- `error_count` — 0 or 1 (did an error happen?)
- `rework_count` — 0 or 1 (was rework needed?)

Optional columns (will use defaults if missing):
- `employee_id` — defaults to "UNKNOWN"
- `priority` — defaults to "Standard"
- `complexity` — defaults to 5
- `case_value` — defaults to 1000.00
- `start_time` — defaults to case_date 09:00
- `end_time` — defaults to case_date 10:00
- `month` — auto-calculated from case_date
- `day_of_week` — auto-calculated from case_date

Save your file as `data/operations_data.csv` and run:

```bash
python main.py
```

### Method 3: Minimum Data (Only 3 Columns Needed)

If you only have basic data, the helper can work with just 3 columns:

```csv
case_id,process_step,cycle_time_min
ORD-001,Order Received,12
ORD-001,Processing,45
ORD-001,Review,20
ORD-001,Completion,10
ORD-002,Order Received,15
ORD-002,Processing,50
ORD-002,Review,18
ORD-002,Completion,8
```

Save this as `my_data.csv` and run:

```bash
python prepare_data.py my_data.csv
python main.py
```

Everything else gets filled with defaults automatically.

---

## STEP 4: View Your Results

After running `python main.py`, you get:

```
reports/
├── operational_efficiency_report.pdf     ← PDF report
└── operational_efficiency_report.pptx    ← PowerPoint presentation (13 slides)

charts/
├── 1_efficiency_scores.png              ← Scores per step
├── 2_cycle_vs_wait.png                  ← Time breakdown
├── 3_error_rework_rates.png             ← Quality metrics
├── 4_monthly_trend.png                  ← Seasonal patterns
├── 5_department_heatmap.png             ← Department comparison
└── 6_prediction_analysis.png            ← ML predictions
```

Open them from File Explorer:
- PDF: `C:\Users\User\universal-ops-scorer\reports\operational_efficiency_report.pdf`
- PowerPoint: `C:\Users\User\universal-ops-scorer\reports\operational_efficiency_report.pptx`

---

## REAL-WORLD EXAMPLES

### Example 1: Analyzing Your Company's Order Fulfillment

You export data from your ERP system as `orders_2025.csv` with columns:
`order_id, date, stage, team, processing_time, waiting_time, errors`

```bash
python prepare_data.py orders_2025.csv --name "Our Order Fulfillment Q1 2025"
python main.py --with-ai
```

### Example 2: Analyzing IT Helpdesk Tickets

You export from your ticketing system as `tickets.xlsx` with columns:
`ticket_id, created_date, status, assigned_to, department, duration`

```bash
python prepare_data.py tickets.xlsx --name "IT Helpdesk Analysis"
python main.py
```

### Example 3: Analyzing HR Onboarding

You have a spreadsheet tracking new hires with columns:
`employee_name, step, start_date, days_taken, department`

Convert `days_taken` to minutes (x 480 for work-minutes per day),
save as CSV, then:

```bash
python prepare_data.py onboarding.csv --name "HR Onboarding Process"
python main.py --with-ai
```

### Example 4: Analyzing a Custom Process

You have a unique process not covered by templates. Create a CSV:

```csv
case_id,process_step,step_number,department,cycle_time_min,wait_time_min,error_count,rework_count,case_date
REQ-001,Submit Request,1,Requester,10,0,0,0,2025-02-10
REQ-001,Manager Approval,2,Management,5,120,0,0,2025-02-10
REQ-001,Budget Check,3,Finance,15,60,1,0,2025-02-10
REQ-001,Execution,4,Operations,90,30,0,0,2025-02-10
REQ-001,Sign-off,5,Management,10,45,0,0,2025-02-10
```

```bash
python prepare_data.py my_process.csv --name "Internal Request Process"
python main.py
```

---

## RUNNING FROM CLAUDE CODE TERMINAL

If you're in Claude Code, add `!` before each command:

```
! cd C:\Users\User\universal-ops-scorer && python generate_data.py --type customer-service && python main.py
```

Or with real data:

```
! cd C:\Users\User\universal-ops-scorer && python prepare_data.py "C:\Users\User\Downloads\my_data.csv" && python main.py
```

---

## TROUBLESHOOTING

### "Data file not found"
Run `generate_data.py` first, or place your CSV at `data/operations_data.csv`.

### "Module not found" errors
Install dependencies: `pip install -r requirements.txt`

### "GEMINI_API_KEY not set"
Only needed if you use `--with-ai`. Without it, you still get rule-based recommendations.
Get a free key at: https://aistudio.google.com/apikey

### Charts look wrong or empty
Make sure your data has enough records (at least 50+ cases recommended).

### PowerPoint won't open
Make sure you have Microsoft PowerPoint, Google Slides, or LibreOffice Impress installed.

---

## FILE STRUCTURE

```
universal-ops-scorer/
├── generate_data.py         ← Generate synthetic data (6 templates + custom)
├── prepare_data.py          ← Convert your real data to the right format
├── main.py                  ← Run the full analysis (scoring, charts, PDF, PPTX)
├── requirements.txt         ← Python dependencies
├── data/
│   ├── template.csv         ← Example CSV format
│   ├── operations_data.csv  ← Your data goes here (generated or real)
│   └── pipeline_meta.json   ← Pipeline metadata (auto-created)
├── charts/                  ← Generated charts (6 PNG files)
└── reports/                 ← Generated reports (PDF + PPTX)
```
