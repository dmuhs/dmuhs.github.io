---
Title: A Universal .zshrc File
Date: 2026-02-15
Category: Software
Status: published
---

Since forver ago, I have been using [oh-my-zsh](https://ohmyz.sh/) with a fairly standard configuration. Plugins for commands I often use, utility functions, and all the clutter you accumulate after years of building and breaking software. That included fuzzing configuration, an unreal amount of version managers, and custom configurations, including those recklessly appended by automatic installers. Since my day-to-day work is fairly intense, it's safe to say that for the last five years, not just my `.zshrc` but also various other files connected to it were left unattended. Today, this changed.

## Figuring Out What I Want

This was the hardest part. "I don't know man, just make it work like I'm used to but nicer" didn't cut it. After staring at the wall for a few minutes, I got the following:

- *Distribution should be as simple as possible.* I tried managing dotfiles with `rsync`, [GNU Stow](https://www.gnu.org/software/stow/), and a plain old Git repo. I'm also aware of [chezmoi](https://www.chezmoi.io/)  and all of them gave me the feeling like I'm overengineering things.
- *I need things to be readable.* Looking back at my old `.zshrc` and all the other files it included, I have no idea what's going on anymore. Back then I solved problems that I never needed solved - not even once in five years.
- *I need things to be cross-platform.* I decided that the nicest outcome would be to have a config file I can deploy on a every setup I use. The lower bound being a Raspberry Pi 1 A+ (1x700MHz, 512MB RAM).
- *I need it to be familiar.* I have a lot of things on my mind. Please, no studying docs, new keybinds, or new dependencies to install. Your cool management tool has a sub-sub-sub command that fixes my exact issue? Sorry, I probably won't find it out until I migrated away. Also, I can't deal with errors that prevent me from getting my work done.

## y no bash tho?

I toyed with the thought of going back to plain Bash and a small `.bashrc` repeatedly but never really felt comfortable to make the jump. To get the zealots off my back: All I need my shell to do can be done in Bash with enough effort. A few things that still sold me on plain zsh were:

- *Bash needs hacks for instant history sync.* There were many times where I launched a command, opened a new terminal tab, pressed the up arrow key, and was greeted by a random command I typed a week ago. Then I had to click back to the original tab, fight against the stdout stream actively scrolling down, try to copy the original command, accidentally Ctrl-C kill the thing and lose all my progress.. It's a mess, you get it.
- *zsh has the better tab completion.* `compinit` with `zstyle` is a nice way to get case-sensitive matching, menu selection, and per-command completion. It's fast (if tickled right with a few lines of config), and batteries-included. No frameworks to manage.
- *zsh has prefix history search.* I am forgetful and often need to go through my previous commands to get things right. Searching with a prefix by just typing and pressing the up arrow to navigate through the filtered history is muscle memory by now. Doing the same with ^R and ^S in Bash requires me to push two buttons on my keyboard, which is one button too many.

All that being said, I love Bash and regularly use it on external machines. If you like to go full vanilla on your shell or go with a framework like [oh-my-bash](https://ohmybash.nntoan.com/) for some reason, have fun! This is a judgement-free space.

## Some Highlights

There's a few things I'm particularly happy with.

### compinit Caching

The completion system, `compinit`, runs a security check and rebuilds a dump file on every shell start. I think this was a big contributor to the lag I experienced in my old, cluttered setup.

```shell
autoload -Uz compinit
setopt extendedglob
if [[ -n ~/.cache/zcompdump(#qN.mh+24) ]]; then
    compinit -d ~/.cache/zcompdump
else
    compinit -C -d ~/.cache/zcompdump
fi
unsetopt extendedglob
```

The new config uses a zsh glob qualifier `(#qN.mh+24)` to check if the dump is older than 24 hours and only rebuilds then. The rest of the time it loads the cache with -C. This requires `extendedglob`, though, which I enable and immediately disable again after because it makes `^` and `#` special characters in glob patterns. That breaks a few things like `git log HEAD^`.

### Slightly Faster Git Prompt

Most git prompts shell out to `git status --porcelain`, which walks the entire working tree and formats output nobody reads. Instead, I decided to go with `git diff --quiet`, which exits on the first difference it finds. That's enough for me since I don't need additions and deletions, origin data, etc. There are only three separate checks (unstaged, staged, untracked) with an early exit.

```shell
    local branch
    branch=$(GIT_OPTIONAL_LOCKS=0 git symbolic-ref --short HEAD 2>/dev/null)
    if [ -n "$branch" ]; then
        if ! GIT_OPTIONAL_LOCKS=0 git diff --quiet 2>/dev/null \
            || ! GIT_OPTIONAL_LOCKS=0 git diff --cached --quiet 2>/dev/null \
            || [[ -n "$(GIT_OPTIONAL_LOCKS=0 git ls-files --others --exclude-standard -- ':/*' 2>/dev/null | head -1)" ]]; then
            _prompt_git=" %F{red}(${branch})%f"
        else
            _prompt_git=" %F{yellow}(${branch})%f"
        fi
    else
        _prompt_git=""
    fi
```

I also set `GIT_OPTIONAL_LOCKS=0` so the read-only prompt checks don't block or get blocked by concurrent git operations.

### Cross-platform SSH Agent

I had solved this issue on each system individually and attempted to merge my approaches. macOS has its own keychain integration, Linux has `keychain` (if installed), and the fallback writes the agent socket to `~/.ssh/agent-env` so new terminals reuse the same agent instead of spawning a new one each time.

```shell
if [[ "$(uname)" == "Darwin" ]]; then
    ssh-add --apple-load-keychain 2>/dev/null
elif command -v keychain &>/dev/null; then
    _ssh_keys=()
    for _f in ~/.ssh/id_*(N); do
        [[ "$_f" == *.pub ]] && continue
        _ssh_keys+=("$_f")
    done
    if (( ${#_ssh_keys} )); then
        eval "$(keychain --eval --quiet --nogui "${_ssh_keys[@]}" 2>/dev/null)"
    fi
    unset _ssh_keys _f
else
    _ssh_agent_env="$HOME/.ssh/agent-env"
    if [ -f "$_ssh_agent_env" ]; then
        . "$_ssh_agent_env" >/dev/null
        kill -0 "$SSH_AGENT_PID" 2>/dev/null || unset SSH_AGENT_PID
    fi
    if [ -z "$SSH_AGENT_PID" ]; then
        eval "$(ssh-agent -s -t 3600)" >/dev/null
        echo "export SSH_AUTH_SOCK=$SSH_AUTH_SOCK" > "$_ssh_agent_env"
        echo "export SSH_AGENT_PID=$SSH_AGENT_PID" >> "$_ssh_agent_env"
        chmod 600 "$_ssh_agent_env"
        ssh-add 2>/dev/null
    fi
    unset _ssh_agent_env
fi
```

Keys expire after one hour on the fallback path. This is a tradeoff for shared/remote hosts where I don't want keys loaded indefinitely after disconnecting. **"Hold it right there, criminal scum!"** I hear you shout in a Skyrim guard voice. I know, I know, writing SSH agent data to a file *feels* insecure. However, it's set at `600`. If an attacker having access to it would also have access to `/tmp/ssh-*` agent files and the ability to call `ssh-add` against the running agent service. While this configuration doesn't really address the inherent security tradeoffs of the SSH agent, at least it doesn't make them worse.

### Keep The Trash Outside

Everything machine-specific (think `nvm`, `JAVA_HOME`, `sdkman`, weird local paths) goes into `~/.zshlocal`. It gets sourced last so it can override any wrong assumptions the `.zshrc` file makes. The main file stays synced and identical everywhere.

## The Whole Thing

You can find it on [GitHub](https://github.com/dmuhs/dotfiles). If you want to read the whole thing at the time of writing, here it is (at 327 LoC)!

```shell
# ==============================================================================
# Universal .zshrc without all the clutter.
# ==============================================================================
# Targets: macOS, WSL2, Kali Linux, hosted VPS
# Structure: shell behavior → display → tool integration → local overrides
#
# Optional dependencies (loaded if present, silently skipped if not):
#
#   zsh-syntax-highlighting — colors commands as you type (red = invalid)
#     macOS:  brew install zsh-syntax-highlighting
#     Debian: apt install zsh-syntax-highlighting
#
#   zsh-autosuggestions — ghost text suggestions from history
#     macOS:  brew install zsh-autosuggestions
#     Debian: apt install zsh-autosuggestions
#
#   asdf — universal version manager (replaces nvm, sdkman, etc.)
#     https://asdf-vm.com/guide/getting-started.html
#
#   keychain — persistent SSH agent across sessions (Linux only)
#     Debian: apt install keychain
#
# Machine-specific config (NVM, Android SDK, JAVA_HOME, etc.) goes in
# ~/.zshlocal which is sourced at the very end and should NOT be synced.
# ==============================================================================


# ┌────────────────────────────────────────────────────────────────────────────┐
# │ SHELL BEHAVIOR                                                             │
# │ How zsh interprets input. These are safe defaults with no side effects.    │
# └────────────────────────────────────────────────────────────────────────────┘

# ------------------------------------------------------------------------------
# Core options
# ------------------------------------------------------------------------------
setopt autocd              # type a directory name to cd into it
setopt interactivecomments # allow # comments in interactive shell
setopt promptsubst         # allow variable/command expansion in prompt string
setopt numericglobsort     # sort filenames with numbers naturally (1, 2, 10)
setopt nonomatch           # pass failed globs through as literals (like bash)
setopt globdots            # tab completion includes dotfiles without typing .

PROMPT_EOL_MARK=""         # suppress the trailing % on partial output lines
WORDCHARS='_-'             # ctrl+arrow treats - and _ as word boundaries

# ------------------------------------------------------------------------------
# History
# ------------------------------------------------------------------------------
# History file grows up to 1M entries. Duplicates are removed aggressively.
# Commands prefixed with a space are not recorded (useful for secrets).
HISTFILE=~/.zsh_history
HISTSIZE=1000000
SAVEHIST=1000000
setopt share_history            # sync history across all open terminals instantly
setopt hist_ignore_all_dups     # when adding a dupe, remove the older entry
setopt hist_expire_dups_first   # expire dupes first when trimming to SAVEHIST
setopt hist_ignore_space        # commands starting with space are private
setopt hist_verify              # show expanded history command before executing
setopt hist_reduce_blanks       # strip extra whitespace before saving
setopt hist_save_no_dups        # don't write duplicate entries to the file

alias history="history 0"       # show full history (default only shows last 16)

# Arrow up/down search history filtered by what you've already typed.
# Type "ssh" then press up — cycles through previous ssh commands only.
# Multiple keycodes are bound because terminals disagree on what arrow keys send:
#   ^[[A/^[[B  = normal mode (most terminals)
#   ^[OA/^[OB  = application mode (some terminals activate this automatically)
#   $terminfo  = whatever your terminal actually reports (most portable)
autoload -U up-line-or-beginning-search down-line-or-beginning-search
zle -N up-line-or-beginning-search
zle -N down-line-or-beginning-search
bindkey "^[[A" up-line-or-beginning-search
bindkey "^[[B" down-line-or-beginning-search
bindkey "^[OA" up-line-or-beginning-search
bindkey "^[OB" down-line-or-beginning-search
[[ -n "$terminfo[kcuu1]" ]] && bindkey "$terminfo[kcuu1]" up-line-or-beginning-search
[[ -n "$terminfo[kcud1]" ]] && bindkey "$terminfo[kcud1]" down-line-or-beginning-search

# ------------------------------------------------------------------------------
# Completion
# ------------------------------------------------------------------------------
# IMPORTANT: Anything that adds to fpath (completion directories) MUST go
# before the compinit call below. If you add a new tool with completions,
# add its fpath entry here, not after compinit — otherwise the completions
# won't be available until the next shell session.

[ -d ~/.cache ] || mkdir -p ~/.cache

# Register completion directories for tools that may be installed
[ -d "$HOME/.asdf/completions" ] && fpath=($HOME/.asdf/completions $fpath)
[ -d "/opt/homebrew/share/zsh/site-functions" ] && fpath=(/opt/homebrew/share/zsh/site-functions $fpath)

autoload -Uz compinit
# Performance: only rebuild the completion dump once per day.
# compinit -C skips the security check and reuses the cached dump.
# The (#qN.mh+24) glob matches if the file is older than 24 hours.
setopt extendedglob
if [[ -n ~/.cache/zcompdump(#qN.mh+24) ]]; then
    compinit -d ~/.cache/zcompdump
else
    compinit -C -d ~/.cache/zcompdump
fi
unsetopt extendedglob          # disable — extendedglob makes ^ and # special
                               # in patterns, which breaks things like git log HEAD^

zstyle ':completion:*' menu select                             # arrow-key menu
zstyle ':completion:*' matcher-list 'm:{a-zA-Z}={A-Za-z}'     # case-insensitive
zstyle ':completion:*' completer _expand _complete
zstyle ':completion:*' use-compctl false                       # disable legacy system
zstyle ':completion:*' rehash true                             # pick up new binaries

# ------------------------------------------------------------------------------
# Key bindings
# ------------------------------------------------------------------------------
# Uses emacs mode (ctrl+a = beginning, ctrl+e = end, ctrl+w = delete word, etc.)
# If you prefer vi mode, change -e to -v — but many bindings below assume emacs.
bindkey -e
bindkey ' ' magic-space                        # expand !! and !$ on space
bindkey '^[[3~' delete-char                    # delete key
bindkey '^[[1;5C' forward-word                 # ctrl + right arrow
bindkey '^[[1;5D' backward-word                # ctrl + left arrow
bindkey '^[[H' beginning-of-line               # home
bindkey '^[[F' end-of-line                     # end


# ┌────────────────────────────────────────────────────────────────────────────┐
# │ DISPLAY                                                                    │
# │ What the shell looks like — prompt, colors, aliases.                       │
# └────────────────────────────────────────────────────────────────────────────┘

# ------------------------------------------------------------------------------
# Prompt
# ------------------------------------------------------------------------------
# Format: 13:37:42 user@host ~/path (venv) (branch) $
#
# - Timestamp: always visible for retroactive pentest logging
# - user@host: identifies which machine you're on (important for remote sessions)
# - Virtualenv: shown in cyan when a Python venv is active
# - Git branch: yellow = clean, red = dirty (uncommitted changes)
# - $: green after successful command, red after failure
#
# Performance notes:
# - Git info is computed in a precmd hook (not a subshell in the prompt string)
# - GIT_OPTIONAL_LOCKS=0 prevents lock contention with concurrent git processes
# - git diff --quiet exits on first difference (faster than git status --porcelain
#   which scans the entire tree and formats output)

VIRTUAL_ENV_DISABLE_PROMPT=1   # we handle virtualenv display ourselves

_prompt_venv=""
_prompt_git=""

_prompt_precmd() {
    # Virtualenv
    if [ -n "$VIRTUAL_ENV" ]; then
        _prompt_venv=" %F{cyan}($(basename "$VIRTUAL_ENV"))%f"
    else
        _prompt_venv=""
    fi

    # Git branch + dirty state
    local branch
    branch=$(GIT_OPTIONAL_LOCKS=0 git symbolic-ref --short HEAD 2>/dev/null)
    if [ -n "$branch" ]; then
        if ! GIT_OPTIONAL_LOCKS=0 git diff --quiet 2>/dev/null \
            || ! GIT_OPTIONAL_LOCKS=0 git diff --cached --quiet 2>/dev/null \
            || [[ -n "$(GIT_OPTIONAL_LOCKS=0 git ls-files --others --exclude-standard -- ':/*' 2>/dev/null | head -1)" ]]; then
            _prompt_git=" %F{red}(${branch})%f"
        else
            _prompt_git=" %F{yellow}(${branch})%f"
        fi
    else
        _prompt_git=""
    fi
}

autoload -Uz add-zsh-hook
add-zsh-hook precmd _prompt_precmd

PROMPT='%F{245}%*%f %F{blue}%n@%m%f %F{green}%~%f${_prompt_venv}${_prompt_git} %(?.%F{green}.%F{red})$%f '

# ------------------------------------------------------------------------------
# Colors and aliases
# ------------------------------------------------------------------------------
# Detect GNU vs BSD ls for correct color flag
if ls --color=auto / &>/dev/null; then
    alias ls='ls --color=auto'             # GNU ls (Linux)
else
    alias ls='ls -G'                       # BSD ls (macOS)
fi

alias ll='ls -lh'
alias la='ls -lAh'
alias grep='grep --color=auto'

# Colored man pages via less escape codes
export LESS_TERMCAP_mb=$'\E[1;31m'         # begin blink
export LESS_TERMCAP_md=$'\E[1;36m'         # begin bold
export LESS_TERMCAP_me=$'\E[0m'            # end mode
export LESS_TERMCAP_so=$'\E[01;33m'        # begin standout (search highlight)
export LESS_TERMCAP_se=$'\E[0m'            # end standout
export LESS_TERMCAP_us=$'\E[1;32m'         # begin underline
export LESS_TERMCAP_ue=$'\E[0m'            # end underline

# Use LS_COLORS for completion menu coloring (Linux only — macOS uses LSCOLORS)
if command -v dircolors &>/dev/null; then
    eval "$(dircolors -b)"
    zstyle ':completion:*' list-colors "${(s.:.)LS_COLORS}"
fi


# ┌────────────────────────────────────────────────────────────────────────────┐
# │ ENVIRONMENT                                                                │
# │ Editor, locale, and other exported variables used by external programs.    │
# └────────────────────────────────────────────────────────────────────────────┘

export EDITOR='vim'
export LANG='en_US.UTF-8'

# Only force LC_ALL if the locale exists. On minimal VPS images where the
# locale hasn't been generated, setting LC_ALL causes warnings from many tools.
if locale -a 2>/dev/null | grep -qi 'en_US.utf-*8'; then
    export LC_ALL='en_US.UTF-8'
fi

# Fix GPG signing in Git (gpg needs to know the current tty)
export GPG_TTY=$(tty)


# ┌────────────────────────────────────────────────────────────────────────────┐
# │ TOOL INTEGRATION                                                           │
# │ SSH agent, version managers, PATH. All conditional — nothing breaks if     │
# │ the tool isn't installed.                                                  │
# └────────────────────────────────────────────────────────────────────────────┘

# ------------------------------------------------------------------------------
# SSH agent
# ------------------------------------------------------------------------------
# Goal: type your SSH key passphrase once per session, not on every git/ssh op.
#
# macOS:   system agent handles it — just load saved passphrases from keychain.
# Linux:   keychain (if installed) persists agent across logins and terminals.
# Fallback: manual ssh-agent with env file for cross-terminal persistence.
#           Keys expire after 1 hour for security on shared/remote hosts.

if [[ "$(uname)" == "Darwin" ]]; then
    ssh-add --apple-load-keychain 2>/dev/null
elif command -v keychain &>/dev/null; then
    _ssh_keys=()
    for _f in ~/.ssh/id_*(N); do
        [[ "$_f" == *.pub ]] && continue
        _ssh_keys+=("$_f")
    done
    if (( ${#_ssh_keys} )); then
        eval "$(keychain --eval --quiet --nogui "${_ssh_keys[@]}" 2>/dev/null)"
    fi
    unset _ssh_keys _f
else
    _ssh_agent_env="$HOME/.ssh/agent-env"
    if [ -f "$_ssh_agent_env" ]; then
        . "$_ssh_agent_env" >/dev/null
        kill -0 "$SSH_AGENT_PID" 2>/dev/null || unset SSH_AGENT_PID
    fi
    if [ -z "$SSH_AGENT_PID" ]; then
        eval "$(ssh-agent -s -t 3600)" >/dev/null
        echo "export SSH_AUTH_SOCK=$SSH_AUTH_SOCK" > "$_ssh_agent_env"
        echo "export SSH_AGENT_PID=$SSH_AGENT_PID" >> "$_ssh_agent_env"
        chmod 600 "$_ssh_agent_env"
        ssh-add 2>/dev/null
    fi
    unset _ssh_agent_env
fi

# ------------------------------------------------------------------------------
# asdf version manager
# ------------------------------------------------------------------------------
# Replaces nvm, sdkman, and language-specific version managers.
# Completions are registered in the Completion section above (before compinit).
# This block only sources the main asdf script to make the command available.
if [ -f "$HOME/.asdf/asdf.sh" ]; then
    . "$HOME/.asdf/asdf.sh"
elif [ -d "/opt/homebrew/opt/asdf" ]; then
    . /opt/homebrew/opt/asdf/libexec/asdf.sh
fi

# ------------------------------------------------------------------------------
# PATH
# ------------------------------------------------------------------------------
# Only adds directories that actually exist. Prepends to PATH so these take
# priority over system versions. Add machine-specific paths in ~/.zshlocal.
_add_to_path() { [ -d "$1" ] && PATH="$1:$PATH" }

_add_to_path "$HOME/.local/bin"

export PATH

unfunction _add_to_path


# ┌────────────────────────────────────────────────────────────────────────────┐
# │ OPTIONAL PLUGINS                                                           │
# │ Loaded if installed, silently skipped if not. Order matters:               │
# │ autosuggestions first, syntax highlighting MUST be last.                   │
# └────────────────────────────────────────────────────────────────────────────┘

_source_if_exists() { [ -f "$1" ] && source "$1" }

_source_if_exists /usr/share/zsh-autosuggestions/zsh-autosuggestions.zsh
_source_if_exists /opt/homebrew/share/zsh-autosuggestions/zsh-autosuggestions.zsh

# Syntax highlighting MUST be the last plugin sourced — it wraps zle widgets
# and will miss anything registered after it.
_source_if_exists /usr/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh
_source_if_exists /opt/homebrew/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh

unfunction _source_if_exists


# ┌────────────────────────────────────────────────────────────────────────────┐
# │ LOCAL OVERRIDES                                                            │
# │ Machine-specific config that should NOT be synced across hosts.            │
# │ Examples: NVM, JAVA_HOME, Android SDK, pnpm, SDKMAN, company VPN certs.    │
# │ This MUST be the last thing sourced so it can override anything above.     │
# └────────────────────────────────────────────────────────────────────────────┘

[ -f ~/.zshlocal ] && source ~/.zshlocal
```