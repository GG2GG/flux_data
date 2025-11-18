"""
Artifact Logger - Creates human-readable JSON logs for analysis workflow
Helps non-technical users understand what happens during product placement analysis
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional


class ArtifactLogger:
    """
    Creates detailed, human-readable logs of each analysis run.
    Saves logs as JSON files in the artifacts/logs directory.
    """

    def __init__(self, session_id: str):
        """
        Initialize logger for a specific analysis session.

        Args:
            session_id: Unique identifier for this analysis session
        """
        self.session_id = session_id
        self.start_time = datetime.now()

        # Create artifacts directory if it doesn't exist
        self.artifacts_dir = Path(__file__).parent.parent / "artifacts" / "logs"
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)

        # Initialize log structure
        self.log = {
            "session_id": session_id,
            "timestamp": self.start_time.isoformat(),
            "status": "started",
            "summary": "Analysis in progress...",
            "steps": [],
            "warnings": [],
            "errors": [],
            "final_results": None,
            "metadata": {
                "duration_seconds": None,
                "total_steps": 0,
                "ai_enabled": False
            }
        }

        print(f"📋 ArtifactLogger initialized for session: {session_id}")

    def add_step(self,
                 step_name: str,
                 description: str,
                 details: Optional[Dict[str, Any]] = None,
                 status: str = "success"):
        """
        Log a step in the analysis workflow.

        Args:
            step_name: Name of the step (e.g., "Input Validation", "ROI Prediction")
            description: Human-readable explanation of what happened
            details: Additional data about this step
            status: "success", "warning", or "error"
        """
        step = {
            "step_number": len(self.log["steps"]) + 1,
            "step_name": step_name,
            "description": description,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }

        self.log["steps"].append(step)
        self.log["metadata"]["total_steps"] = len(self.log["steps"])

        # Print to console for real-time feedback
        emoji = "✅" if status == "success" else "⚠️" if status == "warning" else "❌"
        print(f"{emoji} Step {step['step_number']}: {step_name} - {description}")

    def add_warning(self, message: str, context: Optional[Dict[str, Any]] = None):
        """
        Log a warning message.

        Args:
            message: Warning message
            context: Additional context about the warning
        """
        warning = {
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "context": context or {}
        }
        self.log["warnings"].append(warning)
        print(f"⚠️  WARNING: {message}")

    def add_error(self, message: str, error_details: Optional[Dict[str, Any]] = None):
        """
        Log an error.

        Args:
            message: Error message
            error_details: Technical details about the error
        """
        error = {
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "details": error_details or {}
        }
        self.log["errors"].append(error)
        self.log["status"] = "error"
        print(f"❌ ERROR: {message}")

    def set_final_results(self,
                         product_info: Dict[str, Any],
                         recommendations: Dict[str, float],
                         top_recommendation: Optional[Dict[str, Any]] = None,
                         explanation: Optional[Dict[str, Any]] = None):
        """
        Set the final results of the analysis.

        Args:
            product_info: Information about the analyzed product
            recommendations: Dictionary of {location: roi_score}
            top_recommendation: Details about the #1 recommended location
            explanation: AI-generated explanation
        """
        self.log["final_results"] = {
            "product": product_info,
            "total_locations_analyzed": len(recommendations),
            "recommendations": [
                {
                    "rank": i + 1,
                    "location": loc,
                    "roi_score": roi,
                    "roi_percentage": f"{(roi - 1) * 100:.1f}%",
                    "interpretation": self._interpret_roi(roi)
                }
                for i, (loc, roi) in enumerate(
                    sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
                )
            ],
            "top_recommendation": top_recommendation,
            "ai_explanation": explanation
        }

        if self.log["status"] != "error":
            self.log["status"] = "completed"
            self.log["summary"] = f"Analysis completed successfully. Top recommendation: {list(recommendations.keys())[0] if recommendations else 'None'}"

    def _interpret_roi(self, roi: float) -> str:
        """
        Convert ROI score to human-readable interpretation.

        Args:
            roi: ROI score (e.g., 1.5 means 50% return)

        Returns:
            Human-readable interpretation
        """
        if roi >= 1.8:
            return "Excellent - Very high return expected"
        elif roi >= 1.5:
            return "Great - Strong return expected"
        elif roi >= 1.2:
            return "Good - Solid return expected"
        elif roi >= 1.0:
            return "Moderate - Positive return expected"
        else:
            return "Poor - May result in loss"

    def enable_ai(self, model_name: str):
        """Mark that AI explanations are enabled."""
        self.log["metadata"]["ai_enabled"] = True
        self.log["metadata"]["ai_model"] = model_name

    def save(self) -> str:
        """
        Save the log to a JSON file.

        Returns:
            Path to the saved log file
        """
        # Calculate duration
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        self.log["metadata"]["duration_seconds"] = round(duration, 2)
        self.log["metadata"]["end_time"] = end_time.isoformat()

        # Create filename with timestamp
        timestamp_str = self.start_time.strftime("%Y%m%d_%H%M%S")
        filename = f"analysis_{timestamp_str}_{self.session_id[:8]}.json"
        filepath = self.artifacts_dir / filename

        # Save with pretty formatting
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.log, f, indent=2, ensure_ascii=False)

        print(f"💾 Analysis log saved to: {filepath}")
        print(f"⏱️  Total duration: {duration:.2f} seconds")
        print(f"📊 Total steps: {self.log['metadata']['total_steps']}")
        print(f"✅ Status: {self.log['status']}")

        # Also create a "latest.json" for easy access
        latest_path = self.artifacts_dir / "latest.json"
        with open(latest_path, 'w', encoding='utf-8') as f:
            json.dump(self.log, f, indent=2, ensure_ascii=False)

        return str(filepath)

    def create_summary(self) -> Dict[str, Any]:
        """
        Create a simplified summary suitable for display.

        Returns:
            Summary dictionary
        """
        summary = {
            "session_id": self.session_id,
            "status": self.log["status"],
            "duration": f"{self.log['metadata']['duration_seconds']:.2f}s" if self.log['metadata']['duration_seconds'] else "N/A",
            "total_steps": self.log["metadata"]["total_steps"],
            "warnings_count": len(self.log["warnings"]),
            "errors_count": len(self.log["errors"]),
            "ai_enabled": self.log["metadata"]["ai_enabled"]
        }

        if self.log["final_results"]:
            summary["top_location"] = self.log["final_results"]["recommendations"][0]["location"] if self.log["final_results"]["recommendations"] else None
            summary["top_roi"] = self.log["final_results"]["recommendations"][0]["roi_score"] if self.log["final_results"]["recommendations"] else None

        return summary


def create_readme():
    """Create a README file explaining the log format."""
    artifacts_dir = Path(__file__).parent.parent / "artifacts" / "logs"
    readme_path = artifacts_dir / "README.md"

    readme_content = """# Analysis Logs - README

## What Are These Files?

Every time you click "Analyze Placement", the system creates a detailed JSON log file that records everything that happened during the analysis. These logs help you understand:

- What steps were taken
- What decisions were made
- Why a specific location was recommended
- Any warnings or issues encountered

## Log File Structure

Each log file contains:

### 1. **Session Information**
- `session_id`: Unique identifier for this analysis
- `timestamp`: When the analysis started
- `status`: "completed", "error", or "started"

### 2. **Steps Array**
A chronological list of everything that happened:
```json
{
  "step_number": 1,
  "step_name": "Input Validation",
  "description": "Checked that product details are valid",
  "status": "success",
  "details": { ... }
}
```

### 3. **Warnings**
Any issues that didn't stop the analysis but you should know about:
- Budget warnings
- Data quality issues
- Recommendations to improve results

### 4. **Final Results**
The recommendations with human-readable explanations:
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

## How to Read the Logs

### For Quick Overview:
1. Open `latest.json` - this always contains your most recent analysis
2. Look at the `summary` field at the top
3. Check `final_results.recommendations` for the ranked list

### For Detailed Analysis:
1. Open any timestamped file (e.g., `analysis_20251117_164500_abc123.json`)
2. Read through the `steps` array in order
3. Each step explains what happened in plain English

### Understanding ROI Scores

- **1.8+**: Excellent - Very high return expected
- **1.5-1.8**: Great - Strong return expected
- **1.2-1.5**: Good - Solid return expected
- **1.0-1.2**: Moderate - Positive return expected
- **Below 1.0**: Poor - May result in loss

## File Naming

Files are named: `analysis_YYYYMMDD_HHMMSS_sessionID.json`

Example: `analysis_20251117_164530_a1b2c3d4.json`
- Date: November 17, 2025
- Time: 4:45:30 PM
- Session: a1b2c3d4

## Questions?

If something in the logs is unclear:
1. Check the `description` field in each step
2. Look at the `interpretation` field in recommendations
3. Review any warnings for additional context

The logs are designed to be self-explanatory for non-technical users!
"""

    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)

    print(f"📖 Created README at: {readme_path}")


# Create README on module import
create_readme()
