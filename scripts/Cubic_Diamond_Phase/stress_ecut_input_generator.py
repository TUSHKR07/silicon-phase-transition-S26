# List of ecutwfc values to test
ecut_values = [45,50,55,60,65,70,75,80,85,90,95,100,105,110,115,120]

# Template for the input file
template = """&CONTROL
    calculation  = 'scf',
    restart_mode = 'from_scratch',
    prefix       = 'si-cd-Ecut-{ecut}.0',
    outdir       = '/home/guest/Rishi-Tushar/cd_silicon/silicon-scf/output/Stress-convergence/',
    pseudo_dir   = '/home/guest/Rishi-Tushar/pseudopotentials/',
    tstress      = .true.
/
&SYSTEM
    ibrav     = 2, 
    celldm(1) = 10.336,
    nat       = 2, 
    ntyp      = 1,
    ecutwfc   = {ecut}.0,
    ecutrho   = {ecutrho}.0
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
 8 8 8 1 1 1
"""

# Generate the files in the current directory
for ecut in ecut_values:
    filename = f"si-cd-Ecut-{ecut}.in"

    ecutrho = ecut * 10    

    with open(filename, "w") as f:
        f.write(template.format(ecut=ecut, ecutrho=ecutrho))
        
    print(f"Generated: {filename}")

print("\nAll files successfully generated in the current directory!")