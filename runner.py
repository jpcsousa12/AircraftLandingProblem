import subprocess
import re
import os
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
    if m_obj2: kpis['OBJECTIVE'] = float(m_obj2.group(1).replace(',', '.'))
    if m_bound: kpis['BestBound'] = float(m_bound.group(1).replace(',', '.'))
    if m_branches: kpis['Branches'] = int(re.sub(r'\s+', '', m_branches.group(1)))
    if m_fails: kpis['Fails'] = int(re.sub(r'\s+', '', m_fails.group(1)))
    if m_sols: kpis['SolutionsFound'] = int(re.sub(r'\s+', '', m_sols.group(1)))
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
print(simulations)

for model in models:
    for s in range(1,9):
        for runway in range(1,5):
            set_r_value(f'./data/airland{s}.dat', runway)
            output, error = run_opl_model('./models/' + model, f'./data/airland{s}.dat')
            print(output)
