# FPT Source Register

**Research use:** source discovery and lineage.  
**Access check:** 2026-10-08.  
**Rule:** financial values entering the model must record document date, publication date, reporting period, page/table and extraction status.

## Tier 1 — Primary company sources

| Source | URL | Expected use | Frequency |
|---|---|---|---|
| FPT Investor Relations | https://fpt.com/en/ir | report index, prices, dividends and disclosures | ongoing |
| Public disclosures | https://fpt.com/en/ir/information-disclosures | filing/publication dates and corporate actions | event-driven |
| 2025 Annual Report | https://bctn2025.fpt.com/en/ | business and segment context | annual |
| Overall evaluation | https://bctn2025.fpt.com/en/business-performance-analysis/overall-evaluation/ | consolidated KPIs and segment overview | annual |
| Technology sector | https://bctn2025.fpt.com/en/business-performance-analysis/technology-sector/ | segment revenue/PBT and service structure | annual |
| Global IT Services | https://bctn2025.fpt.com/business-performance-analysis/technology-sector/it-services-for-foreign-markets/ | signed revenue, deal count, workforce, productivity and mix | annual |
| Domestic IT Services | https://bctn2025.fpt.com/business-performance-analysis/technology-sector/it-services-for-domestic-market/ | signed revenue, Made-by-FPT and AI/cloud indicators | annual |
| Telecommunications | https://bctn2025.fpt.com/en/business-performance-analysis/telecommunications/ | segment revenue/PBT | annual |
| Telecom services | https://bctn2025.fpt.com/business-performance-analysis/telecommunications/telecommunications-services/ | broadband and operating narrative | annual |
| Education | https://bctn2025.fpt.com/business-performance-analysis/education/ | capacity/footprint and investment context | annual |

## Clock A source rule

Clock A cutoff là 2025-10-31. Tài liệu phát hành sau ngày này:

- không được dùng để tạo forecast/assumptions ban đầu;
- chỉ được lưu trong `actuals` để validation/post-mortem;
- phải có cột `available_at` để ngăn leakage.

Tài liệu dự kiến cho Clock A:

- audited FY2020–FY2024 statements;
- annual reports FY2020–FY2024;
- Q1, H1 và 9M 2025 filings/earnings materials xuất bản trước cutoff;
- corporate-action disclosures trước cutoff;
- market price/share data tại research date với nguồn và adjustment rõ.

Inventory máy đọc được nằm tại `configs/sources.yaml`. Các annual reports FY2020–FY2024, 9M2025 earnings report, Q3/2025 financial statements và valuation-market sources đã được resolve cho phạm vi hiện tại. Không đánh dấu `reconciled` chỉ vì tài liệu đã được tìm thấy.

## Source metadata schema

| Field | Meaning |
|---|---|
| `source_id` | identifier ổn định |
| `issuer` | FPT hoặc đơn vị phát hành |
| `document_type` | audited_fs, interim_fs, annual_report, earnings_report, disclosure |
| `reporting_period_end` | kỳ tài chính kết thúc |
| `published_at` | ngày tài liệu được công bố |
| `available_at` | ngày model được phép sử dụng |
| `language` | vi/en |
| `url` | source URL |
| `local_snapshot` | đường dẫn snapshot nếu license cho phép |
| `checksum` | kiểm tra phiên bản tài liệu |
| `extraction_status` | pending/extracted/reconciled/rejected |
| `notes` | restatement, scope hoặc limitation |

## Data licensing rule

- Không commit raw daily market-data history từ nguồn không cho phép redistribution.
- Repo hiện chỉ chứa sparse month-end observations derived từ public endpoint, kèm attribution và phương pháp; phải rà lại provider terms trước production/publication quy mô lớn.
- Nếu quyền redistribution không rõ tại thời điểm publish, thay sample bằng synthetic series hoặc download instructions.
- Company filings công khai vẫn cần giữ source link và attribution.
- Broker research chỉ dùng để tham khảo nếu quyền truy cập cho phép; không commit PDF hay sao chép estimate table.
