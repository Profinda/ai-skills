#!/usr/bin/env sh
# ProFinda ai-skills installer — a friendly wrapper around `npx skills`.
#
# Install (download then run — this installer is interactive, so do NOT pipe it
# straight into `sh`; `curl | sh` gives the script no keyboard and it can't prompt):
#   curl -fsSL https://raw.githubusercontent.com/Profinda/ai-skills/main/install.sh -o /tmp/ai-skills-install.sh && sh /tmp/ai-skills-install.sh
#
# What it does:
#   1. Makes sure Node.js (and so `npx`) is installed, offering to install it
#      (via Homebrew on macOS, the system package manager on Linux).
#   2. Checks you can read Profinda/ai-skills on GitHub, offering to sign you in
#      with the GitHub CLI if not.
#   3. Cleans up symlinks left by the previous version of this installer.
#   4. Lets you add, update or remove skills — for you only (every project), or
#      for the current repo (committed for the whole team). The skill and agent
#      pickers come from `npx skills` itself.
#   5. Optionally adds a weekly background update to ~/.zshrc.
#
# Safe to re-run.

set -eu

REPO_SLUG="Profinda/ai-skills"
REPO_HTTPS="https://github.com/Profinda/ai-skills.git"
REPO_SSH="git@github.com:Profinda/ai-skills.git"
MIN_NODE_MAJOR=18
LEGACY_CLONE_DIR="${AI_SKILLS_HOME:-$HOME/.config/ai-skills}"
LEGACY_SKILL_DIRS="$HOME/.claude/skills $HOME/.config/opencode/skills"
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
ok()   { printf '%s==>%s %s\n' "$GREEN" "$RESET" "$*"; }
warn() { printf '%s==>%s %s\n' "$YELLOW" "$RESET" "$*"; }
err()  { printf '%serror:%s %s\n' "$RED" "$RESET" "$*" >&2; }

# ---------- stdin handling -------------------------------------------------
# This installer reads your choices from the keyboard. If stdin isn't a
# terminal (e.g. `curl ... | sh`), try the controlling terminal; otherwise stop
# with clear instructions instead of hanging at a prompt you can't see.
if [ ! -t 0 ]; then
  if [ -e /dev/tty ] && exec < /dev/tty; then
    :
  else
    err "This installer is interactive and has no terminal to read from."
    err "Don't pipe it into sh. Download it, then run it:"
    err "  curl -fsSL https://raw.githubusercontent.com/$REPO_SLUG/main/install.sh -o /tmp/ai-skills-install.sh && sh /tmp/ai-skills-install.sh"
    exit 1
  fi
fi

ask_yes() { # ask_yes "prompt" -> 0 for yes, 1 for no (default no)
  printf '%s ' "$1"
  read -r _ans || _ans=""
  case "$_ans" in y|Y|yes|YES) return 0 ;; *) return 1 ;; esac
}

ask_choice() { # ask_choice "prompt" default -> echoes the answer (or default)
  printf '%s ' "$1" >&2
  read -r _ans || _ans=""
  printf '%s' "${_ans:-$2}"
}

# ---------- step 1: Node.js / npx ---------------------------------------------
node_major() {
  node -p 'process.versions.node.split(".")[0]' 2>/dev/null || printf '0'
}

has_node() {
  command -v npx >/dev/null 2>&1 && [ "$(node_major)" -ge "$MIN_NODE_MAJOR" ]
}

load_brew() {
  for _b in /opt/homebrew/bin/brew /usr/local/bin/brew /home/linuxbrew/.linuxbrew/bin/brew; do
    [ -x "$_b" ] && { eval "$("$_b" shellenv)"; return 0; }
  done
  return 1
}

ensure_brew() {
  command -v brew >/dev/null 2>&1 && return 0
  load_brew && return 0
  say ""
  say "Homebrew (the standard macOS app installer for developer tools) is needed to install Node.js."
  say "${DIM}It will ask for your Mac login password and may take a few minutes.${RESET}"
  ask_yes "Install Homebrew now? (y/N)" || { err "Homebrew is required. See https://brew.sh"; exit 1; }
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  load_brew || { err "Homebrew installed, but it isn't on PATH. Open a new terminal and re-run."; exit 1; }
}

install_node() {
  case "$(uname -s)" in
    Darwin)
      ensure_brew
      if brew list node >/dev/null 2>&1; then brew upgrade node; else brew install node; fi
      ;;
    Linux)
      if command -v apt-get >/dev/null 2>&1; then
        sudo apt-get update && sudo apt-get install -y nodejs npm
      elif command -v dnf >/dev/null 2>&1; then
        sudo dnf install -y nodejs npm
      else
        err "Couldn't find a package manager to install Node.js. Install it from https://nodejs.org and re-run."
        exit 1
      fi
      ;;
    *)
      err "Unsupported system. Install Node.js from https://nodejs.org and re-run."
      exit 1
      ;;
  esac
}

ensure_node() {
  # nvm users: Node may only be on PATH once nvm is loaded.
  if ! has_node && [ -s "${NVM_DIR:-$HOME/.nvm}/nvm.sh" ]; then
    # shellcheck disable=SC1091
    . "${NVM_DIR:-$HOME/.nvm}/nvm.sh" >/dev/null 2>&1 || true
  fi
  has_node && { ok "Node.js $(node -v) found."; return 0; }

  say ""
  if command -v node >/dev/null 2>&1; then
    say "Your Node.js ($(node -v)) is too old; version $MIN_NODE_MAJOR or newer is needed."
  else
    say "Node.js isn't installed. The skills tool needs it."
  fi
  ask_yes "Install Node.js now? (y/N)" || { err "Node.js $MIN_NODE_MAJOR+ is required. See https://nodejs.org"; exit 1; }
  install_node
  hash -r 2>/dev/null || true
  has_node || { err "Node.js still isn't available. Open a new terminal and re-run."; exit 1; }
  ok "Node.js $(node -v) installed."
}

# ---------- step 2: GitHub access ---------------------------------------------
can_read() { # $1 = repo url
  GIT_TERMINAL_PROMPT=0 GIT_SSH_COMMAND="ssh -o BatchMode=yes -o ConnectTimeout=10" \
    git ls-remote "$1" HEAD >/dev/null 2>&1
}

github_login() {
  say ""
  say "You don't have access to $REPO_SLUG on GitHub from this computer yet."
  say "The GitHub CLI can sign you in through your browser."
  ask_yes "Sign in to GitHub now? (y/N)" || return 1
  if ! command -v gh >/dev/null 2>&1; then
    case "$(uname -s)" in
      Darwin) ensure_brew; brew install gh ;;
      *) err "Install the GitHub CLI (https://cli.github.com), run 'gh auth login', then re-run."; exit 1 ;;
    esac
  fi
  gh auth login --hostname github.com --git-protocol https --web
  gh auth setup-git
}

resolve_source() {
  if can_read "$REPO_HTTPS"; then SOURCE="$REPO_HTTPS"; return 0; fi
  if can_read "$REPO_SSH"; then SOURCE="$REPO_SSH"; return 0; fi
  if github_login && can_read "$REPO_HTTPS"; then SOURCE="$REPO_HTTPS"; return 0; fi
  err "Still can't read $REPO_SLUG. Ask a ProFinda developer to give you access to the repo, then re-run."
  exit 1
}

# ---------- step 3: previous installer leftovers -----------------------------
cleanup_legacy() {
  _removed=0
  for _dir in $LEGACY_SKILL_DIRS; do
    [ -d "$_dir" ] || continue
    for _link in "$_dir"/profinda-*; do
      [ -L "$_link" ] || continue
      case "$(readlink "$_link")" in
        "$LEGACY_CLONE_DIR"/*) rm -f "$_link"; _removed=$((_removed+1)) ;;
      esac
    done
  done
  [ "$_removed" -gt 0 ] && info "Removed $_removed link(s) left by the previous installer."
  return 0
}

# ---------- step 4: skills -----------------------------------------------------
skills() { npx -y skills@latest "$@"; }

in_repo() {
  REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || return 1
  [ "$REPO_ROOT" != "$LEGACY_CLONE_DIR" ]
}

choose_scope() {
  SCOPE="global"
  in_repo || return 0
  say ""
  say "${BOLD}Who should get the skills?${RESET}"
  say "  ${GREEN}1${RESET}) Just me, in every project ${DIM}(recommended)${RESET}"
  say "  ${GREEN}2${RESET}) Everyone working on this repo ${DIM}($REPO_ROOT — you commit the result)${RESET}"
  case "$(ask_choice '  choose [1/2] (Enter=1):' 1)" in
    2) SCOPE="repo"; cd "$REPO_ROOT" ;;
    *) SCOPE="global" ;;
  esac
}

scope_flag() { [ "$SCOPE" = "global" ] && printf -- '-g' || printf -- '-p'; }

repo_commit_hint() {
  [ "$SCOPE" = "repo" ] || return 0
  say ""
  info "Commit the change so the team gets it:"
  say "    git add -f .agents/skills .claude/skills skills-lock.json && git commit"
}

run_action() {
  say ""
  say "${BOLD}What would you like to do?${RESET}"
  say "  ${GREEN}1${RESET}) Add or change skills"
  say "  ${GREEN}2${RESET}) Update installed skills to the latest version"
  say "  ${GREEN}3${RESET}) Remove skills"
  case "$(ask_choice '  choose [1/2/3] (Enter=1):' 1)" in
    2)
      skills update "$(scope_flag)" -y
      ;;
    3)
      [ "$SCOPE" = "repo" ] && warn "Pick only the skills to remove — repo-local skills live in the same folder."
      if [ "$SCOPE" = "global" ]; then skills remove -g; else skills remove; fi
      ;;
    *)
      say ""
      say "${DIM}Next, pick skills with the arrow keys and space, then Enter. When asked which"
      say "agents to install to, pick the AI tools you use (e.g. Claude Code).${RESET}"
      if [ "$SCOPE" = "global" ]; then skills add "$SOURCE" -g; else skills add "$SOURCE"; fi
      ;;
  esac
  repo_commit_hint
}

# ---------- step 5: weekly auto-update ----------------------------------------
remove_auto_update_block() { # $1 = file
  awk -v marker="$AUTO_UPDATE_MARKER" '
    $0 == marker { skip = 1; next }
    skip && $0 == "fi" { skip = 0; next }
    !skip { print }
  ' "$1" > "$1.ai-skills.tmp" && mv "$1.ai-skills.tmp" "$1"
}

setup_auto_update() {
  [ "$SCOPE" = "global" ] || return 0
  _zshrc="$HOME/.zshrc"
  if grep -qF "$AUTO_UPDATE_MARKER" "$_zshrc" 2>/dev/null; then
    if grep -qF "npx -y skills@latest update -g" "$_zshrc"; then
      info "Weekly auto-update already configured in ~/.zshrc"
      return 0
    fi
    info "Replacing the previous installer's weekly auto-update in ~/.zshrc"
    remove_auto_update_block "$_zshrc"
  else
    say ""
    ask_yes "Keep your skills up to date automatically (weekly, in the background)? (y/N)" || return 0
  fi
  # shellcheck disable=SC2016 # written to ~/.zshrc literally; expands there, not here
  {
    printf '\n%s\n' "$AUTO_UPDATE_MARKER"
    printf '%s\n' '_ais_stamp="$HOME/.cache/ai-skills-last-update"'
    printf '%s\n' 'if command -v npx >/dev/null 2>&1 && { [ ! -f "$_ais_stamp" ] || [ -n "$(find "$_ais_stamp" -mtime +7 2>/dev/null)" ]; }; then'
    printf '%s\n' '  (GIT_TERMINAL_PROMPT=0 npx -y skills@latest update -g -y >/dev/null 2>&1 && mkdir -p "$HOME/.cache" && touch "$_ais_stamp") &!'
    printf '%s\n' 'fi'
  } >> "$_zshrc"
  ok "Added weekly auto-update to ~/.zshrc."
}

# ---------- main -------------------------------------------------------------
main() {
  command -v git >/dev/null 2>&1 || { err "git is required (on macOS run: xcode-select --install)"; exit 1; }

  say ""
  say "${BOLD}ProFinda ai-skills installer${RESET}"
  say "Installs ProFinda's AI skills (conventions and workflows for AI coding tools)."

  ensure_node
  resolve_source
  cleanup_legacy
  choose_scope
  run_action
  setup_auto_update

  say ""
  ok "Done. Restart your AI tool (or start a new session) to pick up the changes."
}

main "$@"
