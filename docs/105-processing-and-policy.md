# 1.0.5 — mottagning, kontrollerat index och avslutad artikel 6/14-prövning

Datum: 2026-11-13. Kodbas: `8284eee9e162840044cd1bcffaf426ac8395a0fd`.
Detta ersätter den föregående bedömningen i samma fil. Ett konkret fel i lokal
företagsrollsmaskering har korrigerats och snävt testats. Inga aktiva poster,
produktionskonfigurationer eller produktomfattning har ändrats.
ARN:s mejlsvar är inte ett generellt väntkrav. 1.0.4:s trepostbeslut står kvar.

## Senaste ställningstagande efter individuell prövning

Detta ersätter tidigare generella slutsatser om att en blandad
källa måste minimeras av någon annan före Qysleys mottagning. Det är ett
alternativ, inte ett generellt rättsligt krav. Blandat HTML-innehåll är inte
automatiskt förbjudet att ta emot. Faktisk personanknytning, uppgiftskategori,
ändamål och tillämpligt stöd måste prövas för respektive behandling.

**Konkret väg framåt:** avgränsad redaktionell förberedelse och faktakontroll,
följd av ett lokalt index med individuellt godkända publiceringsfält. Inga
råa HTML-/PDF-flöden till användarna. Redaktionell förberedelse och den senare
ordinära indexdriften är skilda behandlingar och behöver inte ha samma stöd.
Att förberedelsen kan omfattas av ett undantag godkänner inte all publicering.

### Begränsad förberedelse: verkligt stöd och dess gränser

**Bindande rätt:** GDPR artikel85 tillsammans med 1kap.7§ andra stycket
dataskyddslagen kan omfatta verklig journalistisk/redaktionell behandling.
EU-domstolens C-199/24, ECLI:EU:C:2026:564, punkterna66–73, klargör att detta
även kan omfatta nödvändig förberedelse och uppgifter som väljs bort. Det är
inte nödvändigt att allt mottaget material sedan blir publicerbart. Domen
gäller begreppet journalistiska ändamål; nödvändighet/proportionalitet för
respektive derogation ska fortfarande prövas, särskilt enligt punkt70.

Den aktuella förberedelsen kan knytas till ett verkligt redaktionellt ändamål:
att kontrollera, välja och bearbeta offentlig konsumenträttslig information för
begripliga källhänvisade rättsfallsreferat, inte sammanställa personprofiler.
Den individuella läsningen och de faktiska textkorrigeringarna i detta arbete
är konkreta redaktionella moment, inte bara ett namn på en automatisk skrapa.
Betalning eller MCP som medium utesluter inte journalistik. En osorterad
sökmotor, leverans av råa handlingar eller en policy utan faktisk tillämpning
uppfyller däremot inte automatiskt domens krav. IMYRS2022:2 och senare
C-199/24 ska läsas tillsammans; domen har företräde vid konflikt.

**Bedömning, inte ägarens redan fattade beslut:** detta är en konkret och
rättsligt underbyggd möjlig grund för DEN BEGRÄNSADE förberedelsen, förutsatt
att ägaren faktiskt åtar sig och tillämpar följande redaktionella arbetsform:

- Urval och redigering styrs av konsumentnytta, rättslig relevans, saklighet
  och skydd för privatlivet, inte efterfrågan på uppgifter om enskilda.
- Sakpåståenden kontrolleras mot officiell HTML. Påståenden från parter
  skiljs från ARN:s konstateranden och rättsliga slutsatser; obekräftade
  brottsmisstankar beskrivs inte som sanna eller som fällande domar.
- Relevant yrkesetik tillämpas i praktiken: källkritik, försiktig identifiering,
  integritetshänsyn, rättelser och möjlighet att bemöta fel. Ingen anslutning
  till MO/MEN eller journalistbehörighet påstås ha verifierats eller vara ett
  automatiskt formkrav. Att endast underteckna dessa ord räcker inte.
- Bara tillåtet offentligt HTML-urval inom uppdraget tas emot, under ett
  avgränsat granskningspass. Ingen databasomgång i strid med åtkomstspärr,
  PDF, privat aktinsamling, personsökning, onödig råcache eller råtextlogg.
- Den tillfälliga behandlingen begränsas till kontroll, urval och minimering.
  Publicering prövas separat. Säkerhet och GDPR:s rättsmedel tas inte bort.

Ägaren behöver fastställa att detta är den FAKTISKA verksamheten, ansvarig
operatör/redaktör och den dokumenterade nödvändighetsavgränsningen. Detta är
det konkreta nya beslutet; inte ett allmänt tillstånd att kalla projektet
journalistik. Modellen kan användas utan ARN:s mejlsvar, men ingen dom eller
myndighet har förhandsklassificerat just Qysleys behandling.

För ordinär förberedande behandling kan artikel6.1f användas med nedanstående
avvägning. För identifierbara9/10-uppgifter räcker inte6.1f ensam. Om ovanstående
redaktionella förutsättningar inte är uppfyllda måste annat faktiskt tillämpligt
stöd visas eller en redan tillåtet minimerad källa användas. Artikel9.2e kräver
mer än ARN:s publicering;9.2f/5§ kompletteringsförordningen kräver anknytning och
nödvändighet till konkreta rättsliga anspråk, inte hypotetiska användares behov.
Allmän GDPR-efterlevnad skapar inte automatiskt ett undantag från artikel9.

### Individuellt resultat: 186 referenser, inte automatiskt 154 godkännanden

Fullständig posttabell: `105-individual-index-review.md`.
Exakta föreslagna fält, ursprungshash, ny fälthash och skäl finns i den privata
`review-local/INDIVIDUAL-INDEX-DECISIONS.json`. Detta är INTE approvals.json.

| Resultat | Antal | Vad det betyder |
|---|---:|---|
| Tidigare exakt godkända1.0.4-texter | 3 | Gamla versioner/hashar bevaras; längre liveutdrag är inte därmed godkända |
| Nya ordinära fältversioner som kan godkännas villkorat | 146 | Individuellt lästa/prövade, inklusive9 omformulerade tidigare flaggor och7 utförda privata textkorrigeringar; kräver fastställd förberedelsemodell och artikel6/14-beslut |
| Nuvarande innehåll kräver särskild prövning/stöd eller revidering | 37 | Inte37bevisat olagliga fall; inte godkända för särskild uppgiftsbehandling/publicering |
| Ärenden som visats behöva uteslutas permanent i alla former | 0 | Enskilda fält kan behöva utelämnas; ingen permanent helärendeuteslutning har styrkts eller genomförts |

Alla154tidigare synliga texter lästes individuellt, inte bara genom regex.
För32tidigare innehållsflaggor återanvändes och preciserades de riktade
källfynden. Fjorton ytterligare riskkontexter hittades bland flaggfria texter,
bl.a. hudskador och konkreta bedragar-/hotförfaranden. Nio gamla ord-/sidflaggor
kunde ersättas med ordinära juridiska kärnfält efter separat källprövning.
Arbetet innehåller inte ett försök att identifiera de verkliga privatpersonerna.

**37posters gräns:** identifierbara hälso-/brottsuppgifter får inte publiceras
utan tillämpligt stöd. För vissa poster återstår kvalificering/identifierbarhet,
inte ett konstaterat förbud. En journalistisk förberedelsegrund godkänner inte
deras utgående fält. Dessa behöver antingen en särskilt dokumenterad nödvändig
och proportionerlig redaktionell publiceringsbedömning, annat särskilt stöd,
eller en individuellt kontrollerad textversion som inte längre behandlar den
aktuella särskilda uppgiften. En sådan ändrings påverkan på juridisk nytta ska
anges före omfattningsbeslut. Inga37poster har tagits bort ur kandidaten.

Faktiskt korrigerat i PRIVATA förslag: två felaktiga företagsroller, ett
gemensamt tvåärendereferat som annars riskerade fel utgångskoppling, och fyra
texter med onödiga kalender-/familje-/registrerings-/hushållsdetaljer. Ett minimalt skydd för uttryckliga företagsroller har även införts i den lokala
HTML-minimeringen. Gamla godkännanden och de publicerade treposterna är orörda. Företagsrollfelen
visar varför regex inte får fungera som slutgodkännande.

### Rättsliga krav respektive våra val av skydd

| Rättsligt krav | Vald eller föreslagen praktisk åtgärd — inte en egen GDPR-regel |
|---|---|
| Tillämpligt stöd och ansvarsskyldighet | Exakta post-/fältbeslut och hashmanifest; GDPR föreskriver inte ett visst JSON-format eller manuell signering av varje post |
| Minimering, riktighet och nödvändighet | Lokalt index, redaktionell urvalsgranskning och ingen råhämtning vid sökning; inte ett generellt lagkrav att aldrig ta emot blandad HTML |
| Särskilda uppgifter hanteras enligt tillämpliga regler | Separata37postbeslut; en keywordflagga är endast granskningshjälp |
| Säkerhet och rättigheter | Befintliga pins, separata skriv-/läsroller, återkallelsejournal och ankare; behållna verifierade arkitekturval |
| Lagring får inte vara obehövlig | Redan ägarbeslutad relevans/stöd och minst årlig omprövning; GDPR kräver inte exakt12månader för varje datakategori |
| Faktiskt riktiga och rättade uppgifter | Föreslagen veckovis källavstämning och uppdateringskö; intervallet är ett driftförslag, inte en ny rättslig tidsfrist |

### Nya och rättade referat — löpande bred sökning

1. Ett separat operatörssteg kontrollerar de tillåtna HTML-källorna; inte varje
   användarsökning. Förslag: veckovis och vid kännedom om rättelse/nytt material.
   Robot-/åtkomstregler kontrolleras då; inga spärrar kringgås.
2. Discovery ger nya ärendereferenser och ändrade källavsnitt. Gemensamma
   flerärendereferat hålls samman i källbeviset men mappas uttryckligt per ärende.
   Inga nya referenser räknas som publicerbara innan de är kontrollerade.
3. Spara källa, källkontrolldatum, hash för kontrollerat underlag och föreslagna
   minimerade fält i STAGING. Inte råmaterial i publikt index eller loggar.
4. Jämför mot föregående indexversion: ny, ändrad, oförändrad eller borttagen
   vid källan. Ändrade bytes får inte ärva gammalt innehållsgodkännande.
5. Pröva samma artikel6/14- och vid behov9/10-/redaktionella villkor. Samma
   operatörsrutin kan användas för en batch; ingen ny serverkod per nytt fall.
6. Efter separat införandebeslut publiceras ett atomärt verifierat snapshot med
   ny godkännandepin. Aktuell journal/ankare bevaras. En återkallelse kan inte
   kringgås genom att öka versionen eller återställa gammal innehållsbackup.
7. En konstaterat felaktig eller otillåten redan publicerad post spärras enligt
   befintlig rutin under rättelseprövningen. Att ARN tar bort en länk är däremot
   en granskningssignal, inte automatiskt bevis att alla tidigare referat är fel.

Användarna får ett växande versionsbundet urval med synligt kontroll-/snapshot-
datum. Ny ARN-publicering är inte omedelbart tillgänglig före granskning.
Ingen automatisk full historisk databasåtkomst påstås. Ingen fast gräns på
tre,149eller186införs. De åtta verktygen och betalningsmodellen behöver inte
ändras för varje uppdatering. Uppdateringsrutinen är förberedd, inte driftsatt.

### Konkret beslut som nu återstår

Fastställ eller avvisa den avgränsade REDAKTIONELLA FÖRBEREDELSEMODELLEN ovan,
inklusive faktiskt redaktörsansvar och etik/faktakontroll. Det är en genomförbar
alternativ väg till uppströmsminimering. Därefter kan de146exakta ordinära
fältversionerna godkännas som en hashbunden batch med det förberedda6/14-beslutet.
Tre gamla versioner kvarstår. De37andra behöver sin separata publiceringsprövning;
ingen minskning av omfattningen är föreslagen som redan beslutad.

Nya primärkällor: [C-199/24,punkterna66–77](https://juris.curia.europa.eu/juris/document/document.jsf?docid=313495&doclang=en),
[dataskyddslagen1kap.7§](https://data.riksdagen.se/dokument/sfs-2018-218.html),
[IMYRS2022:2](https://www.imy.se/globalassets/dokument/rattsligt-stallningstagande/imyrs-2022-2-undantaget-for-journalistiska-andamal.pdf).
För inköp av läkemedel är [C-21/23,punkterna84–88](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:62023CJ0021)
relevant; det krävs inte en utskriven diagnos för att en koppling kan avslöja
hälsa. [Publicitetsreglerna](https://medieombudsmannen.se/det-har-ar-medieombudsmannen/publicitetsreglerna-grunden-i-det-medieetiska-systemet/)
är yrkesetiska regler, inte självständig GDPR-grund eller bevis för MO-anslutning.

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

## Införandestatus och testbelägg

Förberedelsemodellen är beslutsfärdig, men varken ett nytt rättsligt beslut,
ett färdigt aktiverat index eller ett nytt installationsmandat har utfärdats.
Det är inte längre korrekt att beskriva uppströmsminimering som den enda vägen.
Det konkreta ägarbeslutet gäller verklig redaktionell förberedelse enligt ovan,
inte att bortse från artikel9/10 eller kalla en sökmotor journalistik.

Efter detta kan exakt146ordinära nya fältförslag fastställas som en batch med
artikel6/14-beslut.37andra fältversioner behöver egen publiceringsprövning;
ingen permanent uteslutning eller minskad produktomfattning har genomförts.
Alla åtta verktyg, priser, kvoter, Auth och1.0.4förblir bevarade.

Företagsrollskorrigeringen avser enbart `_minimized_excerpt` i arn_html_search.py.
Fyra syntetiska regressionsfall lades till befintliga test_broad_html.py.
Berörd fil:57/57PASS på Windows och Linux, Python3.14.4/MCP2.3.0. Ingen
allmän testomkörning; tidigare fulla Windows396+4 och Linux398+4 är basbelägg,
inte en påstådd ny full CI-körning. Ingen GitHub-push har gjorts.

Policyförslaget i `privacy-105-index-draft.md` har kompletterats med den
avgränsade redaktionella förberedelsen. Leverantörer, överföringar, kontofri
rättighetskanal och redan beslutade retentionskriterier bevaras. Inga nya
lagringstider, gallringsmandat eller allmänna rättsliga undantag införs.

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
