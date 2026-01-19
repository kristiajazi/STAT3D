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

# Require a config via --configfile or STAT3D_CONFIG
args=("$@")
report_default=0
configfile_path=""
for ((i=0; i<${#args[@]}; i++)); do
    arg="${args[$i]}"
    if [[ "$arg" == "--configfile" ]]; then
        next_index=$((i+1))
        configfile_path="${args[$next_index]:-}"
        break
    elif [[ "$arg" == --configfile=* ]]; then
        configfile_path="${arg#--configfile=}"; break
    fi
done

if [[ -z "$configfile_path" ]]; then
    if [[ -n "${STAT3D_CONFIG:-}" ]]; then
        # Inject configfile if provided via environment variable
        args=("--configfile" "$STAT3D_CONFIG" "${args[@]}")
        configfile_path="$STAT3D_CONFIG"
    else
        echo "Error: No config provided."
        echo "Provide one via: --configfile /path/to/config.yaml"
        echo "Or set STAT3D_CONFIG=/path/to/config.yaml"
        echo "Run: stat3d --help"
        exit 2
    fi
fi

# Determine working directory from config and pass it to Snakemake.
benchmark_dir=""
if [[ -n "$configfile_path" ]]; then
    config_dir=$(python - "$configfile_path" <<'PY'
import sys
import yaml

path = sys.argv[1]
try:
    with open(path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    print(cfg.get("directory", ""))
except Exception:
    print("")
PY
)
    if [[ -n "$config_dir" ]]; then
        # Ensure report output folder exists if --report is used.
        report_path=""
        for ((i=0; i<${#args[@]}; i++)); do
            arg="${args[$i]}"
            if [[ "$arg" == "--report" ]]; then
                next_index=$((i+1))
                report_path="${args[$next_index]:-}"
                break
            elif [[ "$arg" == --report=* ]]; then
                report_path="${arg#--report=}"; break
            fi
        done
        # Support --report-default (no argument) to generate report to results/benchmarks
        for ((i=0; i<${#args[@]}; i++)); do
            if [[ "${args[$i]}" == "--report-default" ]]; then
                report_default=1
                unset 'args[$i]'
            fi
        done
        # Re-pack args array after unset
        args=("${args[@]}")

        if [[ $report_default -eq 1 && -z "$report_path" ]]; then
            report_path="$config_dir/results/benchmarks/stat3d-report.html"
        fi
        benchmark_dir="$config_dir/results/benchmarks"
        mkdir -p "$benchmark_dir"

        if [[ -n "$report_path" ]]; then
            report_dir=$(dirname "$report_path")
            mkdir -p "$report_dir"
        fi
    fi
fi

run_snakemake_with_metrics() {
    local start_ts end_ts start_epoch end_epoch elapsed rc time_log max_rss
    start_ts=$(date -u "+%Y-%m-%dT%H:%M:%SZ")
    start_epoch=$(date +%s)

    if command -v /usr/bin/time >/dev/null 2>&1; then
        time_log=$(mktemp)
        /usr/bin/time -v -o "$time_log" snakemake "${args[@]}"
        rc=$?
    else
        time_log=""
        snakemake "${args[@]}"
        rc=$?
    fi

    end_ts=$(date -u "+%Y-%m-%dT%H:%M:%SZ")
    end_epoch=$(date +%s)
    elapsed=$((end_epoch - start_epoch))

    if [[ -n "$benchmark_dir" ]]; then
        {
            echo "start_ts=${start_ts}"
            echo "end_ts=${end_ts}"
            echo "elapsed_seconds=${elapsed}"
            echo "exit_code=${rc}"
            if [[ -n "$time_log" && -f "$time_log" ]]; then
                max_rss=$(grep -i "Maximum resident set size" "$time_log" | awk -F: '{print $2}' | xargs)
                if [[ -n "$max_rss" ]]; then
                    echo "max_rss_kb=${max_rss}"
                fi
            fi
        } > "$benchmark_dir/workflow_resource_usage.txt"
    fi

    return $rc
}

# Navigate to workflow directory and execute snakemake
cd "$WORKFLOW_DIR"
if [[ $report_default -eq 1 ]]; then
    run_snakemake_with_metrics
    snakemake "${args[@]}" --report "$report_path"
    exit $?
fi
run_snakemake_with_metrics
exit $?
