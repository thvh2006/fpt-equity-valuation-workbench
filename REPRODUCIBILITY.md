# Reproducibility

## Quick start

Requirements: Python 3.10 or newer. The core Clock B model uses only the Python standard library.

```bash
python scripts/run_clock_b.py
python scripts/run_checks.py
```

The first command reads `data/sample/clock_b_inputs.json` and writes `reports/clock_b_summary.json`. The second runs historical-data integrity checks and Clock B valuation tests.

## Expected Base result

- WACC: 10.8873%
- operating enterprise value: VND130,660 billion
- SOTP value: VND97,511 per share
- 2027E P/E cross-check: VND89,978 per share
- blended value: VND94,498 per share
- upside to the 9 October 2026 market price: 63.2%

Small differences below VND1 per share may arise from display rounding. The JSON output keeps full precision.

## Model lineage

`clock_b_inputs.json` mirrors the reviewed values in `reports/fpt_equity_valuation_v0_8.xlsx`. The Python implementation is intentionally independent of spreadsheet formulas and serves as a second calculation engine.

The valuation sequence is:

1. forecast continuing-operation revenue, EBIT, NOPAT and FCFF;
2. discount 2027E–2031E FCFF using mid-year timing;
3. capitalise 2027E associate earnings separately;
4. add cash and short-term investments, then subtract debt and NCI;
5. cross-check with 2027E P/E and blend 60% SOTP / 40% P/E.

Clock A and Clock B are separate research clocks. Post-cutoff evidence must never be backfilled into Clock A.
