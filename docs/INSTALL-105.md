# 1.0.5 — förberett införande, EJ INSTALLATIONSGODKÄNT

Senaste mottagningsprövning utgår från kodrevision
`8284eee9e162840044cd1bcffaf426ac8395a0fd`, med därefter snävt verifierad lokal
företagsrollskorrigering (57/57 Windows och Linux). Det äldre fyrfilspaketet
har inte denna nya modulhash och får inte användas som aktuell payload.
Filurvalet nedan beskriver den
tekniskt verifierade livekandidaten, inte en införd lokal indexvariant.
`105-processing-and-policy.md` preciserar det kvarstående insamlingshindret
och skiljer rättsliga krav från försiktighetsval. Individuell fältprövning finns
i `105-individual-index-review.md`: 3 gamla exakta versioner, 175 ordinära
minimeringskandidater och 8 fall med särskild artikel 9/10-prövning om innehållet
behålls. Av de 175 ordinära kandidaterna har 146 tidigare förslag hashkontinuitetskontrollerats och 29 minimerade textutkast har nya hashpar. Alla 175 är fortfarande ej godkända; inget
nytt index har aktiverats.
`privacy-105-index-draft.md` gäller den lokalt implementerade men inte
införda indexkopplingen. Varken dokumenten eller en avstängd liveflagga
gör det befintliga paketet godkänt för publik drift. Paketet ska inte köras
innan den faktiska mottagningsvägen, urvalet och införandet godkänts.

Arbetsformen för redaktionell förberedelse är godkänd enligt
ARN-105-OWNER-20261113-EDITORIAL-PREPARATION-001. Det är inte godkännande av
enskilda poster eller drift.
För ett senare indexinförande ska källäget uttryckligen vara reviewed_index;
inget godkänt index får falla tillbaka till official_html. Innehåll, approvalpin,
aktuell journal/ankare och filrättigheter måste ingå i samma införandegrind.
De privata stagingfilerna med 183 väntande poster är inte aktiveringsunderlag.
Se den uppdaterade artikel 6/14-bedömningen och individuella dispositionen innan
framtida installationsbeslut.

Utgångspunkt: produktion 1.0.4 på `18e79a070899900caa1972f65514141269b15696`. Ingen push/merge/tagg/installation ingår
i detta uppdrag. Ändra inte 1.0.4-taggen, bibliotekets treposter, pin, journal,
ankare, databaser, OAuth, PayPal eller andra tjänster.

## Före ägarens installationsbeslut

1. Granska kandidatens manifest och Windows/Linux-resultat. Ingen GitHub-CI-körning
   påstås för 1.0.5: pushmandat saknas. Kontrollera aktiveringsblockerarna i
   105-processing-and-policy.md. Robots-disallow får inte kringgås med UA eller
   config. Accepterad källtäckning måste anges uttryckligen, inte kallas hela ARN.
2. Gör en färsk skrivskyddad baslinjekontroll av berörda runtimefiler, Python/SDK,
   ARN ExecStart/UID och kontrollfiler. Använd inte en gammal match som livebevis.
3. Bygg en privat kompatibilitets-/installationspayload från exakt kandidatmanifest.
   Nödvändigt runtimefilurval är ENDAST arn_html_search.py (ny), arn_mcp.py,
   arn_public_responses.py och hashbunden common_case_catalog.json (ny). Övriga runtimekomponenter ska matcha 1.0.4-baslinjen.
   README/CHANGELOG/server.json är releaseartefakter, inte serverkonfiguration.
4. Skyddad backup före ändring: dessa två befintliga Python-filer, eventuell tidigare
   arn_html_search.py och common_case_catalog.json, den avgränsade systemd-dropin som styr aktivering och
   versions-/hashinventering. Rootägd 0700 backup/0600 filer. Verifiera SHA och
   återläsning till separat temporär katalog innan ändring. Återställ inte databaser.
   Spara kontrollfilsmetadata/hash utan att reinitialisera dem. Ingen full .venv-kopia.

## Planerad ändring efter separat godkännande

- Installera endast de fyra hashbundna runtimefilerna atomärt med befintligt
  ägarskap/behörighet; inga paketinstalleringar eller ändringar av låsfiler i drift.
- Separat ARN-dropin får ange ARN_BROAD_HTML_ENABLED=1 endast efter uppfyllda
  sakvillkor. Default är 0; en installerad men avstängd kandidat uppfyller inte
  produktmålet och ska inte presenteras som fungerande bred publik sökning.
- Publicera godkänt policydelta före ny personuppgiftsutlämning. Gamla villkor,
  avtalssnapshots och ansvarig-/rättighets-/retentionsinformation bevaras.
- Endast ARN får kort omstart. Auth/Nginx/SMTP/övriga system ska inte ändras.

## Obligatoriska efterkontroller

Verifiera installerade SHA/initialize-version 1.0.5; åtta verktygsnamn och samma
argument; OAuth/discovery 200 och oautentiserad MCP 401 Bearer; tre godkända
bibliotekshashar och senastejournal/ankare oförändrade. Ingen riktig betalning.

Verifiera syntetisk nekad admission ger 0 källanrop, medgiven kombination ger en
kvotoperation, robotsblockeddb ger 0 form/PDF-anrop, bred verklig HTML-träff utanför
treposter och korrekt källa/länktyp, godkänd biblioteksläsning samt okänd referens/
källfel. Autentiserad wire-kontroll görs med ägarens befintliga klient och
angiven kvotkostnad. Varken intern stub eller tools/list ersätter faktisk wire.
Återkallad referens får inte återkomma via bred källa eller gammal backup.

## Säker rollback

Stoppa endast ARN. Återför exakt de verifierade 1.0.4-kodfilerna och tidigare
aktiveringsdropin ur backup (ta bort nytillagd fil/dropin endast om den saknades
före installationen och endast inom exakt dokumenterad målväg). Återför aldrig
äldre kontrolljournal/ankare eller kunddatabaser. Verifiera 1.0.4-filer mot backup,
1.0.4:s lokala trepostadapter utan PDF-fallback, och starta ARN först efter
kontroller. Vid osäkerhet håll ARN stoppad; inga andra tjänster påverkas.

Detta är en komplett avgränsning för ett senare hashbundet installationsscript,
inte en procedur som nu körts eller bevis att framtida baslinje fortfarande matchar.


## Obligatorisk bevaring av de tre 1.0.4-posterna — fail closed

1.0.5-kandidatens lokala `library/approved.json` och `library/approvals.json` är tomma, eftersom inga nya 1.0.5-poster har godkänts. **De filerna får aldrig kopieras över produktionens separata `/etc/arn-library-content/approved.json` eller `approvals.json`.** Installationspayloadens allowlist ovan utesluter båda biblioteksdatafilerna samt staging- och approvalsfiler.

Före service-stopp ska en skrivskyddad preflight verifiera att de installerade produktionsfilerna fortfarande motsvarar 1.0.4-inventeringen: `approved.json` SHA256 `f1bd1bb448a2fe7e01e6c4cb89fadcfced0d9f7e2c213ef30fac2a763390a10d`; `approvals.json` SHA256 `0afa6fa648dc9db992c639c57f8c2d202d1de49e793a24372525f65412a69845`. Semantiskt ska exakt följande godkända referenser finnas kvar med oförändrat innehållshash: `BIB-HTML-EL-001` / `2022-15738` / `cf68b2063017cd995e4804d102d26014fa0c791c4ddc453e88946f787e24da27`; `BIB-HTML-MOTOR-001` / `2026-00382` / `135a551a0b810ceaf837eb5019ad042a9f1a8e80d0f45116bced0bda34fecb9d`; `BIB-HTML-LEASING-001` / `2026-00591` / `89b2b03ba4166941665fd607dcf80101287aeaadf9bc5d5030c62f5fff80ee9b`. Om filhash, antal, status eller innehållshash avviker: stoppa före produktionsändring och utred den aktuella legitima dataversionen. Försök inte ersätta med kandidatens tomma filer.

Efter runtimeinförande ska båda produktionsfilerna åter hashverifieras mot preflightvärdena och de tre referenserna kontrolleras igen. Databibliotek, approvals, återkallelsejournal och oberoende ankare kopieras inte från releasekandidaten och skrivs inte om. Om ett senare separat godkännande lägger till nya poster måste det göras som en uttrycklig, hashbunden och additiv biblioteksändring; denna installationsprocedur godkänner inga sådana nya poster. Rollback får inte återställa äldre journal/ankare eller databaser.


## Status efter hashbunden ägarbedömning och källkontroll — 2026-11-14

Detta dokument är fortfarande en förberedelse, inte ett godkänt installationspaket. Ägarens artikel 6.1 f- och artikel 14.5 b-beslut är dokumenterade för exakta hashversioner, men separata innehållsgodkännanden står pending. Den slutliga källkontrollen ger 172 versioner kvar i den villkorade beslutsmängden och tre versioner återförda till källänksgranskning (2019-16037, 2020-27482, 2021-03350). Åtta specialposter kvarstår på HOLD. De tre godkända 1.0.4-posterna ska bevaras exakt.

Ingen ny post får läggas i produktionsbiblioteket förrän de 172 exakta postversionerna var för sig har passerat befintlig hashbunden innehållsgodkännandegrind, de tre undantagen har fått en separat ny bedömning, 1.0.5-integritetsinformationen har publicerats med separat mandat och rättighets-/invändnings-/spärrvägen har verifierats operativt. Paketet som kan överlämnas nu är endast ett granskningsunderlag; det är inte en körbar runtimepayload och får inte användas för installation.
