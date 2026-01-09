#!/bin/bash
# STAT3D wrapper script - executes Snakemake from /stat3d/workflow/

set -e

# Activate pixi environment directly (faster than 'pixi run')
export PATH="/etc/stat3d/.pixi/envs/default/bin:$PATH"

WORKFLOW_DIR="/stat3d/workflow"

# Handle special commands
if [[ "$1" == "sysinfo" ]]; then
    exec /usr/local/bin/stat3d-sysinfo
fi

# Check if --help or -h is passed
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    stat3d-help.sh
    exit 0
fi

# Verify workflow directory exists
if [ ! -d "$WORKFLOW_DIR" ]; then
    echo "Error: Workflow directory not found at $WORKFLOW_DIR"
    echo "Please mount your project directory with: -v /path/to/project:/stat3d"
    exit 1
fi

# Verify Snakefile exists
if [ ! -f "$WORKFLOW_DIR/Snakefile" ]; then
    echo "Error: Snakefile not found in $WORKFLOW_DIR/"
    echo "Your project directory should contain: workflow/Snakefile"
    exit 1
fi

# Verify config.yaml exists
if [ ! -f "$WORKFLOW_DIR/config.yaml" ]; then
    echo "Error: config.yaml not found in $WORKFLOW_DIR/"
    echo "Your project directory should contain: workflow/config.yaml"
    exit 1
fi

# Navigate to workflow directory and execute snakemake
cd "$WORKFLOW_DIR"
exec snakemake "$@"
