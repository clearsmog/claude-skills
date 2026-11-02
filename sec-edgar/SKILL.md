---
name: sec-edgar
description: Pull primary-source data on US-listed companies from SEC EDGAR's free APIs (10-K/10-Q/8-K/proxy text, full-text search across all filings since 2001, XBRL financials). Use whenever a task needs a US public company's filings, reported financials, risk factors, segment data, exec comp, or "which companies mention X" — for valuation, job/employer research or coursework — instead of scraping finance sites.
---
# SEC EDGAR

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
- US issuers only. Foreign private issuers file 20-F/6-K with sparse XBRL; UK companies go through the companies-house MCP.
