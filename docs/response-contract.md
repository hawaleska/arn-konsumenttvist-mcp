#1.0.5-kandidatens ändrade omfattning

Denna arbetskopia är inte installerad. Bred sökning beskrivs i README.md och
105-processing-and-policy.md; källutdrag är inte godkänd lästext och PDF ingår
inte. Databasens robots-disallow respekteras, aktuell sökbar översikt är inte
helaARN-databasen. Verktygsargument, OAuth, betalning och kvotregler är bevarade.
Följande bevarade1.0.4-underlag gäller där det inte motsägs av denna uttryckliga
deltaavgränsning; se INSTALL-105.md för framtida införande.

---

# Response contracts — summary release 1.0.4

All eight tool names are preserved. In the local 1.0.5 candidate, `arn_search`
adds one backward-compatible optional `cursor` argument; other tool arguments
are unchanged. The six data tools
use one reviewed local library, with no ARN/PDF live fallback. Returned text is
a reviewed summary, not a complete decision. Coverage is limited to approved
records. Unknown company names or outcomes are not invented.

`arn_search` rejects a blank query and returns no more than 20 relevance-sorted
results per response. A `next_cursor` plus `has_more` continues the exact query,
filters and approved-index snapshot; a stale cursor is rejected. The response
states the total matching count and that each page is a separate data call.
Every continuation uses the existing per-call quota rule; no free-use amount,
price or admission rule changes. Pagination preserves access to all matches
over multiple calls, but the per-response cap does not prevent cumulative export.
This is a local candidate delta, not installed or published.

Existing public allowlists, neutral errors and reference IDs remain. Internal
license fields, raw input echoes and private upstream/session fields are not
public response fields. Minimization is not a guarantee of anonymity.

Subscription tools, prices and admission rules are unchanged. See quota.md.
The PayPal return page reports verified, pending, inactive or failed verification;
loading it is not proof of successful payment. The customer information and
withdrawal routes are installed; confirmation acceptance gates new paid access.

The selected runtime file hashes and eight function contracts are checked against
the independently read installed production snapshot in the test fixtures.
