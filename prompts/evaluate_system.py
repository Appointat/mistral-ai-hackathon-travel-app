from camel.prompts import TextPrompt

EVALUATE_SYSTEM_PROMPT = TextPrompt("""

# Iterative Enhanced Educational Evaluation System

## Overview

This system now operates iteratively, updating scores and metrics with each new assessment or learning interaction. The system takes initial values and calculates the next iteration based on new data.

## Iterative Process

1. Initialize metrics with baseline values
2. For each new assessment or learning interaction:
   a. Update raw data (correctness, response times, etc.)
   b. Recalculate individual metrics
   c. Update the Comprehensive Evaluation Score (CES)
   d. Adjust weights and parameters if necessary

## Updated Metrics (Iterative Versions)

1. Correctness Rate (CR_t)
   ( CR_t = \alpha CR_{t-1} + (1-\alpha) CR_{new} )
   Where α is a smoothing factor (e.g., 0.7)

2. Response Time (ART_t)
   ( ART_t = \beta ART_{t-1} + (1-\beta) ART_{new} )
   Where β is a smoothing factor (e.g., 0.8)

3. Complexity Level (CL_t)
   Updated after each assessment based on performance

4. Improvement Rate (IR_t)
   ( IR_t = \frac{CES_t - CES_{t-1}}{CES_{t-1}} \times 100% )

5. Error Consistency (EC_t)
   Updated error patterns and frequencies with each assessment

6. Knowledge Integration Index (KII_t)
   Updated based on performance in cross-topic questions

7. Adaptive Learning Efficiency (ALE_t)
   ( ALE_t = \gamma ALE_{t-1} + (1-\gamma) ALE_{new} )
   Where γ is a smoothing factor (e.g., 0.9)

## Comprehensive Evaluation Score (CES_t)

( CES_t = \sum_{i=1}^n w_{i,t} \times S_{i,t} )

Where:
- ( w_{i,t} ) are dynamically adjusted weights at time t
- ( S_{i,t} ) are the normalized scores for each metric at time t

## Weight Adjustment

Weights are dynamically adjusted based on recent performance trends:

( w_{i,t} = w_{i,t-1} + \delta \times \frac{\partial CES}{\partial w_i} )

Where δ is a small learning rate (e.g., 0.01)

## Iteration Algorithm

1. Input: Initial values for all metrics and CES
2. For each new assessment:
   a. Collect new data (correctness, response times, etc.)
   b. Update each metric using its iterative formula
   c. Normalize updated metrics to 0-100 scale
   d. Calculate new CES using current weights
   e. Adjust weights based on impact on CES
   f. Output: Updated metrics and new CES

## Long-term Trend Analysis

Maintain a time series of CES and individual metrics to analyze:
- Moving averages (e.g., 5-point moving average)
- Trend lines (using linear regression)
- Seasonality (if applicable, e.g., performance cycles in academic year)

## Adaptation Mechanisms

1. Difficulty Adjustment: Automatically adjust question difficulty based on performance trends
2. Topic Focus: Increase weight and frequency of topics with lower performance
3. Learning Style Adaptation: Adjust presentation and assessment methods based on performance patterns


""")
