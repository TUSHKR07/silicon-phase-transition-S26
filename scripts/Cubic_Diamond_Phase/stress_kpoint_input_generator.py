# List of ecutwfc values to test
Kpoint_values = [4,6,7,8,9,10,12]

# Template for the input file
template = """&CONTROL
    calculation  = 'scf',
    restart_mode = 'from_scratch',
    prefix       = 'si-cd-Kpoint-{Kpoint}',
    outdir       = '/home/guest/Rishi-Tushar/cd_silicon/silicon-scf/output/Stress-convergence/Kpoint/',
    pseudo_dir   = '/home/guest/Rishi-Tushar/pseudopotentials/',
    tstress      = .true.
/
&SYSTEM
    ibrav     = 2, 
    celldm(1) = 10.336,
    nat       = 2, 
    ntyp      = 1,
    ecutwfc   = 90.0,
    ecutrho   = 900.0
/
&ELECTRONS
    conv_thr    = 1.0d-8
/

ATOMIC_SPECIES
 Si  28.0855  Si.pbe-n-rrkjus_psl.1.0.0.UPF

ATOMIC_POSITIONS (alat)
 Si 0.00 0.00 0.00
 Si 0.25 0.25 0.25

K_POINTS (automatic)
 {Kpoint} {Kpoint} {Kpoint} 1 1 1
"""

# Generate the files in the current directory
for Kpoint in Kpoint_values:
    filename = f"si-cd-Kpoint-{Kpoint}.in"

    with open(filename, "w") as f:
        f.write(template.format(Kpoint=Kpoint))
        
    print(f"Generated: {filename}")

print("\nAll files successfully generated in the current directory!")