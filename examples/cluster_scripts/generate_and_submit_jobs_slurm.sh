#!/bin/bash

# -----------------------------------------------------------------------------
# Script Name:  Generate and Submit SLURM Simulation Jobs
#
# Description:  This script generates a series of SLURM submission scripts
#               based on a template. It varies the --prob-stem parameter and
#               updates the job name for each generated script. After 
#               generating these scripts, it submits them to the job queue 
#               using sbatch.
#
#               The generated scripts will incorporate a simulation number
#               for batch identification.
#
# Usage:        ./generate_and_submit_jobs_slurm.sh
# -----------------------------------------------------------------------------

# Simulation number to identify the batch of simulations.
SIMULATION_NUMBER=16

# Initial and final values for the 'prob-stem' parameter between files.
INITIAL_VAL=0.65
FINAL_VAL=0.75
FILE_STEP=0.02

# Step value for the 'prob-stem' parameter within a single file.
INTERNAL_STEP=0.01

# Template file name to use as the base for generating new scripts.
TEMPLATE_FILE="submit_slurm_sim_${SIMULATION_NUMBER}_template.sh"

# Initialize job index (j).
j=1

#-----------------------------------------------------------
# generate_slurm_submission_script Function
#
# Generates a single submission script for a SLURM cluster by modifying
# a template file.
#
# Arguments:
#   val1 : The starting value of 'prob-stem' for the simulation.
#   j    : The index of the job, used for naming the generated files.
#
# Returns:
#   None
#-----------------------------------------------------------
generate_slurm_submission_script() {
  local val1=$1
  local val2=$(echo "$val1 + $INTERNAL_STEP" | bc)
  local j=$2

  # Create the new file name.
  local file_name="submit_slurm_sim_${SIMULATION_NUMBER}_${j}.sh"

  # Modify the template using 'sed' and output to the new file.
  sed "s/--job-name=tumorsphere_1/--job-name=tumorsphere_${j}/g;
       s/--prob-stem \"0.65,0.66\"/--prob-stem \"${val1},${val2}\"/g" \
  $TEMPLATE_FILE > $file_name

  # Make the generated file executable.
  chmod +x $file_name
}

# Loop through the range of 'prob-stem' values to generate scripts.
for val1 in $(seq $INITIAL_VAL $FILE_STEP $FINAL_VAL); do
  # Generate a new submission script for this value.
  generate_slurm_submission_script $val1 $j
  
  # Increment the job index for the next iteration.
  ((j++))
done

# Loop to submit all generated scripts to the job queue.
j=1
for val1 in $(seq $INITIAL_VAL $FILE_STEP $FINAL_VAL); do
  sbatch "submit_slurm_sim_${SIMULATION_NUMBER}_${j}.sh"
  ((j++))
done
