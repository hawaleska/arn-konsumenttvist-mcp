# Local 1.0.4 contract changes

All eight tool names, argument schemas and R5 annotations/descriptions are
preserved. The six read/search tools still return their existing result shapes.
R3's allowlists, safe source/hämtningstid fields and R4's error codes/reference
IDs remain; internal license fields and upstream session URLs are not public
contract fields. `arn_auth.py` is byte-identical to the approved R6 snapshot.

The already locally approved R7 change removes redundant input echoes:
`query`, `company`, `problem`, `search_terms`, `matched_queries` where present
in the former public output. Clients using these explanatory fields must keep
their own request; they must not require the fields to be returned. Selected
email and explicitly labelled identifier strings are masked in client text
paths. Case numbers, amounts and substantive decision reasoning are preserved
by focused regression tests. This is limited minimization, not anonymization.

R8/R9 change when a free use is consumed, not the tool arguments: see
[quota.md](quota.md). A denied debit never reaches ARN. Ordinary upstream errors
remain neutral R4 tool errors; admitted attempts may still cost one use.

R11 changes the HTML callback from unconditional success to verified (200),
pending (202), inactive (409) or failed verification (400), all `no-store`.
Subscription tool names, parameters and approval/cancel output shapes remain.
No promise of successful payment is made merely because a return URL loaded.

The planned 1.0.4 compatibility assessment accepts these bounded corrections;
they still require owner review and installation/client checks. It is not a
claim that untested clients consume the optional fields correctly.
