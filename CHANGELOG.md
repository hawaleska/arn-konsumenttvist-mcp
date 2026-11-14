# CHANGELOG

## 1.0.5 — lokal kandidat, inte publicerad

Ägarbeslutet om avgränsad redaktionell förberedelse gäller endast arbetsmetoden.
Det godkänner inte nya innehållsposter, drift eller publicering. De 183 nya
poster som utvärderats är fortfarande pending.

- reviewed_index är säkert standardläge: endast individuellt godkända hashbundna poster, utan nätverks-/PDF-fallback. Det separata official_html-läget är inte godkänt för offentlig drift.
- Hashfel och pending-poster förblir spärrade; godkända Vanliga-fall-källor kan märkas ärendespecifikt.
- Ägargodkänd avgränsad redaktionell arbetsform registrerad; inga nya innehålls- eller driftgodkännanden följer automatiskt.
- `arn_search` avvisar blank fråga, relevanssorterar resultat och lämnar högst 20 per svar. Bakåtkompatibel frivillig cursor fortsätter genom hela matchmängden för samma godkända snapshot; varje sida räknas som ett vanligt anrop enligt oförändrad kvot. Ännu endast lokal implementation.

- 45 individuellt källkontrollerade Vanliga-fall-referenser integrerade som särskild källtyp.
- 186 unika referenser verifierade tillsammans med 141 vägledande översiktsträffar, utan dubbletter.
- Innehållshash, källtyp och snapshotdatum skyddar nya katalogen utan att utge den för godkänd lästext.
- Dold bortfiltrerad kontext används inte längre för matchning; känd fallreferens kan hämtas utan ny helsida.

- Separat officiell HTML-sökadapter utan PDF, med snäva värd-/sökvägs-/redirectgrindar.
- Bredare källutdrag skiljs från hashgodkända lästexter och okända uppgifter.
- Källa, länktyp, faktisk källtillgänglighet och partiella fel redovisas.
- Robotsregler respekteras före databas/översiktsanrop; ingen kringgång.
- Befintlig återkallelsejournal används även för breda ärendereferenser.
- Ingen ändring av OAuth, betalning, priser, kvoter eller befintlig 1.0.4-drift.


## 1.0.4

- Individuellt granskat, växande bibliotek av HTML-sammanfattningar utan ARN-livefallback eller PDF-hämtning.
- Alla åtta MCP-verktyg och befintliga argument/svarsfält bevarade; okända uppgifter uppfinns inte.
- Hashbundna godkännanden, återkallelsejournal och separat ankare mot återaktivering från äldre innehållskopia.
- Förhandsinformation, krypterad ångerfunktion och varaktig avtalsbekräftelse via Ubuntu utan kundretur.
- Nya betalda avtal inväntar bekräftelseacceptans; osäkra sändutfall omsänds inte blint.
- Kontobundna rättighets-/kopiespärrar och skyddad manuell operatörshantering.
- Omgivande blanksteg i ärendereferenser hanteras som i tidigare klient; säkra läsfelsdiagnoser.
- Kontaktadresser visas utan avkodningsskript och utan att CSP försvagas.
- Offentlig svensk/engelsk integritetsinformation och kontofri rättighetskanal.

10 fria användningar, 59 SEK/månad och 590 SEK/år bevaras. Tidigare godkända
R2-/R11-avvikelser består. R11:s installerade betalningsverifiering ändras inte.
Inga verkliga PayPal-debiteringar eller automatiska raderingar ingår i verifieringen.
Kod och innehåll införs genom separata hashbundna paket; detta dokument bevisar
inte i sig en GitHub-release, tagg eller Registry-publicering.
