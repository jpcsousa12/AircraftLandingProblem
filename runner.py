import subprocess
import re
import os
import csv
import ast  # For safely evaluating Python list representations

def run_opl_model(mod_file, dat_file, oplrun_path="oplrun"):
    command = [oplrun_path, mod_file, dat_file]
    result = subprocess.run(command, capture_output=True, text=True)
    return result.stdout, result.stderr

def extract_cp_kpis(output):
    kpis = {}
    m_vars = re.search(r'Minimization problem - ([\d\s]+) variables', output)
    m_cons = re.search(r'Minimization problem - [\d\s]+ variables, ([\d\s]+) constraints', output)
    m_mem = re.search(r'Total memory usage\s*:\s*([\d.,]+)\s*MB', output)
    m_time = re.search(r'Time spent in solve\s*:\s*([\d.,]+)s', output)
    m_obj = re.search(r'Best objective\s*:\s*([\d.,]+)', output)
    m_obj2 = re.search(r'OBJECTIVE:\s*([\d.,]+)', output)
    m_bound = re.search(r'Best bound\s*:\s*([\d.,]+)', output)
    m_branches = re.search(r'Number of branches\s*:\s*([\d\s\xa0]+)', output)
    m_fails = re.search(r'Number of fails\s*:\s*([\d\s\xa0]+)', output)
    m_sols = re.search(r'Search completed, ([\d\s\xa0]+) solutions found', output)

    if m_vars: kpis['Variables'] = int(re.sub(r'\s+', '', m_vars.group(1)))
    if m_cons: kpis['Constraints'] = int(re.sub(r'\s+', '', m_cons.group(1)))
    if m_mem:  kpis['Memory_MB'] = float(m_mem.group(1).replace(',', '.'))
    if m_time: kpis['Time_sec'] = float(m_time.group(1).replace(',', '.'))
    if m_obj:  kpis['BestObjective'] = float(m_obj.group(1).replace(',', '.'))
    if m_obj2: kpis['Objective'] = float(m_obj2.group(1).replace(',', '.'))
    if m_bound: kpis['BestBound'] = float(m_bound.group(1).replace(',', '.'))
    if m_branches: kpis['Branches'] = int(re.sub(r'\s+', '', m_branches.group(1)))
    if m_fails: kpis['Fails'] = int(re.sub(r'\s+', '', m_fails.group(1)))
    if m_sols: kpis['SolutionsFound'] = int(re.sub(r'\s+', '', m_sols.group(1)))
    
    return kpis

def extract_milp_kpis(output):
    kpis = {}
    # Constraints (rows)
    m_rows = re.search(r'Reduced MIP has ([\d\s]+) rows', output)
    # Variables (columns)
    m_cols = re.search(r'Reduced MIP has [\d\s]+ rows, ([\d\s]+) columns', output)
    # Nonzeros
    m_nz = re.search(r'Reduced MIP has [\d\s]+ rows, [\d\s]+ columns, and ([\d\s]+) nonzeros', output)
    # Binaries
    m_bin = re.search(r'Reduced MIP has ([\d\s]+) binaries', output)
    # Objective (from last incumbent or OBJECTIVE)
    m_obj = re.search(r'OBJECTIVE:\s*([\d.,]+)', output)
    # Best bound (from "Best Bound" or last table line)
    m_bound = re.search(r'Best Bound\s*:\s*([\d.,]+)', output)
    if not m_bound:
        m_bound = re.search(r'Best bound\s*=\s*([\d.,]+)', output)
    # Gap % (from log, last appearance)
    m_gap = re.findall(r'Gap\s*=\s*([\d.,]+)%', output)
    gap_val = m_gap[-1] if m_gap else None
    # Nodes (from Elapsed time block)
    m_nodes = re.search(r'Nodes\s*=\s*([\d\s]+)', output)
    if not m_nodes:
        # Or, from the last node table (take max Node index)
        nodes = re.findall(r'^\s*(\d+)\s+\d+', output, re.MULTILINE)
        if nodes:
            m_nodes = int(nodes[-1])
        else:
            m_nodes = None
    # Iterations
    m_iter = re.search(r'ItCnt\s*=\s*([\d\s]+)', output)
    # Time (Elapsed time)
    m_time = re.search(r'Elapsed time\s*=\s*([\d.,]+) sec', output)
    # Solutions
    m_sol = re.search(r'solutions = ([\d\s]+)', output)
    
    # Assign and clean up
    if m_rows: kpis['Rows'] = int(re.sub(r'\s+', '', m_rows.group(1)))
    if m_cols: kpis['Columns'] = int(re.sub(r'\s+', '', m_cols.group(1)))
    if m_nz: kpis['Nonzeros'] = int(re.sub(r'\s+', '', m_nz.group(1)))
    if m_bin: kpis['Binaries'] = int(re.sub(r'\s+', '', m_bin.group(1)))
    if m_obj: kpis['Objective'] = float(m_obj.group(1).replace(',', '.'))
    if m_bound: kpis['BestBound'] = float(m_bound.group(1).replace(',', '.'))
    if gap_val: kpis['GapPercent'] = float(gap_val.replace(',', '.'))
    # Use solutions from last summary or from table
    if m_sol: kpis['Solutions'] = int(re.sub(r'\s+', '', m_sol.group(1)))
    # Nodes
    if m_nodes and hasattr(m_nodes, 'group'):
        kpis['Nodes'] = int(re.sub(r'\s+', '', m_nodes.group(1)))
    elif isinstance(m_nodes, int):
        kpis['Nodes'] = m_nodes
    # Iterations
    if m_iter: kpis['Iterations'] = int(re.sub(r'\s+', '', m_iter.group(1)))
    # Time
    if m_time: kpis['Time_sec'] = float(m_time.group(1).replace(',', '.'))

    return kpis

def set_r_value(filename, new_r_value):
    with open(filename, "r") as file:
        lines = file.readlines()
    
    # Update R = ... line
    for i, line in enumerate(lines):
        if line.strip().startswith("R ="):
            lines[i] = f"R = {new_r_value};\n"
            break
    
    with open(filename, "w") as file:
        file.writelines(lines)

models = os.listdir('./models')
simulations = os.listdir('./data')

milp_kpis_list = []
cp_kpis_list = []

milp_file = "milp_results.csv"
cp_file = "cp_results.csv"

# Remove existing files (optional, for fresh run)
for filename in [milp_file, cp_file]:
    if os.path.exists(filename):
        os.remove(filename)

milp_header_written = False
cp_header_written = False

for model in models:
    for s in range(1, 9):
        for runway in range(1, 4):
            print(model, s, runway)
            set_r_value(f'./data/airland{s}.dat', runway)
            output, error = run_opl_model('./models/' + model, f'./data/airland{s}.dat')

            if model == "ClassicalMILP.mod":
                kpis = extract_milp_kpis(output)
                kpis['model'] = model
                kpis['airland'] = s
                kpis['runway'] = runway
                # Write immediately to milp_file
                mode = 'a'
                file_exists = os.path.exists(milp_file)
                with open(milp_file, mode, newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=kpis.keys())
                    if not file_exists or not milp_header_written:
                        writer.writeheader()
                        milp_header_written = True
                    writer.writerow(kpis)

            elif model == "ConstraintProgramming.mod":
                kpis = extract_cp_kpis(output)
                kpis['model'] = model
                kpis['airland'] = s
                kpis['runway'] = runway
                # Write immediately to cp_file
                mode = 'a'
                file_exists = os.path.exists(cp_file)
                with open(cp_file, mode, newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=kpis.keys())
                    if not file_exists or not cp_header_written:
                        writer.writeheader()
                        cp_header_written = True
                    writer.writerow(kpis)