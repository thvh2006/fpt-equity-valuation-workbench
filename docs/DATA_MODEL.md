# FPT Analytical Data Model

## 1. Design principles

- Point-in-time: mọi record có `period_end`, `published_at`, `available_at`.
- Bitemporal-ready: tách kỳ kinh tế khỏi ngày thông tin trở nên biết được.
- Reported before normalized: không ghi đè số báo cáo bằng số điều chỉnh.
- Units explicit: currency, scale và per-share unit luôn là field/data contract.
- Restatements append, không silently overwrite.

## 2. Core tables

### `source_document`

Metadata và lineage của filing/report.

### `financial_fact_reported`

```text
issuer
statement
metric
period_start
period_end
period_type
value
currency
scale
consolidation_scope
source_id
published_at
available_at
is_restatement
```

### `financial_fact_normalized`

```text
metric
period_end
reported_value
adjustment_value
normalized_value
adjustment_category
adjustment_rationale
analyst_version
source_id
```

### `segment_fact`

```text
segment_taxonomy_version
segment
subsegment
metric
period_end
value
currency
scope
source_id
```

### `operating_kpi`

Candidate metrics:

- signed revenue;
- number/value bucket of large contracts;
- global IT revenue by geography;
- digital-transformation revenue/mix;
- average total and production workforce;
- revenue per employee;
- telecom/broadband metrics where disclosed;
- education learner/campus/capacity proxies.

### `corporate_action`

```text
action_type
announcement_date
effective_date
ratio_or_quantity
cash_amount
affected_share_class
source_id
```

### `market_observation`

Price, shares, risk-free inputs và market assumptions; public repo có thể chỉ chứa sample.

### `assumption_version`

```text
version
effective_at
scenario
driver
value
unit
rationale
evidence_source_ids
author
```

### `forecast_output`

```text
forecast_origin
model_version
scenario
metric
period_end
point_estimate
lower_bound
upper_bound
```

### `valuation_output`

```text
valuation_date
method
scenario
segment
enterprise_value
equity_adjustment
parent_equity_value
diluted_shares
value_per_share
```

### `thesis_evidence`

```text
hypothesis_id
as_of_date
metric
observed_value
expected_range
evidence_status
analyst_note
source_id
```

## 3. Reconciliation controls

- assets = liabilities + equity;
- cash-flow movement reconciles opening/closing cash subject to FX/classification;
- sum of segment revenue/PBT reconciles consolidated figures or has explicit elimination;
- parent PAT + NCI allocation reconciles consolidated PAT;
- reported basic/diluted EPS reconciles earnings and weighted shares within tolerance;
- FCFF bridge reconciles EBIT, tax, D&A, capex và working capital;
- enterprise-to-equity bridge includes net debt/cash, associates and minority treatment.

## 4. Cutoff enforcement

Clock A query rule:

```text
available_at <= 2025-10-31
```

Actuals published later live in a separate validation view. Tests must fail if a post-cutoff source enters Clock A features or assumptions.

## 5. Public-repo outputs

- `sample_financial_facts.csv`: reduced/attributed sample;
- `sample_operating_kpis.csv`;
- `assumptions.yaml`;
- `forecast_outputs.parquet`;
- `valuation_summary.json`;
- `decision_memo.md` and rendered PDF;
- charts as SVG/WebP.

Raw filings and licensed market data are not automatically committed.

