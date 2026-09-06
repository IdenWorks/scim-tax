# SCIM Tax Index, dataset schema v3 (September 2026 refresh)

One object per vendor in `data.json` (`vendors[]`). `data.json` is the source of truth from this release onward; `build.js` generates the embedded table in `index.html`, `data.csv` and the `badge/` SVGs from it.

Fields marked (v2) existed before this release. Everything else is new in v3.

| Field | Type | Meaning |
|---|---|---|
| `vendor` (v2) | string | Vendor or product name as the vendor writes it |
| `slug` (v2) | string | URL-safe id, lowercase, hyphens |
| `category` | string | One of the categories in `CATEGORIES.md` |
| `status` (v2) | enum | `free` (No Tax), `gated`, `partial`, `none` (No SCIM), `unknown` |
| `scim_plan` (v2) | string | Lowest plan that includes SCIM, or the add-on name. `—` when none |
| `scim_price_text` (v2) | string | Human-readable price of that plan or add-on. `Contact Sales` when unlisted |
| `scim_price_per_user_mo` (v2) | number or null | Normalised USD per user per month, annual billing. Null when flat, quote-based or usage-priced |
| `team_plan` (v2) | string or null | Lowest paid tier above free (or cheapest paid tier) |
| `team_price_text` (v2) | string | Human-readable price of the team plan |
| `team_price_per_user_mo` (v2) | number or null | Normalised USD per user per month |
| `price_multiplier` (v2) | number or null | `scim_price_per_user_mo / team_price_per_user_mo`, one decimal. Null when either side is null |
| `sso_plan` | string or null | Lowest plan that includes SAML or OIDC SSO. Lets readers see the "SSO yes, SCIM no" middle tier |
| `sso_price_per_user_mo` | number or null | Normalised price of the SSO plan |
| `sso_required_for_scim` | bool or null | Vendor docs say SSO must be configured before SCIM |
| `scim_addon_price_text` | string or null | When SCIM is sold as a separate add-on, its price (for example Vercel Directory Sync $150/mo) |
| `min_seats` | number or null | Seat minimum on the SCIM-bearing plan when the vendor publishes one |
| `scim_ops` | object or null | `{create, update, deactivate, delete, groups}` each `true`, `false` or `null` (undocumented). From vendor docs only |
| `idp` | object | `{okta, entra, google, onelogin, jumpcloud, generic}` each `native`, `via_generic`, `sso_only`, `none` or `null`. `generic` is `true` when the vendor exposes a standard SCIM 2.0 endpoint any IdP can call |
| `pricing_page_url` (v2) | string | Public pricing page used as evidence |
| `docs_url` | string or null | Public SCIM or provisioning documentation used as evidence |
| `evidence` | string | One sentence quoted or closely paraphrased from the source pages that supports `status` and `scim_plan` |
| `notes` (v2) | string | Edge cases: flat pricing, per-device, IdP restrictions, add-on on add-on, regional variation |
| `confidence` | enum | `high` (pricing page states it), `medium` (docs or help centre state it, price inferred), `low` (community or third-party source only) |
| `last_verified` (v2) | string | ISO date the row was checked against the live source |
| `first_added` | string | Release that introduced the row (`2026-04`, `2026-06`, `2026-09`) |
| `status_prev` | enum or null | Status in the previous release, for year-over-year deltas. Null for new rows |

## Status rules (unchanged from METHODOLOGY.md)

- `free`: SCIM on all plans or on the team tier with no separate upcharge.
- `gated`: SCIM only on Enterprise / Contact Sales, or as a paid add-on.
- `partial`: IdP-specific, JIT-only, or missing lifecycle operations.
- `none`: not offered at any tier. Manual, CSV or proprietary sync only.
- `unknown`: not disclosed publicly. Never promote `unknown` to `gated` on a guess.

## Evidence rules

- Every row needs `pricing_page_url`. Rows with `status` in `free|gated|partial` also need `docs_url` when the vendor publishes SCIM docs.
- `evidence` is the line a reader can find on the linked page. No invented numbers.
- Prices: USD, annual billing, as listed. Monthly-only vendors: record the monthly price and say so in `notes`.
- Third-party price disclosures (Vendr, community threads) go in `notes` with the source named, never in the numeric fields.
