# Methodology

The SCIM Tax Index is an open survey of how SaaS vendors price automated user provisioning. This document explains how vendors are selected, how each row is recorded, and how status labels are assigned.

## Vendor selection

Vendors are drawn from cross-referenced industry sources, weighted toward the apps most-deployed in mid-market and enterprise stacks:

- [notsosso.com](https://notsosso.com) (the community SSO tax list)
- [sso.tax](https://sso.tax) (the original community SSO tax list)
- Okta Business at Work (annual SaaS usage report)
- Zylo SaaS Index
- Productiv App Inventory
- Ramp Velocity (SMB / mid-market spend report)
- Okta Integration Network catalogue
- Rippling App Shop catalogue

Coverage spans horizontal SaaS (collaboration, productivity, dev tools, security, finance, HR, marketing) and the largest vertical apps (healthcare, education, real estate, legal). The dataset is not exhaustive of every SaaS company. It is representative of the vendors a typical mid-market IT stack actually buys.

## What we record per vendor

For each vendor:

1. **Whether SCIM is offered**, or an equivalent automated provisioning protocol (some vendors use proprietary directory-sync, JIT, or IdP-specific bridges; we record what is offered, not what we wish was offered).
2. **The lowest plan that includes SCIM** (`scim_plan`), as listed publicly. If SCIM is sold as an add-on, we record the add-on name and price.
3. **The price of that SCIM-bearing plan** (`scim_price_text` for the human-readable string, `scim_price_per_user_mo` for the normalized per-user-per-month numeric where possible). In US dollars, annual billing, publicly listed where available. If gated behind Contact Sales, we record "Contact Sales" and include a confirmed annual-contract range in the notes where customers or analysts have disclosed it.
4. **The Team Plan** (`team_plan`, `team_price_text`, `team_price_per_user_mo`): the lowest paid tier above the vendor's free tier (or the cheapest paid tier if there is no free tier). This is what a typical small or mid team would default to.
5. **A price-jump multiplier** (`price_multiplier`): the ratio of `scim_price_per_user_mo / team_price_per_user_mo`, rounded to one decimal. Null where either side is non-numeric (Contact Sales, per-host pricing, MAU-based pricing, etc.).
6. **A direct URL to the pricing page** (`pricing_page_url`) used as evidence for that vendor.
7. **Edge-case notes** (`notes`) explaining flat pricing, per-device pricing, IdP restrictions on SCIM, add-on-on-top-of-add-on patterns, and similar non-uniform shapes.
8. **A last-verified date** (`last_verified`, ISO) for the row.

## Status definitions

Each vendor is assigned one of five status labels:

| Label | Meaning |
|---|---|
| **No Tax** | SCIM included on all plans, or on the team tier, with no separate upcharge. |
| **Gated** | SCIM available only on an Enterprise / Contact Sales tier, or as a paid add-on layered on top of a base plan. |
| **Partial** | Limited or conditional support: IdP-specific (only works with Okta or only with Microsoft Entra), JIT-provisioning only (no full lifecycle), or only via a separate enterprise SKU. |
| **No SCIM** | Not offered at any tier; manual or CSV-based admin only. |
| **Unknown** | Not disclosed publicly. We could not find a clear answer on the pricing page, in published docs, or in vendor support articles. |

We avoid promoting "Unknown" rows into "Gated" rows. If a vendor refuses to publish their answer, "Unknown" is the answer.

## Pricing rules

- Prices are publicly listed prices, US dollars, on annual billing, as of the data timestamp.
- Where a vendor lists multiple currencies, we use the USD price.
- Where a vendor only lists a non-USD price (for example, some EU-only vendors), we keep the original currency and flag it.
- For consumption-priced vendors (Snowflake, Twilio), we record the relevant unit price rather than a flat plan price.
- For add-ons, we record the add-on price separately from the base plan price.

## Update cadence

The dataset was first published in April 2026 and refreshed in June 2026. The next scheduled refresh is Q1 2027. Year-over-year changes will be published in the changelog: which vendors removed the SCIM gate, which added one, which raised the price.

In between scheduled refreshes, individual entries can be corrected via GitHub issue or pull request. See [README.md](README.md).

## Known limitations

- **Custom-quoted enterprise pricing** is opaque by design. Where a vendor says "Contact Sales", we note that fact rather than guess at the price.
- **Geographic variation.** Some vendors offer different SCIM availability by region. We report the US/global default.
- **In-flight changes.** Pricing pages are revised quietly and without notice. The data is accurate as of the timestamp, not perpetually live.
- **Vendor self-reporting.** A vendor's pricing page may understate or overstate what is actually available. Where we have direct customer confirmation, the row is annotated.

## How to suggest a change

- Open an issue at the [GitHub repository](https://github.com/IdenWorks/scim-tax/issues) with the vendor name, the change, and a link to your source.
- Or open a pull request directly against `data.json`.
- All changes are reviewed before merge. We require a public source URL, not a private quote.

## License

The dataset is released under [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/). Re-use freely with attribution to *SCIM Tax Index (Iden)*.
