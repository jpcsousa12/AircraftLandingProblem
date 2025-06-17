# Aircraft Landing Scheduling Problem

This repository addresses the **Aircraft Landing Scheduling Problem (ALSP)** using both Mixed-Integer Linear Programming (MILP) and Constraint Programming (CP) approaches. The ALSP is a classic optimization challenge in air traffic control, focused on finding optimal and feasible landing times for multiple aircraft on one or more runways, respecting time windows and minimum separation constraints.

## Table of Contents

- [Project Structure](#project-structure)
- [Problem Description](#problem-description)
- [Approaches](#approaches)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Benchmark Instances](#benchmark-instances)
- [Results](#results)
- [References](#references)

---

## Project Structure

```
AIRCRAFTLANDINGPROBLEM/
│
├── data/
│   ├── airland1.dat ... airland13.dat    # Benchmark instance files
│
├── helpers/
│   └── extract_kpis.py                   # Script for extracting KPIs from results
│
├── models/
│   ├── ClassicalMILP.mod                 # MILP model formulation
│   └── ConstraintProgramming.mod         # CP model formulation
│
├── raw_data/                             # Directory for raw data (from OR-library)
│
├── cp_results.csv                        # Output/results from CP runs
├── data_transformation.py                # Script for preprocessing/transforming data
├── runner.py                             # Main script to run experiments/models
├── README.md                             # Project documentation
└── .gitignore                            # Git ignore file
```

---

## Problem Description

The **Aircraft Landing Scheduling Problem (ALSP)** involves scheduling the landings of multiple aircraft, each with its:
- Earliest and latest acceptable landing times (time windows)
- Preferred landing time
- Penalties for early/late landings
- Minimum separation times between consecutive landings (to ensure safety)

**Goal:**  
Find a landing schedule for all aircraft that minimizes the total penalty (earliness/lateness), while ensuring all operational and safety constraints are met.

---

## Approaches

### 1. Mixed-Integer Linear Programming (MILP)
- Formulated in `models/ClassicalMILP.mod`
- Uses binary and continuous variables to model order, assignment, and landing times
- Solved via CPLEX (other solvers may be adapted)
- Suitable for larger and more tightly-constrained instances

### 2. Constraint Programming (CP)
- Formulated in `models/ConstraintProgramming.mod`
- Models scheduling as constraint satisfaction with logical rules
- Well-suited for custom or logic-heavy constraints
- May be more sensitive to instance size or tightness

See the report in the repo for detailed mathematical formulations.

---

## Getting Started

**Requirements:**
- Python 3.x
- CPLEX solver (or compatible MILP/CP solvers)
- Common Python libraries: `pandas`, `numpy`, etc.

---

## Usage

### Running Experiments

1. **Prepare Data:**  
   The `data/` folder contains `.dat` files (benchmark instances) for testing.

2. **Run Models:**  
   Use `runner.py` to launch experiments with either model.

3. **KPI Extraction:**  
   Use `helpers/extract_kpis.py` to process results and extract performance metrics.

4. **Data Transformation:**  
   Use `data_transformation.py` if you need to preprocess raw data or convert formats.

---

## Benchmark Instances

Standard benchmark datasets (from the OR-Library) are included in `data/airland1.dat` to `data/airland13.dat`. These enable comparison against published results and scalability tests.

---

## Results

- **MILP Model:**  
  - Consistently finds optimal solutions, with very fast runtimes even for 50 aircraft and multiple runways.
  - Solution quality remains high as problem size grows.
  - Suitable for large-scale, industrial scheduling tasks.

- **CP Model:**  
  - Competitive for small to medium instances.
  - May experience timeouts or higher memory usage on large/tightly-constrained problems.
  - Useful for highly customized scheduling constraints.

---

## References

- [Beasley, J.E., et al. Scheduling Aircraft Landings—The Static Case.](https://doi.org/10.1287/trsc.34.2.180.12302)
- OR-Library: [Aircraft Landing Problem Instances](https://people.brunel.ac.uk/~mastjjb/jeb/orlib/airlandinfo.html)

---

## Contact

For questions or collaboration, contact:
- João Sousa (@jpcsousa12, joao.pedro.sousa@ieee.org)

---

**Happy scheduling!**

