# Baseline Data Quality & Provenance Audit Report

**Generated At:** `2026-09-04T05:15:16.705617+00:00`  
**Database Engine:** `PostgreSQL 16+`  

---

## 1. Executive Summary & Inventory

| Entity / Table | Total Records | Active / High Priority | Missing Source URL | Relationship Gaps |
| :--- | :---: | :---: | :---: | :---: |
| **Opportunities** | 5,741 | 312 active | 115 | 0 missing Org Link |
| **Organizations** | 212 | 212 | 212 | 0 missing parents |
| **Programs** | 174 | 174 | 156 | N/A |
| **Awards** | 54,313 | 54,313 | 98 | 0 missing Opp Link |
| **Recipients** | 13,948 | 13,724 | N/A | N/A |
| **Contacts** | 3,090 | 3,090 | 3,090 | 0 |

---

## 2. Critical Findings & Data Quality Gaps

1. **Active Opportunities Deadlines**: 
   - **0** active/open opportunities have `close_date = NULL` and require deadline parsing from original solicitation text.
2. **Missing Source URLs**:
   - **89** active opportunities lack direct `source_url`.
3. **Award to Opportunity Linkage**:
   - **0** awards (0.0%) are currently unlinked to a specific parent opportunity.
4. **Field-Level Provenance Coverage**:
   - **0.0%**: Additive `field_provenances` architecture must be instantiated in Phase 2 to store source hashes, citations, and confidence scores.

---

## 3. Prioritized Remediation Roadmap

1. **Tier 1 (Active Opportunities)**: 312 open opportunities across NYSERDA, DOE, CEC, MassCEC, Utilities.
2. **Tier 2 (Connected Programs & Orgs)**: 386 records.
3. **Tier 3 (Closed Precedents)**: 2,677 opportunities.
4. **Tier 4 (Awards & Awardees)**: 68,261 records.
5. **Tier 5 & 6 (Historical & Peripheral)**: 5,415 records.
