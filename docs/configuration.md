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
plan and user binding, and stores the returned status. `ACTIVE` and a future
`next_billing_time` are not sufficient payment evidence. The local R11 revision
also requires a full SEK payment in the current fixed-price calendar cycle,
confirmed as `COMPLETED` by the subscription-scoped transaction API, with a
matching last-payment time/amount, no outstanding balance and no consecutive
payment failures. The fetched plan must have one regular monthly/yearly cycle,
the configured price and no setup fee/trial. Unsupported or ambiguous data
does not grant or extend access.

The initial provider billing clock need not equal the subscription start clock:
the expected calendar date is checked, and the exact provider end is retained.
Renewals must join the preceding independently proved boundary. The transactions
API may omit optional page counters; explicit additional pages or next links
still block verification, and exactly one completed matching payment is required.
The first monthly Sandbox payment has verified these response shapes and
activation. Yearly payment and actual renewal/failure evidence still remain;
this is not a guarantee about all PayPal schedules.
For renewals, the immediately preceding paid boundary must already be proved
locally. A transaction date alone cannot distinguish a current-cycle payment
from collection of an older debt. Gaps, legacy subscriptions without proof,
aggregated debt payments and nonmatching schedules require reconciliation and
do not automatically grant a new period. An explicit refunded/reversed payment
response invalidates cached evidence. Automatic refund processing is not added.
A pending or
failed verification never reports success. Cancellation preserves a previously
verified end date from the local payment-proof store if PayPal omits it; raw
historical D1 expiry values are not imported as payment proof. A previously
proved, unexpired paid period is not extended because a later payment fails.
No new grace period is implemented.

The private backend must separately enforce status/end-date checks, including
expiry of `CANCEL_REQUESTED`. No global cached `paid` flag is sufficient.
Missing period information fails closed and may require manual reconciliation;
match existing Sandbox evidence to the candidate before adding only missing or
changed checks. No real-money/Live purchase is a release requirement.
`next_billing_time` is a
provider billing boundary, not independently verified proof of settled payment.
Trials, finite plans and failed-payment behavior are not certified by mocks.

Signature verification remains. Webhook processing is serialized with a local
OS lock shared by creation, callback, cancellation and webhook handlers. A
crashed process releases the lock; unfinished events are recovered on retry.
Only completed (including historical `processed`) events return
`already_processed`. A busy handler returns retryable HTTP 503, and failed
events remain recorded for retry. This requires a single shared local database
and lock file, not multiple independent hosts or network filesystems.
Do not purge
deduplication rows: replay after future deletion remains an unresolved R7 issue.
The rejected `create_time` patch is not included.

Before creating a subscription, `ensure_user` must be supported by the matching
private backend. Its insert-only operation preserves quota, API-key hash,
paid flag and all existing fields. A durable local creation intent precedes
the external POST, with a stable PayPal-Request-Id. A stored provider ID allows
backend registration retry without another POST. An uncertain POST without a
stored provider ID is blocked for manual provider reconciliation; it is never
automatically repeated after the provider's 72-hour key-retention window.
Request history and payment boundaries are private SQLite data and must be
included in backup/rights/retention assessments. No cleanup is introduced.
The R11 revision is local only: coordinated backend/component installation,
existing paid-period reconciliation, backup and safe rollback remain gates.

Reference: [PayPal subscriptions API](https://developer.paypal.com/docs/api/subscriptions/v1/).
The configured Live plans were subsequently checked read-only for active status,
price, currency, period and zero setup fee on 2026-11-05. No plan or payment was
changed. Sandbox subscription outcomes remain unverified where evidence is missing.
