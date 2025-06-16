import subprocess
import os
import csv

from helpers.extract_kpis import extract_milp_kpis, extract_cp_kpis

def run_opl_model(mod_file, dat_file, oplrun_path="oplrun"):
    command = [oplrun_path, mod_file, dat_file]
    result = subprocess.run(command, capture_output=True, text=True)
    return result.stdout, result.stderr

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
        for runway in range(1, 5):
            print(model, s, runway)
            set_r_value(f'./data/airland{s}.dat', runway)
            output, error = run_opl_model('./models/' + model, f'./data/airland{s}.dat')
            print(output)

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