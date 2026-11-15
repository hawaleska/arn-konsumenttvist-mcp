# ARN Konsumenttvist MCP 1.0.5

Version 1.0.5 söker i ett växande, hashgodkänt index med 175 ARN-sammanfattningar:
172 nya godkända poster och de tre poster som bevarats från 1.0.4. Detta är ett
granskat urval, inte hela ARN:s databas; sammanfattningarna är inte fullständiga
beslut. Dataverktygen använder `reviewed_index` utan livehämtning eller PDF-fallback.
Driftsättningen bevarar de åtta MCP-verktygen, OAuth, betalningar och kvotregler.

## Faktisk täckning och källor

Produktionsläget är `ARN_BROAD_SOURCE_MODE=reviewed_index`. Det använder endast
poster som godkänts mot innehållshash och approval-pin och som passerar den
aktuella återkallelsekontrollen. Ogranskade källutdrag, stagingposter och
hashfel lämnas inte ut. Indexläget gör inga ARN-HTTP- eller PDF-anrop och saknar
livefallback. De tre återförda versionerna och åtta särskilda HOLD-posterna ingår
inte bland de 175 sökbara posterna.

`official_html` är ett separat undersökningsläge, inte den rekommenderade
offentliga sökvägen. Det kan hämta och visa HTML-utdrag och har egna rättsliga
och åtkomstvillkor. Det får inte slås på i offentlig drift genom att enbart
aktivera `ARN_BROAD_HTML_ENABLED`.

- Officiellt HTML-sökformulär: https://adokweb.arn.se/referatwebb . Manuell
  provsökning gav äldre referat och fler träffar än biblioteket, men värdens
  robots.txt anger `User-agent:* / Disallow:/`. Kandidaten kontrollerar detta
  före formulärhämtning och använder därför INTE databasen automatiskt i dag.
  Ett rättsligt/avtalsmässigt klarlagt tillåtet automatiseringssätt krävs för
  denna del. Ingen UA-växling eller kringgång används.
- https://www.arn.se/om-arn/vagledande-beslut/ beskriver själv urvalet som de
  senaste vägledande besluten, inte hela databasen. Kandidaten kan söka lokalt
  i dess offentliga HTML-text efter hämtning; råsidan lagras inte på disk.
- En hashbunden källkatalog innehåller 45 individuellt källkontrollerade fall från
  https://www.arn.se/vanligafall/ . Det är pedagogiska fallbeskrivningar, inte
  automatiskt vägledande beslut. De hämtas inte om från nätet för varje sökning.
  Tolv beskrivningar hålls tillbaka efter konservativa innehållsflaggor; referens
  och tillåten rubrikinformation kan fortfarande sökas. Inget juridiskt godkännande
  eller garanterad anonymitet följer av innehållshashen.
- Det hashgodkända biblioteket behåller egen prövning och återkallelse. De tre
  tidigare aktiverade posterna är bevarade i 1.0.5.
- `coverage.sources` anger `ok`, `disallowed_by_robots`, `not_consulted` eller `unavailable`.
  Om en källa fallerar får dess begränsning inte döljas bakom bibliotekets träffar.
  Om inga källor kan verifieras returneras neutralt fel, inte ett påhittat nollresultat.

## Alla åtta verktyg

`arn_search`, `arn_search_company` och kombinationsverktygen söker det godkända
lokala indexet. Företagssökning är textsökning i godkända referat, inte verifierad
partsidentitet eller ett fullständigt företagsregister. `arn_similar_cases`
använder ordöverlapp över samma godkända index; ingen LLM eller extern sökmotor.

`arn_search` avvisar en tom fråga och returnerar
högst 20 relevanssorterade träffar per svar. Följ `next_cursor` i nästa
`arn_search`-anrop för att fortsätta samma fråga och filter genom alla matchande
godkända poster. Sidorna är knutna till samma indexsnapshot; en inaktuell markör
avvisas och sökningen behöver startas om. Varje sida är ett separat dataanrop
och använder befintlig kvotdebitering per anrop. Detta begränsar mängden per
svar, inte kumulativ hämtning över flera anrop.

`arn_get_decision` returnerar enbart en godkänd post i det lokala biblioteket.
Om posten saknas, är väntande, återkallad eller har fel hash returneras ett
neutralt ej tillgänglig-fel; ingen HTML/PDF-fallback sker. Källtyp och länknivå
följer den godkända posten. Datum/kategori förblir okända när de saknas.
PDF/fulltext hör fortsatt till 2.0.

`arn_create_subscription` och `arn_cancel_subscription`, OAuth, PayPal och
befintliga kvot-/betalningsregler är oförändrade: 10 fria användningar, 59/590 SEK.
Ett medgivet dataverktygsanrop debiteras före källarbetet, även vid tomt resultat
eller källfel; varje fortsättningssida är ett nytt anrop och kan använda ett
fritt försök. Kombination/begreppssökning debiteras inte en gång per HTTP-anrop.
Ingen prissättningsutveckling ingår i kandidaten.

## Integritet och säker drift

Indexläget matchar sökfrågan lokalt. Frågor skickas inte till ARN eller extern
söktjänst, och inget rått HTML/PDF-material hämtas. Det går endast att exponera
hashgodkända biblioteksposter och deras aktuella, ej återkallade versioner.

Sökfrågor matchas lokalt mot godkända indexfält. Indexläget hämtar inte rå HTML/PDF
vid sökning och skickar inte sökfrågor till ARN eller en extern söktjänst. Endast
hashgodkända, ej återkallade poster kan lämnas ut. Nya poster kräver separat
granskning och hashbundet godkännande. `official_html` är inte produktionsläget.

Verifieringsunderlag omfattar GitHub Actions för den släppta källrevisionen och
produktionskontroller efter den additiva installationen. Se projektets CI och
införandedokument för revisions-, paket- och kontrolluppgifter.

## Befintlig anslutning och rättigheter

MCP-endpoint: https://mcp.qysley.se/arn/mcp .
OAuth-/klientguiden, proprietär [LICENSE](LICENSE) och [SECURITY](SECURITY.md)
bevaras. Support: arn-support@qysley.se. Rättigheter: arn-privacy@qysley.se.
Nuvarande policy: https://qysley.se/privacy/arn/ och engelsk version på
https://qysley.se/en/privacy/arn/ . Villkor/ånger: https://mcp.qysley.se/arn/consumer/information
och https://mcp.qysley.se/arn/consumer/withdrawal.

## Täckning och avgränsningar

Källinventeringen innehöll 186 unika referenser: 141 från den vägledande
beslutsöversikten (inklusive de tre tidigare godkända posterna) och 45 från
Vanliga fall. Av de 183 nya versionerna godkändes och aktiverades 172; tre
återfördes till granskning och åtta är HOLD. Källinventeringens antal ska inte
förväxlas med antalet sökbara poster. Indexet är inte heltäckande för ARN:s
publicerade material.

Ärendenumrens år i inventeringen sträckte sig 2014–2026. Detta innebär inte
fullständig täckning för dessa år och verifierad täckning för 2000–2013 har inte
fastställts. Ärendeår är inte beslutsdatum. Saknade beslutsdatum och kategorier
anges som okända; datumfilter gissar inte från ärendenumret.

I `reviewed_index` matchas frågan endast mot godkända fält; ingen rå HTML-mottagning
eller dold sökning efter bortfiltrerad text sker. Det separata `official_html`-läget
är inte aktiverat i produktion. Ett eventuellt framtida ändrat källflöde kräver
separat rättslig och teknisk prövning.
