#!/bin/bash
# Weekly wrapper for the staggered blog rollout. Invoked by the launchd job
# com.autac.publish-blog-batch (Mondays 9am local). Pulls, releases the next
# batch via publish_blog_batch.py, then commits + pushes (Vercel auto-deploys).
# Pass --dry-run to preview without committing.
set -uo pipefail
export PATH="/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin"
REPO="/Users/newimac/Documents/workspace/autac"
cd "$REPO" || { echo "ERROR: repo not found"; exit 1; }

echo "===== publish-blog-batch $(date) ====="
git pull --ff-only origin main || { echo "ERROR: git pull failed"; exit 1; }

OUT="$(python3 seo-reports/publish_blog_batch.py "$@" 2>&1)"
echo "$OUT"

if echo "$OUT" | grep -q "queue empty"; then
  echo "Queue empty — staggered rollout complete. You can unload this job:"
  echo "  launchctl bootout gui/$(id -u)/com.autac.publish-blog-batch"
  exit 0
fi

for a in "$@"; do
  [ "$a" = "--dry-run" ] && { echo "(dry-run: no commit)"; exit 0; }
done

N="$(echo "$OUT" | grep -c '^  + ')"
if [ "$N" -lt 1 ]; then echo "No posts published; nothing to commit."; exit 0; fi

git add blog/ sitemap.xml seo-reports/request-indexing-priority.txt seo-reports/blog-publish-queue.txt
git commit -m "Publish blog batch ($N state posts) [scheduled]" || { echo "ERROR: commit failed"; exit 1; }
git push origin main || { echo "ERROR: push failed (check keychain/network); rerun later"; exit 1; }
echo "Published and pushed $N post(s)."
