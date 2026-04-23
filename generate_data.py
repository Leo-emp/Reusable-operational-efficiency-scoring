"""
==========================================================================
SYNTHETIC DATA GENERATOR - Universal Operations
==========================================================================

Generates realistic synthetic data for ANY type of business operation.
Choose from built-in templates or define your own custom pipeline.

Built-in templates:
    1. order-fulfillment   - E-commerce order processing pipeline
    2. customer-service    - Support ticket lifecycle
    3. manufacturing       - Production line workflow
    4. hr-onboarding       - New employee onboarding process
    5. it-incident         - IT incident response pipeline
    6. procurement         - Purchase order processing
    7. custom              - Define your own from a JSON config file

Usage:
    python generate_data.py --type order-fulfillment
    python generate_data.py --type customer-service
    python generate_data.py --type manufacturing --orders 5000
    python generate_data.py --type custom --config my_pipeline.json
    python generate_data.py --list   (shows all available templates)
"""

# ============================================================
# IMPORTS
# ============================================================

import argparse       # For command-line arguments
import json           # For loading custom pipeline configs
import random         # For generating random numbers
import sys            # For exiting on errors
from pathlib import Path          # For file path operations
from datetime import datetime, timedelta  # For generating dates/times

import pandas as pd   # For creating and saving the dataset
import numpy as np    # For statistical distributions


# ============================================================
# OPERATION TEMPLATES
# Each template defines the process steps for a specific
# type of business operation. Every step has:
#   - name:        What the step is called
#   - department:  Which team handles it
#   - avg_cycle:   Average processing time (minutes)
#   - cycle_std:   How much cycle time varies
#   - avg_wait:    Average wait before step starts (minutes)
#   - wait_std:    How much wait time varies
#   - error_rate:  Probability of error (0.0 to 1.0)
#   - rework_rate: Probability of rework needed (0.0 to 1.0)
# ============================================================

TEMPLATES = {

    # --- Template 1: Order Fulfillment ---
    # E-commerce / retail order processing
    "order-fulfillment": {
        "name": "Order Fulfillment Pipeline",
        "description": "E-commerce order processing from receipt to delivery",
        "steps": [
            {"name": "Order Received",       "department": "Sales",      "avg_cycle": 15,  "cycle_std": 5,  "avg_wait": 0,  "wait_std": 0,  "error_rate": 0.02, "rework_rate": 0.01},
            {"name": "Order Validation",     "department": "Operations", "avg_cycle": 20,  "cycle_std": 8,  "avg_wait": 10, "wait_std": 5,  "error_rate": 0.05, "rework_rate": 0.03},
            {"name": "Inventory Check",      "department": "Warehouse",  "avg_cycle": 25,  "cycle_std": 10, "avg_wait": 45, "wait_std": 20, "error_rate": 0.08, "rework_rate": 0.05},
            {"name": "Picking & Packing",    "department": "Warehouse",  "avg_cycle": 55,  "cycle_std": 20, "avg_wait": 30, "wait_std": 15, "error_rate": 0.12, "rework_rate": 0.08},
            {"name": "Quality Inspection",   "department": "Quality",    "avg_cycle": 20,  "cycle_std": 8,  "avg_wait": 25, "wait_std": 10, "error_rate": 0.15, "rework_rate": 0.10},
            {"name": "Shipping Preparation", "department": "Logistics",  "avg_cycle": 15,  "cycle_std": 5,  "avg_wait": 10, "wait_std": 5,  "error_rate": 0.03, "rework_rate": 0.02},
            {"name": "Dispatch & Delivery",  "department": "Logistics",  "avg_cycle": 180, "cycle_std": 60, "avg_wait": 20, "wait_std": 10, "error_rate": 0.04, "rework_rate": 0.02},
        ],
        "employees": {
            "Sales": ["EMP_S01", "EMP_S02", "EMP_S03", "EMP_S04"],
            "Operations": ["EMP_O01", "EMP_O02", "EMP_O03"],
            "Warehouse": ["EMP_W01", "EMP_W02", "EMP_W03", "EMP_W04", "EMP_W05", "EMP_W06"],
            "Quality": ["EMP_Q01", "EMP_Q02"],
            "Logistics": ["EMP_L01", "EMP_L02", "EMP_L03", "EMP_L04"],
        },
    },

    # --- Template 2: Customer Service ---
    # Support ticket lifecycle from creation to resolution
    "customer-service": {
        "name": "Customer Service Pipeline",
        "description": "Support ticket lifecycle from creation to resolution",
        "steps": [
            {"name": "Ticket Created",       "department": "Frontline",    "avg_cycle": 5,   "cycle_std": 2,  "avg_wait": 0,  "wait_std": 0,  "error_rate": 0.03, "rework_rate": 0.01},
            {"name": "Ticket Triage",        "department": "Frontline",    "avg_cycle": 10,  "cycle_std": 5,  "avg_wait": 15, "wait_std": 10, "error_rate": 0.08, "rework_rate": 0.04},
            {"name": "Agent Assignment",     "department": "Dispatch",     "avg_cycle": 5,   "cycle_std": 3,  "avg_wait": 30, "wait_std": 20, "error_rate": 0.05, "rework_rate": 0.03},
            {"name": "Investigation",        "department": "Support",      "avg_cycle": 45,  "cycle_std": 25, "avg_wait": 20, "wait_std": 15, "error_rate": 0.10, "rework_rate": 0.06},
            {"name": "Resolution",           "department": "Support",      "avg_cycle": 30,  "cycle_std": 15, "avg_wait": 10, "wait_std": 8,  "error_rate": 0.12, "rework_rate": 0.08},
            {"name": "Customer Confirmation", "department": "Frontline",   "avg_cycle": 10,  "cycle_std": 5,  "avg_wait": 60, "wait_std": 40, "error_rate": 0.04, "rework_rate": 0.02},
            {"name": "Ticket Closure",       "department": "Quality",      "avg_cycle": 5,   "cycle_std": 2,  "avg_wait": 5,  "wait_std": 3,  "error_rate": 0.02, "rework_rate": 0.01},
        ],
        "employees": {
            "Frontline": ["AGT_F01", "AGT_F02", "AGT_F03", "AGT_F04", "AGT_F05"],
            "Dispatch": ["AGT_D01", "AGT_D02"],
            "Support": ["AGT_S01", "AGT_S02", "AGT_S03", "AGT_S04"],
            "Quality": ["AGT_Q01", "AGT_Q02"],
        },
    },

    # --- Template 3: Manufacturing ---
    # Production line from raw materials to finished goods
    "manufacturing": {
        "name": "Manufacturing Production Line",
        "description": "Production workflow from raw materials to finished goods",
        "steps": [
            {"name": "Material Receiving",    "department": "Receiving",   "avg_cycle": 30,  "cycle_std": 10, "avg_wait": 0,  "wait_std": 0,  "error_rate": 0.03, "rework_rate": 0.01},
            {"name": "Material Inspection",   "department": "Quality",     "avg_cycle": 20,  "cycle_std": 8,  "avg_wait": 15, "wait_std": 8,  "error_rate": 0.06, "rework_rate": 0.04},
            {"name": "Pre-Processing",        "department": "Production",  "avg_cycle": 45,  "cycle_std": 15, "avg_wait": 20, "wait_std": 10, "error_rate": 0.05, "rework_rate": 0.03},
            {"name": "Assembly",              "department": "Production",  "avg_cycle": 90,  "cycle_std": 30, "avg_wait": 35, "wait_std": 20, "error_rate": 0.10, "rework_rate": 0.07},
            {"name": "Quality Control",       "department": "Quality",     "avg_cycle": 25,  "cycle_std": 10, "avg_wait": 20, "wait_std": 12, "error_rate": 0.15, "rework_rate": 0.10},
            {"name": "Finishing & Packaging",  "department": "Finishing",  "avg_cycle": 35,  "cycle_std": 12, "avg_wait": 15, "wait_std": 8,  "error_rate": 0.04, "rework_rate": 0.02},
            {"name": "Final Inspection",      "department": "Quality",     "avg_cycle": 15,  "cycle_std": 5,  "avg_wait": 10, "wait_std": 5,  "error_rate": 0.08, "rework_rate": 0.05},
            {"name": "Warehouse Storage",     "department": "Warehouse",   "avg_cycle": 20,  "cycle_std": 8,  "avg_wait": 10, "wait_std": 5,  "error_rate": 0.02, "rework_rate": 0.01},
        ],
        "employees": {
            "Receiving": ["MFG_R01", "MFG_R02", "MFG_R03"],
            "Quality": ["MFG_Q01", "MFG_Q02", "MFG_Q03"],
            "Production": ["MFG_P01", "MFG_P02", "MFG_P03", "MFG_P04", "MFG_P05", "MFG_P06"],
            "Finishing": ["MFG_F01", "MFG_F02", "MFG_F03"],
            "Warehouse": ["MFG_W01", "MFG_W02"],
        },
    },

    # --- Template 4: HR Onboarding ---
    # New employee onboarding process
    "hr-onboarding": {
        "name": "HR Onboarding Pipeline",
        "description": "New employee onboarding from offer to fully productive",
        "steps": [
            {"name": "Offer Acceptance",      "department": "HR",          "avg_cycle": 30,   "cycle_std": 15,  "avg_wait": 0,    "wait_std": 0,    "error_rate": 0.02, "rework_rate": 0.01},
            {"name": "Document Collection",   "department": "HR",          "avg_cycle": 120,  "cycle_std": 60,  "avg_wait": 1440, "wait_std": 720,  "error_rate": 0.10, "rework_rate": 0.06},
            {"name": "IT Setup",              "department": "IT",          "avg_cycle": 180,  "cycle_std": 60,  "avg_wait": 480,  "wait_std": 240,  "error_rate": 0.08, "rework_rate": 0.05},
            {"name": "Workspace Setup",       "department": "Facilities",  "avg_cycle": 60,   "cycle_std": 20,  "avg_wait": 240,  "wait_std": 120,  "error_rate": 0.04, "rework_rate": 0.02},
            {"name": "Orientation",           "department": "HR",          "avg_cycle": 480,  "cycle_std": 60,  "avg_wait": 120,  "wait_std": 60,   "error_rate": 0.03, "rework_rate": 0.01},
            {"name": "Team Introduction",     "department": "Management",  "avg_cycle": 60,   "cycle_std": 20,  "avg_wait": 60,   "wait_std": 30,   "error_rate": 0.02, "rework_rate": 0.01},
            {"name": "Training",              "department": "Training",    "avg_cycle": 2400, "cycle_std": 480, "avg_wait": 480,  "wait_std": 240,  "error_rate": 0.06, "rework_rate": 0.04},
            {"name": "Probation Review",      "department": "Management",  "avg_cycle": 60,   "cycle_std": 20,  "avg_wait": 1440, "wait_std": 480,  "error_rate": 0.05, "rework_rate": 0.03},
        ],
        "employees": {
            "HR": ["HR_01", "HR_02", "HR_03"],
            "IT": ["IT_01", "IT_02"],
            "Facilities": ["FAC_01", "FAC_02"],
            "Management": ["MGR_01", "MGR_02", "MGR_03", "MGR_04"],
            "Training": ["TRN_01", "TRN_02"],
        },
    },

    # --- Template 5: IT Incident Management ---
    # IT incident response from detection to post-mortem
    "it-incident": {
        "name": "IT Incident Management Pipeline",
        "description": "IT incident response from detection to post-mortem review",
        "steps": [
            {"name": "Incident Detection",   "department": "Monitoring",  "avg_cycle": 5,   "cycle_std": 3,  "avg_wait": 0,  "wait_std": 0,  "error_rate": 0.05, "rework_rate": 0.02},
            {"name": "Incident Logging",     "department": "Service Desk", "avg_cycle": 10,  "cycle_std": 5,  "avg_wait": 5,  "wait_std": 3,  "error_rate": 0.04, "rework_rate": 0.02},
            {"name": "Severity Assessment",  "department": "Service Desk", "avg_cycle": 8,   "cycle_std": 4,  "avg_wait": 10, "wait_std": 8,  "error_rate": 0.10, "rework_rate": 0.05},
            {"name": "Team Assignment",      "department": "Management",   "avg_cycle": 5,   "cycle_std": 3,  "avg_wait": 20, "wait_std": 15, "error_rate": 0.06, "rework_rate": 0.03},
            {"name": "Diagnosis",            "department": "Engineering",  "avg_cycle": 60,  "cycle_std": 30, "avg_wait": 15, "wait_std": 10, "error_rate": 0.12, "rework_rate": 0.08},
            {"name": "Fix Implementation",   "department": "Engineering",  "avg_cycle": 45,  "cycle_std": 25, "avg_wait": 10, "wait_std": 8,  "error_rate": 0.08, "rework_rate": 0.06},
            {"name": "Testing & Validation", "department": "QA",           "avg_cycle": 30,  "cycle_std": 15, "avg_wait": 15, "wait_std": 10, "error_rate": 0.10, "rework_rate": 0.07},
            {"name": "Deployment",           "department": "DevOps",       "avg_cycle": 20,  "cycle_std": 10, "avg_wait": 20, "wait_std": 15, "error_rate": 0.05, "rework_rate": 0.03},
            {"name": "Post-Mortem Review",   "department": "Management",   "avg_cycle": 60,  "cycle_std": 20, "avg_wait": 1440, "wait_std": 480, "error_rate": 0.02, "rework_rate": 0.01},
        ],
        "employees": {
            "Monitoring": ["MON_01", "MON_02"],
            "Service Desk": ["SD_01", "SD_02", "SD_03"],
            "Management": ["MGR_01", "MGR_02"],
            "Engineering": ["ENG_01", "ENG_02", "ENG_03", "ENG_04"],
            "QA": ["QA_01", "QA_02"],
            "DevOps": ["DEV_01", "DEV_02"],
        },
    },

    # --- Template 6: Procurement ---
    # Purchase order processing pipeline
    "procurement": {
        "name": "Procurement Pipeline",
        "description": "Purchase order processing from request to payment",
        "steps": [
            {"name": "Purchase Request",      "department": "Requesting",  "avg_cycle": 20,  "cycle_std": 10, "avg_wait": 0,   "wait_std": 0,   "error_rate": 0.06, "rework_rate": 0.03},
            {"name": "Budget Approval",       "department": "Finance",     "avg_cycle": 30,  "cycle_std": 15, "avg_wait": 120, "wait_std": 60,  "error_rate": 0.08, "rework_rate": 0.05},
            {"name": "Vendor Selection",      "department": "Procurement", "avg_cycle": 60,  "cycle_std": 30, "avg_wait": 30,  "wait_std": 15,  "error_rate": 0.05, "rework_rate": 0.03},
            {"name": "PO Creation",           "department": "Procurement", "avg_cycle": 20,  "cycle_std": 8,  "avg_wait": 15,  "wait_std": 8,   "error_rate": 0.04, "rework_rate": 0.02},
            {"name": "Vendor Confirmation",   "department": "Procurement", "avg_cycle": 15,  "cycle_std": 8,  "avg_wait": 240, "wait_std": 120, "error_rate": 0.03, "rework_rate": 0.01},
            {"name": "Goods Receipt",         "department": "Warehouse",   "avg_cycle": 30,  "cycle_std": 12, "avg_wait": 1440, "wait_std": 720, "error_rate": 0.07, "rework_rate": 0.04},
            {"name": "Invoice Verification",  "department": "Finance",     "avg_cycle": 25,  "cycle_std": 10, "avg_wait": 60,  "wait_std": 30,  "error_rate": 0.10, "rework_rate": 0.06},
            {"name": "Payment Processing",    "department": "Finance",     "avg_cycle": 15,  "cycle_std": 5,  "avg_wait": 30,  "wait_std": 15,  "error_rate": 0.03, "rework_rate": 0.01},
        ],
        "employees": {
            "Requesting": ["REQ_01", "REQ_02", "REQ_03", "REQ_04", "REQ_05"],
            "Finance": ["FIN_01", "FIN_02", "FIN_03"],
            "Procurement": ["PRO_01", "PRO_02", "PRO_03"],
            "Warehouse": ["WHS_01", "WHS_02"],
        },
    },
}


# ============================================================
# PRIORITY SETTINGS
# These apply to all operation types
# ============================================================

PRIORITIES = ["Standard", "Express", "Rush"]
PRIORITY_WEIGHTS = [0.60, 0.30, 0.10]  # 60% standard, 30% express, 10% rush
PRIORITY_SPEED = {
    "Standard": 1.0,    # Normal speed
    "Express": 0.8,     # 20% faster
    "Rush": 0.6,        # 40% faster
}


# ============================================================
# LOAD CUSTOM PIPELINE FROM JSON
# ============================================================

def load_custom_pipeline(config_path: str) -> dict:
    """
    Loads a custom pipeline definition from a JSON file.

    The JSON file should have this structure:
    {
        "name": "My Custom Pipeline",
        "description": "Description of what this pipeline does",
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
            },
            ...more steps...
        ],
        "employees": {
            "Department Name": ["EMP_01", "EMP_02", "EMP_03"],
            ...more departments...
        }
    }

    Args:
        config_path: Path to the JSON configuration file.

    Returns:
        A pipeline dictionary in the same format as the built-in templates.
    """
    if not Path(config_path).exists():
        print(f"Error: Config file not found: {config_path}")
        sys.exit(1)

    with open(config_path, "r", encoding="utf-8") as f:
        pipeline = json.load(f)

    # Validate required fields
    required_fields = ["name", "steps", "employees"]
    for field in required_fields:
        if field not in pipeline:
            print(f"Error: Config file missing required field: '{field}'")
            sys.exit(1)

    # Validate each step has required fields
    step_fields = ["name", "department", "avg_cycle", "cycle_std", "avg_wait", "wait_std", "error_rate", "rework_rate"]
    for i, step in enumerate(pipeline["steps"]):
        for field in step_fields:
            if field not in step:
                print(f"Error: Step {i+1} missing required field: '{field}'")
                sys.exit(1)

    print(f"Loaded custom pipeline: {pipeline['name']}")
    print(f"  Steps: {len(pipeline['steps'])}")
    print(f"  Departments: {len(pipeline['employees'])}")
    print()

    return pipeline


# ============================================================
# DATA GENERATION FUNCTION
# ============================================================

def generate_operations_data(pipeline: dict, num_orders: int = 2000, seed: int = 42) -> pd.DataFrame:
    """
    Generates a realistic synthetic dataset for any operation type.

    This function is GENERIC - it works with any pipeline definition
    (built-in template or custom JSON). It simulates realistic operations
    with seasonal effects, priority handling, and intentional bottlenecks.

    Args:
        pipeline:   The pipeline definition (from TEMPLATES or custom JSON).
        num_orders: How many orders/cases to simulate (default 2000).
        seed:       Random seed for reproducibility.

    Returns:
        A pandas DataFrame with one row per process step per order.
    """
    # Set random seeds so the data is the same every time
    random.seed(seed)
    np.random.seed(seed)

    steps = pipeline["steps"]
    employees = pipeline["employees"]

    # This list will hold all the rows of our dataset
    all_records = []

    # Generate orders spread across 6 months
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2025, 6, 30)
    total_days = (end_date - start_date).days

    for order_num in range(1, num_orders + 1):

        # --- Generate order-level properties ---
        order_id = f"CASE-{order_num:04d}"

        # Pick a random date within our 6-month range
        random_day = random.randint(0, total_days)
        order_date = start_date + timedelta(days=random_day)

        # Add a random time of day (business hours: 7am to 6pm)
        order_hour = random.randint(7, 17)
        order_minute = random.randint(0, 59)
        current_time = order_date.replace(hour=order_hour, minute=order_minute)

        # Pick priority level
        priority = random.choices(PRIORITIES, weights=PRIORITY_WEIGHTS, k=1)[0]
        speed_multiplier = PRIORITY_SPEED[priority]

        # Generate a random case value ($50 to $5000)
        case_value = round(random.uniform(50, 5000), 2)

        # Complexity score (1 to 10) - affects processing time
        complexity = max(1, min(10, int(np.random.poisson(lam=4))))

        # Seasonal effect - months 3-5 are busier (peak season)
        month = order_date.month
        if month in [3, 4, 5]:
            seasonal_factor = 1.3   # 30% slower during peak
        elif month in [1, 6]:
            seasonal_factor = 0.9   # 10% faster during slow months
        else:
            seasonal_factor = 1.0

        # --- Generate data for each process step ---
        for step_index, step in enumerate(steps):

            # Calculate wait time
            avg_wait = step["avg_wait"] * speed_multiplier * seasonal_factor
            wait_time = max(0, np.random.normal(avg_wait, step["wait_std"]))
            wait_time = round(wait_time, 1)

            # Calculate cycle time (complexity makes it longer)
            avg_cycle = step["avg_cycle"] * speed_multiplier * seasonal_factor
            avg_cycle *= (1 + complexity * 0.03)  # 3% longer per complexity point
            cycle_time = max(5, np.random.normal(avg_cycle, step["cycle_std"]))
            cycle_time = round(cycle_time, 1)

            # Calculate start and end times
            step_start = current_time + timedelta(minutes=wait_time)
            step_end = step_start + timedelta(minutes=cycle_time)

            # Determine if errors occurred
            error_occurred = random.random() < step["error_rate"]
            error_count = 1 if error_occurred else 0

            # Determine if rework was needed
            rework_occurred = random.random() < step["rework_rate"]
            rework_count = 1 if rework_occurred else 0

            # If rework happened, add extra time (50% of original cycle)
            if rework_count > 0:
                rework_time = round(cycle_time * 0.5, 1)
                cycle_time += rework_time
                step_end += timedelta(minutes=rework_time)

            # Pick a random employee from the department
            dept = step["department"]
            employee = random.choice(employees.get(dept, [f"{dept}_01"]))

            # Total time = wait + cycle
            total_time = round(wait_time + cycle_time, 1)

            # Build the record
            record = {
                "case_id": order_id,
                "case_date": order_date.strftime("%Y-%m-%d"),
                "process_step": step["name"],
                "step_number": step_index + 1,
                "department": dept,
                "employee_id": employee,
                "priority": priority,
                "complexity": complexity,
                "case_value": case_value,
                "wait_time_min": wait_time,
                "cycle_time_min": cycle_time,
                "total_time_min": total_time,
                "start_time": step_start.strftime("%Y-%m-%d %H:%M"),
                "end_time": step_end.strftime("%Y-%m-%d %H:%M"),
                "error_count": error_count,
                "rework_count": rework_count,
                "month": month,
                "day_of_week": order_date.strftime("%A"),
            }

            all_records.append(record)

            # Move current_time forward for the next step
            current_time = step_end

    # Convert to DataFrame
    df = pd.DataFrame(all_records)
    return df


# ============================================================
# LIST ALL AVAILABLE TEMPLATES
# ============================================================

def list_templates():
    """Prints all available operation templates."""
    print("Available operation templates:")
    print("-" * 60)
    for key, template in TEMPLATES.items():
        num_steps = len(template["steps"])
        depts = list(template["employees"].keys())
        print(f"  {key:<25} {template['name']}")
        print(f"  {'':25} Steps: {num_steps} | Departments: {', '.join(depts)}")
        print()
    print("  custom                    Load from a JSON config file")
    print("                            Use: --type custom --config my_pipeline.json")
    print()


# ============================================================
# GENERATE EXAMPLE CUSTOM CONFIG
# ============================================================

def generate_example_config(output_path: str = "example_pipeline.json"):
    """
    Creates an example JSON config file that users can customize.
    This makes it easy to define a custom pipeline.
    """
    example = {
        "name": "My Custom Pipeline",
        "description": "Description of your operation",
        "steps": [
            {
                "name": "Step 1 - Intake",
                "department": "Front Office",
                "avg_cycle": 15,
                "cycle_std": 5,
                "avg_wait": 0,
                "wait_std": 0,
                "error_rate": 0.03,
                "rework_rate": 0.01
            },
            {
                "name": "Step 2 - Processing",
                "department": "Operations",
                "avg_cycle": 45,
                "cycle_std": 15,
                "avg_wait": 20,
                "wait_std": 10,
                "error_rate": 0.08,
                "rework_rate": 0.05
            },
            {
                "name": "Step 3 - Review",
                "department": "Quality",
                "avg_cycle": 20,
                "cycle_std": 8,
                "avg_wait": 15,
                "wait_std": 8,
                "error_rate": 0.05,
                "rework_rate": 0.03
            },
            {
                "name": "Step 4 - Completion",
                "department": "Operations",
                "avg_cycle": 10,
                "cycle_std": 3,
                "avg_wait": 5,
                "wait_std": 3,
                "error_rate": 0.02,
                "rework_rate": 0.01
            }
        ],
        "employees": {
            "Front Office": ["FO_01", "FO_02", "FO_03"],
            "Operations": ["OP_01", "OP_02", "OP_03", "OP_04"],
            "Quality": ["QA_01", "QA_02"]
        }
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(example, f, indent=2)

    print(f"Example config saved to: {output_path}")
    print("Edit this file with your own process steps, then run:")
    print(f"  python generate_data.py --type custom --config {output_path}")


# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Generate synthetic operations data for any business pipeline."
    )
    parser.add_argument("--type", default="order-fulfillment",
                        help="Operation type (default: order-fulfillment). Use --list to see all.")
    parser.add_argument("--orders", type=int, default=2000,
                        help="Number of cases to simulate (default: 2000)")
    parser.add_argument("--config", default=None,
                        help="Path to custom pipeline JSON config (use with --type custom)")
    parser.add_argument("--list", action="store_true",
                        help="List all available operation templates")
    parser.add_argument("--example-config", action="store_true",
                        help="Generate an example custom pipeline JSON config")
    parser.add_argument("--output", default="data/operations_data.csv",
                        help="Output CSV path (default: data/operations_data.csv)")
    args = parser.parse_args()

    # Show available templates
    if args.list:
        list_templates()
        return

    # Generate example config
    if args.example_config:
        generate_example_config()
        return

    # Load the pipeline definition
    if args.type == "custom":
        if not args.config:
            print("Error: --config is required when using --type custom")
            print("  Example: python generate_data.py --type custom --config my_pipeline.json")
            print("  To create an example config: python generate_data.py --example-config")
            sys.exit(1)
        pipeline = load_custom_pipeline(args.config)
    elif args.type in TEMPLATES:
        pipeline = TEMPLATES[args.type]
    else:
        print(f"Error: Unknown operation type: '{args.type}'")
        print("Use --list to see available templates.")
        sys.exit(1)

    # Generate the data
    num_steps = len(pipeline["steps"])
    total_records = args.orders * num_steps

    print(f"Generating synthetic data: {pipeline['name']}")
    print(f"  Cases: {args.orders:,}")
    print(f"  Steps per case: {num_steps}")
    print(f"  Total records: {total_records:,}")
    print(f"  Date range: January 2025 to June 2025")
    print()

    df = generate_operations_data(pipeline, num_orders=args.orders)

    # Save to CSV
    Path(args.output).parent.mkdir(exist_ok=True)
    df.to_csv(args.output, index=False)

    # Also save the pipeline name for main.py to read
    meta = {"name": pipeline["name"], "type": args.type, "description": pipeline.get("description", "")}
    meta_path = Path(args.output).parent / "pipeline_meta.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    print(f"Dataset saved to: {args.output}")
    print(f"Pipeline metadata saved to: {meta_path}")
    print(f"Total records: {len(df):,}")
    print()

    # Quick summary
    print("Average times per process step:")
    summary = df.groupby("process_step").agg(
        avg_cycle=("cycle_time_min", "mean"),
        avg_wait=("wait_time_min", "mean"),
        error_rate=("error_count", "mean"),
    ).round(1)
    print(summary.to_string())


if __name__ == "__main__":
    main()
