---
name: equity-data
description: >-
  Pull primary-source data on listed companies from free sources - US issuers through SEC
  EDGAR's APIs (10-K/10-Q/8-K/proxy text, full-text search across all filings since 2001,
  XBRL financials), China A-shares through AkShare (daily prices, income/balance/cash-flow
  statements, financial ratios, 巨潮 cninfo announcements and annual reports, 龙虎榜,
  margin balances). Use whenever a task needs a public company's filings, reported
  financials, risk factors, segment data, exec comp, price history or "which companies
  mention X" - for valuation, job/employer research or coursework - instead of scraping
  finance sites. 中文说法 — "查 10-K", "看财报原文", "SEC 文件", "招股书", "全文本搜索公告",
  "A股行情", "利润表", "年报", "巨潮公告", "龙虎榜", "融资融券". Not for UK companies
  (companies-house MCP) or trading advice.
---
# Listed-company data

Pick the half by where the company is listed. A company listed in both places (A+H,
a US ADR of a Chinese issuer) has filings in both; say which one you used.

## US issuers: SEC EDGAR

Every request needs a User-Agent with a contact, or SEC returns 403:
`curl -s -A "$SEC_USER_AGENT" ...`, where `SEC_USER_AGENT` is an app name plus a contact email
(`export SEC_USER_AGENT="my-research me@example.com"`). If it is unset, ask the user for a contact
email before the first request; never invent one. Stay under 10 requests/second.

| Need | Endpoint |
|---|---|
| Ticker to CIK | `https://www.sec.gov/files/company_tickers.json` (`cik_str`; zero-pad to 10 digits for data.sec.gov) |
| Filing list | `https://data.sec.gov/submissions/CIK##########.json` (`filings.recent`: parallel arrays `form`, `accessionNumber`, `filingDate`, `primaryDocument`) |
| Full-text search | `https://efts.sec.gov/LATEST/search-index?q=%22exact%20phrase%22&forms=10-K&dateRange=custom&startdt=YYYY-MM-DD&enddt=YYYY-MM-DD` |
| All XBRL facts | `https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json` |
| One concept over time | `https://data.sec.gov/api/xbrl/companyconcept/CIK##########/us-gaap/<Tag>.json` |
| Same concept across companies | `https://data.sec.gov/api/xbrl/frames/us-gaap/<Tag>/USD/CY2024Q4I.json` |

Document URL: `https://www.sec.gov/Archives/edgar/data/<CIK without padding>/<accession without dashes>/<primaryDocument>`.
Full-text search hits have `_id` = `<accession>:<filename>`, which gives both parts.

Gotchas:
- XBRL tags vary by filer and year (`Revenues` vs `RevenueFromContractWithCustomerExcludingAssessedTax`); check which tags exist in companyfacts before concluding data is missing.
- companyfacts repeats a value in every later filing that restates it; dedupe on `accn`/`fy`/`fp`/`form`, or filter `form == "10-K"` and `fp == "FY"`.
- Filings come back as raw HTML; strip tags before analysing, and quote section names (Item 1A, Item 7) when citing.
- US issuers only. Foreign private issuers file 20-F/6-K with sparse XBRL.

## China A-shares: AkShare

AkShare is a Python library that wraps exchange, cninfo, Sina, Tencent and Eastmoney
endpoints; no key. Run it without installing anything:
`uv run --no-project --with akshare python -I script.py` (inside a project, `uv add akshare`).
Every call returns a pandas DataFrame. Codes are six digits; some functions want a
market prefix, and the prefix style differs per function, as the table shows.

Checked against akshare 1.20.65 on 2026-11-21 (600519 as the test code):

| Need | Call |
|---|---|
| Daily/weekly/monthly prices | `ak.stock_zh_a_hist_em(symbol="600519", period="daily", start_date="20250101", end_date="20251231", adjust="qfq")` (Chinese column names) |
| Same, fallback sources | `ak.stock_zh_a_hist_tx(symbol="sh600519", start_date=..., end_date=..., adjust="qfq")`, `ak.stock_zh_a_hist_sina(symbol="sh600519", ...)` |
| Key metrics, all periods | `ak.stock_financial_abstract(symbol="600519")` (one column per report date) |
| Income / balance / cash flow | `ak.stock_profit_sheet_by_report_em(symbol="SH600519")`; `stock_balance_sheet_by_report_em`, `stock_cash_flow_sheet_by_report_em` take the same argument. English field codes, one row per report |
| Same, Chinese line items | `ak.stock_financial_report_sina(symbol="sh600519", indicator="利润表")` (`资产负债表`, `现金流量表`) |
| Financial ratios | `ak.stock_financial_analysis_indicator_em(symbol="600519.SH", indicator="按报告期")` |
| Announcements and reports (巨潮) | `ak.stock_zh_a_disclosure_report_cninfo(symbol="600519", market="沪深京", category="年报", start_date="20240101", end_date="20251231")`: title, date, `公告链接` to the cninfo page that holds the PDF |
| 龙虎榜 | `ak.stock_lhb_detail_em(start_date="20251110", end_date="20251114")` |
| Margin balances (SSE) | `ak.stock_margin_detail_sse(date="20251114")`; SZSE: `stock_margin_detail_szse` |

Gotchas:
- Function names change between AkShare releases (`stock_zh_a_hist` became
  `stock_zh_a_hist_em`; `stock_financial_abstract_ths`, `stock_individual_fund_flow` and
  `stock_new_ipo_em` are gone). On an `AttributeError`, list the current names with
  `[n for n in dir(ak) if "keyword" in n]` and read the signature with
  `inspect.signature`; don't guess.
- Eastmoney's push2 quote server rate-limits by IP (`Push2RateLimitError`; about 5
  minutes the first time, 40+ after repeats). That covers the whole-market spot list
  `stock_zh_a_spot_em`, sector constituents `stock_board_*_cons_em` and Hong Kong prices
  `stock_hk_hist_em`. Call them once, cache the frame to disk, and use the Tencent or
  Sina function for prices while blocked. Never retry in a loop.
- `stock_info_a_code_name` (code-to-name list) downloads from szse.cn, which failed TLS
  from this Mac; `stock_individual_info_em` returned empty. Resolve a name to a code
  through the cninfo announcement search, or ask the user for the code.
- `qfq` is forward-adjusted, `hfq` backward, `""` raw. Say which one a chart or return
  figure uses.
- The report columns are cumulative year-to-date (Q3 = nine months). Difference
  consecutive quarters before quoting a single quarter.
- Data is for research. Don't turn it into buy/sell advice.
