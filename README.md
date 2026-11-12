# ARN Konsumenttvist MCP 1.0.4

ARN MCP ger konsumentupplysning genom individuellt granskade och minimerade
sammanfattningar av ARN:s publicerade HTML-referat. Det är en fristående tjänst,
inte en del av ARN och inte individuell juridisk rådgivning.

## Täckning och verktyg

Alla sex dataverktyg använder samma godkända bibliotek. Den kontrollerade driften
har tre godkända referat. Biblioteket kan utökas utan serverändring efter separat
granskning och hashbundet godkännande; det finns ingen fast gräns på tre.
Sökningen omfattar inte hela ARN:s arkiv. Sammanfattningar är inte fullständiga
beslut. Ingen automatisk ARN-/PDF-hämtning eller livefallback används; PDF-stöd
ingår inte i 1.0.4.

- `arn_search`: sök godkända sammanfattningar.
- `arn_get_decision`: läs en godkänd sammanfattning med ärendereferens och källa.
- `arn_search_and_read`: sök och läs sammanfattningar i ett anrop.
- `arn_search_company`: sök verifierade företagsuppgifter i biblioteket.
- `arn_search_company_and_read`: läs sammanfattningarna från företagsträffarna.
- `arn_similar_cases`: jämför rättsfrågor och hitta liknande sammanfattningar.
- `arn_create_subscription`: påbörja månads- eller årsabonnemang via kundinformation och PayPal.
- `arn_cancel_subscription`: begär uppsägning av det egna abonnemanget.

Okända företag, utfall och andra detaljer fylls inte i. Företagssökningen kan
ge noll träffar även om biblioteket innehåller en relevant rättsfråga. Kontrollera
viktig information mot källhänvisningen.

## Anslutning, pris och avtal

Endpoint: https://mcp.qysley.se/arn/mcp . Se [klientguiden](docs/usage.md).
Tio fria användningar delas mellan sex dataverktyg. Ett kombinerat sök-/läsanrop
räknas en gång. Även läsning, tomma resultat, fel och upprepade anrop kan förbruka
kvot när anropet har släppts igenom. Abonnemangsverktygen förbrukar inte datakvot.
Månadspris: **59 SEK**. Årspris: **590 SEK**. Ingen betalningsregel ändras här.

[Avtalsinformation](https://mcp.qysley.se/arn/consumer/information) visas före
PayPal-godkännande. Abonnemang förnyas tills de sägs upp. Betald åtkomst kräver
verifierad betalning; status ACTIVE eller nästa debiteringstid är inte ensam
betalningsbevis. Nya betalda avtal inväntar även SMTP-acceptans för bekräftelsen.
Vid mejlfel kan åtkomst dröja; osäkra utfall kräver manuell avstämning.
R11 är införd med tidigare godkänd avvikelse för naturlig andra betalperiod.

Nya avtal har 14 dagars full ångerrätt även efter användning.
[Ångra avtalet här](https://mcp.qysley.se/arn/consumer/withdrawal), eller kontakta
arn-support@qysley.se. Berättigad återbetalning hanteras manuellt, inte automatiskt.

## Integritet och rättigheter

[Integritetsinformation](https://qysley.se/privacy/arn/) ·
[English privacy information](https://qysley.se/en/privacy/arn/).
Kontakta **arn-privacy@qysley.se** för rättigheter och invändningar, även utan konto.
Support: **arn-support@qysley.se**. Skicka inte lösenord, tokens, ID-kopior eller
onödiga personuppgifter. Granskning/minimering är inte en anonymitetsgaranti.

## Drift och verifiering

Python 3.14.4 och MCP SDK 2.3.0 används med hashbundna låsfiler.
[Konfiguration](docs/configuration.md) skiljer klientanslutning från skyddad drift.
Kodpaketet distribuerar inte de aktiverade biblioteksposterna eller operativa
hemligheter. Innehåll, godkännanden/pin och senaste återkallelsejournal med
separat ankare införs separat. Äldre backup får inte återaktivera återkallat innehåll.

Syntetiska publika kontroller: skapa en isolerad venv, installera
`requirements-test.lock` med `pip install --require-hashes --only-binary=:all:`
och kör `python -B -m pytest tests -q`. Ingen verklig betalning eller ARN-import
ska göras som utvecklingsprov. Privata operatörs-/systemd-prov redovisas separat.
Version 1.0.4 är en releasekandidat; GitHub-release och Registry kräver separat
ägargodkännande. Se [CHANGELOG](CHANGELOG.md) och [licensen](LICENSE).
