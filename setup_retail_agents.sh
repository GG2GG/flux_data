#!/bin/bash

echo "🚀 Setting up Retail Placement ROI Multi-Agent Workspace..."

# Root folder
ROOT="retail-placement-agents"
mkdir -p $ROOT

# Subfolders
mkdir -p $ROOT/agents
mkdir -p $ROOT/data
mkdir -p $ROOT/docs
mkdir -p $ROOT/workspace/outputs

echo "📁 Folder structure created."

# ------------------------------
# Agent Prompts
# ------------------------------

declare -A prompts

prompts["product_architect_prompt.md"]="# Product Architect Agent
You are the Product Architect Agent...
(Your architect prompt content will be inserted here during expansion)
"

prompts["data_kb_prompt.md"]="# Data & Knowledge Base Agent
You are the Data + KB Agent...
"

prompts["unity_engineer_prompt.md"]="# Unity Engineer Agent
You are the Unity Engineer Agent...
"

prompts["backend_stub_prompt.md"]="# Backend Stub Agent
You are the Backend Stub Agent...
"

prompts["roi_agent_prompt.md"]="# ROI Intelligence Agent
You are the ROI Intelligence Agent...
"

prompts["analytics_agent_prompt.md"]="# Analytics Dashboard Agent
You are the Analytics Dashboard Agent...
"

prompts["devops_packager_prompt.md"]="# DevOps Packager Agent
You are the DevOps Packager Agent...
"

prompts["pitch_agent_prompt.md"]="# Pitch & Storytelling Agent
You are the Pitch & Storytelling Agent...
"

echo "🧠 Creating agent prompt files..."

for file in "${!prompts[@]}"; do
    echo "${prompts[$file]}" > "$ROOT/agents/$file"
done

echo "✅ Agent prompt files created."


# ------------------------------
# Data Files
# ------------------------------

echo "📊 Creating dataset files..."

cat << 'EOF' > $ROOT/data/products.csv
id,sku,name,category,price,cost,margin_pct,notes
1,PK-SN-001,Crunchy Chips,snacks,40,15,62.5,Popular salty snack
2,PK-DR-001,Fresh Cola,beverages,50,20,60,Carbonated drink
3,PK-CH-002,Protein Chocolate,snacks,80,30,62.5,High demand premium snack
4,PK-JC-003,Orange Juice,beverages,90,35,61.1,Healthy beverage option
EOF

cat << 'EOF' > $ROOT/data/shelves.csv
shelf_id,name,x,y,width,height,zone,traffic_index,visibility_factor,notes
S1,Endcap A,300,120,80,40,endcap,250,1.5,Near entrance high traffic
S2,EyeLevel Row 3,150,220,60,30,eye_level,180,1.2,Central aisle
S3,BottomShelf Row 5,80,320,60,30,low_shelf,120,0.8,Low visibility
S4,Checkout Shelf,420,150,90,35,checkout,300,1.6,Impulse buying zone
EOF

cat << 'EOF' > $ROOT/data/retail_kb.csv
category,avg_conversion_rate,avg_basket_value,lift_eye_level_pct,lift_endcap_pct,lift_checkout_pct,baseline_daily_footfall,notes
snacks,0.08,150,1.2,1.5,1.7,200,Synthetic benchmark for snacks
beverages,0.06,200,1.15,1.4,1.3,180,Synthetic benchmark for beverages
EOF

cat << 'EOF' > $ROOT/data/shelves_roi.json
{
  "S1": {"expected_daily_units": 32, "expected_daily_profit": 800, "expected_30d_profit": 24000, "roi_30d": 5.2},
  "S2": {"expected_daily_units": 21, "expected_daily_profit": 520, "expected_30d_profit": 15600, "roi_30d": 3.3},
  "S3": {"expected_daily_units": 12, "expected_daily_profit": 220, "expected_30d_profit": 6600, "roi_30d": 1.4},
  "S4": {"expected_daily_units": 36, "expected_daily_profit": 900, "expected_30d_profit": 27000, "roi_30d": 6.0}
}
EOF

echo "✅ Data files created."


# ------------------------------
# Docs
# ------------------------------

cat << 'EOF' > $ROOT/docs/system_overview.md
# System Overview — Retail Placement ROI Multi-Agent System

This system uses multiple AI agents to generate a complete prototype:
- System architecture
- Datasets
- Unity UI
- ROI logic
- Dashboards
- Pitch

Use the agents one-by-one or orchestrated via OpenRouter, n8n, LangGraph.
EOF

echo "📄 Docs created."

# ------------------------------
# Final Message
# ------------------------------

echo "🎉 Setup complete!"
echo "Navigate to $ROOT and start running agents."


