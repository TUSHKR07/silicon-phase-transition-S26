# List of k-point grid dimensions to test for Btin
Kpoint_values = [6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26]

# Template for the Btin input file
template = """&CONTROL
    calculation  = 'scf',
    restart_mode = 'from_scratch',
    prefix       = 'si-btin-Kpoint-{Kpoint}',
    outdir       = '/home/guest/Rishi-Tushar/bt_silicon/output/Stress-convergence/Kpoint/',
    pseudo_dir   = '/home/guest/Rishi-Tushar/pseudopotentials/',
    tstress      = .true.
/
&SYSTEM
    ibrav     = 7, 
    celldm(1) = 9.12672449,
    celldm(3) = 0.54476280,
    nat       = 2, 
    ntyp      = 1,
    ecutwfc   = 90.0,
    ecutrho   = 900.0,
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
 {Kpoint} {Kpoint} {Kpoint} 1 1 1
"""

# Generate the files
for Kpoint in Kpoint_values:
    filename = f"si-btin-Kpoint-{Kpoint}.in"
    with open(filename, "w") as f:
        f.write(template.format(Kpoint=Kpoint))
    print(f"Generated: {filename}")

print("\nAll Btin K-point files successfully generated!")