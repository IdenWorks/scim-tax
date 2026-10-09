# Methodology

The SCIM Tax Index is an open survey of how SaaS vendors price automated user provisioning. This document explains how vendors are selected, how each row is recorded, and how status labels are assigned.

## Vendor selection

Vendor names come from public SaaS directories, identity-provider app catalogues and Iden's connector catalogue, weighted toward the apps mid-market and enterprise teams buy. The first release (April 2026) started from the community SSO tax lists ([sso.tax](https://sso.tax) and [notsosso.com](https://notsosso.com)) and SaaS usage reports. These lists only decide which vendors are included; nothing about a vendor is taken from them.

Coverage spans horizontal SaaS (collaboration, productivity, dev tools, security, finance, HR, marketing) and the largest vertical apps (healthcare, education, real estate, legal). The dataset is not exhaustive of every SaaS company. It is representative of the vendors a typical mid-market IT stack actually buys.

## Evidence

Every fact about a vendor comes from the vendor's own pages: its pricing page, documentation, help centre and API reference. Whether an app is listed in the Okta or Microsoft Entra catalogue, and what that listing does, is checked on Okta's and Microsoft's own pages.

Third-party sources are never used as evidence: community lists, review and comparison sites, resellers, blogs and AI summaries can point to a vendor page, but the citation is always the vendor's page.

Each vendor has a research file in [research/2026-09/vendors/](research/2026-09/vendors/) that links the page and quotes the sentence behind every fact. The format is described in [DEEP_SCHEMA.md](research/2026-09/DEEP_SCHEMA.md). As of October 2026, all 849 rows were re-checked against vendor pages, and the quoted sentences are re-found on the live pages by `check_quotes.py`.

## What we record per vendor

The dataset moved to schema v3 in September 2026. The full field list with types is in [research/2026-09/SCHEMA.md](research/2026-09/SCHEMA.md). In plain terms, each row records:

1. **Whether SCIM is offered**, or an equivalent automated provisioning protocol (some vendors use proprietary directory sync, JIT, or IdP-specific bridges; we record what is offered, not what we wish was offered).
2. **The lowest plan that includes SCIM** (`scim_plan`), as listed publicly. If SCIM is sold as an add-on, we record the add-on name and its price separately (`scim_addon_price_text`).
3. **The price of that SCIM-bearing plan** (`scim_price_text` for the human-readable string, `scim_price_per_user_mo` for the normalized per-user-per-month numeric where possible). In US dollars, annual billing, publicly listed where available. If gated behind Contact Sales, we record "Contact Sales". Third-party price estimates are not recorded.
4. **The standard plan** (`team_plan`, `team_price_text`, `team_price_per_user_mo`; the "Standard Plan" column on the site): the cheapest paid plan that more than one person can use. This is what a typical small or mid team would default to.
5. **The SSO Plan** (`sso_plan`, `sso_price_per_user_mo`): the lowest plan that includes SAML or OIDC single sign-on. Many vendors put SSO one tier below SCIM, and that gap is where most of the SCIM tax sits. New in v3.
6. **A price-jump multiplier** (`price_multiplier`): the ratio of `scim_price_per_user_mo / team_price_per_user_mo`, rounded to one decimal. Null where either side is non-numeric (Contact Sales, per-host pricing, MAU-based pricing, etc.).
7. **Seat minimums and prerequisites** (`min_seats`, `sso_required_for_scim`): the gates behind the gate, when the vendor publishes them. New in v3.
8. **What the SCIM endpoint does** (`scim_ops`: create, update, deactivate, delete, groups) and **which identity providers are supported** (`idp`: Okta, Entra ID, Google Workspace, OneLogin, JumpCloud, and whether a generic SCIM 2.0 endpoint exists). Both come from the vendor's own documentation only; where the docs are silent the value is null, never assumed. New in v3.
9. **Evidence**: a direct URL to the pricing page (`pricing_page_url`), a URL to the SCIM documentation where one exists (`docs_url`), and one sentence quoted or closely paraphrased from those pages (`evidence`) that supports the status. New in v3.
10. **A category** from a fixed list of 21 ([research/2026-09/CATEGORIES.md](research/2026-09/CATEGORIES.md)), so category-level statistics are comparable. New in v3.
11. **Edge-case notes** (`notes`) explaining flat pricing, per-device pricing, IdP restrictions on SCIM, add-on-on-top-of-add-on patterns, and similar non-uniform shapes.
12. **Confidence and dates** (`confidence`, `last_verified`, `first_added`, `status_prev`): how strong the public evidence is, when the row was last checked, when it entered the dataset, and what its status was in the previous release so year-over-year changes can be computed. New in v3.

## Status definitions

Each vendor is assigned one of 5 status labels:

| Label | Meaning |
|---|---|
| **No Tax** | SCIM on the standard plan at no extra cost. Needs a vendor page that names the plan. |
| **Gated** | SCIM only on a higher plan, behind sales, or as a paid add-on. Vendors that publish no prices but document SCIM are Gated at low confidence, with notes starting "Quote-only". |
| **Partial** | Limited SCIM: works with one identity provider only, or cannot deactivate users. |
| **No SCIM** | Not offered on any plan. Creating accounts at sign-in (JIT), provisioning through the vendor's own non-SCIM API, and outbound-only SCIM do not count as SCIM. |
| **Unknown** | Could not be confirmed from the vendor's public pages. |

We avoid promoting "Unknown" rows into "Gated" rows. If a vendor refuses to publish their answer, "Unknown" is the answer.

## Pricing rules

- Prices are publicly listed prices, US dollars, on annual billing, as of the data timestamp.
- Where a vendor lists multiple currencies, we use the USD price.
- Where a vendor only lists a non-USD price (for example, some EU-only vendors), we keep the original currency and flag it.
- For consumption-priced vendors (Snowflake, Twilio), we record the relevant unit price rather than a flat plan price.
- For add-ons, we record the add-on price separately from the base plan price.

## Update cadence

The dataset was first published in April 2026, refreshed in June 2026, and expanded to 849 vendors and re-verified in October 2026 (the 2026-09 refresh). The next scheduled refresh is Q1 2027. Year-over-year changes will be published in the changelog: which vendors removed the SCIM gate, which added one, which raised the price.

In between scheduled refreshes, individual entries can be corrected via GitHub issue or pull request. See [README.md](README.md).

## Known limitations

- **Custom-quoted enterprise pricing** is opaque by design. Where a vendor says "Contact Sales", we note that fact rather than guess at the price.
- **Geographic variation.** Some vendors offer different SCIM availability by region. We report the US/global default.
- **In-flight changes.** Pricing pages are revised quietly and without notice. The data is accurate as of the timestamp, not perpetually live.
- **Vendor self-reporting.** A vendor's pricing page may understate or overstate what is actually available. We report what the vendor publishes.

## How to suggest a change

- Open an issue at the [GitHub repository](https://github.com/IdenWorks/scim-tax/issues) with the vendor name, the change, and a link to your source.
- Or open a pull request against `data.json` (the source of truth) and run `node build.js` to regenerate the site, `data.csv` and the badges.
- All changes are reviewed before merge. We require a public source URL, not a private quote.

## License

The dataset is released under [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/). Re-use freely with attribution to *SCIM Tax Index (Iden)*.
