# Retail Placement ROI Prototype — Hackathon

This is a 24-hour rapid prototype to simulate retail shelf placement ROI using:
- Unity (2D scene + No-code UI buttons for shelves)
- Google Sheets (data & analytics)
- Synthetic knowledge base
- Precomputed ROI JSON
- Simple shelf hotspot interactions

## Assumptions
- All retail stats are synthetic and created for demo purposes.
- `traffic_index` = approximate relative footfall per shelf.
- `visibility_factor` = multiplier based on shelf type:
  - endcap = 1.5
  - eye_level = 1.2
  - low_shelf = 0.8
  - checkout = 1.6
- Category conversion rates are generic industry estimates.
- ROI values in shelves_roi.json are precomputed for speed.

## Data Files
- products.csv — product pricing & margin
- shelves.csv — coordinates + visibility data
- retail_kb.csv — category-level retail insights
- shelves_roi.json — expected ROI for each shelf

## Unity Usage
- 2D scene with floorplan.png
- Place UI buttons over each shelf region
- Click shelf → show ROI panel
- “Best Shelf Suggestion” highlights highest ROI shelf from JSON (S4)
