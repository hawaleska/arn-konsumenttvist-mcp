# Token lifecycle and revocation

Documentation reviewed on 3 November 2026. The verified client flow is
[Glama MCP Inspector](https://glama.ai/mcp/inspector) using OAuth 2.0 and
Streamable HTTP. See [the connection guide](usage.md).

## OAuth issuance and renewal

After sign-in and consent, Glama exchanges a one-time authorization code
using PKCE S256. Qysley Auth issues an RS256-signed access JWT for the
resource `https://mcp.qysley.se/arn`, with the `arn` scope. The connection
endpoint is `https://mcp.qysley.se/arn/mcp`.

Access JWTs expire 900 seconds (15 minutes) after issuance. Token issuance
requires an active account with a verified email address. The same check
applies when a refresh token is exchanged.

The refresh flow issues a replacement refresh token and a new access JWT.
Reusing a consumed refresh token revokes its refresh-token family. This
does not by itself revoke every access JWT previously issued from that
family. The production refresh-token lifetime is not specified here;
synthetic test lifetimes are not presented as production configuration.

Glama handles the OAuth token exchange. Do not manually copy tokens into
chat or support requests. When authorization can no longer be renewed,
start a new connection and complete sign-in and consent again.

## Revocation and account blocking

ARN checks the JWT locally, then requires an affirmative response from
`https://auth.qysley.se/access-token-status`. The status endpoint verifies
the JWT independently. It is not a public endpoint for revoking accounts.

- **Individual access-token revocation** invalidates the selected JWT.
  It does not automatically invalidate a refresh token that might obtain
  another access JWT.
- **Account-wide access revocation** invalidates access JWTs issued at or
  before the account cutoff and revokes existing login sessions, refresh
  tokens and outstanding authorization codes. The account is retained;
  its owner can sign in again if the account remains active.
- **Account blocking** denies existing JWT access and new token issuance
  while the account is blocked. Operators combine blocking with account-wide
  revocation to prevent old credentials becoming usable after re-enablement.
- **Successful password reset** also applies account-wide revocation.
  Use **Glömt lösenord?** on the Qysley sign-in page when a password reset
  is appropriate. For other access-revocation assistance, contact
  **arn-support@qysley.se** without sending a token or password.

There is no standalone public logout/revoke page in this implementation.
Closing Glama or removing a saved connection is not evidence that Qysley
has revoked the issued credentials.

There is no positive status cache. A revocation takes effect on the next
status check that observes the committed change. Requests already accepted
before that change are not cancelled retroactively. Tokens issued in the
same second as the cutoff are denied; immediate reauthorization may need
to be restarted after that second.

If the status check times out, cannot connect, or returns an invalid response,
ARN denies access. The status request has a three-second total deadline.
The present limit is 120 status requests per peer IP per minute and 1200
globally per minute. ARN users on the same outbound path share the IP limit.
Rate limiting also denies access rather than bypassing revocation checks.

## Existing bearer API keys

Existing API keys are verified through the license backend. Its existing
key-creation operation replaces the user's stored key hash. Rotation therefore
invalidates the old key when the next backend lookup observes that replacement.
Neither the Worker nor the API-key adapter contains an application-level
positive lookup cache in the reviewed source.

Rotation is an authorized operator operation; no new self-service key portal
is provided by this release work. The replacement must be delivered through
an agreed confidential channel and configured in the client's existing bearer
setting. Never publish either key or send it to support in chat/email.
A distinct procedure that revokes a key without issuing a replacement has
not been established. Actual deployed D1 propagation time is not measured.
Key rotation is separate from cancelling or changing a paid subscription.

## Verification evidence and limits

- Self-registration, email verification, sign-in, consent and authenticated
  Glama connection displaying all eight tools were verified in production
  on 2 November 2026. A valid connection also succeeded after installation
  of the JWT revocation implementation. Tool discovery does not verify tool
  execution, quota behavior or payments.
- The 49 approved isolated Ubuntu tests used Python 3.14.4 and the real MCP
  SDK 2.3.0. A separately signed synthetic JWT was accepted, individually
  revoked, and then denied with HTTP 401 in the same MCP session. Synthetic
  keys and SQLite were used. HTTP transport was ASGI-based, not public TLS
  through Cloudflare. Installed-file hashes matched the tested candidate.
- That functional JWT-revocation evidence was accepted by the owner on
  3 November 2026. Denial of the original signed Glama JWT could not be
  attributed conclusively from production logs and is not claimed here.
- Refresh rotation/replay and unchanged Worker API-key rotation were tested
  with synthetic data. No production API key was rotated for these tests.
- Glama's version/build for the successful connection is unknown. The
  evidence identifies the client by name, URL, date and confirmed result.
  Browser and MCP-SDK versions are not substituted for Glama's build.
- The remaining uncertainty about Cloudflare's internal token/header logging
  was explicitly accepted for installation; absence of such logging is not
  claimed as independently verified.

No other MCP client is claimed as verified by this evidence.

## Resource validation in the existing ARN verifier

The SDK setting `validate_token_resource=False` does not disable the ARN
verifier's JWT audience validation. That unchanged verifier requires RS256,
the Qysley issuer and audience `https://mcp.qysley.se/arn`, the required temporal
claims and `arn` scope, then an affirmative token-status response. A JWT-shaped
value failing JWT verification is not retried as an API key. Existing API keys
are resolved by the server-controlled license backend.

This documents where the resource/permission checks reside in the approved
implementation; it does not claim a new client test or change SDK policy.
The external endpoint remains `https://mcp.qysley.se/arn/mcp`. The resource and
connection URL have distinct purposes and must not be interchanged.
