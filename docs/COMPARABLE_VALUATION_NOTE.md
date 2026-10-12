# FPT Comparable Valuation Note

## Objective

Use a point-in-time relative-valuation cross-check without replacing the company-specific DCF. The analysis asks whether FPT's market price and DCF are plausible relative to listed companies exposed to similar profit pools.

## Research clock

- Valuation date: 31 October 2025.
- Global IT and telecom peer data: 21 October 2025.
- Education peer data: 12 August 2025.
- No operating result published after the cutoff is used in the forecast or valuation.

## Peer architecture

The peer set follows FPT's business mix instead of treating FPT as a pure-play software company.

1. **Global IT services**: listed Indian IT-services companies with material offshore delivery and digital-transformation exposure.
2. **Telecom**: Asian integrated telecom, broadband and digital-infrastructure operators.
3. **Education**: listed Asian education providers. This is the weakest comparison because FPT's disclosed segment also includes investment and other activities.

The workbook preserves all published observations, including high telecom multiples. Medians limit outlier influence without silently deleting the observations.

## Earnings bridge

The applied P/E uses the portfolio model's own FY2026E parent earnings:

```text
FY2026E EBIT
× FY2024 PBT / EBIT calibration
= FY2026E PBT
× (1 - selected-case tax rate)
= FY2026E group PAT
× 9M2025 parent share of group PAT
= FY2026E NPAT-MI
÷ reported shares outstanding
= FY2026E EPS
```

This produces FY2026E EPS of approximately VND5,794. It is intentionally independent of broker EPS forecasts.

## Multiple selection

The segment medians are weighted by 9M2025 PBT contribution:

| Segment | PBT weight | 2026F peer P/E median | Weighted contribution |
| --- | ---: | ---: | ---: |
| Technology | 45.4% | 26.6x | 12.1x |
| Telecom | 33.8% | 16.5x | 5.6x |
| Education, investment and other | 20.7% | 17.1x | 3.5x |
| **Mix-adjusted median** | **100.0%** |  | **21.2x** |

A 5% comparability adjustment reduces the applied multiple to 20.2x. The adjustment reflects FPT's conglomerate structure and the imperfect match between the disclosed education/investment/other segment and pure education peers.

## Valuation interpretation

- P/E comparable value: approximately VND116,754 per share.
- DCF value: approximately VND132,527 per share.
- 60% DCF / 40% comparable blended value: approximately VND126,218 per share.
- Blended price gap to the 31 October 2025 close: approximately 22.7%.

The valuation gap between DCF and P/E is analytically useful. The DCF assigns more value to FPT's medium-term cash-flow growth, while the peer method reflects the lower market multiples observed during the 2025 IT-services slowdown.

## Limitations

- The peer set comes from broker research sourced from Bloomberg, not a licensed dataset committed to the repository.
- P/E is sensitive to tax, non-controlling interests and non-operating income. The earnings bridge exposes these assumptions rather than hiding them in a consensus EPS input.
- Education peers are dated earlier than the global IT and telecom peers.
- The low P/E case uses FPT's observed 17.0x 2026F P/E as a market reference. It is not a peer quartile.
- Historical FPT trading bands are not yet included; they are the next valuation extension.
