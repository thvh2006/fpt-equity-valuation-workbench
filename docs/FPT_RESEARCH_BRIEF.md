# FPT Equity Research Brief

## 1. Research mandate

### Persona

Equity analyst chuẩn bị recommendation cho investment committee.

### Decision

Xác định market-implied expectations có được operating evidence hỗ trợ hay không; từ đó hình thành valuation range, monitoring triggers và điều kiện bác bỏ thesis.

### Không phải mục tiêu

- dự báo giá cổ phiếu ngắn hạn;
- tạo buy/sell signal tự động;
- dùng AI để tóm tắt tin tức rồi gọi đó là valuation;
- tối ưu target price theo hindsight.

## 2. Hai research clocks

### Clock A — Historical reconstruction, dùng để kiểm định

- **Forecast origin:** 9M 2025.
- **Information cutoff:** 2025-10-31.
- Chỉ sử dụng thông tin công khai trước hoặc tại cutoff.
- Forecast FY2025 và giai đoạn sau.
- Dùng actual FY2025 công bố sau cutoff để đo forecast error và viết post-mortem.

Clock A chứng minh model không nhìn tương lai và cho phép kiểm định thật thay vì chỉ fit lịch sử.

### Clock B — Live research view

- Cập nhật bằng filing/earnings report chính thức gần nhất.
- Giá thị trường và share count dùng cùng effective date được ghi rõ.
- Mọi thay đổi assumption phải có version và reason.
- Clock B chỉ được mở sau khi Clock A chạy ổn định.

Không trộn hai clock trong cùng một valuation output.

## 3. Central research question

> Bao nhiêu phần của market-implied value phụ thuộc vào tăng trưởng và margin của Global IT Services; signed revenue, large-deal mix và productivity có cung cấp đủ evidence để hỗ trợ kỳ vọng đó không?

### Secondary questions

1. Technology growth đến từ headcount, productivity hay service/geography mix?
2. Telecommunications tạo downside protection và cash-flow stability đến mức nào?
3. Education/other nên được model chi tiết hay chỉ như một value bucket thận trọng?
4. Consolidation, minority interest và dilution thay đổi equity value per share ra sao?
5. Terminal assumptions có nhất quán với reinvestment và ROIC không?

## 4. Hypotheses

### H1 — Implied-expectations concentration

Phần lớn upside/downside của equity value sẽ tập trung vào Global IT Services revenue CAGR và steady-state margin, không phải terminal growth đơn lẻ.

**Có thể bác bỏ nếu:** telecom/other hoặc WACC giải thích phần lớn variation trong valuation decomposition.

### H2 — Productivity matters more than raw headcount

Revenue per production employee và high-value contract mix giải thích incremental margin tốt hơn tốc độ tăng headcount đơn thuần.

**Có thể bác bỏ nếu:** driver model không cải thiện forecast/interpretability so với revenue growth baseline.

### H3 — Signed revenue is useful but not sufficient

Signed revenue giúp dự báo near-term Global IT Services revenue, nhưng conversion timing và contract duration tạo sai số material.

**Có thể bác bỏ nếu:** signed revenue không tăng predictive value ngoài lagged revenue hoặc disclosure không nhất quán.

### H4 — Telecom stabilizes downside

Telecommunications có cash-flow/margin profile ổn định hơn Technology và giảm downside trong bear case.

**Có thể bác bỏ nếu:** capex/content cost/regulatory or consolidation effects làm free cash flow biến động tương đương Technology.

### H5 — Per-share value is sensitive to normalization

Minority interest, ESOP/stock dividends và thay đổi consolidation có thể tạo chênh lệch material giữa headline earnings growth và value attributable per share.

**Có thể bác bỏ nếu:** fully diluted bridge chỉ thay đổi value per share không đáng kể.

## 5. Value-driver tree

```text
Equity value per diluted share
│
├── Enterprise value by segment
│   ├── Global IT Services
│   │   ├── opening backlog / signed revenue
│   │   ├── conversion and project duration
│   │   ├── production workforce
│   │   ├── revenue per employee / productivity
│   │   ├── geography and currency mix
│   │   ├── digital/AI/cloud/service mix
│   │   └── operating margin and reinvestment
│   ├── Domestic IT Services
│   │   ├── signed revenue and conversion
│   │   ├── public/private demand
│   │   ├── Made-by-FPT / AI-cloud mix
│   │   └── margin and working capital
│   ├── Telecommunications
│   │   ├── broadband subscribers / market reach
│   │   ├── ARPU / package upgrades
│   │   ├── churn/retention
│   │   ├── data-center/content contribution
│   │   ├── EBITDA margin
│   │   └── capex intensity
│   └── Education, Investment & Others
│       ├── learners/capacity
│       ├── tuition/yield proxy
│       ├── campus expansion
│       └── capex and margin
│
├── Corporate adjustments
│   ├── net cash/debt
│   ├── associates/investments
│   ├── minority interest
│   ├── leases and provisions
│   └── non-operating assets/liabilities
│
└── Diluted share count
    ├── reported shares
    ├── stock dividends/splits
    ├── ESOP
    └── treasury shares/potential dilution
```

## 6. Forecast architecture

### Layer 1 — Reported statements

- Income statement, balance sheet và cash flow;
- annual 2020–2024 cho Clock A, 9M 2025 YTD/interim;
- quarterly series nếu filing dates và comparability cho phép;
- segment revenue và segment PBT;
- share-count history đã điều chỉnh corporate actions.

### Layer 2 — Normalized history

- continuing operating earnings;
- recurring vs non-recurring items;
- consolidation-scope bridge;
- FX/translation distinction nếu disclosure đủ;
- cash, debt, leases và investments;
- parent-attributable earnings và minority bridge.

### Layer 3 — Operating forecast

**Global IT Services:** driver model + simple growth baseline.  
**Domestic IT:** signed-revenue/conversion proxy + baseline.  
**Telecom:** revenue/margin/capex model, giữ assumptions thận trọng nếu thiếu subscriber data.  
**Education/Other:** simplified driver model hoặc conservative top-down range.

### Layer 4 — Statements and cash flow

- consolidated revenue/PBT/EBIT;
- tax and parent/minority allocation;
- D&A, capex và working capital;
- FCFF và equity bridge;
- balance-sheet consistency checks.

### Layer 5 — Valuation

1. Consolidated DCF — control total.
2. Segment/SOTP DCF — primary insight view.
3. Reverse DCF — flagship.
4. Multiples — cross-check, chỉ thêm khi peer data có license và definition nhất quán.

## 7. Scenario design

### Bear

- slower IT budget conversion;
- productivity uplift thấp;
- margin pressure;
- telecom capex/content costs cao hơn;
- WACC/risk premium cao hơn;
- dilution không được bù bằng value creation.

### Base

- signed revenue chuyển hóa theo historical range;
- productivity/mix cải thiện có giới hạn;
- telecom ổn định;
- reinvestment đủ hỗ trợ growth;
- terminal ROIC/growth internally consistent.

### Bull

- large deals chuyển hóa tốt;
- higher-value AI/cloud/managed-services mix nâng revenue productivity;
- margin mở rộng nhưng không vượt range thiếu căn cứ;
- telecom/data-center economics tốt hơn;
- cost of capital ổn định.

Scenario không được chỉ thay growth. Mỗi scenario cần narrative nhất quán giữa revenue, margin, reinvestment, working capital và WACC.

## 8. Accounting and valuation traps

### Consolidation scope

FPT đã công bố thay đổi phương pháp hợp nhất FPT Telecom trong 2025. Cần lưu cả reported view và pro-forma/comparable view; không nối chuỗi history cơ học.

### Minority interest

Không dùng consolidated profit/enterprise value rồi chia thẳng cho shares của parent. Cần bridge value attributable to parent.

### Share count and dilution

Stock dividends, ESOP và corporate actions phải được phản ánh trong diluted share count và lịch sử per-share metrics.

### Capitalized investment and intangibles

Kiểm tra goodwill, M&A, capitalized software/intangibles và amortisation; tránh coi mọi investment là operating expense hoặc ngược lại.

### FX

Global IT revenue chịu translation và transaction exposure khác nhau. Không quy mọi tăng trưởng VND thành organic constant-currency growth.

### Working capital

Signed contracts không đồng nghĩa cash conversion. Receivables, contract assets/liabilities và customer advances cần được theo dõi nếu disclosed.

### Terminal value

Terminal growth phải nối với reinvestment rate và return on incremental capital. Không dùng terminal margin/growth chỉ để khớp market price.

## 9. Expected flagship screens

### Screen 1 — Market-implied expectations

- current/research-clock price;
- implied Global IT revenue CAGR;
- implied steady-state margin;
- probability/range, không chỉ một nghiệm;
- comparison với historical/base-rate evidence.

### Screen 2 — Driver evidence

- signed revenue → recognised revenue bridge;
- workforce/productivity decomposition;
- geography/service mix;
- forecast vs actual history.

### Screen 3 — SOTP and risk

- value by segment;
- corporate/minority/dilution bridge;
- scenario waterfall;
- key sensitivity.

### Screen 4 — Thesis monitor

- hypothesis;
- metric/trigger;
- latest evidence;
- status: supporting / neutral / contradicting;
- assumption/version changed;
- analyst note.

## 10. MVP exit criteria

- Clock A dataset respects information cutoff;
- statements reconcile and segment totals bridge;
- baseline and driver model both run;
- FY2025 forecast error is reported honestly;
- consolidated DCF and SOTP reconcile within explained adjustments;
- reverse DCF solves for at least two operating drivers;
- dilution/minority/consolidation treatment is documented;
- one-page decision view answers “what must be true?”;
- limitations and no-investment-advice disclaimer are visible.

