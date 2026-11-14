# ARN Konsumenttvist MCP 1.0.5 — lokal kandidat

1.0.5-kandidat för växande sökning i ett lokalt, individuellt godkänt ARN-index.
Biblioteket kan utökas utan kodändring när nya poster har godkänts. Det är inte
hela ARN:s databas och sammanfattningarna är inte hela besluten.
Publicerad 1.0.4 och dess tagg är oförändrade. Ingen 1.0.5-installation/publicering
är godkänd. Agensi-/prissättningsarbete är pausat; befintliga betalningar bevaras.

## Faktisk täckning och källor

Standardläget är `ARN_BROAD_SOURCE_MODE=reviewed_index`. Det använder endast
poster som godkänts mot innehållshash och approval-pin och som passerar den
aktuella återkallelsekontrollen. Ogranskade källutdrag, stagingposter och
hashfel lämnas inte ut. Indexläget gör inga HTTP-, databassökningar eller
PDF-anrop och saknar livefallback. Den lokala 175-posterbatchen och åtta
särskilda HOLD-poster är fortfarande förslag, inte godkända indexposter.

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
- Det befintliga hashgodkända biblioteket behåller egen prövning och återkallelse.
  Dess tre aktiverade poster kopieras/importeras inte till denna arbetskopia.
- `coverage.sources` anger `ok`, `disallowed_by_robots`, `not_consulted` eller `unavailable`.
  Om en källa fallerar får dess begränsning inte döljas bakom bibliotekets träffar.
  Om inga källor kan verifieras returneras neutralt fel, inte ett påhittat nollresultat.

## Alla åtta verktyg

`arn_search`, `arn_search_company` och kombinationsverktygen söker det godkända
lokala indexet. Företagssökning är textsökning i godkända referat, inte verifierad
partsidentitet eller ett fullständigt företagsregister. `arn_similar_cases`
använder ordöverlapp över samma godkända index; ingen LLM eller extern sökmotor.

I den lokala 1.0.5-kandidaten avvisar `arn_search` en tom fråga och returnerar
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

Utökad behandling omfattas INTE av 1.0.4:s trepostbeslut. Se
[postspecifik 1.0.5-bedömning](docs/105-processing-and-policy.md) för kvarstående
artikel 6/14/9/10- och källvillkor. `ARN_BROAD_HTML_ENABLED=1` aktiverar inte
självt live-HTML; standardkälläget är reviewed_index. Staging blir inte sökbart
utan uttryckligt hashbundet godkännande. Ingen 1.0.5-post aktiveras av denna kodändring.

Syntetiska prov: `python -B -m pytest tests -q -p no:cacheprovider` med samma
Python 3.14.4/MCP 2.3.0 och hashbundna låsfiler som 1.0.4. Faktiska läsande källprov
redovisas separat utan råtexter eller kunduppgifter. Inget CI-pushmandat finns.
[Införande och rollback](docs/INSTALL-105.md) kräver separat godkännande.

## Befintlig anslutning och rättigheter

Nuvarande publicerade 1.0.4-endpoint är https://mcp.qysley.se/arn/mcp .
OAuth-/klientguiden, proprietär [LICENSE](LICENSE) och [SECURITY](SECURITY.md)
bevaras. Support: arn-support@qysley.se. Rättigheter: arn-privacy@qysley.se.
Nuvarande policy: https://qysley.se/privacy/arn/ och engelsk version på
https://qysley.se/en/privacy/arn/ . De beskriver godkänd 1.0.4-drift; 1.0.5:s
opublicerade behandlingsdelta måste godkännas/införas före eventuell drift.
Villkor/ånger: https://mcp.qysley.se/arn/consumer/information och
https://mcp.qysley.se/arn/consumer/withdrawal . Inga nya kundtexter publiceras här.

## Lokal kandidat efter källgranskning — 2026-11-13

Källunderlaget innehåller 186 unika referenser utan dubbletter: 141 från den
vägledande översikten (däribland 3 tidigare godkända bibliotekstexter) och 45
från Vanliga fall. Det är inte 186 godkända indexposter. De 183 nya
postversionerna är fortsatt pending. I det uttryckliga `official_html`
undersökningsläget kunde tidigare upp till 154 utdrag visas och 32 hölls tillbaka
av innehållsflaggor; det läget omfattas inte av den rekommenderade publika
indexvägen och är inte ett rättsligt godkännande. En innehållsflagga är inte en
fastställd artikel 9/10-klassificering. Indexläget exponerar bara poster som
godkänts mot exakt innehållshash och approval-pin.

Ärendenumrens år sträcker sig 2014–2026. Ingen verifierad HTML-täckning för
2000–2013 eller 2015 har tillkommit. Ärendeår är inte beslutsdatum. För 45 nya
poster är beslutsdatum/kategori inte verifierade; de anges okända. Datumfilter
utesluter okänt beslutsdatum i stället för att gissa från ärendenumret.

I reviewed_index-läget matchas frågan endast mot godkända fält; ingen rå
HTML-mottagning eller dold sökning efter bortfiltrerad text sker. Det separata
`official_html`-läget kan ta emot och filtrera rå HTML före visning och omfattas
av en egen behandlingsgrind. Ett ARN-mejl är varken ett generellt väntkrav eller
ett GDPR-godkännande.
