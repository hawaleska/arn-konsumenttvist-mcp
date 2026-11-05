# Configuration and private dependencies

This repository contains the MCP component, not a complete self-hosting package.
Authentication and the private license backend are separate operational
dependencies. Their credentials, identifiers and deployment configuration are
not supplied here. No Qysley Auth change is included in this candidate.

See [.env.example](../.env.example) for names only. Set values securely outside
version control. The component reads its existing local `.env` when present;
the example is never a usable credential file.

`PAYPAL_ENV` must be `live` or `sandbox` (case-normalized). Missing or unknown
values stop startup. Both plan IDs must be supplied explicitly and be distinct;
there are no account-specific defaults. Client ID, secret and webhook ID are
also required. Before any future restart, an authorized operator must verify
the selected environment and its matching plans without printing secrets.

An allowed plan is a configured monthly/yearly plan. The candidate fetches the
current subscription from PayPal over the selected API host, validates its ID,
plan and user binding, and stores the returned status. Only `ACTIVE` with a
valid future access-period boundary is eligible for activation. A pending or
failed verification never reports success. Cancellation preserves a previously
verified end date if PayPal omits it; it does not invent a new paid period.

The private backend must separately enforce status/end-date checks, including
expiry of `CANCEL_REQUESTED`. No global cached `paid` flag is sufficient.
Missing period information fails closed and may require manual reconciliation;
match existing Sandbox evidence to the candidate before adding only missing or
changed checks. No real-money/Live purchase is a release requirement.
`next_billing_time` is a
provider billing boundary, not independently verified proof of settled payment.
Trials, finite plans and failed-payment behavior are not certified by mocks.

Existing signature verification and webhook deduplication remain. Do not purge
deduplication rows: replay after future deletion remains an unresolved R7 issue.
The rejected `create_time` patch is not included.

Reference: [PayPal subscriptions API](https://developer.paypal.com/docs/api/subscriptions/v1/).
No PayPal account or API was accessed to prepare this candidate.
