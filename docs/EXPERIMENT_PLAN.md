# FPT Experiment & Validation Plan

## 1. Forecast experiments

### E1 — Revenue baseline

Compare:

- last-year growth;
- trailing growth average;
- segment historical CAGR;
- driver-based forecast.

Evaluate annual and, where valid, quarterly rolling origins. Report MAE/WAPE plus the effect of forecast error on valuation.

### E2 — Global IT signed-revenue value

Compare models with and without signed-revenue variables available at forecast origin.

Questions:

- Does signed revenue improve near-term forecast beyond lagged revenue?
- Is the relationship stable across periods?
- Does disclosure-definition drift break comparability?

### E3 — Workforce/productivity decomposition

Compare revenue forecast based on:

1. aggregate growth;
2. workforce growth only;
3. workforce × revenue per employee;
4. workforce × productivity with mix/geography overlays.

Do not claim causal productivity drivers unless design supports it.

### E4 — Margin model

Compare:

- constant margin;
- mean-reverting margin;
- driver margin using productivity and segment mix.

Primary decision metric: valuation and implied-expectation error, not tiny in-sample fit improvements.

## 2. Valuation experiments

### E5 — Consolidated DCF vs SOTP

Reconcile both methods. Decompose difference into segment WACC/growth, corporate costs, net cash, investments and minority interest.

### E6 — Reverse DCF surface

Instead of solving one variable, solve a surface of:

- Global IT revenue CAGR;
- steady-state Global IT/Technology margin;
- optional WACC bands.

Plot combinations consistent with market price and overlay historical/analyst-plausible regions.

### E7 — Terminal-value discipline

Test:

- terminal value share of EV;
- implied reinvestment rate;
- implied incremental ROIC;
- fade period sensitivity.

Reject configurations with internally inconsistent growth/reinvestment assumptions.

### E8 — Equity bridge

Measure per-share impact of:

- minority interests;
- consolidation scope;
- ESOP/stock dividends;
- cash/investments;
- alternative lease treatment.

## 3. Scenario and stress experiments

### E9 — Global IT demand slowdown

Stress conversion, growth, pricing/productivity and margin jointly.

### E10 — FX translation

Apply transparent revenue/margin translation scenarios by geography only where exposure data supports it.

### E11 — Telecom capex/content stress

Stress margin, capex intensity and cash conversion; report how much downside protection remains.

### E12 — Reverse stress

Find the smallest joint operating changes that reduce equity value by a chosen percentage or eliminate margin of safety.

## 4. Validation outputs

Every experiment logs:

- hypothesis;
- data cutoff;
- feature/assumption set;
- baseline;
- metric;
- result;
- economic interpretation;
- known limitation;
- decision: retain/reject/defer.

## 5. Anti-overfitting rules

- Predefine hypothesis and baseline.
- Prefer small, interpretable driver sets.
- Do not tune using FY2025 actual before freezing Clock A forecast.
- Keep post-cutoff data invisible until forecast artifact is versioned.
- Report negative results.
- Do not choose WACC/terminal growth to manufacture upside.

## 6. Minimum credible result

The project succeeds even if the driver model does not beat a simple baseline, provided it:

- identifies why;
- quantifies decision impact;
- constrains the valuation honestly;
- improves interpretability or monitoring;
- documents what additional data would be required.

