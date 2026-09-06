import os

# 1. Define your arrays for Primitive Volumes (in bohr^3) and c/a ratios
# Note: Since this is the 2-atom cell, your volumes should be roughly half of the 4-atom cell!
volumes = [
181.4889192,
185.5220094,
189.5550996,
193.5881898,
197.62126100,
201.65435102,
203.6708935,
205.68744104,
207.7039805,
209.72052106,
213.75361108,
217.78670110,
221.81979
] 
ca_ratios = [0.51, 0.53, 0.54, 0.55, 0.56, 0.57, 0.59]

# 2. Template using your exact settings
qe_template = """&CONTROL
    calculation  = 'relax',
    prefix  	 = 'betatin_v{pct_str}_ca{ca:.2f}',
    pseudo_dir   = '/home/guest/Rishi-Tushar/pseudopotentials/',
    outdir       = '/home/guest/Rishi-Tushar/bt_silicon/output/Volchange',
    restart_mode = 'from_scratch',
/
&SYSTEM
    ibrav        = 7,
    celldm(1)    = {a_bohr:.5f},      ! Calculated for ibrav=7
    celldm(3)    = {ca:.3f},          ! c/a ratio
    nat          = 2,
    ntyp         = 1,
    ecutwfc      = 50.0,
    ecutrho      = 500.0,
    occupations  = 'smearing',
    smearing     = 'mv',
    degauss      = 0.02,
/
&ELECTRONS
    conv_thr     = 1.0d-8,
    mixing_beta  = 0.6,
/
&IONS
    ion_dynamics = 'bfgs'
/
ATOMIC_SPECIES
 Si  28.086  Si.pbe-n-rrkjus_psl.1.0.0.UPF

ATOMIC_POSITIONS (alat)
 Si   0.000000000   0.000000000   0.000000000
 Si   0.000000000   0.500000000   0.250000000

K_POINTS automatic
 12 12 12 1 1 1
"""

# 3. Generation loop
file_count = 0
for vol in volumes:
    for ca in ca_ratios:
        # CRITICAL MATHEMATICAL CORRECTION FOR IBRAV=7
        a_bohr = ((2.0 * vol) / ca) ** (1.0 / 3.0)
        
        # 1. Calculate the percentage of volume deviation FIRST
        pct = int(round(((vol - 201.65435) / 201.65435) * 100))
        pct_str = f"+{pct}" if pct >= 0 else f"{pct}"
        
        # 2. NOW format the text template (passing pct_str so it matches the template key!)
        input_text = qe_template.format(vol=vol, ca=ca, a_bohr=a_bohr, pct_str=pct_str)
		
        # 3. Define clean filename
        filename = f"btin_v{pct_str}_ca{ca:.2f}.in"
		
        # 4. Open and write the file directly in the current folder
        with open(filename, 'w') as f:
            f.write(input_text)

        file_count += 1

print(f"Success! {file_count} optimized inputs generated in this directory.")