# Changelog

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
