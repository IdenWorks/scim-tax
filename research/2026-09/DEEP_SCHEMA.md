# SCIM Tax Index, per-vendor deep research file (September 2026 refresh)

One file per vendor at `research/2026-09/vendors/{slug}.json`. It holds two things:

1. `row`: the v3 summary row exactly as defined in `SCHEMA.md`. `extract_rows.py` collects these into `results/` for `merge.py`, so `data.json` stays the lean source the site is built from.
2. Everything else: the deep record of what the vendor's SCIM and user-management API actually do, with a citation behind every fact. How this is shown on scimtax.org is not decided yet, so collect everything and present nothing.

## Sources

- **Allowed:** the vendor's own domains (marketing site, pricing page, docs, developer portal, API reference, help centre, trust or status page, changelog) and, for `idp_apps` only, the IdP's own catalogue page (Okta Integration Network, Microsoft Entra app gallery or Learn tutorial, Google Workspace Marketplace or admin help, OneLogin, JumpCloud).
- **Not allowed as evidence:** third-party SCIM directories, sso.tax, notsosso, G2, Capterra, Vendr, Reddit, blogs, AI summaries, or any reseller. They can point you to a page; the citation must be the vendor's page.
- Vendor names in the candidate list came from third-party lists and may be title-cased wrongly (`Aws`, `Ukg`). Use the vendor's own spelling.

## Citation rules

- `citations[]` entries: `{id, url, title, quote, accessed}`. `id` is `c1`, `c2`, … `quote` is verbatim text from that page, 300 characters or fewer, enough for a reader to find it with Ctrl-F. `accessed` is the ISO date you loaded the page.
- Every non-null fact in `plans`, `scim`, `user_api`, `idp_apps` and `fallbacks` carries a `cite` array of citation ids. An object whose values are all null needs no citation. Any object may carry a `notes` string. A fact you cannot cite is `null`, and the gap goes in `open_questions`.
- `row.evidence` is one of those quotes (or a close paraphrase of one). `row.pricing_page_url` and `row.docs_url` must also appear in `citations`.
- Never guess. `null` means "not documented publicly". `false` means "the vendor's docs say no". Never promote `unknown` to `gated` on a guess.
- Endpoints are listed only when you saw them in the vendor's API reference. Copy method and path as documented.

## Shape

```jsonc
{
  "slug": "1password",
  "vendor": "1Password",
  "vendor_url": "https://1password.com",
  "researched_at": "2026-10-05",
  "row": { /* v3 summary row, see SCHEMA.md */ },

  "plans": [                       // the vendor's public tier table, cheapest first
    { "name": "Teams Starter Pack", "price_text": "$19.95/mo for up to 10 users",
      "price_per_user_mo": null, "billing": "annual|monthly|unknown",
      "sso": true|false|null, "scim": true|false|null, "user_api": true|false|null,
      "audit_log_api": true|false|null, "cite": ["c1"] }
  ],

  "scim": {
    "available": true|false|null,
    "cite": ["c3"],                        // backs available / plan / addon / sso_required / version / base_url
    "plan": "Business",                    // lowest plan with SCIM, or null
    "addon_price_text": null,              // when SCIM is a paid add-on
    "sso_required": true|false|null,
    "version": "2.0|1.1|null",
    "base_url": "https://{tenant}.example.com/scim/v2",   // pattern as documented
    "auth": { "method": "bearer|oauth2|basic|other|null", "token_source": "admin console path or null",
              "token_expiry": "never|90 days|…|null", "cite": [] },
    "endpoints": { "Users": true|false|null, "Groups": …, "ServiceProviderConfig": …, "Schemas": …,
                   "ResourceTypes": …, "Bulk": …, "Me": …, "cite": [] },
    "operations": { "create": …, "read": …, "update_put": …, "update_patch": …, "deactivate": …,
                    "reactivate": …, "delete": …, "group_push": …, "group_membership": …, "cite": [] },
    "deprovision": { "action": "deactivate|suspend|delete|remove_from_org|other|null",
                     "frees_seat": true|false|null, "revokes_sessions": true|false|null,
                     "data_retained": "text or null", "cite": [] },
    "filtering": { "supported": true|false|null, "attributes": ["userName", "externalId"], "cite": [] },
    "pagination": { "supported": true|false|null, "max_page_size": null, "cite": [] },
    "attributes": {
      "core": ["userName", "name.givenName", "emails[type eq \"work\"].value", "active"],
      "enterprise": ["department", "manager"],          // urn:ietf:params:scim:schemas:extension:enterprise:2.0:User
      "custom": { "supported": true|false|null, "how": "text or null" },
      "group": ["displayName", "members"],
      "cite": []
    },
    "roles": { "supported": true|false|null, "how": "e.g. roles attribute, group-to-role mapping", "cite": [] },
    "rate_limits": { "text": null, "cite": [] },
    "limitations": [ { "text": "Groups push not supported with Entra", "cite": ["c7"] } ]
  },

  "user_api": {                            // non-SCIM admin / user-management API
    "available": true|false|"partner_only"|null,
    "cite": ["c9"],                        // backs available / plan / api_tax / style / base_url
    "plan": "lowest plan with API access or null",
    "api_tax": true|false|null,            // API locked above the team plan, or sold separately
    "style": "REST|GraphQL|SOAP|other|null",
    "base_url": null,
    "docs_url": null,
    "auth": { "methods": ["api_key", "oauth2"], "scopes": ["users:read", "users:write"], "cite": [] },
    "capabilities": { "list_users": …, "get_user": …, "create_user": …, "invite_user": …, "update_user": …,
                      "deactivate_user": …, "delete_user": …, "reactivate_user": …, "manage_groups": …,
                      "assign_roles": …, "assign_licenses": …, "cite": [] },
    "endpoints": [ { "method": "GET", "path": "/v1/users", "purpose": "List users", "cite": ["c9"] } ],
    "webhooks_user_events": { "supported": true|false|null, "events": [], "cite": [] },
    "audit_log_api": { "supported": true|false|"addon"|null, "plan": null, "cite": [] },
    "rate_limits": { "text": null, "cite": [] },
    "limitations": []
  },

  "idp_apps": {                            // the vendor's app in each IdP catalogue
    "okta":     { "listed": true|false|null, "sso": …, "provisioning": …,
                  "kind": "scim|api_connector|directory_sync|swa|sso_only|null",   // how that app provisions
                  "built_by": "vendor|idp|third_party|null",                      // e.g. Aquera = third_party
                  "url": null, "cite": [] },
    "entra":    { … }, "google": { … }, "onelogin": { … }, "jumpcloud": { … }
  },

  "fallbacks": {
    "jit": true|false|null,                // accounts created on first SSO sign-in
    "jit_protocol": "saml|oidc|both|null",
    "csv_import": true|false|null,
    "other_sync": "e.g. Google Workspace directory sync, HRIS sync, or null",
    "docs_public": true|false,             // false when SCIM / API docs sit behind a login
    "cite": []
  },

  "citations": [ { "id": "c1", "url": "https://…", "title": "…", "quote": "…", "accessed": "2026-10-05",
                   "page_url": null } ],   // when `url` is a .md export or JSON API, the page a reader would open
  "conflicts": [ { "text": "Pricing cards say $10, the FAQ on the same page says $10.25", "cite": ["c2", "c5"] } ],
  "searched": [ "https://vendor.com/pricing", "https://docs.vendor.com/sitemap.xml", "help-centre search: scim" ],
  "open_questions": [ "Docs do not say whether deprovisioning frees the seat." ]
}
```

## How the summary row is derived

- `row.status` follows `METHODOLOGY.md`. `row.idp` maps from `idp_apps` and `scim`: `native` when the IdP catalogue app provisions, `via_generic` when only a generic SCIM 2.0 endpoint is documented, `sso_only` when the app signs in but does not provision, `none` when not listed. `generic` is `true` when `scim.endpoints.Users` is true.
- `row.scim_ops` copies `scim.operations` (`create`, `update` = PUT or PATCH, `deactivate`, `delete`, `groups` = `group_push`).
- `row.confidence`: `high` when the pricing page states the SCIM plan, `medium` when only docs or help centre do, `low` otherwise.
- Existing rows keep `first_added` and get `status_prev` from the June 2026 release. New rows get `first_added: "2026-09"` and `status_prev: null`.

## Rules added after the 20-vendor pilot (these override anything above)

**Status**
1. **Price gate first.** `free` when SCIM is on the team tier with no upcharge, `gated` when it needs Enterprise, Contact Sales or a paid add-on. Only then consider `partial`.
1a. **`free` needs positive evidence**: a vendor page says SCIM is on all plans or on the team plan, or the product has a single paid plan. A documented SCIM feature with no plan named, on a product with several tiers, is `unknown` (or `gated` under rule 6a if the product is quote-only). Absence of a stated gate is not evidence of no gate.
2. **`partial`** is for SCIM that works with exactly one IdP, or SCIM that can create users but not deactivate/deprovision them. A vendor with **no SCIM endpoint whose only automation is JIT on SSO sign-in is `none`** (record `fallbacks.jit: true`); the user may reclassify JIT-only at merge. SCIM that works with two or more IdPs is not partial; record the limits in `idp` and `idp_apps`.
3. **Provisioning without SCIM** (an IdP creates/removes users through the vendor's own REST API, no SCIM endpoint: Zendesk, Coupa) is `none`, with `row.api_provisioning: true` and `idp.<x>: "api_connector"`.
3a. **Outbound-only SCIM** (HR systems that act as the source and only let an IdP read users: BambooHR, Remote, Deel) does not count as SCIM into the vendor. Status follows how users get into the vendor itself (usually `none`); record the outbound feed in `fallbacks.other_sync`, set `scim.available: false` and `idp.generic: false`.
3b. **Score every vendor as a provisioning target**: can a customer's IdP create, update and deactivate users *in this product* over SCIM? Vendors that are themselves IdPs or HR sources (Okta, Rippling, JumpCloud, Google Workspace, Microsoft 365, OneLogin) are scored the same way. Their outbound SCIM (pushing users to other apps) goes in `notes` and `fallbacks.other_sync`, never in `status`.
4. **Third-party connectors** (Aquera and similar) never change the vendor's status. Record them with `built_by: "third_party"` and `idp.<x>: "third_party"`.
5. **`none` by absence** is allowed at `confidence: "medium"` when the vendor never says "no" but you searched the pricing page, the docs index or sitemap, the API reference and the help centre, and listed each in `searched`. Anything less stays `unknown`.
6. **Plan gate known only from an IdP page** (e.g. Microsoft's Entra tutorial): allowed, `confidence: "low"`, and `notes` says the gate comes from the IdP's page.
6a. **Quote-only vendors** (no public plans at all, everything via Contact Sales) that document SCIM are `gated`, `confidence: "low"`, and `notes` begins with `Quote-only:`. SCIM can only be bought through sales, which matches the methodology's "Contact Sales tier". "Documents SCIM" means the vendor's own pages describe it. When the only SCIM evidence is an IdP catalogue listing (Okta OIN tick marks, an Entra tutorial), the status is `unknown`, not gated. If SCIM is not documented, the normal none/unknown rules apply.
7. **Rebranded or multi-product vendors**: name the row after what is sold today, e.g. `Hotjar (Contentsquare)`, keeping the slug. For suites (UKG Pro, Ready, WFM) research the main admin product and note the others; do not split rows.

**Definitions**
- `generic`: the vendor documents a SCIM 2.0 endpoint that any SCIM client can call with a token.
- `sso_plan`: SAML or OIDC with the customer's own IdP. Social sign-in does not count.
- Okta password-vaulting (SWA) apps are `kind: "swa"`, `sso: false`, and `idp.okta: "none"`.
- Vendor-run non-SCIM directory sync (1Password or Tailscale with Google Workspace) is `kind: "directory_sync"`, `idp.<x>: "directory_sync"`.
- `team_plan`: the cheapest paid tier that lets more than one user work together. Skip single-user plans (Solo, Personal) and tiers that can't add users.
- Flat or usage-priced plans: per-user fields stay null and `notes` explains the pricing.
- Prices: annual billing when the page offers it; otherwise record the monthly price and say so in `notes`.
- When two vendor pages disagree, cite both in `conflicts` and use the more specific page (pricing page for prices, docs for behaviour).
- Endpoints: record the HTTP method as used in requests (`DELETE`, not `DEL`). SOAP calls use method `SOAP`.
- Machine-readable sources (`.md` exports, OpenAPI JSON, help-centre JSON APIs on the vendor's domain, the vendor's Stoplight/ReadMe project) are fine; set `page_url` to the human page.
