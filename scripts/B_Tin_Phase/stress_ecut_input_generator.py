# List of ecutwfc values to test for Btin stress convergence
ecut_values = [40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 105, 110, 115, 120]

# Template for the Btin input file
template = """&CONTROL
    calculation  = 'scf',
    restart_mode = 'from_scratch',
    prefix       = 'si-bt-Ecut-{ecutwfc}',
    outdir       = '/home/guest/Rishi-Tushar/bt_silicon/output/Stress-convergence/Ecut/',
    pseudo_dir   = '/home/guest/Rishi-Tushar/pseudopotentials/',
    tstress      = .true.
/
&SYSTEM
    ibrav     = 7, 
    celldm(1) = 9.12672449,
    celldm(3) = 0.54476280,
    nat       = 2, 
    ntyp      = 1,
    ecutwfc   = {ecutwfc}.0,
    ecutrho   = {ecutrho}.0,
    occupations = 'smearing',
    smearing    = 'mv',
    degauss     = 0.02
/
&ELECTRONS
    conv_thr    = 1.0d-8
/

ATOMIC_SPECIES
 Si  28.086  Si.pbe-n-rrkjus_psl.1.0.0.UPF

ATOMIC_POSITIONS (crystal)
 Si 0.00 0.00 0.00
 Si 0.50 0.75 0.25

K_POINTS (automatic)
 12 12 12 1 1 1
"""

# Generate the files
for ecutwfc in ecut_values:
    # Scale ecutrho (10x is used here to match your 90/900 template ratio)
    ecutrho = ecutwfc * 10 
    
    filename = f"si-btin-ecut-{ecutwfc}.in"
    with open(filename, "w") as f:
        f.write(template.format(ecutwfc=ecutwfc, ecutrho=ecutrho))
    print(f"Generated: {filename}")

print("\nAll Btin ecut convergence files successfully generated!")