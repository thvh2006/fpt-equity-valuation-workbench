# Equity Valuation Project Charter

## Problem statement

Khi có filing hoặc market evidence mới, equity analyst cần cập nhật earnings outlook và valuation để quyết định giữ, thay đổi hoặc bác bỏ investment thesis.

## Research wedge

So sánh **market-implied expectations** từ reverse DCF với driver-based forecast và base rates. Câu hỏi cụ thể sẽ được viết sau khi chọn công ty.

## Baselines

- last-period/seasonal revenue growth;
- stable-margin forecast;
- historical median multiple;
- analyst driver model là primary, statistical model chỉ là challenger nếu dữ liệu đủ.

## Failure criteria

- không reconcile được statements;
- terminal value chi phối nhưng không có sensitivity rõ;
- forecast không thắng/không giải thích tốt hơn baseline;
- research thesis chỉ dựa trên target price;
- app không cho thấy assumption-to-decision bridge.

## MVP definition

- một công ty phi tài chính;
- historical statements và driver tree;
- base/bull/bear forecast;
- DCF + reverse DCF;
- sensitivity;
- one-page decision view;
- methodology và limitations.

## Out of scope v0.1

- automated trading;
- intraday price prediction;
- NLP trên mọi filing;
- multi-company portfolio recommendation;
- live broker integration.

