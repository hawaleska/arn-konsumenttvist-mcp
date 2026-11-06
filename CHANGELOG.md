# Changelog

## Unreleased — 1.0.4 local release candidate

Not a published tag, release or Registry entry. Coordinated operator deployment
completed on 2026-11-05; remaining privacy and Sandbox gates prevent release approval.
The subsequent R11 review corrections below are local only and are not covered
by that production installation or the earlier 204-test CI snapshot.

- R11: insert missing subscriber identities without resetting existing fields;
  persist creation intents before PayPal requests and recover local registration
  without duplicating an external subscription after a known successful POST.
- R11: recover interrupted webhook processing under a shared OS lock; distinguish
  completed, processing and failed records, retaining historical deduplication.
- R11: require independently completed payment evidence for a supported current
  paid cycle; ACTIVE and the next billing date alone cannot activate access.
  No new grace policy, webhook cleanup or production installation is included.

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
  verified, pending and failed return pages. Historical Sandbox evidence must
   be matched to the candidate; reuse approved cases. No Live purchase is required.
- Add proprietary LICENSE, SECURITY.md, coverage limits and stricter ignore
  rules. Privacy and subscription terms remain explicitly marked drafts.
- Reuse pinned/hash-verified Python 3.14.4 dependencies and MCP SDK 2.3.0 CI.
  The technical CI snapshot passed at fb7b0b83965e9dae9daf4b623d4552946f2bd385.
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
