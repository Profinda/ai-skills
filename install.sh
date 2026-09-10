#!/usr/bin/env sh
# ProFinda ai-skills installer.
#
# One-liner:
#   curl -fsSL https://raw.githubusercontent.com/Profinda/ai-skills/main/install.sh | sh
#
# What it does:
#   1. Clones or updates ~/.config/ai-skills from Profinda/ai-skills (main).
#   2. Shows the skills you already have, marking each as GLOBAL, LOCAL (to the
#      repo you ran this from), or not installed.
#   3. Lets you add or remove skills interactively. Adds can be GLOBAL
#      (~/.config/opencode/skills) or LOCAL (the current repo's .claude/skills).
#   4. For LOCAL installs it wires the repo's .claude/skills/shared submodule,
#      updates it to the latest, symlinks the chosen skills, and gitignores them.
#   5. Optionally adds a weekly auto-update line to ~/.zshrc so the global clone
#      stays fresh (brew/rvm style).
#
# Safe to re-run. It never deletes skill content, only symlinks.

set -eu

REPO_URL="git@github.com:Profinda/ai-skills.git"
REPO_URL_HTTPS="https://github.com/Profinda/ai-skills.git"
BRANCH="main"
CLONE_DIR="${AI_SKILLS_HOME:-$HOME/.config/ai-skills}"
GLOBAL_SKILLS_DIR="${OPENCODE_SKILLS_DIR:-$HOME/.config/opencode/skills}"
AUTO_UPDATE_MARKER="# ai-skills weekly auto-update"

# ---------- pretty output ----------------------------------------------------
if [ -t 1 ]; then
  BOLD="$(printf '\033[1m')"; DIM="$(printf '\033[2m')"; RESET="$(printf '\033[0m')"
  GREEN="$(printf '\033[32m')"; YELLOW="$(printf '\033[33m')"; BLUE="$(printf '\033[34m')"; RED="$(printf '\033[31m')"
else
  BOLD=""; DIM=""; RESET=""; GREEN=""; YELLOW=""; BLUE=""; RED=""
fi
say()  { printf '%s\n' "$*"; }
info() { printf '%s==>%s %s\n' "$BLUE" "$RESET" "$*"; }
warn() { printf '%s==>%s %s\n' "$YELLOW" "$RESET" "$*"; }
err()  { printf '%serror:%s %s\n' "$RED" "$RESET" "$*" >&2; }

# ---------- stdin handling for curl | sh ------------------------------------
# When piped (curl | sh) stdin is the script, not the keyboard. Reopen the tty
# so the prompts actually work. If there's no tty we bail with instructions.
if [ ! -t 0 ]; then
  if [ -e /dev/tty ]; then
    exec < /dev/tty
  else
    err "No interactive terminal available. Download and run the script directly:"
    err "  curl -fsSL https://raw.githubusercontent.com/Profinda/ai-skills/$BRANCH/install.sh -o install.sh && sh install.sh"
    exit 1
  fi
fi

ask_yes() { # ask_yes "prompt"  -> returns 0 for yes, 1 for no (default no)
  printf '%s ' "$1"
  read -r _ans || _ans=""
  case "$_ans" in y|Y|yes|YES) return 0 ;; *) return 1 ;; esac
}

# ---------- step 1: clone or update the global clone -------------------------
clone_or_update() {
  if [ -d "$CLONE_DIR/.git" ]; then
    info "Updating $CLONE_DIR"
    git -C "$CLONE_DIR" fetch --quiet origin "$BRANCH"
    git -C "$CLONE_DIR" checkout --quiet "$BRANCH" 2>/dev/null || true
    git -C "$CLONE_DIR" reset --hard --quiet "origin/$BRANCH"
  else
    info "Cloning ai-skills into $CLONE_DIR"
    mkdir -p "$(dirname "$CLONE_DIR")"
    if ! git clone --quiet --branch "$BRANCH" "$REPO_URL" "$CLONE_DIR" 2>/dev/null; then
      warn "SSH clone failed, trying HTTPS"
      git clone --quiet --branch "$BRANCH" "$REPO_URL_HTTPS" "$CLONE_DIR"
    fi
  fi
}

# ---------- discover available skills ---------------------------------------
list_available() { # prints skill names, one per line
  for d in "$CLONE_DIR"/profinda-*/; do
    [ -d "$d" ] || continue
    basename "$d"
  done
}

# ---------- status helpers ---------------------------------------------------
is_global_installed() { # $1 = skill
  [ -L "$GLOBAL_SKILLS_DIR/$1" ] || [ -e "$GLOBAL_SKILLS_DIR/$1" ]
}
is_local_installed() { # $1 = skill ; needs REPO_SKILLS_DIR set
  [ -n "${REPO_SKILLS_DIR:-}" ] && { [ -L "$REPO_SKILLS_DIR/$1" ] || [ -e "$REPO_SKILLS_DIR/$1" ]; }
}

status_label() { # $1 = skill
  _g=n; _l=n
  is_global_installed "$1" && _g=y
  is_local_installed  "$1" && _l=y
  if [ "$_g" = y ] && [ "$_l" = y ]; then printf '%sGLOBAL+LOCAL%s' "$GREEN" "$RESET"
  elif [ "$_g" = y ];               then printf '%sGLOBAL%s' "$GREEN" "$RESET"
  elif [ "$_l" = y ];               then printf '%sLOCAL%s' "$BLUE" "$RESET"
  else printf '%snot installed%s' "$DIM" "$RESET"; fi
}

# ---------- global add / remove ---------------------------------------------
global_add() { # $1 = skill
  mkdir -p "$GLOBAL_SKILLS_DIR"
  _target="$CLONE_DIR/$1"
  _link="$GLOBAL_SKILLS_DIR/$1"
  if [ -e "$_link" ] && [ ! -L "$_link" ]; then
    warn "$1: a real directory exists at $_link (not a symlink); leaving it alone."
    return
  fi
  ln -sfn "$_target" "$_link"
  info "global: linked $1"
}
global_remove() { # $1 = skill
  _link="$GLOBAL_SKILLS_DIR/$1"
  if [ -L "$_link" ]; then rm -f "$_link"; info "global: removed $1"
  elif [ -e "$_link" ]; then warn "$1: $_link is a real directory, not removing."
  fi
}

# ---------- local (repo) add / remove ---------------------------------------
ensure_submodule() {
  # Ensure the current repo has .claude/skills/shared pointing at ai-skills,
  # then update it to the latest main.
  if [ ! -e "$REPO_ROOT/.claude/skills/shared/.git" ] && [ ! -f "$REPO_ROOT/.claude/skills/shared/.git" ]; then
    if git -C "$REPO_ROOT" config --file .gitmodules --get-regexp path >/dev/null 2>&1 && \
       git -C "$REPO_ROOT" config --file .gitmodules --get submodule..claude/skills/shared.url >/dev/null 2>&1; then
      info "Initialising existing .claude/skills/shared submodule"
      git -C "$REPO_ROOT" submodule update --init .claude/skills/shared
    else
      info "Adding ai-skills as a submodule at .claude/skills/shared"
      git -C "$REPO_ROOT" submodule add "$REPO_URL" .claude/skills/shared 2>/dev/null \
        || git -C "$REPO_ROOT" submodule add "$REPO_URL_HTTPS" .claude/skills/shared
    fi
  fi
  info "Updating .claude/skills/shared to latest $BRANCH"
  git -C "$REPO_ROOT" submodule update --remote .claude/skills/shared >/dev/null 2>&1 || true
}

gitignore_add() { # $1 = path relative to repo root
  _gi="$REPO_ROOT/.gitignore"
  touch "$_gi"
  grep -qxF "$1" "$_gi" 2>/dev/null || printf '%s\n' "$1" >> "$_gi"
}
gitignore_remove() { # $1 = path relative to repo root
  _gi="$REPO_ROOT/.gitignore"
  [ -f "$_gi" ] || return 0
  # grep -v exits 1 when it filters out every line; that's success here, so
  # ignore its exit status rather than treating it as an error.
  grep -vxF "$1" "$_gi" > "$_gi.tmp" 2>/dev/null || true
  mv "$_gi.tmp" "$_gi"
}

local_add() { # $1 = skill
  mkdir -p "$REPO_SKILLS_DIR"
  _link="$REPO_SKILLS_DIR/$1"
  if [ -e "$_link" ] && [ ! -L "$_link" ]; then
    warn "$1: a real path exists at $_link (not a symlink); leaving it alone."
    return
  fi
  ( cd "$REPO_SKILLS_DIR" && ln -sfn "shared/$1" "$1" )
  gitignore_add ".claude/skills/$1"
  info "local: linked $1 (gitignored)"
}
local_remove() { # $1 = skill
  _link="$REPO_SKILLS_DIR/$1"
  if [ -L "$_link" ]; then
    rm -f "$_link"; gitignore_remove ".claude/skills/$1"; info "local: removed $1"
  elif [ -e "$_link" ]; then
    warn "$1: $_link is a real path, not removing."
  fi
}

# ---------- weekly auto-update ----------------------------------------------
setup_auto_update() {
  _zshrc="$HOME/.zshrc"
  if grep -qF "$AUTO_UPDATE_MARKER" "$_zshrc" 2>/dev/null; then
    info "Weekly auto-update already configured in ~/.zshrc"
    return
  fi
  {
    printf '\n%s\n' "$AUTO_UPDATE_MARKER"
    printf '%s\n' "if [ -d \"$CLONE_DIR/.git\" ]; then"
    printf '%s\n' "  _ais_stamp=\"\$HOME/.cache/ai-skills-last-update\""
    printf '%s\n' "  if [ ! -f \"\$_ais_stamp\" ] || [ -n \"\$(find \"\$_ais_stamp\" -mtime +7 2>/dev/null)\" ]; then"
    printf '%s\n' "    (git -C \"$CLONE_DIR\" pull --quiet --ff-only >/dev/null 2>&1 && mkdir -p \"\$HOME/.cache\" && touch \"\$_ais_stamp\") &!"
    printf '%s\n' "  fi"
    printf '%s\n' "fi"
  } >> "$_zshrc"
  info "Added weekly auto-update to ~/.zshrc (pulls $CLONE_DIR in the background, once a week)."
}

# ---------- main -------------------------------------------------------------
main() {
  command -v git >/dev/null 2>&1 || { err "git is required"; exit 1; }

  clone_or_update

  # Detect if we're inside a git repo -> enables LOCAL installs.
  REPO_ROOT=""
  REPO_SKILLS_DIR=""
  if git rev-parse --show-toplevel >/dev/null 2>&1; then
    REPO_ROOT="$(git rev-parse --show-toplevel)"
    case "$REPO_ROOT" in
      "$CLONE_DIR"|"$HOME/.config/opencode") REPO_ROOT="" ;;  # don't treat config dirs as target repos
      *) REPO_SKILLS_DIR="$REPO_ROOT/.claude/skills" ;;
    esac
  fi

  say ""
  say "${BOLD}ProFinda ai-skills${RESET}"
  say "  global skills dir : $GLOBAL_SKILLS_DIR"
  if [ -n "$REPO_ROOT" ]; then
    say "  current repo      : $REPO_ROOT (LOCAL installs available)"
  else
    say "  current repo      : ${DIM}none — run from inside a repo for LOCAL installs${RESET}"
  fi
  say ""

  SKILLS="$(list_available)"
  [ -n "$SKILLS" ] || { err "No profinda-* skills found in $CLONE_DIR"; exit 1; }

  say "${BOLD}Available skills:${RESET}"
  _i=0
  for s in $SKILLS; do
    _i=$((_i+1))
    printf '  %2d) %-32s [%s]\n' "$_i" "$s" "$(status_label "$s")"
  done
  say ""
  say "For each skill choose: ${GREEN}g${RESET}=global  ${BLUE}l${RESET}=local  ${RED}r${RESET}=remove  ${DIM}s${RESET}=skip (default)"
  say ""

  _need_submodule=n
  # queue of local adds so we only touch the submodule once
  _local_adds=""

  for s in $SKILLS; do
    printf '  %s [%s] (g/l/r/s)? ' "$s" "$(status_label "$s")"
    read -r choice || choice=""
    case "$choice" in
      g|G) global_add "$s" ;;
      l|L)
        if [ -z "$REPO_ROOT" ]; then
          warn "$s: no repo here, skipping local install."
        else
          _need_submodule=y
          _local_adds="$_local_adds $s"
        fi
        ;;
      r|R)
        global_remove "$s"
        [ -n "$REPO_ROOT" ] && local_remove "$s"
        ;;
      *) : ;;  # skip
    esac
  done

  if [ "$_need_submodule" = y ]; then
    ensure_submodule
    for s in $_local_adds; do local_add "$s"; done
  fi

  say ""
  if ask_yes "Add a weekly auto-update for global skills to ~/.zshrc? (y/N)"; then
    setup_auto_update
  fi

  say ""
  info "Done. Restart OpenCode (or reload the session) to pick up skill changes."
}

main "$@"
