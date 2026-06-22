#!/bin/zsh
# Weekly auto-refresh of the AUTAC recovery scorecard.
# Pulls latest code, regenerates the scorecard from live GSC data, and pushes
# the result so the numbers are visible from any machine. Driven by the
# com.autac.refresh-scorecard LaunchAgent (Mondays 08:00).
# Manual run: zsh seo-reports/refresh-scorecard.sh

export PATH="/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin"
REPO="/Users/newimac/Documents/workspace/autac"
PY="/Users/newimac/gsc-reports/.venv/bin/python"
LOG="$REPO/seo-reports/scorecard-cron.log"

cd "$REPO" || { echo "$(date) repo not found" >> "$LOG"; exit 1; }
echo "===== $(date) =====" >> "$LOG"

git pull --rebase --autostash origin main >> "$LOG" 2>&1

if [ ! -x "$PY" ]; then
  echo "python venv missing at $PY — aborting" >> "$LOG"; exit 1
fi

"$PY" seo-reports/track_recovery.py >> "$LOG" 2>&1 || {
  echo "track_recovery.py failed (see above)" >> "$LOG"; exit 1; }

git add seo-reports/recovery-scorecard seo-reports/recovery-scorecard-*
if git diff --cached --quiet; then
  echo "no scorecard changes" >> "$LOG"
else
  git commit -m "Auto-refresh recovery scorecard ($(date +%Y-%m-%d))" >> "$LOG" 2>&1
  git push origin main >> "$LOG" 2>&1 && echo "pushed" >> "$LOG"
fi
