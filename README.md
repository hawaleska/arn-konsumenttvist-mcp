# ARN Konsumenttvist MCP1.0.5 — lokal kandidat

Bred HTML-sökning i ARN:s publicerade vägledande material, skild från lokalt
godkända sammanfattningar. Inte hela ARN:s databas, inte hela beslutet.
Publicerad1.0.4 och dess tagg är oförändrade. Ingen1.0.5-installation/publicering
är godkänd. Agensi-/prissättningsarbete är pausat; befintliga betalningar bevaras.

## Faktisk täckning och källor

- Officiellt HTML-sökformulär: https://adokweb.arn.se/referatwebb . Manuell
  provsökning gav äldre referat och fler träffar än biblioteket, men värdens
  robots.txt anger `User-agent:* / Disallow:/`. Kandidaten kontrollerar detta
  före formulärhämtning och använder därför INTE databasen automatiskt i dag.
  Ett rättsligt/avtalsmässigt klarlagt tillåtet automatiseringssätt krävs för
  denna del. Ingen UA-växling eller kringgång används.
- https://www.arn.se/om-arn/vagledande-beslut/ beskriver själv urvalet som de
  senaste vägledande besluten, inte hela databasen. Kandidaten kan söka lokalt
  i dess offentliga HTML-text efter hämtning; råsidan lagras inte på disk.
- En hashbunden källkatalog innehåller45 individuellt källkontrollerade fall från
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

`arn_search`, `arn_search_company` och kombinationsverktygen söker tillgänglig
HTML och bibliotek. Företagssökning är textsökning, inte verifierad partsidentitet
eller ett fullständigt företagsregister. `arn_similar_cases` använder ordöverlapp
med högst två begreppsfrågor som komplement; ingen LLM eller extern sökmotor.

`arn_get_decision` läser en godkänd bibliotekstext när sådan finns. Annars visas
endast tillgängligt källutdrag, referens och uttrycklig uppgift att godkänd lästext
saknas. `content_kind`, `read_status` och `source_link_kind` skiljer detta åt.
Källänken märks `overview` om ingen verklig ärendespecifik HTML-länk finns.
Inga sessions-/PDF-länkar lämnas ut. Datum/kategori markeras okända när de saknas.
Inga företagsnamn eller utfall gissas. PDF/fulltext hör fortsatt till2.0.

`arn_create_subscription` och `arn_cancel_subscription`, OAuth, PayPal och
befintliga kvot-/betalningsregler är oförändrade:10fria användningar,59/590SEK.
Ett medgivet dataverktygsanrop debiteras före källarbetet, även vid tomt resultat
eller källfel; kombination/begreppssökning debiteras inte en gång per HTTP-anrop.
Ingen prissättningsutveckling ingår i kandidaten.

## Integritet och säker drift

Inga sökfrågor skickas till kommersiell sökmotor. Om databasens robotsregler
senare tillåter åtkomst skickas sakfrågan via dess vanliga HTTPS-formulär till
ARN. Översiktssökningen skickar INTE frågan till ARN; matchningen sker i minnet.
Tillfälliga cookies/HTML/formdata tas bort när anropet avslutas; ingen corpuscache
eller rå HTML/PDF lagras av koden. OS-/tjänste-/leverantörskopior garanteras inte.
Namn och indirekta identifierare kan undgå den begränsade maskeringen.
Potentiellt känsliga utdrag hålls tillbaka heuristiskt, inte juridiskt klassificerat
eller garanterat anonymiserat. Rå HTML kan redan ha innehållit sådana uppgifter.

Utökad behandling omfattas INTE av1.0.4:s trepostbeslut. Se
[postspecifik1.0.5-bedömning](docs/105-processing-and-policy.md) för kvarstående
artikel6/14/9/10- och källvillkor. `ARN_BROAD_HTML_ENABLED=1` är en explicit
teknisk aktiveringsgrind, inget rättsligt godkännande. Standard är avstängt,
med tydligt fel vid bred sökning, inte tyst återgång till treposter.

Syntetiska prov: `python -B -m pytest tests -q -p no:cacheprovider` med samma
Python3.14.4/MCP2.3.0 och hashbundna låsfiler som1.0.4. Faktiska läsande källprov
redovisas separat utan råtexter eller kunduppgifter. Inget CI-pushmandat finns.
[Införande och rollback](docs/INSTALL-105.md) kräver separat godkännande.

## Befintlig anslutning och rättigheter

Nuvarande publicerade1.0.4-endpoint är https://mcp.qysley.se/arn/mcp .
OAuth-/klientguiden, proprietär [LICENSE](LICENSE) och [SECURITY](SECURITY.md)
bevaras. Support:arn-support@qysley.se. Rättigheter:arn-privacy@qysley.se.
Nuvarande policy:https://qysley.se/privacy/arn/ och engelsk version på
https://qysley.se/en/privacy/arn/ . De beskriver godkänd1.0.4-drift;1.0.5:s
opublicerade behandlingsdelta måste godkännas/införas före eventuell drift.
Villkor/ånger:https://mcp.qysley.se/arn/consumer/information och
https://mcp.qysley.se/arn/consumer/withdrawal . Inga nya kundtexter publiceras här.

## Verifierad kandidat efter källgranskning2026-11-13

186unika referenser kan sökas utan dubbletter:141från den vägledande översikten
(inklusive3redan godkända bibliotekstexter) samt45från Vanliga fall. Bara154har
ett synligt källutdrag i breda vägen;32beskrivningar hålls tillbaka av konservativa
flaggor, inte32konstaterade artikel9/10-fall. Direkt hämtning av en känd
Vanliga-fall-referens sker ur den verifierade lokala källkatalogen utan ny
hel-HTML-hämtning. source_kind och source_checked_at skiljer källa och snapshot.

Ärendenumrens år sträcker sig2014–2026. Ingen verifierad HTML-täckning för
2000–2013 eller2015 har tillkommit. Ärendeår är inte beslutsdatum. För45nya
poster är beslutsdatum/kategori inte verifierade; de anges okända. Datumfilter
utesluter okänt beslutsdatum i stället för att gissa från ärendenumret.

En bortfiltrerad hälsa-/brottskontext är inte längre ett dolt sökindex: frågan
matchas mot de uppgifter som faktiskt får visas. Råhel-HTML kan dock fortfarande
innehålla sådan kontext före filtreringen i översiktsvägen. Den konkreta
behandlingsgrinden kvarstår oberoende av när ARN svarar. Ett ARN-mejl är varken
ett generellt väntkrav eller ett GDPR-godkännande.
