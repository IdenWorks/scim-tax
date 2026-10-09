# The SCIM Tax Index

An open dataset of SaaS vendor SCIM (user provisioning) availability and pricing.

**Live site:** https://scimtax.org/
**License:** [CC-BY 4.0](LICENSE)
**Last updated:** October 2026
**Next update:** Q1 2027

## What this is

SCIM (System for Cross-domain Identity Management) is the protocol IT teams use to automate user provisioning and deprovisioning across the SaaS stack. Most SaaS vendors support it. Most lock it behind an Enterprise plan or a paid add-on. This dataset surveys 850 of the most-deployed SaaS apps to document who gates SCIM and what it costs.

The result is sometimes called the "SCIM tax": the systematic premium paid across a SaaS portfolio for the right to manage your own users.

## Files

| File | Purpose |
|---|---|
| `data.json` | The dataset, schema v3. Source of truth. CC-BY 4.0. |
| `data.csv` | The same dataset flattened to CSV. Generated. CC-BY 4.0. |
| `index.html` | The published site. Generated table, otherwise hand-written. |
| `badge/{slug}.svg` | One embeddable status badge per vendor, plus `badge/index.json`. Generated. |
| `research/2026-09/` | Schema v3 definition, the merge scripts, and one research file per vendor (`vendors/{slug}.json`) with SCIM and user-API depth and a citation for every fact. |
| `METHODOLOGY.md` | How vendors were selected and how each row was recorded. |
| `LICENSE` | CC-BY 4.0 terms. |
| `CHANGELOG.md` | Version-to-version changes. |
| `build.js` | Reads `data.json` and regenerates the table in `index.html`, `data.csv` and `badge/`. Run after editing the dataset. |
| `scim-tax-master.md` | Long-form research notes (raw source). |
| `notsosso-scim-pricing.md` | Source extract: notsosso.com. |
| `ssotax-scim-pricing.md` | Source extract: sso.tax. |
| `missing-vendors-scim-pricing.md` | Vendors not on either source list. |

## Using the data

```bash
# Raw CSV
curl -O https://scimtax.org/data.csv

# Raw JSON
curl -O https://scimtax.org/data.json
```

Embed a vendor badge (one SVG per vendor, rebuilt with every release):

```html
<a href="https://scimtax.org/#v-notion"><img src="https://scimtax.org/badge/notion.svg" alt="Notion: SCIM gated"></a>
```

Cite as:

```
SCIM Tax Index (Iden, 2026). https://scimtax.org/
```

## Contributing

Found a vendor we missed? Pricing changed? Status wrong?

- Open an issue: https://github.com/IdenWorks/scim-tax/issues
- Or open a pull request modifying `data.json` and run `node build.js` to regenerate `index.html`, `data.csv` and `badge/`. Field definitions: `research/2026-09/SCHEMA.md`.

All changes need a public source URL. Private quotes are not accepted.

## Why we made this

We are [Iden](https://idenhq.com). We build identity governance for SaaS stacks that include vendors charging extra for SCIM. We have a commercial interest in seeing the SCIM tax discussed in the open. We do not have a commercial interest in skewing the dataset, and the data is auditable against the linked pricing pages on every row.

If you find a row that misrepresents a vendor, open an issue. We will fix it.

## Building locally

The site is one static HTML file. To preview:

```bash
python3 -m http.server 8000
# open http://localhost:8000
```

To regenerate the site, CSV and badges after editing `data.json`:

```bash
node build.js
```
