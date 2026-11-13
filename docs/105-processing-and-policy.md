# 1.0.5 — mottagning, kontrollerat index och avslutad artikel 6/14-prövning

Datum: 2026-11-13. Kodbas: `8284eee9e162840044cd1bcffaf426ac8395a0fd`.
Detta ersätter den föregående bedömningen i samma fil. Ingen runtime, källa,
aktiv post, produktionskonfiguration eller produktomfattning har ändrats.
ARN:s mejlsvar är inte ett generellt väntkrav. 1.0.4:s trepostbeslut står kvar.

## Besked och evidensgräns

Koden är tekniskt provad men 186-referensvarianten är inte införandeklar.
32 innehållsflaggor är INTE 32 konstaterade artikel 9/10-fall. Inga personer
har identifierats genom externa register eller akter. Ingen PDF har hämtats.
Exakta referenser, källor och separata observationer/bedömningar finns i
`review-local/RECEPTION-DECISION-EVIDENCE.json`. Frånvaro av regexträff bevisar
inte att övriga 154 innehåll är fria från sådana uppgifter.

### Källor och vad som faktiskt har påträffats

| Källa / referens | Konstaterat innehåll | Vad som INTE är fastställt |
|---|---|---|
| Vägledande översikten, 2023-24464 | Hälsorelaterad samtyckesfråga | Viss parts diagnos och faktisk identifierbarhet |
| Samma sida, 2020-08400 | Hälsa hos besättningsmedlem ingår i rättsfrågan | Att läsaren kan identifiera personen |
| Samma sida, 2024-20240 | Köp av specificerat läkemedel | Köparens diagnos eller faktisk användning |
| Samma sida, 2019-04475 | Försäkringsregel om graviditet | Faktisk graviditet hos en identifierbar person |
| Samma sida, 2025-00318/2024-24471 | Hänvisning till penningtvättsregler | Konkret personanknuten brottsmisstanke; ordet räcker inte |
| Samma sida, 2024-24944/2024-22797/2024-14210 | Kundkännedom/kontouppsägning | Att texten därmed är en artikel 10-uppgift |
| Samma sida, elva referenser i evidensfilen | Konkreta brottshändelser/utsatta konsumenter | Att alla brottsofferuppgifter automatiskt omfattas av artikel 10 |
| Vanliga fall, 2020-16845 på `/vanligafall/5.1.-forsakringsfall/` | Hälsorelaterad riskgruppstillhörighet kopplas till konsumenten | Den verkliga identiteten; ärendenumret ger dock kopplingsrisk |
| Vanliga fall, 2020-08290 på `/vanligafall/4.9.-tillgang-till-betalkonto/` | Konkret brottsmisstanke återges om kontohavaren | Att misstanken är sann eller att personen har dömts |
| Vanliga fall, sex stöld-/bedrägeri-/inbrottsfall i evidensfilen | Personanknutna händelser eller påståenden | Automatisk artikel 10-klassificering av samtliga |
| Vanliga fall, 2017-02218/2019-00739 | Produktbeteckning respektive allmän regel | Individuell hälsouppgift i de granskade avsnitten |
| Vanliga fall, 2021-03350/2020-27482 | Ordinära sakskadeavsnitt | Hälsouppgift i dessa avsnitt; nuvarande flagga ärvs från annan del av samma sida |

Hälsosidan med flera fall innehåller fyra ärenden totalt. En sidgemensam
flagga får inte omvandlas till ett påstående att samtliga parter har samma
hälsotillstånd. Kandidaten lämnar inte ut den råa gemensamma texten, men dess
spärr är grövre än en individuell bedömning. Även titlar och specifika URL:er
kan avslöja brottskontext trots att beskrivningen hålls tillbaka.

Den senaste översikten är EN HTML-resurs med 141 referenser. Att utelämna en
post efter parsning, använda URL-fragment, CSS, strömfiltrering, lokal proxy
eller en LLM innebär inte att Qysley har undvikit mottagning av sidans övriga
uppgifter. Ingen verifierad ärendefiltrerad HTML/feed-endpoint har påträffats.
Databasen har robotsförbud och används inte. Vanliga-fall-katalogens 45 poster
är redan lokala snapshots; deras 52 källsidor hämtas inte per användarsökning.

## Rättslig kvalificering — vad hindret faktiskt gäller

Artikel 9 aktualiseras när information om t.ex. hälsa avser en identifierad
eller identifierbar människa, även genom slutsatser. En abstrakt rättsregel,
djursjukdom eller allmän produktbeteckning är inte ensam ett sådant bevis.
2020-16845 innehåller en faktisk personanknuten hälsouppgift; identifikations-
bedömningen måste omfatta ärendenummer, källa och rimligt användbara externa
kopplingar, utan att bygga ett nytt personregister.

Artikel 10 gäller inte varje omnämnande av penningtvätt, avtalsbrott eller
oaktsamhet. 2020-08290 innehåller däremot en konkret brottsmisstanke om en part.
Artikel 10-frågan är då reell om parten är identifierbar. Brottsofferfallen
behöver särskild kvalificering; ingen generell slutsats har styrkts här.
Precisering av tidigare källhänvisning: IMYRS 2021:1:s diskussion om brottsoffer
i avsnittet om mediegrundlagarna är inte ensam ett avgörande att varje offer-
uppgift omfattas av artikel 10. IMY upplyste 2026-09-23 om en pågående begäran
om EDPB-klargörande för uppgifter utan inlett rättsligt förfarande. Inget
slutligt nytt EDPB-besked har verifierats i detta arbete; det är inte ett
generellt väntkrav för ordinära rättsfallsuppgifter.

Ingen generell artikel 9.2-grund eller särskild artikel 10-auktorisation har
visats för Qysleys allmänna praxissökning. ARN:s publicering styrker inte att
den registrerade själv tydligt offentliggjort uppgiften (9.2 e). Att någon
kan använda tjänsten för ett anspråk visar inte nödvändighet för ett konkret
anspråk (9.2 f eller 5 § kompletteringsförordningen). Ett ägarbeslut kan inte
skapa det saknade stödet. Behövs sådana uppgifter måste faktisk identifierbarhet,
kvalificering och tillämpligt särskilt stöd beläggas, annars ska de inte tas in.

## Konkret mottagningslösning: lokalt godkänt index

**Rekommendation:** ersätt livekällan i användarsökningen med ett kontrollerat,
versionsbundet lokalt index. Alla sex dataverktyg kan använda samma index;
de två abonnemangsverktygen och admission/kvot behöver inte ändras. Det ger
stabil granskningsbar täckning och ingen ny råmottagning när användaren söker.

Tillåtna fält efter individuell prövning: ärendenummer, verifierat datum och
kategori, rättsfråga, minimerade juridiska sak-/bedömningsuppgifter och utfall,
officiell käll-URL/länktyp, källtyp, granskningsdatum, version och innehållshash.
Okända fält förblir okända. Namn, privat kontakt, initialer som partsnyckel,
diagnos, personanknuten brottsmisstanke och onödiga särpräglade omständigheter
ingår inte utan separat styrkt stöd. Även URL/titel/ärendenummer prövas; de
är inte automatiskt harmlösa när texten tagits bort.

**Insamlingsgrind före indexet:**

1. Använd ett redan lagligen framställt och dokumenterat, minimerat underlag,
   eller en individuellt avgränsad källresurs vars mottagning stöds rättsligt.
   Om en sida blandar ordinära och särskilda uppgifter behövs stöd för hela
   det som faktiskt tas emot. Manuellt klippande är inte ett undantag.
2. Ett alternativ är att ARN eller annan självständigt ansvarig, behörig
   leverantör minimerar före Qysleys mottagning. Dess behörighet, urval,
   leveransfält och Qysleys egen artikel 6/14 måste kunna visas. En för Qysley
   arbetande proxy/biträde flyttar inte bort ansvaret och löser inte detta.
3. Befintliga snapshots är inte retroaktivt godkända av att de redan finns.
   De får inte föras in som `approved` utan förberedelsens och fältens stöd.
4. Granska exakt mottagen version. Bind laglig insamling, artikel 6/14,
   9/10-kvalificering, rättslig korrekthet, identifikationsbedömning och
   återanvändning till samma innehållshash. Därefter separat godkännande.
5. Återanvänd betrodda hashpins, root-writer/non-root-reader, aktuell journal,
   separat ankare och återkallelsegrind. Ingen återställning får återaktivera.

Det behövs inte ett nytt kontrollsystem. `SummaryLibraryClient` har redan
individuell hashbunden publiceringsgranskning. Tekniska deltan efter beslut
är att koppla den lokala källan i stället för `OfficialHTML.search`, tillåta
granskade Vanliga-fall-URL:er i rätt källvalidator och bevara okända metadata.
Nuvarande `CommonCaseCatalog`-pin är endast integritetsskydd, INTE individuell
publiceringsauktorisation. `ARN_BROAD_HTML_ENABLED=0` är inte ett färdigt brett
indexläge. Inga sådana runtimeändringar eller postgodkännanden har gjorts här.

### Täckningskonsekvenser före eventuellt omfattningsbeslut

| Alternativ | Referenser | Visningstexter med nuvarande underlag | Förlust mot kandidaten |
|---|---:|---:|---|
| Oförändrad livekandidat | 186 | 154 | Ingen; mottagningsfrågan kvarstår |
| Lokalt index med samma 186 | 186 möjliga | 154 möjliga | Ingen strukturell förlust; insamling/fältgodkännanden ännu saknas |
| Hela översiktskällan bort, tre godkända + 45 snapshots | 48 | 36 | 138 referenser och 118 visningstexter |
| Lokalt index där samtliga 32 flaggade referenser sätts i karantän | 154 kandidater | 154 | 32 referenser; ingen nu visad beskrivning försvinner, men ämnes-/referenstäckning minskar |

Sista raden är ett exakt tekniskt urval, INTE juridiskt godkännande av de 154.
Den överutesluter också kända oskyldiga signaler. Ingen automatisk bortsortering
eller ändring av produktmålet har beslutats. Källfel/löpande uppdateringar skulle
i indexmodellen ersättas av kontrollerad uppdatering och synligt snapshotdatum.
Nya ARN-poster blir inte omedelbart sökbara. Alla åtta verktyg kan finnas kvar,
men läsning/jämförelse av uteslutna referenser och datum-/ämnestäckning minskar.
Aktiva tre godkända texter påverkas inte av något av dessa beräknade alternativ.

## Slutlig artikel 6.1 f-bedömning för ordinära godkända indexfält

Ändamål: sökbara, källhänvisade och uppgiftsminimerade referat för konsument-
upplysning och förståelse av konsumenträttslig praxis. Ett legitimt kommersiellt
intresse kan förenas med denna konsumentnytta; det är inte myndighetsutövning.

| Moment | Nödvändighet och avvägning | Ställningstagande |
|---|---|---|
| Avgränsad insamling | Juridisk fråga och källa behövs; hela blandade översikten behövs inte i drift när ett kontrollerat index ger samma träffar | 6.1 f kan bära ordinära fält; inte ovidkommande 9/10-råkontext |
| Tillfällig bearbetning | Korrekt referens, roll-/sakminimering och kvalitet krävs; inga privata partsnycklar/råcache | Samma ordinära grund; förberedelsen måste vara laglig före filtret |
| Indexlagring/sökning | Lokal lagring undviker upprepad råhämtning; rättsfråga gör mer nytta än enbart länkar | Försvarbar för prövade minimerade fält med relevans-/stödomprövning |
| Utlämning till MCP-klient | Källkontroll/juridisk förståelse kräver vissa sakuppgifter; ingen personsökning eller ranking av individer | Begränsad uppgiftsmängd och rättighetsgrind krävs; klientkopior är en kvarstående risk |
| Sökfråga/kvot | Oförändrad åtkomst-/kvotadministration; lokal matchning behöver inte skicka frågan till ARN/sökmotor | Befintlig avtalsbehandling återanvänds; ovidkommande uppgifter om tredje person är inte nödvändiga |

Rimlig förväntan om återanvändbar konsumenträttslig information stöds av ARN:s
publiceringssammanhang, men inte av personprofilering. Qysley skapar ytterligare
sökbarhet, kombinationsmöjlighet och klientkopior. Konto/kvot är inte ett bevis på
låg spridning: kandidaten kan lämna hela urvalet vid tom fråga. Namn-/kontaktfria
fält, inga personnycklar eller extern frågeöverföring, exakt godkännande, synlig
källa och spärr även efter gammal backup minskar den tillkommande risken.

**Avslutad bedömning:** 6.1 f är en motiverad och försvarbar grund för dessa
ordinära godkända indexfält under villkoren ovan. Det krävs inte ett generellt
externjuristintyg, men ägaren ska fastställa ändamål, exakt versions-/fälturval,
avvägning och skydd före ny drift. Detta ersätter inte artikel 9/10-stöd och
fastställer inte att alla 186 redan uppfyller villkoren.

## Artikel 14 — genomförbar lösning och beslutsgräns

För ett index som ENDAST består av prövade, indirekt identifierande ordinära
uppgifter utan privata kontaktkanaler är artikel 14.5 b på grunden oproportionerlig
ansträngning en försvarbar, villkorad lösning. Motivet är inte att 186 är många:
ytterligare namn-/kontaktidentifiering skulle annars behöva göras enbart för
informationen, trots att tjänstens ändamål inte behöver denna identifiering.
CNIL ger uttryckligt stöd för detta resonemang vid laglig insamling av indirekt
identifierande nätdata. Dess AI-vägledning är en relevant analogi, inte bindande
svensk rätt eller ett särskilt undantag för denna MCP-tjänst. WP260 punkt 64
kräver en dokumenterad balans och offentlig fullständig information.

Faktiskt styrkt: katalogfält innehåller inte privata kontaktfält; tidigare
141-avsnittskontroll fann inte e-post/personnummermönster; ingen direkt relation,
kontaktlista eller partsidentifiering har skapats; trepostkanalen och spärrarna
finns. INTE styrkt: exakt antal fysiska personer eller att regexfrånvaro innebär
frånvaro av alla direkta identifierare/kontaktmöjligheter i allt mottaget HTML.

Beslut som ägaren kan fastställa vid indexgodkännande:
"För de exakta individuellt granskade indexposterna i godkänt hashmanifest,
som saknar direkta identifierare och betrodda privata kontaktkanaler, lämnas
full information offentligt enligt artikel 14.5 b. Extra partsidentifiering
och kontaktinsamling bedöms oproportionerlig i förhållande till den avgränsade
ordinära behandlingen och dess dokumenterade tilläggsrisk. Uppgifterna får inte
användas för personprofilering. Kontofri information och invändningsväg samt
verifierad återkallelse ska finnas före första utlämnandet. Beslutet omprövas
vid ändrat innehåll, risk, kontaktmöjlighet eller invändning. Finns en faktisk
användbar kontaktkanal ska den prövas för individuell information enligt 14.3;
14.5 b tillämpas inte automatiskt på sådana poster eller på särskilda uppgifter."

Inget ARN-svar eller påhittat antal kontaktarbetstimmar behövs för detta beslut.
Artikel 11 stöder att inte samla extra identitetsuppgifter enbart för efterlevnad,
men är ingen fristående informationsdispens. Vid laglig indirekt insamling gäller
14.3:s tidsfrister, bl.a. före första tillämpliga utlämnande; att behålla staging
skjuter inte automatiskt upp all informationsskyldighet. För redan mottaget
forsknings-/stagingmaterial krävs samma dokumenterade avgränsning, och ett nytt
beslut gör inte eventuell tidigare behandling retroaktivt laglig.

**Kvar innan detta kan tillämpas:** ett exakt individuellt prövat indexmanifest
och laglig förberedelse/mottagning. Den nuvarande kodpinnen för 45 snapshots är
inte detta underlag. Artikel 14 är inte en särskild grund för artikel 9/10.

## Policyförslag och kvarstående införandevillkor

`docs/privacy-105-index-draft.md` är ett sammanhållet förslag för den rekommenderade
indexmodellen, byggt på hashverifierad befintlig policy. Ansvarig, rättighetskanal,
leverantörer, överföringsinformation och beslutade retentionkriterier bevaras.
Inga nya leverantörer, tider, gallringsmandat eller godkännanden har lagts till.
Den får inte beskrivas som införd eller publiceras före fastställt indexurval,
artikel 6/14-beslut och faktiskt införda skydd. Ingen generell laglighet för
råa blandade källor påstås i policytexten.

**Precist kvarstående hinder:** en laglig, dokumenterad förberedelseväg och
individuell fältprövning för det breda indexet saknas. För personanknuten
hälsokontext/konkreta brottsmisstankar saknas styrkt särskilt stöd när personen
är identifierbar. Antingen visas sådant stöd, eller mottas endast ett i förväg
minimerat tillåtet underlag. Det är inte ett kodfel och kan inte lösas med en
ny lokal regex. Därefter behövs ägarens exakta omfattnings-/6/14-/policybeslut,
den lilla indexkopplingen och separat installation med befintlig backup/rollback.

Ingen omfattningsminskning har genomförts. Ingen ny testomkörning krävs för denna
dokumentationsändring: runtime/testbytes matchar provad revision 8284eee;
Windows396+4delprov och Linux398+4delprov återanvänds (Windows2plattformsskip).

Befintligt återanvändningsunderlag enligt 26 a § upphovsrättslagen behålls där
dess förutsättningar gäller för myndighetstext. Det är varken ett GDPR-stöd
eller rätt att kringgå robotsregler. Inga nya återanvändningsvillkor eller
leverantörsavtal har antagits genom indexförslaget.

## Rättskällor och bevis

Bindande: [GDPR artiklarna4,5,6,9,10,11,14,21,25 och skäl26/62](https://eur-lex.europa.eu/eli/reg/2016/679/oj/swe),
[förordning2018:219,5§](https://www.riksdagen.se/sv/dokument-och-lagar/dokument/svensk-forfattningssamling/forordning-2018219-med-kompletterande_sfs-2018-219/),
[C-252/21,punkterna76–85](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:62021CJ0252).
EUR-Lex svenska fulltext gav åtkomstkontroll vid detta tillfälle; den kringgicks
inte. Tidigare verifierad förordningstext och officiellt index återanvänds.

Vägledning (inte nytt lagstöd): [IMY intresseavvägning](https://www.imy.se/verksamhet/dataskydd/det-har-galler-enligt-gdpr/rattslig-grund/intresseavvagning/),
[WP260rev01,punkterna61–64](https://www.edpb.europa.eu/system/files/documents/2023-09/wp260rev01_en.pdf),
[CNIL,indirekt identifierbara uppgifter](https://www.cnil.fr/fr/ia-informer-les-personnes-concernees),
[IMYRS2021:1,avsnitt3.4 respektive4](https://www.imy.se/globalassets/dokument/rattsligt-stallningstagande/imyrs-2021-1-lagovertradelser.pdf),
[IMY:s pågående artikel10-fråga,2026-09-23](https://www.imy.se/nyheter/imy-begar-klargorande-om-vilka-brottsuppgifter-som-omfattas-av-artikel-10/).

Officiella innehållskällor: [vägledande översikten](https://www.arn.se/om-arn/vagledande-beslut/),
[gemensam försäkringssida](https://www.arn.se/vanligafall/5.1.-forsakringsfall/),
[betalkontosidan](https://www.arn.se/vanligafall/4.9.-tillgang-till-betalkonto/).
Samtliga32exakta referenser/URL:er och de övriga källorna finns i den lokala
evidensfilen. Inga privata identifierare eller råreferat lagras i bedömningen.
