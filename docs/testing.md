# Reproducible tests — local 1.0.4 candidate

Target: Python **3.14.4**, MCP SDK **2.3.0**. Direct requirements and all four
requirements/lock files are byte-identical to the approved R6 set. Installation:

```sh
python3.14 -m venv .venv
.venv/bin/python -m pip install --require-hashes --only-binary=:all: -r requirements-test.lock
.venv/bin/python -m pip check
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -B -m pytest -q --tb=short -p no:cacheprovider tests
```

Run only in an isolated development copy, never the production directory. The
suite uses synthetic identities/configuration and temporary databases. Startup
is exercised through the real module, SDK and ASGI lifespan; the final Uvicorn
serve step is intercepted so no listening port is opened. External transports
are blocked in that startup test. Other tests use explicit mock boundaries and
in-process ASGI. Real tokens, keys, PayPal credentials and production data are
neither required nor included.

Coverage includes R2 status checks/fail-closed deadlines; R3 public allowlists;
R4 neutral public/logged errors; all eight R5 metadata/input schemas through real
SDK tools/list; R7 limited content minimization; R8 empty/technical/partial-result
policy; R9 positive admission before data and parallel last-credit denial; R10
strict configuration; R11 synthetic plan/status/binding/period/callback cases;
and R15 actual Git ignore behavior in a temporary repository with no commits.

R5's former whole-module AST equality is intentionally narrowed now that R9–R11
change module logic. All eight argument/return contracts and full wire metadata
are still compared; a separate six-tool AST test accepts only the specified
admission-order/message change inside those bodies. Earlier error/filter tests
are retained and input-echo assertions reflect the already approved R7 delta.

The private Worker candidate is outside the public component. Its separate
local tests execute actual Worker handlers/SQL with synthetic SQLite, overlapping
async requests and a blocked network. They are not a real Cloudflare D1 runtime
or deployment test and are not part of this public workflow.

Historical R6: 122 tests passed after isolated clean Linux/hash installation;
GitHub Actions succeeded for commit
`64369506fbbee7f8aab293fcaa79dada023c3dd5` (owner-approved evidence). That approval
is retained. It does not certify unpushed candidate bytes. The new local suite
and exact SHA-256 files are reported in the release review. Current-candidate
Linux and GitHub Actions have not run; no GitHub change was authorized.

No real Sandbox payment, production authenticated tools/list capture, complete
rights operation, actual retention or secure handover is proved by local mocks.
Those release gates remain explicit. The postponed PayPal create_time patch and
paused log-retention solution are not applied or retested here.
