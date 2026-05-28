#!/usr/bin/env bash
# Seed the running backend with three realistic demo workflows: one completed,
# one awaiting approval, and one freshly drafted.
#
# Usage:
#   bash scripts/seed.sh                 # http://localhost:8000
#   API_BASE=http://my-host:8000 bash scripts/seed.sh

set -euo pipefail

API_BASE="${API_BASE:-http://localhost:8000}"
SAMPLE="$(cd "$(dirname "$0")/.." && pwd)/scripts/demo-workflows.json"

echo "→ Seeding $API_BASE from $SAMPLE"

for attempt in $(seq 1 30); do
  if curl -sf "$API_BASE/health" > /dev/null; then
    break
  fi
  echo "  ...waiting for backend (attempt $attempt/30)"
  sleep 1
done

count=$(python3 -c "import json,sys; print(len(json.load(open(sys.argv[1]))))" "$SAMPLE")

for i in $(seq 0 $((count - 1))); do
  entry=$(python3 -c "
import json, sys
with open(sys.argv[1]) as f:
    data = json.load(f)
print(json.dumps(data[int(sys.argv[2])]))
" "$SAMPLE" "$i")

  title=$(python3 -c "import json,sys; print(json.loads(sys.argv[1])['payload']['title'])" "$entry")
  payload=$(python3 -c "import json,sys; print(json.dumps(json.loads(sys.argv[1])['payload']))" "$entry")
  stage=$(python3 -c "import json,sys; print(json.loads(sys.argv[1])['stage'])" "$entry")

  echo "  creating \"$title\" (stage: $stage)"
  wf_id=$(curl -sf -X POST "$API_BASE/workflows" \
    -H "Content-Type: application/json" \
    -d "$payload" | python3 -c "import json,sys; print(json.load(sys.stdin)['id'])")

  case "$stage" in
    draft) ;;
    planned)
      curl -sf -X POST "$API_BASE/workflows/$wf_id/plan" > /dev/null
      ;;
    completed)
      curl -sf -X POST "$API_BASE/workflows/$wf_id/plan" > /dev/null
      curl -sf -X POST "$API_BASE/workflows/$wf_id/approve" > /dev/null
      curl -sf -X POST "$API_BASE/workflows/$wf_id/execute" > /dev/null
      curl -sf "$API_BASE/workflows/$wf_id/report" > /dev/null
      ;;
    *)
      echo "  unknown stage $stage, skipping"
      ;;
  esac
done

echo "✓ Seed complete."
