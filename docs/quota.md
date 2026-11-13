#1.0.5-kandidatens ändrade omfattning

Denna arbetskopia är inte installerad. Bred sökning beskrivs i README.md och
105-processing-and-policy.md; källutdrag är inte godkänd lästext och PDF ingår
inte. Databasens robots-disallow respekteras, aktuell sökbar översikt är inte
helaARN-databasen. Verktygsargument, OAuth, betalning och kvotregler är bevarade.
Följande bevarade1.0.4-underlag gäller där det inte motsägs av denna uttryckliga
deltaavgränsning; se INSTALL-105.md för framtida införande.

---

# Usage and subscriptions — 1.0.4

Ten free admitted attempts are shared by the six data tools. Combined search/read
counts once. Empty results, technical failures and repeated calls can consume a
use after admission. Authentication failures, rejected admission, tools/list and
the two subscription tools do not consume a data use. A valid paid subscription
removes the free cap; the usage counter can still increase.

Admission occurs before reading the reviewed local library. There is no live ARN
request or PDF fallback. A backend timeout after a committed debit can still
leave a charge; there is no exactly-once retry/refund promise.

The reviewed quota backend and R11 payment verification are already installed.
Prices remain 59 SEK/month and 590 SEK/year. ACTIVE status alone is not payment
proof. New paid contracts also wait for confirmation SMTP acceptance; uncertain
send outcomes require operator reconciliation. This does not change R11 rules.
