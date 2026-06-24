# Bluestock Mutual Fund Analytics - Data Quality Audit Report

**Date of Audit**: 2026-06-24
**Audit Status**: PASSED

## 1. Key Metrics Summary
- **Total Schemes in Fund Master**: 40
- **Total Schemes in NAV History**: 40
- **Matching Schemes (Overlapping)**: 40
- **Master Schemes Missing NAV History**: 0
- **Extra Schemes in NAV History (Not in Master)**: 0

## 2. Integrity Analysis
✔ **Referential Integrity Check Passed**: All AMFI codes in `fund_master` possess corresponding daily NAV history rows.

