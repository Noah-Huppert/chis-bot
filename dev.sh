#!/usr/bin/env bash
declare -ri TRUE=$(true ; echo "$?")
declare -ri FALSE=$(false ; echo "$?")

declare -r PROG_DIR=$(realpath $(dirname "$0"))
declare -r INSTALL_FLAG_FILE="$PROG_DIR/.Pipfile.installed"
declare -r PIPENV_LOCK_FILE="$PROG_DIR/Pipfile.lock"

declare -ri EXIT_PIPENV_INSTALL=10
declare -ri EXIT_PIPENV_LOCK_DATE=11
declare -ri EXIT_INSTALL_FLAG_DATE=12
declare -ri EXIT_TOUCH_INSTALL_FLAG=13
declare -ri EXIT_BOT_RUN=14


# Print message prefixed by timestamp to stdout
log() { # ( msg )
    local -r msg="$1"
    echo "$(date --iso-8601=seconds) $msg"
}

# log() but to stderr
elog() { # ( msg )
    local -r msg="$1"

    log "$msg" >&2
}

# Print error to stdout and exit with code.
die() { # ( code, msg )
    local -ri code="$1"
    local -r msg="$2"

    elog "Error: $msg" >&2
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
    lock_age=$(run_check "$EXIT_PIPENV_LOCK_DATE" "date -r $PIPENV_LOCK_FILE +%s")
    flag_age=$(run_check "$EXIT_INSTALL_FLAG_DATE" "date -r $INSTALL_FLAG_FILE +%s")

    if (($lock_age < $flag_age)); then
	   return "$TRUE"
    else
	   return "$FALSE"
    fi
}

if [[ ! -f "$INSTALL_FLAG_FILE" ]] || dep_lock_newer ; then
    log "Dependencies out of date, installing"
    
    run_check "$EXIT_PIPENV_INSTALL" "pipenv install --dev"
    run_check "$EXIT_TOUCH_INSTALL_FLAG" "touch $INSTALL_FLAG_FILE"
    
    log "Dependencies successfully updated"
else
    log "Dependencies up to date"
fi

log "Running bot"
run_check "$EXIT_BOT_RUN" "pipenv run $PROG_DIR/src/bot.py"
