# 📋 Artifact Logging System - Complete Guide

## ✅ What's Been Fixed & Implemented

### 1. **Gemini API Integration** ✅
- Fixed model name from `gemini-pro` (deprecated) to `gemini-2.0-flash`
- AI-powered explanations are now working perfectly
- Location: [utils/llm_client.py:147](../utils/llm_client.py#L147)

### 2. **Store Layout** ✅
- Fixed messy placements with organized coordinate system
- Set canvas to fixed max-width of 1000px
- Reorganized all 10 locations in a clear grid pattern
- Location: [data/locations.json](../data/locations.json)

### 3. **Comprehensive Artifact Logging** ✅ **NEW!**
- Every analysis now creates a detailed JSON log file
- Logs saved in: `artifacts/logs/`
- Human-readable format designed for non-technical users

---

## 🎯 What is Artifact Logging?

Every time you click **"Analyze Placement"** in the web interface, the system now:

1. **Records every step** of the analysis process
2. **Tracks timing** - how long each step took
3. **Captures warnings** - anything you should know about
4. **Logs errors** - if something goes wrong
5. **Saves results** - final recommendations with explanations
6. **Stores AI details** - whether Gemini was used, what it said

All this information is saved as a **timestamped JSON file** that you can read later to understand exactly what happened.

---

## 📁 Where to Find Your Logs

### File Locations

```
artifacts/logs/
├── README.md                              # Guide to understanding logs
├── viewer.html                            # Visual log viewer (OPEN THIS!)
├── latest.json                            # Most recent analysis
└── analysis_20251117_180446_bf8982a2.json # Timestamped logs
```

### Quick Access

1. **View in Browser** (Recommended):
   ```bash
   open artifacts/logs/viewer.html
   ```

2. **Read JSON Directly**:
   ```bash
   cat artifacts/logs/latest.json
   ```

3. **List All Logs**:
   ```bash
   ls -lh artifacts/logs/*.json
   ```

---

## 📊 What's Inside Each Log File

### 1. Session Information
```json
{
  "session_id": "bf8982a2-a418-4d57-82b4-06eb5d779e3a",
  "timestamp": "2025-11-17T18:04:46.183907",
  "status": "completed",
  "summary": "Analysis completed successfully. Top recommendation: BottomShelf Row 5"
}
```

**What this means:**
- `session_id`: Unique ID for this analysis (useful for debugging)
- `timestamp`: When the analysis started
- `status`: "completed", "error", or "started"
- `summary`: One-sentence overview of what happened

### 2. Steps Array

Every action is logged as a step:

```json
{
  "step_number": 1,
  "step_name": "Workflow Started",
  "description": "Beginning analysis for product: Premium Energy Drink",
  "status": "success",
  "timestamp": "2025-11-17T18:04:46.183981",
  "details": {
    "product": {
      "name": "Premium Energy Drink",
      "category": "Beverages",
      "price": "$2.99",
      "budget": "$2000.00"
    }
  }
}
```

**Typical workflow steps:**
1. **Workflow Started** - Analysis begins
2. **Input Validation** - Checking product details
3. **ROI Analysis** - Analyzing all store locations
4. **ROI Rankings Generated** - Sorting by best ROI
5. **AI Explanation Generation** - Gemini creates explanations

### 3. Warnings

Things that aren't errors but you should know about:

```json
{
  "message": "Budget ($5000) exceeds expected revenue ($2990). May result in negative ROI.",
  "timestamp": "2025-11-17T18:04:46.184100",
  "context": {
    "budget": 5000,
    "expected_revenue": 2990
  }
}
```

### 4. Final Results

The recommendations with human-readable interpretation:

```json
{
  "recommendations": [
    {
      "rank": 1,
      "location": "End Cap 1 - Beverages",
      "roi_score": 1.63,
      "roi_percentage": "63.0%",
      "interpretation": "Great - Strong return expected"
    }
  ]
}
```

**ROI Interpretations:**
- **1.8+**: "Excellent - Very high return expected"
- **1.5-1.8**: "Great - Strong return expected"
- **1.2-1.5**: "Good - Solid return expected"
- **1.0-1.2**: "Moderate - Positive return expected"
- **Below 1.0**: "Poor - May result in loss"

### 5. Metadata

Performance and configuration info:

```json
{
  "duration_seconds": 6.02,
  "total_steps": 5,
  "ai_enabled": true,
  "ai_model": "gemini-2.0-flash",
  "end_time": "2025-11-17T18:04:52.199333"
}
```

---

## 🖥️ Using the Log Viewer

### Opening the Viewer

```bash
open artifacts/logs/viewer.html
```

### Features

1. **Auto-loads latest analysis** - Shows your most recent run
2. **Color-coded steps** - Green = success, Yellow = warning, Red = error
3. **Visual recommendations** - Top recommendation highlighted in gold
4. **Timeline view** - See how long each step took
5. **Refresh button** - Load latest analysis anytime

### What You'll See

- **Session Summary Card** - Status, duration, steps, AI usage
- **Workflow Steps** - Chronological list with descriptions
- **Warnings & Errors** - Highlighted in yellow/red boxes
- **Recommendations** - Ranked list with ROI scores and interpretations

---

## 🔍 Understanding the Logs (Layman's Terms)

### Example Scenario

You analyze a "Premium Energy Drink" with a $2000 budget:

**Step 1: Workflow Started**
> "Beginning analysis for product: Premium Energy Drink"
>
> **What's happening:** The system received your product details and created a new session to track everything.

**Step 2: Input Validation**
> "Checking that all product details are valid and complete"
>
> **What's happening:** Making sure you filled in all required fields (name, price, category, etc.) and the values make sense.

**Step 3: ROI Analysis**
> "Analyzing all available store locations and predicting ROI for each one"
>
> **What's happening:** The system is checking every shelf location in the store, calculating which ones are affordable within your $2000 budget, and predicting how much profit you'll make in each spot.

**Step 4: ROI Rankings Generated**
> "Successfully analyzed 1 locations within budget"
>
> **What's happening:** Found that only 1 location fits your budget. The system ranked all options and is showing you the best ones first.

**Step 5: AI Explanation Generation**
> "Using Google Gemini AI to create natural language explanations"
>
> **What's happening:** Instead of just showing numbers, the AI is writing a detailed explanation in plain English about why this location is recommended, what the risks are, and how to maximize success.

### Why Only 1 Location?

If you see "analyzed 1 locations", it means:
- Most store locations cost more than your $2000 budget
- The system automatically filtered out expensive options
- Only budget-friendly locations are shown

**Solution:** Increase your budget or look at the "skipped" locations in the console logs to see what you're missing.

---

## 📈 What to Look For

### ✅ Good Signs

- **Status: "completed"** - Analysis finished successfully
- **AI Enabled: true** - You're getting Gemini's smart explanations
- **5 steps completed** - Full workflow executed
- **ROI > 1.0** - You'll make a profit
- **No errors** - Everything worked perfectly

### ⚠️ Warning Signs

- **Warnings about budget** - You might be overspending
- **Only 1-2 locations found** - Budget too tight
- **ROI < 1.0** - Placement might lose money
- **AI Enabled: false** - Not getting smart explanations (check API key)

### ❌ Error Signs

- **Status: "error"** - Something went wrong
- **Errors array has items** - Read the error messages
- **0 recommendations** - No suitable locations found
- **Steps incomplete** - Workflow stopped early

---

## 🛠️ Troubleshooting

### Problem: No logs are being created

**Check:**
```bash
ls -la artifacts/logs/
```

**Solution:**
- Make sure the `artifacts/logs/` directory exists
- Check that the API server is running
- Try running an analysis to generate a new log

### Problem: Viewer shows "Error Loading Log"

**Causes:**
1. No analysis has been run yet
2. `latest.json` doesn't exist
3. JSON file is corrupted

**Solution:**
```bash
# Run a test analysis
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Test Product",
    "category": "Beverages",
    "price": 2.99,
    "budget": 2000,
    "target_sales": 1000,
    "target_customers": "Everyone",
    "expected_roi": 1.5
  }'
```

### Problem: AI Explanations are templates, not natural language

**Check:**
```bash
# Look for this in the log
cat artifacts/logs/latest.json | grep "ai_enabled"
```

**Solution:**
- If `ai_enabled: false`, your Gemini API key isn't working
- Check `.env` file has `GEMINI_API_KEY=...`
- Restart the API server

---

## 📝 Real-World Example

Here's what a complete analysis looks like:

### Input
- Product: "Premium Energy Drink"
- Category: Beverages
- Price: $2.99
- Budget: $2000

### Output (from log)

```json
{
  "status": "completed",
  "duration_seconds": 6.02,
  "total_steps": 5,
  "recommendations": [
    {
      "rank": 1,
      "location": "BottomShelf Row 5",
      "roi_score": 0.85,
      "roi_percentage": "-15.0%",
      "interpretation": "Poor - May result in loss"
    }
  ]
}
```

### What This Tells You

1. **Analysis succeeded** - All 5 steps completed in 6 seconds
2. **Budget was tight** - Only 1 location under $2000
3. **Placement isn't ideal** - ROI of 0.85 means you'll lose 15%
4. **AI provided context** - Explained why this happens and what to do

### Actionable Insights

From the AI explanation in the log:
- Negotiate lower placement cost
- Run promotions to boost sales
- Increase budget to access better locations
- Consider delaying placement until more budget available

---

## 🎯 Best Practices

### 1. Check Logs After Every Analysis

After clicking "Analyze Placement":
1. Open `viewer.html` to see visual summary
2. Check for warnings and errors
3. Read the AI explanation for insights

### 2. Compare Multiple Analyses

Keep old log files to compare:
- Same product, different budgets
- Different products, same location
- Before/after optimization

### 3. Share Logs for Help

If you need support:
1. Find the relevant timestamped JSON file
2. Share the session_id
3. Paste the "errors" or "warnings" sections

### 4. Monitor Performance

Track these metrics over time:
- **duration_seconds** - Is the system getting slower?
- **total_steps** - Are all steps completing?
- **ai_enabled** - Is Gemini consistently available?

---

## 🚀 Next Steps

Now that logging is set up:

1. **✅ Test it yourself**
   - Click "Analyze Placement" in the web UI
   - Open `viewer.html` to see the log
   - Verify all 5 steps completed

2. **📖 Read the README**
   ```bash
   cat artifacts/logs/README.md
   ```

3. **🔍 Explore the JSON**
   - Open `latest.json` in a text editor
   - See the raw data structure
   - Understand what each field means

4. **📊 Run multiple analyses**
   - Try different products
   - Change budgets
   - Compare the logs

---

## 📞 Quick Reference

```bash
# View latest log in browser
open artifacts/logs/viewer.html

# Read latest JSON
cat artifacts/logs/latest.json | python3 -m json.tool

# List all logs
ls -lh artifacts/logs/*.json

# Count total analyses
ls artifacts/logs/analysis_*.json | wc -l

# Find logs with errors
grep -l '"status": "error"' artifacts/logs/*.json

# View only summaries
for f in artifacts/logs/analysis_*.json; do
  echo "File: $f"
  cat "$f" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f\"  Status: {d['status']}, Duration: {d['metadata']['duration_seconds']}s\")"
done
```

---

## ✅ Summary

You now have:

1. **✅ Working Gemini API** - Natural language explanations
2. **✅ Fixed store layout** - Organized, clear placements
3. **✅ Comprehensive logging** - Every action tracked
4. **✅ Visual log viewer** - Easy-to-read interface
5. **✅ Human-readable format** - No technical jargon

**Every analysis is now fully documented and easy to understand!**
