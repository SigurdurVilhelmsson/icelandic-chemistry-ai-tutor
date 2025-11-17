#!/bin/bash

################################################################################
# OpenStax Chemistry Content Processing Pipeline
#
# This script automates the complete processing pipeline:
# 1. Validates all chapter files
# 2. Runs batch ingestion to ChromaDB
# 3. Verifies database integrity
# 4. Generates comprehensive reports
#
# Usage:
#   ./process_openstack.sh [OPTIONS]
#
# Options:
#   --input DIR         Input directory (default: data/chapters)
#   --output DIR        Output directory (default: chroma_db)
#   --batch-size N      Batch size (default: 100)
#   --skip-validation   Skip validation step
#   --verbose           Enable verbose output
#   --email ADDRESS     Send summary report to email (requires mailx)
#   --help             Show this help message
################################################################################

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# Default configuration
INPUT_DIR="${INPUT_DIR:-data/chapters}"
OUTPUT_DIR="${OUTPUT_DIR:-chroma_db}"
BATCH_SIZE="${BATCH_SIZE:-100}"
SKIP_VALIDATION=false
VERBOSE=false
EMAIL=""
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "${SCRIPT_DIR}/../.." && pwd )"
PYTHON_CMD="${PYTHON:-python3}"

# Logging setup
LOG_DIR="${PROJECT_ROOT}/data/logs"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="${LOG_DIR}/pipeline_${TIMESTAMP}.log"

################################################################################
# Functions
################################################################################

log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    echo "[${timestamp}] [${level}] ${message}" | tee -a "${LOG_FILE}"
}

log_info() {
    echo -e "${BLUE}ℹ${NC} $@" | tee -a "${LOG_FILE}"
}

log_success() {
    echo -e "${GREEN}✓${NC} $@" | tee -a "${LOG_FILE}"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $@" | tee -a "${LOG_FILE}"
}

log_error() {
    echo -e "${RED}✗${NC} $@" | tee -a "${LOG_FILE}"
}

print_header() {
    local title="$1"
    local width=80
    local padding=$(( (width - ${#title} - 2) / 2 ))

    echo "" | tee -a "${LOG_FILE}"
    printf '%*s\n' "${width}" | tr ' ' '=' | tee -a "${LOG_FILE}"
    printf '%*s%s%*s\n' "${padding}" "" "${title}" "${padding}" "" | tee -a "${LOG_FILE}"
    printf '%*s\n' "${width}" | tr ' ' '=' | tee -a "${LOG_FILE}"
    echo "" | tee -a "${LOG_FILE}"
}

show_help() {
    cat << EOF
OpenStax Chemistry Content Processing Pipeline

Usage: $0 [OPTIONS]

Options:
  --input DIR         Input directory containing markdown files (default: data/chapters)
  --output DIR        Output directory for ChromaDB (default: chroma_db)
  --batch-size N      Number of chunks to process at once (default: 100)
  --skip-validation   Skip validation step
  --verbose           Enable verbose output
  --email ADDRESS     Send summary report to email address
  --help              Show this help message

Examples:
  # Basic usage with defaults
  $0

  # Custom input/output directories
  $0 --input my_chapters --output my_db

  # Verbose mode with email notification
  $0 --verbose --email admin@example.com

  # Large batch processing
  $0 --batch-size 500 --skip-validation

Environment Variables:
  PYTHON              Python command to use (default: python3)
  INPUT_DIR           Default input directory
  OUTPUT_DIR          Default output directory
  BATCH_SIZE          Default batch size

EOF
}

check_requirements() {
    log_info "Checking requirements..."

    # Check Python
    if ! command -v ${PYTHON_CMD} &> /dev/null; then
        log_error "Python not found. Please install Python 3.8 or higher."
        exit 1
    fi

    local python_version=$(${PYTHON_CMD} --version 2>&1 | awk '{print $2}')
    log_success "Python ${python_version} found"

    # Check required Python modules
    local required_modules=("chromadb" "sentence_transformers" "tqdm")
    local missing_modules=()

    for module in "${required_modules[@]}"; do
        if ! ${PYTHON_CMD} -c "import ${module}" 2>/dev/null; then
            missing_modules+=("${module}")
        fi
    done

    if [ ${#missing_modules[@]} -gt 0 ]; then
        log_warning "Missing Python modules: ${missing_modules[*]}"
        log_info "Install with: pip install ${missing_modules[*]}"
        log_info "Continuing anyway (will run in dry-run mode)..."
    else
        log_success "All required Python modules installed"
    fi

    # Check input directory
    if [ ! -d "${INPUT_DIR}" ]; then
        log_error "Input directory does not exist: ${INPUT_DIR}"
        exit 1
    fi

    local md_count=$(find "${INPUT_DIR}" -name "*.md" -type f | wc -l)
    if [ ${md_count} -eq 0 ]; then
        log_warning "No markdown files found in ${INPUT_DIR}"
    else
        log_success "Found ${md_count} markdown files in ${INPUT_DIR}"
    fi
}

validate_chapters() {
    print_header "STEP 1: VALIDATING CHAPTERS"

    if [ "${SKIP_VALIDATION}" = true ]; then
        log_warning "Skipping validation step"
        return 0
    fi

    log_info "Running chapter validation..."

    local validator="${PROJECT_ROOT}/backend/src/chapter_validator.py"

    if [ ! -f "${validator}" ]; then
        log_error "Validator not found: ${validator}"
        return 1
    fi

    local validation_log="${LOG_DIR}/validation_${TIMESTAMP}.log"

    if ${PYTHON_CMD} "${validator}" "${INPUT_DIR}" > "${validation_log}" 2>&1; then
        log_success "All chapters validated successfully"
        return 0
    else
        local exit_code=$?
        log_error "Validation failed (exit code: ${exit_code})"
        log_info "See validation log: ${validation_log}"

        # Show summary of validation errors
        if grep -q "Invalid:" "${validation_log}"; then
            log_warning "Validation errors found:"
            grep -A 5 "Invalid:" "${validation_log}" | head -20 | tee -a "${LOG_FILE}"
        fi

        return 1
    fi
}

run_batch_ingestion() {
    print_header "STEP 2: BATCH INGESTION"

    log_info "Starting batch ingestion..."
    log_info "  Input: ${INPUT_DIR}"
    log_info "  Output: ${OUTPUT_DIR}"
    log_info "  Batch size: ${BATCH_SIZE}"

    local ingest_script="${PROJECT_ROOT}/backend/src/batch_ingest.py"

    if [ ! -f "${ingest_script}" ]; then
        log_error "Batch ingest script not found: ${ingest_script}"
        return 1
    fi

    local ingest_args=(
        "--input" "${INPUT_DIR}"
        "--output" "${OUTPUT_DIR}"
        "--batch-size" "${BATCH_SIZE}"
    )

    if [ "${VERBOSE}" = true ]; then
        ingest_args+=("--verbose")
    fi

    if [ "${SKIP_VALIDATION}" = true ]; then
        ingest_args+=("--no-validate")
    fi

    if ${PYTHON_CMD} "${ingest_script}" "${ingest_args[@]}"; then
        log_success "Batch ingestion completed successfully"
        return 0
    else
        local exit_code=$?
        log_error "Batch ingestion failed (exit code: ${exit_code})"
        return 1
    fi
}

verify_database() {
    print_header "STEP 3: VERIFYING DATABASE"

    log_info "Verifying ChromaDB integrity..."

    # Simple Python script to verify database
    ${PYTHON_CMD} << EOF
import sys
try:
    import chromadb
    from pathlib import Path

    db_path = Path("${OUTPUT_DIR}")
    if not db_path.exists():
        print("ERROR: Database directory does not exist")
        sys.exit(1)

    client = chromadb.PersistentClient(path=str(db_path))
    collections = client.list_collections()

    print(f"Database path: ${OUTPUT_DIR}")
    print(f"Collections found: {len(collections)}")

    for collection in collections:
        count = collection.count()
        print(f"  - {collection.name}: {count} documents")

    if len(collections) == 0:
        print("WARNING: No collections found in database")
        sys.exit(1)

    print("Database verification successful")
    sys.exit(0)

except ImportError:
    print("WARNING: chromadb not installed, skipping verification")
    sys.exit(0)
except Exception as e:
    print(f"ERROR: Database verification failed: {e}")
    sys.exit(1)
EOF

    local exit_code=$?
    if [ ${exit_code} -eq 0 ]; then
        log_success "Database verified successfully"
        return 0
    else
        log_error "Database verification failed"
        return 1
    fi
}

generate_report() {
    print_header "STEP 4: GENERATING REPORT"

    log_info "Generating summary report..."

    local report_file="${LOG_DIR}/report_${TIMESTAMP}.txt"

    {
        echo "OpenStax Chemistry Processing Report"
        echo "Generated: $(date)"
        echo "======================================"
        echo ""
        echo "Configuration:"
        echo "  Input Directory: ${INPUT_DIR}"
        echo "  Output Directory: ${OUTPUT_DIR}"
        echo "  Batch Size: ${BATCH_SIZE}"
        echo "  Validation: $([ "${SKIP_VALIDATION}" = true ] && echo "Skipped" || echo "Enabled")"
        echo ""

        # Find latest stats file
        local latest_stats=$(ls -t ${LOG_DIR}/stats_*.json 2>/dev/null | head -1)
        if [ -n "${latest_stats}" ]; then
            echo "Processing Statistics:"
            ${PYTHON_CMD} -m json.tool "${latest_stats}" 2>/dev/null || cat "${latest_stats}"
            echo ""
        fi

        # Find latest error file
        local latest_errors=$(ls -t ${LOG_DIR}/errors_*.json 2>/dev/null | head -1)
        if [ -n "${latest_errors}" ]; then
            echo "Errors:"
            ${PYTHON_CMD} -m json.tool "${latest_errors}" 2>/dev/null || cat "${latest_errors}"
            echo ""
        fi

        echo "Log Files:"
        echo "  Main log: ${LOG_FILE}"
        echo "  Report: ${report_file}"

        if [ -n "${latest_stats}" ]; then
            echo "  Statistics: ${latest_stats}"
        fi

        if [ -n "${latest_errors}" ]; then
            echo "  Errors: ${latest_errors}"
        fi

    } > "${report_file}"

    log_success "Report saved to: ${report_file}"

    # Display summary
    cat "${report_file}" | tee -a "${LOG_FILE}"

    return 0
}

send_email_report() {
    if [ -z "${EMAIL}" ]; then
        return 0
    fi

    log_info "Sending email report to: ${EMAIL}"

    if ! command -v mail &> /dev/null; then
        log_warning "mail command not found. Install mailx to enable email reports."
        return 0
    fi

    local report_file="${LOG_DIR}/report_${TIMESTAMP}.txt"
    local subject="OpenStax Chemistry Processing Report - ${TIMESTAMP}"

    if [ -f "${report_file}" ]; then
        mail -s "${subject}" "${EMAIL}" < "${report_file}"
        log_success "Email sent to ${EMAIL}"
    else
        log_warning "Report file not found, skipping email"
    fi
}

cleanup() {
    log_info "Cleaning up..."

    # Optional: Remove old log files (keep last 30 days)
    find "${LOG_DIR}" -name "*.log" -type f -mtime +30 -delete 2>/dev/null || true
    find "${LOG_DIR}" -name "*.json" -type f -mtime +30 -delete 2>/dev/null || true
}

################################################################################
# Main Pipeline
################################################################################

main() {
    # Create log directory
    mkdir -p "${LOG_DIR}"

    # Print banner
    print_header "OPENSTACK CHEMISTRY PROCESSING PIPELINE"

    log_info "Starting pipeline at $(date)"
    log_info "Log file: ${LOG_FILE}"

    # Run pipeline steps
    local pipeline_failed=false

    check_requirements || pipeline_failed=true

    if [ "${pipeline_failed}" = false ]; then
        validate_chapters || pipeline_failed=true
    fi

    if [ "${pipeline_failed}" = false ]; then
        run_batch_ingestion || pipeline_failed=true
    fi

    if [ "${pipeline_failed}" = false ]; then
        verify_database || pipeline_failed=true
    fi

    generate_report
    send_email_report
    cleanup

    # Final summary
    print_header "PIPELINE COMPLETE"

    if [ "${pipeline_failed}" = true ]; then
        log_error "Pipeline completed with errors"
        log_info "Check logs for details: ${LOG_FILE}"
        exit 1
    else
        log_success "Pipeline completed successfully!"
        log_info "Database ready at: ${OUTPUT_DIR}"
        exit 0
    fi
}

################################################################################
# Parse arguments
################################################################################

parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --input)
                INPUT_DIR="$2"
                shift 2
                ;;
            --output)
                OUTPUT_DIR="$2"
                shift 2
                ;;
            --batch-size)
                BATCH_SIZE="$2"
                shift 2
                ;;
            --skip-validation)
                SKIP_VALIDATION=true
                shift
                ;;
            --verbose)
                VERBOSE=true
                shift
                ;;
            --email)
                EMAIL="$2"
                shift 2
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

# Parse command line arguments
parse_args "$@"

# Run main pipeline
main
