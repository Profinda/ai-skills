#!/usr/bin/env sh
# ProFinda ai-skills installer.
#
# Install (download then run — this installer is interactive, so do NOT pipe it
# straight into `sh`; `curl | sh` gives the script no keyboard and it can't prompt):
#   curl -fsSL https://raw.githubusercontent.com/Profinda/ai-skills/main/install.sh -o /tmp/ai-skills-install.sh && sh /tmp/ai-skills-install.sh
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

# positional get/set on a space-separated list (1-based), POSIX sh (no arrays)
field() { # $1 = list  $2 = index
  _n=0
  for _v in $1; do
    _n=$((_n+1))
    [ "$_n" = "$2" ] && { printf '%s' "$_v"; return; }
  done
}
set_field() { # $1 = list  $2 = index  $3 = new value -> echoes updated list
  _n=0; _out=""
  for _v in $1; do
    _n=$((_n+1))
    [ "$_n" = "$2" ] && _v="$3"
    _out="$_out $_v"
  done
  printf '%s' "${_out# }"
}

# ---------- stdin handling -------------------------------------------------
# This installer is interactive: it reads your choices from the keyboard.
# If stdin isn't a terminal (e.g. you ran `curl ... | sh`, which feeds the
# downloaded script to sh as stdin, leaving no keyboard) try to grab the
# controlling terminal. If that fails, stop with clear instructions instead
# of hanging silently at a prompt you can't see.
if [ ! -t 0 ]; then
  if [ -e /dev/tty ] && exec < /dev/tty; then
    :
  else
    err "This installer is interactive and has no terminal to read from."
    err "Don't pipe it into sh. Download it, then run it:"
    err "  curl -fsSL https://raw.githubusercontent.com/Profinda/ai-skills/$BRANCH/install.sh -o /tmp/ai-skills-install.sh && sh /tmp/ai-skills-install.sh"
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
  # Never let git block on an invisible credential/host-key prompt: fail fast instead of hanging.
  export GIT_TERMINAL_PROMPT=0
  if [ -d "$CLONE_DIR/.git" ]; then
    info "Updating skills in $CLONE_DIR ..."
    git -C "$CLONE_DIR" fetch origin "$BRANCH" || { err "Could not fetch updates from origin."; exit 1; }
    git -C "$CLONE_DIR" checkout "$BRANCH" >/dev/null 2>&1 || true
    git -C "$CLONE_DIR" reset --hard "origin/$BRANCH" >/dev/null
    info "Up to date."
  else
    info "Cloning ai-skills into $CLONE_DIR (first run downloads the repo) ..."
    mkdir -p "$(dirname "$CLONE_DIR")"
    if git clone --branch "$BRANCH" "$REPO_URL" "$CLONE_DIR" 2>/dev/null; then
      :
    else
      warn "SSH clone unavailable, using HTTPS ..."
      git clone --branch "$BRANCH" "$REPO_URL_HTTPS" "$CLONE_DIR" \
        || { err "Clone failed. Check your network and GitHub access, then re-run."; exit 1; }
    fi
    info "Clone complete."
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

# current state of a skill as a single char: G (global), L (local), - (missing)
current_state() { # $1 = skill
  if is_global_installed "$1"; then printf 'G'
  elif is_local_installed "$1"; then printf 'L'
  else printf '-'; fi
}

# human colour for a state char
state_color() { # $1 = state char
  case "$1" in
    G) printf '%s' "$GREEN" ;;
    L) printf '%s' "$BLUE" ;;
    *) printf '%s' "$DIM" ;;
  esac
}

# one-word meaning for a want vs now transition, for the confirmation summary
transition_word() { # $1 = now  $2 = want
  [ "$1" = "$2" ] && { printf 'keep'; return; }
  case "$2" in
    G) printf 'set global' ;;
    L) printf 'set local' ;;
    -) printf 'remove' ;;
  esac
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
  # Ensure the current repo has .claude/skills/shared, then update it to the
  # latest of $BRANCH. If it already exists we still bump it to latest (that is
  # the whole point: stop repos drifting behind the shared skills). The bump
  # shows up as a submodule-pointer change in `git status` for you to commit.
  if [ -e "$REPO_ROOT/.claude/skills/shared/.git" ]; then
    info ".claude/skills/shared submodule present — updating to latest $BRANCH"
  elif git -C "$REPO_ROOT" config --file .gitmodules --get submodule..claude/skills/shared.url >/dev/null 2>&1; then
    info "Initialising existing .claude/skills/shared submodule"
    git -C "$REPO_ROOT" submodule update --init .claude/skills/shared >/dev/null 2>&1 || true
  else
    info "Adding ai-skills as a submodule at .claude/skills/shared"
    git -C "$REPO_ROOT" submodule add "$REPO_URL" .claude/skills/shared 2>/dev/null \
      || git -C "$REPO_ROOT" submodule add "$REPO_URL_HTTPS" .claude/skills/shared \
      || { err "Could not add the ai-skills submodule."; return 1; }
  fi
  # Pull the submodule to the tip of $BRANCH from its remote.
  if git -C "$REPO_ROOT" submodule update --remote --init .claude/skills/shared >/dev/null 2>&1; then
    _sub_head="$(git -C "$REPO_ROOT/.claude/skills/shared" rev-parse --short HEAD 2>/dev/null)"
    info "Submodule now at $_sub_head. If the pointer moved, commit it: git add .claude/skills/shared"
  else
    warn "Could not update the submodule to latest; using whatever commit is checked out."
  fi
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

  # Greeting.
  say ""
  say "${BOLD}ProFinda ai-skills installer${RESET}"
  say "This installer is interactive. It shows every skill and its current location,"
  say "then asks you, one skill at a time, what you want its state to be."
  say ""
  say "  The 'now' column shows where each skill is currently active:"
  say "    ${GREEN}G${RESET}=global   ${BLUE}L${RESET}=local (this repo)   ${DIM}-${RESET}=not active"
  say "  For each skill, set the desired state (press Enter to keep it unchanged):"
  say "    ${GREEN}g${RESET}=global   ${BLUE}l${RESET}=local   ${RED}-${RESET}=remove / not active"
  say ""
  say "  ${DIM}Note: a shared skill shows '-' until you activate it. Choosing 'l' links it${RESET}"
  say "  ${DIM}into this repo's .claude/skills/ (using the .claude/skills/shared submodule,${RESET}"
  say "  ${DIM}which is added/updated automatically); 'g' links it into your global dir.${RESET}"
  say ""
  say "  global skills dir : $GLOBAL_SKILLS_DIR"
  if [ -n "$REPO_ROOT" ]; then
    say "  current repo      : $REPO_ROOT ${BLUE}(local installs available)${RESET}"
  else
    say "  current repo      : ${DIM}none — run from inside a repo to enable local (l) installs${RESET}"
  fi
  say ""

  # Build ordered skill list: globals first, then locals, then missing.
  _raw="$(list_available)"
  [ -n "$_raw" ] || { err "No profinda-* skills found in $CLONE_DIR"; exit 1; }
  _g=""; _l=""; _m=""
  for s in $_raw; do
    case "$(current_state "$s")" in
      G) _g="$_g $s" ;;
      L) _l="$_l $s" ;;
      *) _m="$_m $s" ;;
    esac
  done
  SKILLS="$(printf '%s %s %s' "$_g" "$_l" "$_m" | tr -s ' ' | sed 's/^ //;s/ $//')"

  # Parallel "want" state, space-separated, defaults to current state. Indexed by position.
  NOW=""; WANT=""
  for s in $SKILLS; do
    _cs="$(current_state "$s")"
    NOW="$NOW $_cs"
    WANT="$WANT $_cs"
  done
  NOW="${NOW# }"; WANT="${WANT# }"

  # Render the table. Arg $1 = index (1-based) of the row to highlight (0 = none).
  render_table() {
    _rt_hl="$1"
    say ""
    printf '   %-3s %-4s %-4s %s\n' "#" "now" "want" "skill"
    printf '   %s\n' "------------------------------------------"
    _rt_i=0
    for _rt_s in $SKILLS; do
      _rt_i=$((_rt_i+1))
      _rt_n="$(field "$NOW" "$_rt_i")"
      _rt_w="$(field "$WANT" "$_rt_i")"
      _rt_nc="$(state_color "$_rt_n")"; _rt_wc="$(state_color "$_rt_w")"
      if [ "$_rt_i" = "$_rt_hl" ]; then
        printf '   %s%2d)  %s%s%s    %s[%s]%s   %s%s%s\n' \
          "$BOLD" "$_rt_i" "$_rt_nc" "$_rt_n" "$RESET$BOLD" "$_rt_wc" "$_rt_w" "$RESET$BOLD" "$_rt_s" "$RESET" ""
      else
        printf '   %2d)  %s%s%s    %s[%s]%s   %s\n' \
          "$_rt_i" "$_rt_nc" "$_rt_n" "$RESET" "$_rt_wc" "$_rt_w" "$RESET" "$_rt_s"
      fi
    done
    say ""
  }

  # Walk each skill: reprint the full table (current row bold), ask for its desired state.
  _idx=0
  for s in $SKILLS; do
    _idx=$((_idx+1))
    _now="$(field "$NOW" "$_idx")"
    while :; do
      render_table "$_idx"
      printf '  %s%s%s  now:%s  desired [g/l/-] (Enter=keep %s): ' \
        "$BOLD" "$s" "$RESET" "$_now" "$_now"
      read -r _c || _c=""
      case "$_c" in
        ""|k|K) _new="$_now" ;;
        g|G)    _new="G" ;;
        l|L)
          if [ -z "$REPO_ROOT" ]; then
            warn "No repo here — 'l' (local) isn't available. Run from inside a repo."
            continue
          fi
          _new="L" ;;
        -|r|R)  _new="-" ;;
        *) warn "Enter one of: g, l, -, or Enter to keep."; continue ;;
      esac
      WANT="$(set_field "$WANT" "$_idx" "$_new")"
      break
    done
  done

  # Final table + diff summary before applying.
  render_table 0
  _changes=0
  _idx=0
  for s in $SKILLS; do
    _idx=$((_idx+1))
    _n="$(field "$NOW" "$_idx")"; _w="$(field "$WANT" "$_idx")"
    [ "$_n" = "$_w" ] && continue
    _changes=$((_changes+1))
    printf '   %s -> %s: %s\n' "$_n" "$_w" "$s  ($(transition_word "$_n" "$_w"))"
  done
  if [ "$_changes" -eq 0 ]; then
    say ""; info "No changes selected. Nothing to do."
  else
    say ""
    if ask_yes "Apply the $_changes change(s) above? (y/N)"; then
      apply_changes
    else
      info "Aborted. No changes made."
      return
    fi
  fi

  say ""
  if ask_yes "Add a weekly auto-update for global skills to ~/.zshrc? (y/N)"; then
    setup_auto_update
  fi

  say ""
  info "Done. Restart OpenCode (or reload the session) to pick up skill changes."
}

# apply the NOW -> WANT diff
apply_changes() {
  _need_submodule=n
  _local_adds=""
  _idx=0
  for s in $SKILLS; do
    _idx=$((_idx+1))
    _n="$(field "$NOW" "$_idx")"; _w="$(field "$WANT" "$_idx")"
    [ "$_n" = "$_w" ] && continue
    # tear down the old state first
    case "$_n" in
      G) global_remove "$s" ;;
      L) local_remove "$s" ;;
    esac
    # build the new state
    case "$_w" in
      G) global_add "$s" ;;
      L) _need_submodule=y; _local_adds="$_local_adds $s" ;;
    esac
  done
  if [ "$_need_submodule" = y ]; then
    ensure_submodule
    for s in $_local_adds; do local_add "$s"; done
  fi
}

main "$@"
