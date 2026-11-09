# Changelog

## Unreleased — 1.0.4 local release candidate

Not a published tag, release or Registry entry. Coordinated quota/backend
installation passed on 2026-11-05; corrected R11 payment code was installed
and checked on 2026-11-06. R7 activity, separate log controls and administrative
D1 reads were installed and checked on 2026-11-07. R7 legal, retention/copy
and full rights-delivery gates remain open. Approved R2 and R11 deviations
remain explicit; unknown client build and natural renewal are not verified.

- R11: insert missing subscriber identities without resetting existing fields;
  persist creation intents before PayPal requests and recover local registration
  without duplicating an external subscription after a known successful POST.
- R11: recover interrupted webhook processing under a shared OS lock; distinguish
  completed, processing and failed records, retaining historical deduplication.
- R11: require independently completed payment evidence for a supported current
  paid cycle; ACTIVE and the next billing date alone cannot activate access.
  No new grace policy or webhook cleanup was introduced.

- Align the component's initialize version and server.json to 1.0.4.
- Reuse verified Qysley/Glama account setup and token-lifecycle documentation.
- Retain public response allowlists, neutral error codes/references, and
  corrected tool annotations from R2–R6.
- Minimize redundant input echoes and selected identifiers in source text;
  this is not general anonymization or final GDPR approval.
- Document ten free uses across all six search/read tools and test empty,
  failed and partial attempts under the candidate admission policy.
- Require a positive quota debit before upstream work. A separate private
  backend correction fixes lost counter increments; coordinated deployment and
  native last-credit concurrency verification passed on 2026-11-05.
- Require explicit PayPal environment and plan configuration. Verify current
  subscription status/plan/binding and retain period boundaries; distinguish
  verified, pending and failed return pages. Sandbox payment, cancel and webhook cases are verified for the corrected code;
  natural renewal remains an approved deviation. No Live purchase is required.
- Add proprietary LICENSE, SECURITY.md, coverage limits and stricter ignore
  rules. Privacy and subscription terms remain explicitly marked drafts.
- Reuse pinned/hash-verified Python 3.14.4 dependencies and MCP SDK 2.3.0 CI.
  The current runtime/test CI passed at a7d16ba8473f022d00af74b2516ce72b220ea3ff
  (290 Python tests; separately, 52 private Worker/SQLite cases passed).
  Post-deployment authenticated SDK metadata and native quota checks passed.
  Later documentation-only status corrections are recorded separately from that CI snapshot.

## Repository history

These entries describe the history recorded in the 30 October review, not
independently verified deployment or Registry publication dates.

### 2026-10-28
- Registry manifest updated to 1.0.3 with Qysley website information.
- README updated with Qysley website and contact information.
- Registry version updated to 1.0.2 earlier that day.

### 2026-10-27
- Public endpoint configuration migrated to Qysley.

### 2026-10-26
- Licensing adapter migrated to a Cloudflare D1 API backend.
- Subscription expiry handling adjusted.
- Public access documentation updated.

### 2026-10-25
- Initial repository publication and README added.
- MCP Registry manifest added and updated to 1.0.1.
