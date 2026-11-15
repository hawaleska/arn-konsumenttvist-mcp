# CHANGELOG

## 1.0.5 — bredare granskad sökning

- Produktionsindex omfattar 175 hashgodkända sammanfattningar: 172 nya poster och de tre bevarade 1.0.4-posterna. Tre återförda versioner och åtta HOLD-poster är fortsatt spärrade.
- `reviewed_index` är produktionsläge. Endast godkända, aktuella och ej återkallade innehållsversioner kan lämnas ut; ingen live-HTML- eller PDF-fallback används.
- Söktäckningen är ett växande urval, inte hela ARN:s databas. Sammanfattningar är inte fullständiga beslut; okända datum och kategorier hittas inte på.
- `arn_search` avvisar tom fråga, relevanssorterar och returnerar högst 20 träffar per sida. En frivillig cursor fortsätter genom samma indexsnapshot; varje sida följer befintlig kvotdebitering per anrop.
- Alla åtta MCP-verktyg, befintliga abonnemang och priser, OAuth, PayPal, kvoter, rättighetsflöden och återkallelsekontroller bevaras.
- Källinventeringen innehöll 186 unika referenser: 141 från den vägledande beslutsöversikten och 45 från Vanliga fall, där de tre tidigare godkända posterna ingår i de 141. Inventeringsantal är inte sökbara poster.
- Officiellt HTML-sökformulär är inte automatiserat; robotregler och källgrindar respekteras. PDF/fulltext ligger utanför 1.0.5.
- GitHub Actions, den additiva installationen och produktionskontrollerna verifierades separat. Status för tagg, GitHub-release och Registry avgörs av publiceringshändelserna, inte av denna changelog.


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
