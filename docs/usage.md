# Connect ARN Konsumenttvist MCP with Glama

## Connect with Glama MCP Inspector

1. Open [Glama MCP Inspector](https://glama.ai/mcp/inspector).
2. Enter the MCP server URL:
   `https://mcp.qysley.se/arn/mcp`.
3. Select **OAuth 2.0** for authentication and start the connection.
   Use Streamable HTTP if a transport selection is presented.
4. On the Qysley sign-in page at `https://auth.qysley.se`, use your existing
   verified Qysley account and click **Logga in**. If you need an account,
   choose **Skapa konto** and follow the registration steps below first.
5. On the consent page, review the client requesting access and the
   requested ARN access. Click **Godkänn** if you want to proceed.
6. Allow the browser to return to Glama. Glama completes the authorization
   code exchange and uses the resulting token for the MCP connection.
7. Confirm that Glama connects and displays all eight ARN tools.

Glama obtains the required `arn` scope through the service's discovery
metadata. You do not need to copy a bearer token into Glama or set a
custom Authorization header for this OAuth flow.

Self-registration, email verification, subsequent sign-in, consent, return
to Glama and authenticated retrieval of all eight tools were confirmed in
production on **2 November 2026**.
This confirms connection and tool discovery, not execution of the tools.
Glama version/build could not be determined. The owner approved the documented
client name, URL, 2 November 2026 test date and authenticated eight-tool production
connection as replacement evidence; no version number is asserted.
Other MCP clients have not been verified by this check.

## Create and verify a Qysley account

1. Choose **Skapa konto** on the Qysley sign-in page, or open
   [Skapa konto](https://auth.qysley.se/signup) directly.
2. Enter your email address and a password of at least 12 characters.
   Click **Skapa konto**.
3. The page displays a neutral message: if registration is possible,
   a verification email will be sent. This message alone does not confirm
   account creation or email delivery. Check your inbox and spam folder.
4. Open the verification link in the email. Check that the page is on
   `https://auth.qysley.se`, then click **Verifiera e-postadress**.
5. When the page says **E-postadressen är verifierad!**, return to
   [Glama MCP Inspector](https://glama.ai/mcp/inspector) and start a new
   OAuth 2.0 connection to `https://mcp.qysley.se/arn/mcp`.
6. Sign in with your new account, review and approve access, and return to
   Glama. Confirm that the connection displays all eight ARN tools.

Start a new connection after verification rather than resubmitting the
original authorization or consent page.

## Request another verification email

If the email is missing or its verification link has expired:

1. Open [Nytt verifieringsmejl](https://auth.qysley.se/resend-verification),
   also linked as **Begär nytt verifieringsmejl** from the registration page.
2. Enter the email address used for your Qysley account and click
   **Nytt verifieringsmejl**.
3. The page gives a neutral response: if the account needs verification,
   a new verification email will be sent. Check your inbox and spam folder.
4. Follow the verification link and click **Verifiera e-postadress**.
   After successful verification, start the connection from Glama again.

The resend function is installed and its HTTP handler has been checked
with synthetic delivery boundaries. Actual resend email delivery has not
been separately confirmed in production.

## If the connection does not complete

Start a new authorization attempt from Glama rather than resubmitting an old
consent page. Tokens issued before the scope correction may lack ARN access;
complete a new OAuth authorization instead of reusing them.

If you forgot your password, use **Glömt lösenord?** on the Qysley login page.
For account or connection assistance, contact **support@qysley.se**.
Share only the error message and the time of the attempt. Do not send
passwords, tokens, cookies, full callback URLs or verification links.

## Existing API-key clients

The existing bearer API-key authentication path remains supported by the
server. API-key rotation replaces the previous key; the old key is then
rejected when the backend lookup sees the replacement. This behavior was
verified with the unchanged Worker and synthetic data, not a live D1 key.
A separate revoke-without-replacement procedure has not been established.

See [Token lifecycle and revocation](token-lifecycle.md) for token renewal,
revocation, account blocking and the limits of the verification evidence.

