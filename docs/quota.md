# Free usage policy — local 1.0.4 candidate

New users receive **10 free uses**, shared by `arn_search`, `arn_get_decision`,
`arn_search_and_read`, `arn_search_company`, `arn_search_company_and_read` and
`arn_similar_cases`. A combined search/read is one use, not one use per decision.
Subscriptions cost 59 SEK/month or 590 SEK/year, with no additional Qysley fees.

The candidate charges **one admitted tool attempt before contacting ARN**.
Empty results, a technical upstream failure and partially unsuccessful reads
all count as one attempt. Repeating a tool call can consume another use.
Client-side/SDK rejection before tool execution and denied authentication do
not enter admission. A denied quota debit returns no ARN data and performs no
upstream search/read. `tools/list` and the two subscription tools do not debit
the search quota. A valid paid subscription permits usage without the free cap;
the usage counter can still increase.

This is a deliberately conservative candidate policy, not a promise to refund
failed searches. A timeout after a backend write can leave a charge even though
the caller receives an error. There is no exactly-once retry/refund protocol.
The adapter requires an actual boolean permission and fails closed on malformed
responses or errors. Every tool checks admission before upstream work.

**Deployment dependency:** the private backend needs its separately reviewed
conditional SQL increment. Local Worker/SQLite concurrency tests do not prove
that change is deployed on D1. Do not advertise the new policy as production
behavior before the coordinated installation is approved and verified.
