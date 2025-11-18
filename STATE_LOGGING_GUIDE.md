# State Transition Logging Guide

## Overview

The multi-agent system now includes **comprehensive state transition logging** that tracks every step of the workflow as JSON files. This makes it easy to:

- Debug data flow issues
- Trace where values come from (like the placement cost)
- Understand agent decision-making
- Audit recommendations
- Profile performance

## How It Works

### Automatic Logging

Every API request automatically creates a session-specific log directory with JSON files tracking:

1. **Agent Input/Output States** - What data each agent receives and produces
2. **State Transitions** - How data flows between agents
3. **Decision Points** - Conditional routing decisions
4. **Data Transformations** - Changes to data structure
5. **Performance Metrics** - Execution time for each agent
6. **Errors** - Full error context with state at time of failure

### Log Location

Logs are stored in:
```
logs/state_transitions/{session_id}/
```

Each session ID (from the API response) gets its own directory.

## Log Files

### By Agent (Step)

- `step1_InputAgent_input.json` - Input validation agent input
- `step1_InputAgent_output.json` - Input validation agent output
- `step3_AnalyzerAgentV2_input.json` - ROI analysis agent input
- `step3_AnalyzerAgentV2_output.json` - ROI analysis agent output
- `step4_ExplainerAgent_input.json` - Explanation generation input
- `step4_ExplainerAgent_output.json` - Explanation generation output

### Workflow Events

- `event_session_start.json` - Session initialization
- `event_session_end.json` - Session completion with summary
- `error_*.json` - Error logs (if any failures occur)

## Example: Tracing Placement Cost

Let's say you want to understand where the $220 placement cost comes from:

### 1. Find Your Session ID

From the API response:
```json
{
  "session_id": "abc123...",
  "recommendations": {...}
}
```

### 2. Navigate to Log Directory

```bash
cd logs/state_transitions/abc123.../
```

### 3. Check AnalyzerAgent Output

```bash
cat step3_AnalyzerAgentV2_output.json
```

Look for the `roi_predictions` section:
```json
{
  "event": "agent_output",
  "agent": "AnalyzerAgentV2",
  "timestamp": "2025-01-18T...",
  "state": {
    "roi_predictions": {
      "End Cap 1 - Beverages": {
        "location": "End Cap 1 - Beverages",
        "roi": 2.05,
        "placement_cost": 220.0,  <-- HERE IT IS!
        "confidence_interval": [1.74, 2.36]
      }
    }
  },
  "metrics": {
    "execution_time_seconds": 0.123
  }
}
```

### 4. Trace Backwards

To see how this cost was calculated:

1. Check `step3_AnalyzerAgentV2_input.json` - see what locations were loaded
2. Look at the cost manager configuration in logs
3. Check if there's a data transformation log

## Debugging Common Issues

### Issue: Wrong Placement Cost

**Steps**:
1. Find session: `logs/state_transitions/{session_id}/`
2. Check `step3_AnalyzerAgentV2_output.json` → `placement_cost` field
3. Verify location data: Look for `locations` in the output
4. Check configuration: Review `config/placement_costs.yaml`

### Issue: Wrong ROI Score

**Steps**:
1. Check `step3_AnalyzerAgentV2_output.json` → `roi_predictions` → `roi` field
2. Look for data quality in `metadata` section
3. Check if category lifts were computed or defaulted
4. Review `data/computed/category_lifts.json` for the actual lift factors used

### Issue: Incorrect Location Names

**Steps**:
1. Check `step3_AnalyzerAgentV2_input.json` → `locations` array
2. Compare with `data/archive/synthetic/locations.json`
3. Verify the demo UI is using exact name matches

## Enabling/Disabling

### Disable Globally

In `api/main.py`:
```python
orchestrator = OrchestratorV2(
    data_dir="data",
    config_dir="config",
    enable_state_logging=False  # <-- Disable
)
```

### Check Logs Were Created

```bash
ls -la logs/state_transitions/
```

You should see directories named with session IDs.

## Performance Impact

- **Minimal** - Logging adds ~5-10ms per agent
- **Storage** - ~50-200KB per session
- **Rotation** - Logs are NOT auto-deleted (manual cleanup needed)

## Log Rotation

Logs accumulate over time. To clean up:

```bash
# Remove logs older than 7 days
find logs/state_transitions -type d -mtime +7 -exec rm -rf {} +

# Or remove all logs
rm -rf logs/state_transitions/*
```

## JSON Structure

All log files follow this structure:

```json
{
  "event": "agent_input|agent_output|error|decision_point|...",
  "agent": "AgentName",
  "timestamp": "ISO 8601 timestamp",
  "step": 1,  // Optional step number
  "state": {
    // Full PlacementState serialized as dict
  },
  "metrics": {
    "execution_time_seconds": 0.123,
    "errors_count": 0,
    "warnings_count": 1
  }
}
```

## Advanced: Custom Logging

To log custom events in your agents:

```python
from utils.state_logger import get_state_logger

state_logger = get_state_logger()

# Log a decision point
state_logger.log_decision_point(
    decision_name="budget_check",
    condition="cost <= budget",
    result=True,
    context={"cost": 2000, "budget": 5000}
)

# Log a data transformation
state_logger.log_data_transformation(
    transformation="filter_by_budget",
    input_data=all_locations,
    output_data=affordable_locations,
    agent="AnalyzerAgent"
)
```

## Troubleshooting

### Logs Not Being Created

**Check**:
1. `enable_state_logging=True` in orchestrator init
2. Session ID is being passed to `orchestrator.execute()`
3. Permissions on `logs/` directory

### Logs Are Empty

**Possible causes**:
1. Workflow failing before agents execute
2. Serialization errors (check console logs)
3. Pydantic models not serializing correctly

### Cannot Find Specific Data

**Tips**:
1. Use `jq` to query JSON: `cat step3_*.json | jq '.state.roi_predictions'`
2. Search all logs: `grep -r "placement_cost" logs/state_transitions/`
3. Check the `event` field to understand log type

## Example Workflow

```bash
# 1. Make API request
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"product_name": "Cola", "price": 2.99, ...}'

# 2. Get session ID from response
export SESSION_ID="abc123..."

# 3. View all logs for this session
ls logs/state_transitions/$SESSION_ID/

# 4. Check analyzer output
cat logs/state_transitions/$SESSION_ID/step3_AnalyzerAgentV2_output.json | jq '.state.roi_predictions'

# 5. Check for errors
cat logs/state_transitions/$SESSION_ID/error_*.json 2>/dev/null || echo "No errors"

# 6. View session summary
cat logs/state_transitions/$SESSION_ID/event_session_end.json | jq '.summary'
```

## Benefits

### 1. Complete Transparency
See exactly what data each agent processes and produces.

### 2. Easy Debugging
Trace any value back to its source with full context.

### 3. Audit Trail
Every recommendation has a complete audit trail showing how it was generated.

### 4. Performance Analysis
See which agents take the longest and optimize accordingly.

### 5. Data Validation
Verify that your data files are being loaded and used correctly.

## Next Steps

1. Run a test analysis
2. Navigate to `logs/state_transitions/{session_id}/`
3. Open the JSON files to understand the data flow
4. Use this to debug any discrepancies in recommendations
