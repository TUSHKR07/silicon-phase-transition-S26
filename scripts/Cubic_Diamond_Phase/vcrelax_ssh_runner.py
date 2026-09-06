import os
import subprocess
import re

# ==========================================
# 1. CONFIGURATION (SSH and Paths)
# ==========================================

#REMOTE SERVER SSH CREDENTIALS
SSH_USER="guest"
SSH_HOST="172.28.2.58"

# Pressures converted from your GPa table to kbar (GPa * 10)

PRESSURES = [149.776,115.874,88.834,64.048,41.344,20.563,12.210,9.690,1.560,0.000,-6.074,-15.801,-29.469,-44.103,-55.599]
PHASE_NAME = "si_cd_Vc-relax"

#REMOTE PATHS

PW_EXEC = "/home/guest/q-e-qe-7.2/bin/pw.x"
REMOTE_INPUT_DIR = "/home/guest/Rishi-Tushar/cd_silicon/input/Volchange/Vc-relax/"
REMOTE_PSEUDO_DIR = "/home/guest/Rishi-Tushar/pseudopotentials/"
REMOTE_OUTDIR = "/home/guest/Rishi-Tushar/cd_silicon/output/Volchange/Vc-relax/"


# INITIAL PARAMETERS FOR ibrav = 2
# (Replace these with your best relaxed values for the Cd phase)
INITIAL_CELLDM1 = 9.90   # 'a' lattice parameter in Bohr

# For ibrav=2 primitive cell, nat=2. Keep in crystal coordinates.
INITIAL_POSITIONS = """ATOMIC_POSITIONS (crystal)
 Si   0.00000000   0.00000000   0.00000000
 Si   0.25000000   0.25000000   0.25000000"""

# ==========================================
# 2. INPUT FILE GENERATOR (ibrav = 2)
# ==========================================
def generate_input(p_kbar, celldm1, pos_block):

    p_Gpa = round(p_kbar/10,3)

    input_text = f"""&CONTROL
    calculation   = 'vc-relax',
    prefix        = '{PHASE_NAME}_{p_Gpa}Gpa',
    pseudo_dir    = '{REMOTE_PSEUDO_DIR}',
    outdir        = '{REMOTE_OUTDIR}',
    forc_conv_thr = 1.0d-4
/

&SYSTEM
    ibrav       = 2,
    celldm(1)   = {celldm1:.6f},
    nat         = 2,
    ntyp        = 1,
    ecutwfc     = 90.0,
    ecutrho     = 360.0,
/

&ELECTRONS
    conv_thr    = 1.0d-8
/

&IONS
    ion_dynamics = 'bfgs'
/

&CELL
    cell_dynamics  = 'bfgs',
    press          = {p_kbar},
    press_conv_thr = 0.5,
    cell_dofree    = 'ibrav'
/

ATOMIC_SPECIES
 Si  28.086  Si.pbe-n-rrkjus_psl.1.0.0.UPF

{pos_block}

K_POINTS automatic
 8 8 8 1 1 1
"""
    return input_text

# ==========================================
# 3. REMOTE EXECUTION
# ==========================================
current_celldm1 = INITIAL_CELLDM1
current_positions = INITIAL_POSITIONS

print(f"Starting ibrav=2 sequential pressure ramp for {PHASE_NAME}...")

for p in PRESSURES:
    p_Gpa = round(p/10,3)
    print(f"\n--- Processing Pressure: {p_Gpa} Gpa ---")

    in_filename = f"{PHASE_NAME}_{p_Gpa}Gpa.in"
    out_filename = f"{PHASE_NAME}_{p_Gpa}Gpa.out"

    # 1. Write the input file
    with open(in_filename, "w") as f:
        f.write(generate_input(p, current_celldm1, current_positions))
    print(f"[Local] Created input file: {in_filename}")

    # 2. Copy the input file to remote server
    print(f"[SSH] Transferring input file to remote server...")
    scp_to_cmd = f"scp {in_filename} {SSH_USER}@{SSH_HOST}:{REMOTE_INPUT_DIR}"
    subprocess.run(scp_to_cmd, shell=True, check=True)

    # 3. Execute Quantum ESPRESSO via MPI on the remote server
    print(f"[SSH] Launching mpirun -np 16 on remote host...")
    remote_exec_cmd = (
        f"ssh {SSH_USER}@{SSH_HOST} "
        f"\"export HWLOC_COMPONENTS=-gl;  unset DISPLAY;source ~/.bashrc; cd {REMOTE_INPUT_DIR} && mpirun -np 16 {PW_EXEC} < {in_filename} > {REMOTE_OUTDIR}{out_filename}\""
    )
    subprocess.run(remote_exec_cmd, shell=True, check=True)

    # 4: Pull the generated output file back to your local machine
    print(f"[SSH] Pulling output file back to local machine...")
    scp_from_cmd = f"scp {SSH_USER}@{SSH_HOST}:{REMOTE_OUTDIR}{out_filename} ."
    subprocess.run(scp_from_cmd, shell=True, check=True)

    # 5: Read local output file copy to check convergence
    with open(out_filename, "r") as f:
        out_content = f.read()

    if "JOB DONE" not in out_content:
        print(f"CRITICAL ERROR: Calculation failed on remote at {p_Gpa} Gpa. Pipeline stopped.")
        break
    else:
        print(f"[Local] Confirmed 'JOB DONE' for {p_Gpa} Gpa.")

    # 6: Parse the coordinates from the downloaded output file
    coord_block = re.search(r"Begin final coordinates(.*?)End final coordinates", out_content, re.DOTALL)

    if coord_block:
        block_text = coord_block.group(1)

        # 1. Parse Atomic Positions
        pos_match = re.search(r"(ATOMIC_POSITIONS.*)", block_text, re.DOTALL)
        if pos_match:
            current_positions = pos_match.group(1).strip()

        # 2. Correctly Parse and compute new celldm(1) from the vector matrix
        alat_match = re.search(r"CELL_PARAMETERS\s*\(\s*alat\s*=\s*([\d\.]+)\s*\)", block_text, re.IGNORECASE)
        if alat_match:
            alat_header = float(alat_match.group(1))

            vectors = re.findall(r"^\s*([\-\d\.]+)\s+([\-\d\.]+)\s+([\-\d\.]+)", block_text, re.MULTILINE)
            if len(vectors) >= 3:
                v1_z = float(vectors[0][2])
                
                # FIXED MATH FOR IBRAV=2: 
                # Since primitive v1_z = a / (2 * alat), the true conventional 'a' is 2 * alat * v1_z
                current_celldm1 = 2.0 * alat_header * abs(v1_z)

            print(f"[Update] Coordinates successfully updated for next run.")
            print(f"         New celldm(1) = {current_celldm1:.6f}")
        else:
            print("ERROR: Failed to parse CELL_PARAMETERS from output. Stopping.")
            break
    else:
        print("ERROR: 'Begin final coordinates' block not found. Stopping.")
        break
