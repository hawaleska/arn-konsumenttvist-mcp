#1.0.5 — konkret behandlingsdelta och policyutkast

STATUS: lokal teknisk kandidat. Ingen ny rättslig grund, artikel14-dispens eller
publicering fastställs här.1.0.4:s tre exakta godkännanden förblir oförändrade.

## Ändamål och faktisk dataväg

Konsumentupplysning genom sökning i offentliga vägledande HTML-referat, med
ärendereferens, relevanta tillgängliga sakuppgifter och kontrollerbar officiell
källa. Inget personindex, ingen profilering som produktändamål, ingen PDF/LLM.

| Moment | Faktisk1.0.5-behandling | Stöd / återstående grind |
|---|---|---|
| Mottagen fråga | Befintlig autentiserad MCP-väg. Kort sakfråga i anropsminnet; kontakt-/personnummermönster avvisas, men namn/indirekt identifiering kan undgå upptäckt. Ingen ny querylogg. | Befintligt användar-/avtalsändamål återanvänds där relevant, artikel6.1b för nödvändiga kontouppgifter. Tredje personers uppgifter omfattas inte automatiskt. Användarinfo enligt13 behöver nytt käll-/överföringsavsnitt. |
| Vidarebefordran | I aktuellt tillåtet översiktsläge skickas inte frågan till ARN. Om databasens robotsregler senare medger åtkomst sänds minimerad fråga via dess HTTPS-formulär. Ingen kommersiell söktjänst. | Framtida queryöverföring till ARN måste beslutas/informeras särskilt; ARN är inte därmed Qysleys biträde. CDN/ursprungsserver ser nätverksmetadata. |
| robots/HTML-hämtning | Två fasta officiella värdar; databasens Disallow:/ innebär ingen automatisk databasfråga. Översiktens hela HTML-sida hämtas i minnet. | robots är inte en dom om rättsligt förbud, men en faktisk automatiseringsbegränsning som kandidaten respekterar. Ordinarie manuell åtkomst är inte bevis på tillstånd till automation. |
| Extraktion/minimering | Referenser, datum/kategori och publicerad sammanfattning extraheras. Script/knappar ignoreras, storlek2MiB, timeout5/12s, max5redirects. Kontaktmönster/kontextinitialer minimeras. Potentiellt känsligt utdrag hålls tillbaka. | Detta sker EFTER mottagandet av HTML. Filtreringen ger ingen artikel9/10-grund och ingen anonymitetsgaranti. |
| Lagring | Ingen diskcache, corpusimport, bakgrundsindexering eller ny databas. Sessioncookies/formdata och anropets minimerade träffar lever endast under begäran; rensas vid avslut. | Befintliga skyddade logg-/backup-/kontorutiner gäller. Ingen ny tidsfrist eller radering. OS-/SDK-/leverantörskopior är inte generellt verifierat frånvarande. |
| Sökning/utlämning | Källutdrag skiljs från hashgodkänd lästext. Ärendereferenser/källlänkar kan fortfarande identifiera indirekt. Nya träffar kan spridas via användarens MCP-klient. | Ändamåls-, nödvändighets- och riskavvägning enligt6.1f för utökat material krävs; trepostbeslutet räcker inte för141källreferenser. |

## Behandlingsspecifik artikel6.1f — förslag, inte fastställelse

Intresset är konkret konsumentnytta: fler relevanta rättsfrågor än treposter och
kontroll mot ursprungskällan. Referens och officiell källhänvisning är nödvändiga
för kontroll; känt datum/kategori behövs för filtrering. Namn, privata kontakter,
partssökning som personprofilering och exakt individuell livshistoria behövs inte.
Biblioteket ensamt ger inte jämförbar källtäckning. Den breda frågan är därför
funktionellt motiverad, men varje återgiven sakuppgift måste fortfarande behövas.

ARN-publicering kan ge viss förväntan om rättslig informationsanvändning, inte
obegränsad kommersiell sammanställning. MCP-sökbarhet, sammanhangsförlust och
vidarespridning ger tilläggsrisk utöver ARN:s publicering. Inloggning, kvot,
kortlivad bearbetning, neutrala fel, tydliga utdrags-/källfält och återkallelse
minskar risk; de eliminerar den inte. Vid automatiskt uppdaterad HTML går det
inte att av en tidigare trepostgranskning dra att alla nya texter har samma risk.
Positiv generell avvägning för utökad drift är därför INTE fastställd här.

## Artikel14 och artiklarna9/10 — exakta olösta frågor

141unika ärendereferenser kunde extraheras ur aktuell översikt; antal berörda
fysiska personer är inte därmed141och har inte fastställts. Minst20utdrag fick
konservativ innehållsflagga. Det är inte20konstaterade artikel9/10-fall. Exempel
på källkontext är indirekt identifierbar hälsa via ärendereferens och konkreta
bedrägeri-/brottshändelser. Generella laghänvisningar kan också ge falsk flagga.
Att hålla tillbaka utdraget hindrar inte redan skedd mottagning av hela råsidan.

Före drift behövs en sakligt underbyggd bedömning av om denna mottagna kontext
faktiskt är identifierbara9/10-uppgifter, och i så fall tillämpligt särskilt stöd
eller en källa som minimeras före Qysleys mottagande.9.2f kan inte antas för alla
MCP-användare;9.2e följer inte av att ARN publicerat texten. Artikel6.1f ensam
räcker inte för9/10. Ingen extern myndighetskontakt har initierats.

Befintlig14.5b-prövning och offentliga rättighetskanal kan återanvändas som metod,
inte som automatisk dispens för nya poster. Utökad prövning måste fastställa
vilka personer som kan beröras, faktiska kontaktmöjligheter i de relevanta
uppgifterna, arbetsinsats/ytterligare identifieringsbehandling, MCP-tilläggsrisk,
informationsfrist före första utlämnande och alternativa skydd. Den generella
policytexten ensam ersätter inte detta. Artikel11 är ingen14-dispens.

Ingen separat tillåtelse till återanvändning av hela referatdatabasen är styrkt.
Tidigare26a§-underlag kan användas för offentliga myndighetstexter där dess
förutsättningar är uppfyllda; det är inte ett generellt tillstånd till åtkomst,
personuppgiftsbehandling eller återgivning av tredje mans skyddade material.

## Publiceringsutkast — tillägg till befintlig SV/EN-policy

Följande tillägg är INTE publicerat och får inte ersätta gällande policy ännu:

”En planerad utökad version söker också i ARN:s offentliga HTML-material.
Sökträffar kan vara källutdrag som Qysley inte har godkänt som bibliotekstext.
De visar tillgänglig ärendereferens, datum/kategori och officiell källhänvisning.
En översiktslänk är inte en ärendespecifik länk. Ingen rå PDF hämtas. Rå HTML och
sökträffar behandlas tillfälligt i minnet utan ny corpuslagring. Frågan matchas
lokalt mot beslutsöversikten. Om databassökning senare införs skickas frågan
till ARN; den vägen är för närvarande spärrad av robotsregler. Skriv inte namn,
kontaktuppgifter, hälsouppgifter eller andra privata uppgifter i frågan.
Källmaterial kan fortfarande vara indirekt identifierande. Rättigheter och
invändningar kan utövas utan konto via arn-privacy@qysley.se.”

FÖRE PUBLICERING: fastställ grund/14-väg/särskilt9/10-stöd eller tillåten annan
källa; ange bara faktiskt aktiverade källor och lägg till slutlig mottagar-/frist-
och undantagsinformation. Övriga ansvarig-/leverantörs-/rättighets-/retentions-
avsnitt i den godkända policyn ska bevaras. Inga nya leverantörsavtal antas.

## Konkret beslutspunkt

Teknisk kandidat finns; den är INTE rättsligt/driftmässigt aktiveringsgodkänd.
För större täckning än aktuell översikt krävs en tillåten automatiserad väg till
referatdatabasen, alternativt annan officiell HTML-feed/API med dokumenterad
faktisk täckning. Ingen sådan extra feed har verifierats. Kontakta inte ARN utan
nytt mandat. Enbart översiktsläget omfattar141referenser vid provet, inte hela
ARN-databasen; att godta det som en etapp är ett uttryckligt produktbeslut.

Källor (bindande lag respektive vägledning skiljs åt):
- GDPR, särskilt4.1/4.2,5,6.1b/f,9,10,13,14.3/14.5b,21/25:
  https://eur-lex.europa.eu/eli/reg/2016/679/oj/swe (bindande rätt).
- IMY intresseavvägning: https://www.imy.se/verksamhet/dataskydd/det-har-galler-enligt-gdpr/rattslig-grund/intresseavvagning/ (vägledning).
- EDPB/WP260rev01,61–64: https://www.edpb.europa.eu/system/files/2023-09/wp260rev01_en.pdf (befintligt granskat vägledningsunderlag).
- CNIL: https://cnil.fr/fr/ia-informer-les-personnes-concernees (kompletterande tolkningsstöd, inte individuellt beslut eller AI-träning i denna tjänst).
- Faktisk källa: https://www.arn.se/om-arn/vagledande-beslut/ och
  https://adokweb.arn.se/robots.txt (läst2026-11-13). Provbelägg i review-local/.
