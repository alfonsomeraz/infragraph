#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${INFRAGRAPH_API_URL:-http://localhost:8000}"
API="${BASE_URL}/api"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

PLAN_FILE="${ROOT_DIR}/examples/terraform-plan.json"
STATE_FILE="${ROOT_DIR}/examples/terraform-state.json"

echo "==> Seeding InfraGraph at ${API}"

# Upload plan
echo "--> Uploading terraform-plan.json ..."
plan_resp=$(curl -s -w "\n%{http_code}" -X POST "${API}/ingest/upload" \
  -F "file=@${PLAN_FILE}")
plan_code=$(echo "$plan_resp" | tail -1)
plan_body=$(echo "$plan_resp" | sed '$d')
if [ "$plan_code" -ne 201 ]; then
  echo "FAILED (HTTP ${plan_code}): ${plan_body}"
  exit 1
fi
echo "    Plan ingested: ${plan_body}" | head -c 200
echo

# Upload state
echo "--> Uploading terraform-state.json ..."
state_resp=$(curl -s -w "\n%{http_code}" -X POST "${API}/ingest/upload" \
  -F "file=@${STATE_FILE}")
state_code=$(echo "$state_resp" | tail -1)
state_body=$(echo "$state_resp" | sed '$d')
if [ "$state_code" -ne 201 ]; then
  echo "FAILED (HTTP ${state_code}): ${state_body}"
  exit 1
fi
echo "    State ingested: ${state_body}" | head -c 200
echo

# Run findings scan
echo "--> Running findings scan ..."
scan_resp=$(curl -s -w "\n%{http_code}" -X POST "${API}/findings/scan")
scan_code=$(echo "$scan_resp" | tail -1)
scan_body=$(echo "$scan_resp" | sed '$d')
if [ "$scan_code" -ne 200 ]; then
  echo "FAILED (HTTP ${scan_code}): ${scan_body}"
  exit 1
fi

# Summary
echo ""
echo "==> Seed complete!"
resource_count=$(curl -s "${API}/resources" | python3 -c "import sys,json; print(len(json.load(sys.stdin)['items']))" 2>/dev/null || echo "?")
finding_count=$(echo "$scan_body" | python3 -c "import sys,json; print(len(json.load(sys.stdin)['items']))" 2>/dev/null || echo "?")
echo "    Resources: ${resource_count}"
echo "    Findings:  ${finding_count}"
