#!/bin/bash
# Unattended Claude Code session for osem_listmode_task.md (survives SSH logout in screen):
#   screen -dmS recon_algorithms bash dev/reports/2026-10_phantom_recon/run_osem_listmode_agent.sh
# Progress: osem_listmode_agent.jsonl (stream-json transcript), osem_listmode_STATUS.
set -u
cd "$(dirname "$0")/../../.."   # repo root
R=dev/reports/2026-10_phantom_recon
CLAUDE=$HOME/.vscode-server/extensions/anthropic.claude-code-2.1.299-linux-x64/resources/native-binary/claude
PY=$HOME/.local/share/micromamba/envs/opengate/bin/python
ALLOW=(Read Write Edit Glob Grep TodoWrite
  "Bash($PY:*)" "Bash(cd:*)" "Bash(nohup:*)" "Bash(timeout:*)" "Bash(sleep:*)" "Bash(nvidia-smi:*)"
  "Bash(ls:*)" "Bash(cat:*)" "Bash(head:*)" "Bash(tail:*)" "Bash(grep:*)" "Bash(wc:*)" "Bash(find:*)"
  "Bash(du:*)" "Bash(df:*)" "Bash(ps:*)" "Bash(kill:*)" "Bash(mkdir:*)" "Bash(echo:*)" "Bash(date:*)"
  "Bash(git status:*)" "Bash(git diff:*)" "Bash(git log:*)")
echo "running: agent started $(date '+%F %T')" > $R/osem_listmode_STATUS
"$CLAUDE" -p "Carry out the task in $R/osem_listmode_task.md. Read it in full first, then work through it to the end without asking questions." \
  --permission-mode acceptEdits --allowedTools "${ALLOW[@]}" \
  --output-format stream-json --verbose > $R/osem_listmode_agent.jsonl 2> $R/osem_listmode_agent.err
echo "agent exited $? at $(date '+%F %T')" >> $R/osem_listmode_STATUS
