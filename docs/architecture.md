# Agent Responsibility Contracts

## 1. Planner Agent
- INPUT: user_query (raw string)
- JOB: classify intent, extract budget, extract category, define plan
- OUTPUT: intent, plan, budget, category
- RULE: Never touches products or LLM research

## 2. Search Agent
- INPUT: budget, category, intent
- JOB: query SQLite DB, filter by price + category + rating
- OUTPUT: product_list (max 5 products)
- RULE: No LLM calls — pure DB logic only

## 3. Research Agent
- INPUT: product_list
- JOB: for each product, extract pros/cons/difficulty/use_cases from reviews
- OUTPUT: research_data list
- RULE: Runs in PARALLEL per product (Phase 4 upgrade)

## 4. Comparison Agent
- INPUT: product_list + research_data
- JOB: score each product, rank them, pick best
- OUTPUT: comparison_result with scoring table
- RULE: Output must be structured JSON, not prose

## 5. Recommendation Agent
- INPUT: comparison_result + research_data
- JOB: generate human-readable final answer with reasoning
- OUTPUT: final_answer (string), recommended_product_id
- RULE: Must reference comparison data — no hallucinated facts

## 6. Critic Agent
- INPUT: final_answer + product_list + comparison_result
- JOB: score the recommendation (0.0-1.0), flag issues
- OUTPUT: validation_score, validation_feedback
- RULE: If score < 0.7 AND retry_count < 3 → loop back
         If score >= 0.7 → pass to output
         If retry_count >= 3 → force pass (avoid infinite loop)

## 7. Action Agent
- INPUT: intent + recommended_product_id + user confirmation
- JOB: write order to DB, return order_id
- OUTPUT: order_status, order_id
- RULE: Only runs if intent == "order" AND user said "yes"


## Workflow

## Workflow Diagram

USER QUERY
    │
    ▼
┌─────────────┐
│   PLANNER   │  ← Groq (fast classification)
│   AGENT     │
└──────┬──────┘
       │
  ┌────┴─────────────────────────┐
  │ intent?                      │
  ▼                              ▼
[recommendation]              [order/return/track]
  │                              │
  ▼                              ▼
┌────────┐              ┌──────────────┐
│ SEARCH │              │    ACTION    │
│ AGENT  │              │    AGENT     │ ← DB write
└───┬────┘              └──────────────┘
    │
    ▼
┌──────────┐
│ RESEARCH │  ← NVIDIA NIM (parallel per product in Phase 4)
│  AGENT   │
└─────┬────┘
      │
      ▼
┌────────────┐
│ COMPARISON │  ← NVIDIA NIM (structured scoring)
│   AGENT    │
└──────┬─────┘
       │
       ▼
┌───────────────┐
│ RECOMMENDATION│  ← NVIDIA Nemotron (best reasoning)
│    AGENT      │
└───────┬───────┘
        │
        ▼
┌──────────────┐
│    CRITIC    │  ← Groq (fast validation)
│    AGENT     │
└──────┬───────┘
       │
  score >= 0.7?
  ┌────┴────┐
  YES       NO (retry_count < 3)
  │         │
  ▼         └──────────────────┐
OUTPUT                         │
(final answer             back to RECOMMENDATION
 shown to user)
