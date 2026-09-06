import os
import re
import subprocess
import pandas as pd

# Path configuration relative to script execution location
TEMPLATE_PATH = "../../input-templates/B_Tin_Phase/benchmarking.in"
INPUT_DIR = "../../input-files/B_Tin_Phase/benchmarking/"
OUTPUT_DIR = "../../data/sample-outputs/B_Tin_Phase/benchmarking/"
PROCESSED_DATA_DIR = "../../data/processed/B_Tin_Phase/benchmarking/"

# Quantum ESPRESSO executable path on Linux
PW_EXEC = "pw.x"

# Ensure directories exist
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)


def load_template(path):
    with open(path, "r") as f:
        return f.read()


def check_qe_status(out_filepath):
    """
    Scans output file to determine execution status.
    Returns: (is_successful, total_energy, num_atoms, error_message)
    """
    if not os.path.exists(out_filepath):
        return False, None, None, "Output file missing"

    total_energy = None
    num_atoms = 2
    job_done = False
    convergence_failed = False

    with open(out_filepath, "r") as f:
        content = f.read()

        # Check for successful completion flag
        if "JOB DONE." in content:
            job_done = True

        # Check for convergence failure or QE aborts
        if "convergence NOT achieved" in content:
            convergence_failed = True

        # Extract number of atoms
        atom_match = re.search(r"number of atoms/cell\s*=\s*(\d+)", content)
        if atom_match:
            num_atoms = int(atom_match.group(1))

        # Extract total energy
        energy_match = re.search(r"!\s*total energy\s*=\s*([-\d\.]+)\s*Ry", content)
        if energy_match:
            total_energy = float(energy_match.group(1))

    # Evaluate Failsafe State
    if job_done and total_energy is not None and not convergence_failed:
        return True, total_energy, num_atoms, "SUCCESS"
    elif convergence_failed:
        return False, total_energy, num_atoms, "SCF_CONVERGENCE_FAILED"
    else:
        return False, None, num_atoms, "CRASHED_OR_ABORTED"


def safe_run_qe(cmd, out_filepath):
    """
    Executes QE command safely without crashing the master script if QE fails.
    """
    try:
        # check=False prevents Python from throwing an exception on non-zero exit codes
        result = subprocess.run(
            cmd, shell=True, check=False, capture_output=True, text=True
        )

        if result.returncode != 0:
            print(
                f" [WARNING] QE process exited with code {result.returncode}. Logged to output."
            )

    except Exception as e:
        print(f" [CRITICAL ERROR] Failed to spawn process: {e}")


def run_ecut_benchmark(  #all the following paramerters are explained in the end
    ecut_list,
    fixed_k,
    dual_ratio,
    template_str,
    nprocs=1,                        # default value
    run_qe=True
):
    results = []

    for ecut in ecut_list:
        ecutrho = ecut * dual_ratio
        file_prefix = f"scf_bt_ecut_{ecut}"
        in_file = os.path.join(INPUT_DIR, f"{file_prefix}.in")
        out_file = os.path.join(OUTPUT_DIR, f"{file_prefix}.out")

        # 1. Generate Input File
        input_content = (
            template_str.replace("{ecutwfc}", str(ecut))
            .replace("{ecutrho}", str(ecutrho))
            .replace("{k}", str(fixed_k))
        )
        with open(in_file, "w") as f:
            f.write(input_content)

        # 2. Failsafe Execution
        if run_qe:
            cmd = (
                f"mpirun -np {nprocs} {PW_EXEC} < {in_file} > {out_file}"
                if nprocs > 1
                else f"{PW_EXEC} < {in_file} > {out_file}"
            )
            print(f"Running ecutwfc = {ecut} Ry...", end="", flush=True)
            safe_run_qe(cmd, out_file)

        # 3. Failsafe Status Check
        success, energy, natoms, status = check_qe_status(out_file)

        if success:
            results.append(
                {
                    "ecutwfc_Ry": ecut,
                    "total_energy_Ry": energy,
                    "natoms": natoms,
                    "status": status
                }
            )
            print(f" [SUCCESS] Energy = {energy:.8f} Ry")
        else:
            print(f" [FAILED] Reason: {status}")

            # Still record the failed run in results so you can trace what failed

            results.append(
                {
                    "ecutwfc_Ry": ecut,
                    "total_energy_Ry": None,
                    "natoms": natoms,
                    "status": status,
                }
            )

    # Filter only successful runs for relative energy calculations
    df = pd.DataFrame(results)
    successful_df = df[df["status"] == "SUCCESS"].copy()

    if not successful_df.empty:
        ref_energy = successful_df["total_energy_Ry"].iloc[-1]
        natoms_val = successful_df["natoms"].iloc[0]
        df["delta_E_Ry_per_atom"] = df["total_energy_Ry"].apply(
            lambda x: (
                ((x - ref_energy) / natoms_val)
                if pd.notnull(x)
                else None
            )
        )

    # Save full log (including failed runs) to CSV
    csv_path = os.path.join(PROCESSED_DATA_DIR, "ecut_convergence.csv")
    df.to_csv(csv_path, index=False)
    print(f"Saved run summary to: {csv_path}\n")


def run_kpoint_benchmark(  #all the following paramerters are explained in the end
    k_list,
    fixed_ecut,
    dual_ratio,
    template_str,
    nprocs=1,                        # default value
    run_qe=True
):

    """Runs K-point grid convergence loop."""

    results = []
    ecutrho = fixed_ecut * dual_ratio
    print("\n==========================================")
    print(" Running Beta-tin K-Point Grid Convergence ")
    print("===========================================\n")

    for k in k_list:
        file_prefix = f"scf_bt_kpoint_{k}"
        in_file = os.path.join(INPUT_DIR, f"{file_prefix}.in")
        out_file = os.path.join(OUTPUT_DIR, f"{file_prefix}.out")

        # 1. Generate Input File
        input_content = (
            template_str.replace("{ecutwfc}", str(fixed_ecut))
            .replace("{ecutrho}", str(ecutrho))
            .replace("{k}", str(k))
        )
        with open(in_file, "w") as f:
            f.write(input_content)

        # 2. Run Quantum ESPRESSO on Linux
        if run_qe:
            cmd = (
                f"mpirun -np {nprocs} {PW_EXEC} < {in_file} > {out_file}"
                if nprocs > 1
                else f"{PW_EXEC} < {in_file} > {out_file}"
            )
            print(f"Executing: K-grid = {k}x{k}x{k} (offset 1 1 1)...", end="", flush=True)
            safe_run_qe(cmd, out_file)

        # 3. Failsafe Status Check
        success, energy, natoms, status = check_qe_status(out_file)

        if success:
            results.append(
                {
                    "k_grid": f"{k}x{k}x{k}",
                    "k_value": k,
                    "total_energy_Ry": energy,
                    "natoms": natoms,
                    "status": status,
                }
            )
            print(f" [SUCCESS] Energy = {energy:.8f} Ry")
        else:
            print(f" [FAILED] Reason: {status}")
            results.append(
                {
                    "k_grid": f"{k}x{k}x{k}",
                    "k_value": k,
                    "total_energy_Ry": None,
                    "natoms": natoms,
                    "status": status,
                }
            )

    # 4. Save Processed CSV Data
    df = pd.DataFrame(results)
    successful_df = df[df["status"] == "SUCCESS"].copy()

    if not successful_df.empty:
        ref_energy = successful_df["total_energy_Ry"].iloc[-1]
        natoms_val = successful_df["natoms"].iloc[0]
        df["delta_E_Ry_per_atom"] = df["total_energy_Ry"].apply(
            lambda x: (
                ((x - ref_energy) / natoms_val)
                if pd.notnull(x)
                else None
            )
        )

    csv_path = os.path.join(PROCESSED_DATA_DIR, "kpoint_convergence.csv")
    df.to_csv(csv_path, index=False)
    print(f"\n Saved processed data to: {csv_path}")


if __name__ == "__main__":
    template = load_template(TEMPLATE_PATH)

    # Convergence scan ranges
    ecut_values = [40, 50, 60, 70, 80, 90, 100, 110, 120]   # set all the values you'd like to check

    k_values = [8,10,12,14,16,18,20]   # set all the values you'd like to check

    run_ecut_benchmark(
        ecut_values,
        fixed_k=14,             # set the Kpoint mesh to be taken for all Ecut calculations (offset by 1 1 1)
        dual_ratio=10,          # (ecutrho/ecutwfc) ~ should be 8-12 for USPPs
        template_str=template,
        nprocs=1,
        run_qe=True             # required for python scripts to run pw.x on linux
    )
    run_kpoint_benchmark(
        k_values,
        fixed_ecut=90,          # set the Ecut value taken for all Kpoint calculations
        dual_ratio=10,          # (ecutrho/ecutwfc) ~ should be 8-12 for USPPs
        template_str=template,
        nprocs=1,
        run_qe=True             # required for python scripts to run pw.x on linux
    )