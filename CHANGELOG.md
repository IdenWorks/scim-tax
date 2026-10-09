# Changelog

## 2026-10: 850 vendors, every fact cited to the vendor's own pages

- 850 vendors, up from 286: 570 new rows and 280 of the June rows re-verified. Checked between 5 and 6 October 2026 against each vendor's pricing page, documentation and API reference.
- Schema unchanged (v3, `research/2026-09/SCHEMA.md`). The deeper research behind each row is in `research/2026-09/vendors/{slug}.json` (format in `DEEP_SCHEMA.md`): SCIM endpoints, operations, attributes and what deprovisioning does, the user-management API and its endpoints, IdP catalogue apps, and 24,830 citations, each with the URL and the quoted sentence. 99.7% of the quotes that could be fetched were re-found on the live page by `check_quotes.py`.
- Headline: of the 331 vendors with SCIM, 84% gate it behind a higher plan or sales (89% in June). 48 include SCIM on the plan most teams buy (12 in June).
- Among the June vendors, 88 changed status. Most common moves: Gated to No SCIM (24), Gated to No Tax (14), Unknown to No SCIM (14), Gated to Unknown (13).
- Rules applied in this release (see `DEEP_SCHEMA.md`): No Tax needs a page that names the plan; provisioning through a vendor's own non-SCIM API, outbound-only SCIM and sign-in-only account creation do not count as SCIM; quote-only vendors that document SCIM are Gated at low confidence, with notes starting "Quote-only" (67 rows).
- Removed: Multi, Pivotal Tracker and Rows (discontinued). Merged: Codeium into Devin, Salesloft into Drift (Salesloft), Toggl Plan into Toggl Track.
- Shopify's 79x is gone: Shopify prices per store, not per user, so no per-user multiplier is computed. Largest per-user jump is now HubSpot at 12.9x.
- IdP catalogue apps that provision through a vendor API, a vendor-run directory sync or a third-party connector have no value in the v3 `idp` enum, so they are `null` in `data.json`. The research files keep the detail.
- Known gaps: 15 vendors blocked automated checks and are marked for a manual re-check; 72 quotes across 21 vendors were not re-found and are listed in `research/2026-09/run/RECHECK_QUOTES.txt`.

## 2026-06 — Full pricing refresh + structured fields

- All 286 vendor records re-verified against current vendor pricing pages.
- 81 vendors had a status change since the April 2026 baseline (28% of dataset). Most common move: `unknown` to `gated` as enterprise SCIM availability became confirmable on public pricing pages.
- New structured fields per vendor in `data.json` / `data.csv`:
  - `team_plan` (the lowest paid tier above free)
  - `team_price_per_user_mo` (numeric)
  - `scim_price_per_user_mo` (numeric)
  - `price_multiplier` (scim / team ratio; null when either side is "Contact Sales" or non-per-user)
  - `notes` (edge cases like flat pricing, per-device pricing, add-on add-ons)
  - `last_verified` (ISO date)
- Original free-text fields (`scim_price_text`, `team_price_text`, `pricing_page_url`, `scim_plan`) retained for back-compat.
- Headline stat update: of the 199 vendors known to have SCIM, **89%** gate it behind Enterprise or Contact Sales (was ~80%). 12 vendors include SCIM on all paid plans with no paywall (was 11; Duo Security newly reclassified after Duo Directory was bundled into Essentials).
- Biggest jump confirmed: Shopify Basic ($29) → Plus ($2,300/mo) at 79×. New runners-up: Copper CRM 11×, HubSpot 7.5×, Salesforce 7.0×.

## 2026-04 — First public release

- ~285 vendors surveyed across horizontal and vertical SaaS.
- Source reconciliation across notsosso.com, sso.tax, Okta BAW, Zylo, Productiv, Ramp Velocity.
- Status taxonomy locked: No Tax, Gated, Partial, No SCIM, Unknown.
- Published at https://scimtax.org/ under CC-BY 4.0.
- Raw data available at `data.csv` and `data.json`.

## Planned — 2027-Q1

- Full annual refresh across all vendors.
- Year-over-year deltas: who removed the gate, who added one, who raised the price.
- Expanded coverage of compliance-adjacent SaaS (audit, GRC, security).
- Methodology revision based on community PRs and issues.
