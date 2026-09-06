#!/bin/bash

PW_EXEC="pw.x"
N_CORES=6
OUTPUT_DIR="/home/guest/Rishi-Tushar/cd_silicon/silicon-scf/output/Stress-convergence/Kpoint/"

if [ ! -d "$OUTPUT_DIR" ]; then
    echo "❌ ERROR: The directory $OUTPUT_DIR does not exist."
    exit 1
fi

echo "=========================================================="
echo " Starting automated Quantum ESPRESSO queue..."
echo " Outputs will be directed to: $OUTPUT_DIR"
echo " Timestamp: $(date)"
echo "=========================================================="

for INPUT_FILE in *.in; do
    
    [ -e "$INPUT_FILE" ] || { echo "No .in files found."; exit 1; }

    BASENAME="${INPUT_FILE%.in}"
    
    OUTPUT_FILE="${OUTPUT_DIR}${BASENAME}.out"
    LOG_FILE="${OUTPUT_DIR}${BASENAME}.log"

    echo "--> Processing: $INPUT_FILE"

    mpirun -np $N_CORES $PW_EXEC -in $INPUT_FILE > "$OUTPUT_FILE" 2> "$LOG_FILE"

    if grep -q "JOB DONE" "$OUTPUT_FILE"; then
        echo "    ✓ Success: $BASENAME finished."
    else
        echo "    ❌ ERROR: $BASENAME failed."
        echo "    Check $OUTPUT_FILE or $LOG_FILE for details."
        exit 1
    fi
    
    echo "----------------------------------------------------------"
done

echo "=========================================================="
echo " All pending jobs completed successfully!"
echo "=========================================================="
