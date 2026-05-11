# The SCIM Tax Index

An open dataset of SaaS vendor SCIM (user provisioning) availability and pricing.

**Live site:** https://scimtax.org/
**License:** [CC-BY 4.0](LICENSE)
**Last updated:** April 2026
**Next update:** Q1 2027

## What this is

SCIM (System for Cross-domain Identity Management) is the protocol IT teams use to automate user provisioning and deprovisioning across the SaaS stack. Most SaaS vendors support it. Most lock it behind an Enterprise plan or a paid add-on. This dataset surveys ~300 of the most-deployed SaaS apps to document who gates SCIM and what it costs.

The result is sometimes called the "SCIM tax": the systematic premium paid across a SaaS portfolio for the right to manage your own users.

## Files

| File | Purpose |
|---|---|
| `index.html` | The published site. Self-contained, no build step required. |
| `data.csv` | Full dataset as CSV. CC-BY 4.0. |
| `data.json` | Full dataset as JSON. CC-BY 4.0. |
| `METHODOLOGY.md` | How vendors were selected and how each row was recorded. |
| `LICENSE` | CC-BY 4.0 terms. |
| `CHANGELOG.md` | Version-to-version changes. |
| `build.js` | Extracts `data.csv` and `data.json` from `index.html`. Run after editing the vendor list. |
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

Cite as:

```
SCIM Tax Index (Iden, 2026). https://scimtax.org/
```

## Contributing

Found a vendor we missed? Pricing changed? Status wrong?

- Open an issue: https://github.com/idenhq/scim-tax/issues
- Or open a pull request modifying `index.html` (the `const V = [...]` array) and run `node build.js` to regenerate `data.csv` and `data.json`.

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

To regenerate the raw data files after editing the vendor list:

```bash
node build.js
```
