#!/usr/bin/env bash
declare -ri TRUE=$(true ; echo "$?")
declare -ri FALSE=$(false ; echo "$?")

declare -r PROG_DIR=$(realpath $(dirname "$0"))
declare -r INSTALL_FLAG_FILE="$PROG_DIR/.Pipenv.installed"
declare -r PIPENV_LOCK_FILE="$PROG_DIR/Pipenv.lock"

declare -ri EXIT_PIPENV_INSTALL=10
declare -ri EXIT_PIPENV_LOCK_DATE=11
declare -ri EXIT_INSTALL_FLAG_DATE=12
declare -ri EXIT_TOUCH_INSTALL_FLAG=13
declare -ri EXIT_BOT_PY=14

# Print error to stdout and exit with code.
die() { # ( code, msg )
    local -ri code="$1"
    local -r msg="$2"

    echo "Error: $msg" >&2
    exit "$code"
}

# Run command and if it fails exit with code
run_check() { # ( code, cmd )
    local -ri code="$1"
    local -r cmd="$2"
    
    if ! eval "$cmd"; then
	   die "code" "Failed to run command '$cmd'"
    fi
}

# Determines if dependencies have been installed recently enough
dep_lock_newer() {
    lock_age=$(run_check "$EXIT_PIPENV_LOCK_DATE" "date -r $PIPENV_LOCK_FILE")
    flag_age=$(run_check "$EXIT_INSTALL_FLAG_DATE" "date -r $INSTALL_FLAG_FILE")

    if (($lock_age < $flag_age)); then
	   return "$TRUE"
    else
	   return "$FALSE"
    fi
}

if [[ ! -f "$INSTALL_FLAG_FILE" ]] || dep_lock_newer ; then
    run_check "$EXIT_PIPENV_INSTALL" "pipenv install"
    run_check "$EXIT_TOUCH_INSTALL_FLAG" "touch $INSTALL_FLAG_FILE"
fi

run_check "$EXIT_BOT_PY" "pipenv run ./src/bot.py"
