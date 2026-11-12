# Konfiguration för ARN MCP 1.0.4

## Klient

Använd https://mcp.qysley.se/arn/mcp och OAuth-discovery enligt usage.md.
Policy och avtalsinformation kan läsas utan MCP-token eller betalning.

## Skyddad drift

Runtime kräver Python 3.14.4/MCP2.3.0 och befintlig licensbackend, Qysley Auth
samt PayPal-konfiguration. `.env.example` innehåller bara exempel, inga nycklar.
Använd inte produktionsvärden i tester. Betalningsmiljö måste vara uttrycklig;
årsplanen är590SEK, månadsplanen59SEK. Aktiv status är inte ensam betalningsbevis.
R11 är redan införd; godkänd avvikelse för naturlig andra period ska inte döljas.

Alla dataverktyg använder ARN_LIBRARY_PATH och ARN_LIBRARY_APPROVALS med
ARN_LIBRARY_APPROVALS_SHA256. ARN_LIBRARY_REVOCATIONS, ARN_LIBRARY_REVOCATION_ANCHOR
och ARN_LIBRARY_REVOCATION_LOCK måste peka på skyddat aktuellt kontrolltillstånd.
Runtime får inte skriva innehåll, godkännanden eller kontroller. Kontrollankaret
förvaras oberoende av innehållets backup/återställning. Återställ aldrig äldre
kontrollstatus och återinitialisera aldrig bort en spärrhistorik.
ARN_LIBRARY_ALLOW_SYNTHETIC får inte aktivera syntetiska poster i verklig drift.
Inget godkänt innehåll finns i kodpaketets tomma JSON-filer. Ingen livefallback.

ARN_CONSUMER_CONFIG pekar på den granskade privata konfigurationen, med
hashbundna godkända villkor/integritets-/ångertexter, befintligt offentligt
mottagarcertifikat och privat ARN-CSRF/kapabilitetshemlighet. Den innehåller
inte mottagarens privata dekrypteringsnyckel. consumer-config.example.json är
avsiktligt INTE aktiverad eller direkt driftsättningsbar. Rätt sändar-UID och
skyddad kvittokatalog måste verifieras i målmiljön.

ARN_DISCLOSURE_POLICY ska vara en rootägd, för runtime skrivskyddad projektion
från den manuella kopiejournalen. Saknad/ogiltig skyddad konfiguration stoppar
aktiverad kundväg. Nya abonnemang får inte kringgå förhandsinformationen.
Hela betalda kundvägen behöver den separat införda, skyddade sändartjänsten;
dess privata kod/konfiguration och verkliga kontakt-/avtalstexter ingår inte i
detta publika kodurval. SMTP-acceptans är inte bevis på brevlådemottagning.

## Införande och rollback

Inför inte hela kodträdet över en befintlig tjänst. Jämför baslinje/beroenden,
validera paketets exakta filurval och skapa skyddad backup med provad återläsning.
Stoppa endast berörd ARN-tjänst för samordnat kod/config-byte. Efterkontrollera
version/åtta verktyg,200discovery,401Bearer, rättigheter, konsumentväg och skyddade
tjänster. Ändra inte Auth eller befintliga betalningsdata.

Rollback återställer kod/config, aldrig nyare ärenden, avtalskopior, ledger,
kvitton eller kontrollstatus. Om tidigare kod skulle öppna köp utan nödvändig
konsumentinformation ska ARN lämnas stoppad tills säkert införande är verifierat.
Ingen automatisk databassnapshot-återställning eller gallring får ingå.
