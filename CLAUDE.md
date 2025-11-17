# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a multi-agent system that suggests optimal retail product placements based on historical sales data and various metrics. The system is designed to help business owners make data-driven decisions about where to place their products in retail environments.

### Core Functionality

The system takes business owner input including:
- Product details
- Placement budget
- Product price
- Category
- Target sales
- Target customers
- Expected ROI

The agent analyzes historical data to suggest placement locations with ROI scores (e.g., "Main Entrance Isle": 0.7, "Beverage Isle": 1.4) and can defend its recommendations with competitor analysis and historical metrics.

## Agent Architecture

This is a multi-agent system with the following flow:

1. **Input Collection Agent**: Gathers product details from the business owner
2. **ROI Analysis Agent**: Analyzes historical sales data and regional performance to calculate ROI scores for different placement locations
3. **Recommendation Agent**: Generates placement suggestions with ROI scores by location
4. **Defense Agent**: Responds to follow-up questions by pulling competitor product data and metrics to validate recommendations with historical accuracy

The agents work together to provide data-backed product placement recommendations that can be justified with historical evidence.

## Development Status

This is an early-stage project. When implementing:

- Design the agent orchestration layer to coordinate the multi-agent workflow
- Plan data structures for historical sales data, regional metrics, and competitor information
- Consider how to store and query historical product placement data efficiently
- Implement the ROI calculation algorithms based on historical patterns
- Build the competitor analysis and data retrieval capabilities for the defense agent

## Key Design Considerations

- The system must be able to query and analyze historical sales data by region/location
- ROI scoring should be transparent and explainable with supporting data
- The defense agent needs access to competitor product metrics for comparison
- Follow-up questions should be answered with specific, data-backed evidence
