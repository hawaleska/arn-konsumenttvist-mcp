# Individuell indexprövning — 1.0.5 textutkast

**Utkast för innehållsgranskning, 2026-11-14. Inget av följande är godkänt för exponering.** De föreslagna källorna och sammanfattningarna bygger på aktuellt offentligt ARN-HTML. Hasharna binder exakt stagingpost och redaktionella fält; hash är inte juridiskt godkännande.


**Uppdaterad avvägning 2026-11-14:** För de 175 ordinära förslagen finns nu en per-post `article6_public_output_assessment_20261114` i `review-local/INDIVIDUAL-INDEX-DECISIONS.json`, som kompletterar respektive `individual_reason` med ändamål, nödvändighet, faktorer för/emot och ett uttryckligt icke-godkännande för offentlig utlämning. Det är en beslutsnotering, inte innehålls- eller juridiskt godkännande. Åtta särskilda poster är fortsatt HOLD och tre tidigare exakta 1.0.4-versioner påverkas inte. Standard-runtime är lokalt ändrad till fail-closed `reviewed_index`; inget live- eller PDF-fallback sker i det läget.

## Rättslig åtskillnad

**Redaktionellt förarbete:** Ägarens metodbeslut `ARN-105-OWNER-20261113-EDITORIAL-PREPARATION-001` medger den avgränsade arbetsformen. GDPR artikel 85 och dataskyddslagen 1 kap. 7 § kan vara relevanta endast när varje moment faktiskt sker för journalistiska ändamål och en derogation är nödvändig och proportionerlig. C-199/24, punkterna 66–73, stöder att nödvändiga förberedelser som urval och redigering kan omfattas, även material som väljs bort; det avgör inte att just Qysleys varje mottagning uppfyller villkoren. Här gjordes sakgranskning, parafrasering och minimeringsbeslut mot officiella ARN-HTML.

**Offentlig sökning och utlämning:** Detta är en separat behandling. De 29 vanliga utkasten innehåller fortfarande ärendenummer, sakuppgifter och källa som kan länka tillbaka till registrerade; de är inte verifierat anonyma. För offentlig exponering måste tillämplig rättslig grund och artikel 14-väg styrkas. Ingen generell artikel 14.5 b-derogation är fastställd här. För de åtta särskilda fallen kan länkningen fortsatt återknyta ett utkast till artikel 9/10-kontext; dessa står därför på HOLD tills en postspecifik rättslig bedömning eller ytterligare säker minimering har granskats.

## Källkontroll och hashbegränsning

Officiella ARN-sidor kontrollerades 2026-11-14. För varje rad finns exakt käll-URL, ärendereferens och kontrollbelägg i `review-local/INDIVIDUAL-INDEX-DECISIONS.json`. Nuvarande live-HTML-svar sparades inte; det finns därför ingen hash av live HTTP-svaret. `source_excerpt_snapshot_sha256` i besluts-JSON binder den tidigare lokala excerpten före omskrivning och märks uttryckligen som sådan. Utkastets nya innehålls- och fälthashar finns i `review-local/index-proposal/trace.json` och i tabellerna nedan.

## A. 29 färdiga textutkast — lättläst innehållsgranskning

**Alla 29 är förslag, inte godkända publiceringsposter.** Ärendenummer och länk gör inte texten anonym. Fält som saknas i ARN-översikten visas som okända; inget ärendeutfall har fyllts i genom antagande. Hashpar finns i det separata registret efter utkasten.

### 1. 2017-07814 — Bank

**Föreslagen text:** Referatet omfattar två ärenden om bedragare som utgav sig för att ringa från bank; i det ena användes ett manipulerat nummer som såg ut att tillhöra banken. Kontohavare vilseleddes att legitimera sig. ARN prövade kontohavarens ansvar för transaktioner som bedragare genomfört. Översikten beskriver två skilda händelseförlopp i samma referat; den anger inte ett separat utfall för detta delärende. Utgången för det enskilda delärendet framgår inte av den offentliga översiktstexten.

**Källa:** [ARN:s vägledande översikt (översiktskälla, inte ärendespecifik länk)](https://www.arn.se/om-arn/vagledande-beslut/)

**Osäkerhet:** Konkret bedragar-/bankidentitetsförfarande; gemensamt referat nämner även annat ärende. Följande fält är inte verifierade i det använda referatet: utfall.

**Status:** väntar på innehållsbeslut och separat rättslig grund för offentlig sökning/utlämning.

### 2. 2017-10285 — Bank

**Föreslagen text:** Referatet omfattar två ärenden där personer som utgav sig för att arbeta på bank ringde och fick kontohavare att lämna ut svarskoder; pengar fördes därefter bort. Frågan gäller kontohavarens ansvar för transaktioner som bedragare utfört efter att koder lämnats ut. Översikten anger inte separata utfall för delärendena. Utgången för detta delärende framgår inte av den offentliga översiktstexten.

**Källa:** [ARN:s vägledande översikt (översiktskälla, inte ärendespecifik länk)](https://www.arn.se/om-arn/vagledande-beslut/)

**Osäkerhet:** Konkret bedragar-/kodförfarande; gemensamt referat nämner även annat ärende. Följande fält är inte verifierade i det använda referatet: utfall.

**Status:** väntar på innehållsbeslut och separat rättslig grund för offentlig sökning/utlämning.

### 3. 2018-06551 — Bank

**Föreslagen text:** En konsument förmåddes att föra över pengar efter att en bedragare skapat intryck av en felaktig betalning. När kontohavaren själv godkände och signerade överföringen i syfte att återföra pengar ansågs transaktionen samtyckt till; reglerna om obehöriga transaktioner var därför inte tillämpliga. Den offentliga översikten anger rättsbedömningen men inte uttryckligen den slutliga rekommendationen.

**Källa:** [ARN:s vägledande översikt (översiktskälla, inte ärendespecifik länk)](https://www.arn.se/om-arn/vagledande-beslut/)

**Osäkerhet:** Stöld/bedrägerihändelse eller utsatt konsument beskrivs; inte en brottmålsdom. Faktisk identifierbarhet och tillämpligt undantag/derogation är inte automatiskt fastställda.

**Status:** väntar på innehållsbeslut och separat rättslig grund för offentlig sökning/utlämning.

### 4. 2018-12086 — Bank

**Föreslagen text:** Ett bankkort försvann medan konsumenten förvarade det nära sig. Kortet användes därefter med kod; banken ansåg att konsumenten varit grovt oaktsam. Att en kod observeras i en normal betalningssituation innebär inte automatiskt grov oaktsamhet. ARN fann inte visat att konsumenten brustit i normal aktsamhet vid betalningen. Banken rekommenderades ersätta förlusten utom lagstadgad självrisk om 400 kr.

**Källa:** [officiell ärendesida](https://www.arn.se/vanligafall/4.4.-stulet-bankkort--tjuven-sett-pinkoden-vid-ett-tidigare-kop/)

**Osäkerhet:** En konkret stöld/bedrägerihändelse eller ett påstått inbrott kopplas till konsumenten. Faktisk identifierbarhet och tillämpligt undantag/derogation är inte automatiskt fastställda. Följande fält är inte verifierade i det använda referatet: datum.

**Status:** väntar på innehållsbeslut och separat rättslig grund för offentlig sökning/utlämning.

### 5. 2019-04475 — Försäkring

**Föreslagen text:** Ärendet gäller ett reseförsäkringsvillkor som uteslöt avbokningsersättning när avbokningsorsaken hade samband med graviditet eller förlossning. Den offentliga översikten formulerar en fråga om villkorets giltighet och diskriminering. Den visar inte att någon part faktiskt haft ett visst hälsotillstånd och anger inte bedömningens slutresultat. Slutligt utfall är okänt från den offentliga översiktstexten.

**Källa:** [ARN:s vägledande översikt (översiktskälla, inte ärendespecifik länk)](https://www.arn.se/om-arn/vagledande-beslut/)

**Osäkerhet:** Försäkringsvillkor om graviditet/förlossning; faktisk graviditet hos en viss part fastställs inte av översiktstexten. Faktisk identifierbarhet och tillämpligt undantag/derogation är inte automatiskt fastställda. Följande fält är inte verifierade i det använda referatet: utfall.

**Status:** väntar på innehållsbeslut och separat rättslig grund för offentlig sökning/utlämning.

### 6. 2019-16037 — Försäkring

**Föreslagen text:** Krav på hemförsäkringsersättning avsåg egendom som påstods ha stulits vid inbrott. Bolaget godtog inbrott men bestred att det begärda innehavet var styrkt. Den försäkrade måste visa både innehav och värde. Bilder på ytterdörren utan kompletterande dokumentation visade inte att det påstådda inbrottet inträffat på det sätt som krävdes för försäkringsfall. Kravet avslogs.

**Källa:** [officiell ärendesida](https://www.arn.se/vanligafall/5.1.-forsakringsfall/)

**Osäkerhet:** En konkret stöld/bedrägerihändelse eller ett påstått inbrott kopplas till konsumenten. Faktisk identifierbarhet och tillämpligt undantag/derogation är inte automatiskt fastställda. Följande fält är inte verifierade i det använda referatet: datum.

**Status:** väntar på innehållsbeslut och separat rättslig grund för offentlig sökning/utlämning.

### 7. 2019-19154 — Bank

**Föreslagen text:** Koder hade lämnats ut till en bedragare, men transaktionen genomfördes av någon annan än kontohavaren. Att kontohavaren möjliggjort ett förfarande genom att lämna ut koder innebar inte i sig att den transaktion som en annan person utförde var behörig enligt reglerna om obehöriga transaktioner. Översikten klassificerar transaktionen som obehörig; bankens slutliga ersättningsskyldighet framgår inte här.

**Källa:** [ARN:s vägledande översikt (översiktskälla, inte ärendespecifik länk)](https://www.arn.se/om-arn/vagledande-beslut/)

**Osäkerhet:** Koder lämnas till en beskriven bedragare; brottskontext är uttrycklig.

**Status:** väntar på innehållsbeslut och separat rättslig grund för offentlig sökning/utlämning.

### 8. 2020-02384 — Bank

**Föreslagen text:** En konsument lurades att själv godkänna en betalning efter kontakt från bedragare. Eftersom konsumenten själv höjt betalgräns och godkänt betalningen med e-legitimation var transaktionen inte obehörig enligt betaltjänstlagen. Bedrägeriet ändrade inte den bedömningen. Krav mot banken avslogs.

**Källa:** [officiell ärendesida](https://www.arn.se/vanligafall/4.6.3.-uppringd-av-bedragare-och-vidarekopplad-till-banken--anmalaren-lurats-att-sjalv-godkanna-transaktioner/)

**Osäkerhet:** En konkret stöld/bedrägerihändelse eller ett påstått inbrott kopplas till konsumenten. Faktisk identifierbarhet och tillämpligt undantag/derogation är inte automatiskt fastställda. Följande fält är inte verifierade i det använda referatet: datum.

**Status:** väntar på innehållsbeslut och separat rättslig grund för offentlig sökning/utlämning.

### 9. 2020-16821 — Bank

**Föreslagen text:** Konsumenten godkände själv en betalning efter att ha blivit vilseledd i samband med en försäljning. En transaktion som kontohavaren själv godkänt är inte obehörig enbart för att godkännandet skett efter bedrägeri. Banken hade enligt översikten inte skyldighet att stoppa en redan godkänd transaktion som ännu visades som reserverad. Banken rekommenderades inte ersätta transaktionen.

**Källa:** [officiell ärendesida](https://www.arn.se/vanligafall/4.6.1.-anmalaren-lurats-att-sjalv-swisha-pengar-till-en-bedragare/)

**Osäkerhet:** En konkret stöld/bedrägerihändelse eller ett påstått inbrott kopplas till konsumenten. Faktisk identifierbarhet och tillämpligt undantag/derogation är inte automatiskt fastställda. Följande fält är inte verifierade i det använda referatet: datum.

**Status:** väntar på innehållsbeslut och separat rättslig grund för offentlig sökning/utlämning.

### 10. 2020-19246 — Försäkring

**Föreslagen text:** Ett ersättningskrav för egendom som uppgavs ha stulits vid inbrott bestreds i fråga om innehav och värde. Den som begär ersättning måste styrka att egendomen innehafts och dess värde. Underlaget ansågs inte tillräckligt mot bolagets invändning. Kravet avslogs.

**Källa:** [officiell ärendesida](https://www.arn.se/vanligafall/5.2.2.-parterna-inte-overens-om-innehav-av-forlorad-eller-skadad-egendom/)

**Osäkerhet:** Bostadsinbrott och konsumentens ersättningskrav beskrivs trots utebliven regexflagga. Följande fält är inte verifierade i det använda referatet: datum.

**Status:** väntar på innehållsbeslut och separat rättslig grund för offentlig sökning/utlämning.

### 11. 2020-21153 — Bank

**Föreslagen text:** Obehöriga korttransaktioner genomfördes med fysisk kortinformation och kod. Konsumenten kunde inte förklara hur den som använde kortet fått kännedom om koden. ARN fann att koden måste ha varit förknippad med kortet eller på annat sätt tillgänglig tillsammans med det. När grov oaktsamhet föreligger är konsumentansvaret enligt betaltjänstlagen begränsat till 12 000 kr. Kravet på ersättning utöver det belopp banken redan betalat avslogs.

**Källa:** [officiell ärendesida](https://www.arn.se/vanligafall/4.3.-forloratstulet-bankkort--obehoriga-transaktioner-godkants-med-pinkod/)

**Osäkerhet:** Förlust/stöld och obehörig kortanvändning; måste skiljas från enbart avtalsrättslig oaktsamhet. Texten är förkortad; uppgift om osynlig utgång får inte fyllas i. Detta godkänner inte resten av källsidan. Följande fält är inte verifierade i det använda referatet: datum.

**Status:** väntar på innehållsbeslut och separat rättslig grund för offentlig sökning/utlämning.

### 12. 2020-21764 — Bank

**Föreslagen text:** Det officiella gemensamma referatet innehåller en sammanblandad inledning med text från ett annat fall. Den säkra delen gäller ett kortköp som registrerats med kortuppgifter och engångskod. ARN bedömde att kombinationen inte uppfyllde kravet på stark kundautentisering. Den bank som genomfört betalningen ansvarade därför för den obehöriga transaktionen oavsett om kunden varit grovt oaktsam. Banken skulle svara för transaktionen. Sakförlopp utöver den säkra delen återges inte.

**Källa:** [officiell ärendesida](https://www.arn.se/vanligafall/4.7.-kortkop-har-inte-godkants-pa-ett-sakert-satt/)

**Osäkerhet:** Konkret falskt bank-/låneföretagsförfarande. Källutdragets inledning är dessutom sammanblandad. Följande fält är inte verifierade i det använda referatet: datum.

**Status:** väntar på innehållsbeslut och separat rättslig grund för offentlig sökning/utlämning.

### 13. 2021-02178 — Bank

**Föreslagen text:** En konsument avsåg att göra en investering och signerade de omtvistade betalningarna själv, trots att en annan person fått fjärråtkomst till datorn. ARN bedömde att betalningarna genomförts med konsumentens samtycke. Ingen annan grund för bankens ersättningsskyldighet visades. Kravet avslogs.

**Källa:** [officiell ärendesida](https://www.arn.se/vanligafall/4.6.2.-investeringsbedrageri/)

**Osäkerhet:** En konkret stöld/bedrägerihändelse eller ett påstått inbrott kopplas till konsumenten. Faktisk identifierbarhet och tillämpligt undantag/derogation är inte automatiskt fastställda. Följande fält är inte verifierade i det använda referatet: datum.

**Status:** väntar på innehållsbeslut och separat rättslig grund för offentlig sökning/utlämning.

### 14. 2021-05878 — Försäkring

**Föreslagen text:** Ersättning begärdes efter att ett fordon förstörts vid stöld. Försäkringsvillkoren krävde att försäkringstagaren var verklig ägare och huvudsaklig brukare. Försäkringstagaren hade bevisbördan och måste styrka båda förhållandena. ARN ansåg inte att underlaget uppfyllde kravet. Kravet avslogs.

**Källa:** [officiell ärendesida](https://www.arn.se/vanligafall/5.3.-forsakrat-intresse/)

**Osäkerhet:** En konkret stöld/bedrägerihändelse eller ett påstått inbrott kopplas till konsumenten. Faktisk identifierbarhet och tillämpligt undantag/derogation är inte automatiskt fastställda. Följande fält är inte verifierade i det använda referatet: datum.

**Status:** väntar på innehållsbeslut och separat rättslig grund för offentlig sökning/utlämning.

### 15. 2021-12666 — Bank

**Föreslagen text:** En konsument skyddade inte sina personliga koder i samband med ett bedrägeri. ARN bedömde agerandet som grovt oaktsamt men inte särskilt klandervärt. Konsumenten skulle stå för endast en del av förlusten; exakt andel framgår inte av översiktstexten.

**Källa:** [ARN:s vägledande översikt (översiktskälla, inte ärendespecifik länk)](https://www.arn.se/om-arn/vagledande-beslut/)

**Osäkerhet:** Stöld/bedrägerihändelse eller utsatt konsument beskrivs; inte en brottmålsdom. Faktisk identifierbarhet och tillämpligt undantag/derogation är inte automatiskt fastställda.

**Status:** väntar på innehållsbeslut och separat rättslig grund för offentlig sökning/utlämning.

### 16. 2021-16194 — Bank

**Föreslagen text:** En falsk säkerhetslänk ledde till att svarskoder lämnades ut och obehöriga transaktioner genomfördes. ARN fann varken grov oaktsamhet eller särskilt klandervärt agerande. Banken rekommenderades ersätta förlusten med avdrag för den lagstadgade självrisken om 400 kr.

**Källa:** [ARN:s vägledande översikt (översiktskälla, inte ärendespecifik länk)](https://www.arn.se/om-arn/vagledande-beslut/)

**Osäkerhet:** Falsk banklänk och beskriven bedragare kopplas till konsumenten.

**Status:** väntar på innehållsbeslut och separat rättslig grund för offentlig sökning/utlämning.

### 17. 2021-18725 — Bank

**Föreslagen text:** En konsument vilseleddes i en kortbetalningssituation och en obehörig person fick senare tillgång till kortet och genomförde uttag. ARN fann varken grov oaktsamhet eller särskilt klandervärt agerande. Banken rekommenderades ersätta förlusten med avdrag för lagstadgad självrisk om 400 kr.

**Källa:** [ARN:s vägledande översikt (översiktskälla, inte ärendespecifik länk)](https://www.arn.se/om-arn/vagledande-beslut/)

**Osäkerhet:** Stöld/bedrägerihändelse eller utsatt konsument beskrivs; inte en brottmålsdom. Faktisk identifierbarhet och tillämpligt undantag/derogation är inte automatiskt fastställda.

**Status:** väntar på innehållsbeslut och separat rättslig grund för offentlig sökning/utlämning.

### 18. 2021-19593 — Bank

**Föreslagen text:** Kort och personlig kod skyddades inte tillräckligt i samband med ett bedrägeri. ARN bedömde agerandet som grovt oaktsamt men inte särskilt klandervärt. Konsumenten skulle stå för endast en del av förlusten; exakt andel framgår inte av översiktstexten.

**Källa:** [ARN:s vägledande översikt (översiktskälla, inte ärendespecifik länk)](https://www.arn.se/om-arn/vagledande-beslut/)

**Osäkerhet:** Stöld/bedrägerihändelse eller utsatt konsument beskrivs; inte en brottmålsdom. Faktisk identifierbarhet och tillämpligt undantag/derogation är inte automatiskt fastställda.

**Status:** väntar på innehållsbeslut och separat rättslig grund för offentlig sökning/utlämning.

### 19. 2022-01950 — Bank

**Föreslagen text:** Personliga koder skyddades inte tillräckligt i samband med ett bedrägeri. ARN bedömde agerandet som grovt oaktsamt men inte särskilt klandervärt. Konsumenten skulle stå för endast en del av förlusten; exakt andel framgår inte av översiktstexten.

**Källa:** [ARN:s vägledande översikt (översiktskälla, inte ärendespecifik länk)](https://www.arn.se/om-arn/vagledande-beslut/)

**Osäkerhet:** Stöld/bedrägerihändelse eller utsatt konsument beskrivs; inte en brottmålsdom. Faktisk identifierbarhet och tillämpligt undantag/derogation är inte automatiskt fastställda.

**Status:** väntar på innehållsbeslut och separat rättslig grund för offentlig sökning/utlämning.

### 20. 2022-02184 — Bank

**Föreslagen text:** Ett bankkort och dess personliga kod skyddades inte tillräckligt i samband med ett bedrägeri. ARN bedömde agerandet som grovt oaktsamt men inte särskilt klandervärt. Konsumenten skulle stå för endast en del av förlusten; exakt andel framgår inte av översiktstexten.

**Källa:** [ARN:s vägledande översikt (översiktskälla, inte ärendespecifik länk)](https://www.arn.se/om-arn/vagledande-beslut/)

**Osäkerhet:** Stöld/bedrägerihändelse eller utsatt konsument beskrivs; inte en brottmålsdom. Faktisk identifierbarhet och tillämpligt undantag/derogation är inte automatiskt fastställda.

**Status:** väntar på innehållsbeslut och separat rättslig grund för offentlig sökning/utlämning.

### 21. 2022-03446 — Bank

**Föreslagen text:** En person som utgav sig för att företräda banken fick konsumenten att lämna ut svarskoder; obehöriga transaktioner följde. ARN fann varken grov oaktsamhet eller särskilt klandervärt agerande. Banken rekommenderades ersätta förlusten med avdrag för den lagstadgade självrisken om 400 kr.

**Källa:** [ARN:s vägledande översikt (översiktskälla, inte ärendespecifik länk)](https://www.arn.se/om-arn/vagledande-beslut/)

**Osäkerhet:** En konkret person utger sig för att vara bankföreträdare och förmår konsumenten lämna koder.

**Status:** väntar på innehållsbeslut och separat rättslig grund för offentlig sökning/utlämning.

### 22. 2022-03828 — Bank

**Föreslagen text:** Under ett bedrägeri fick en annan person fjärråtkomst och betalningen genomfördes efter att nya autentiseringsmoment använts. ARN bedömde agerandet som grovt oaktsamt men inte särskilt klandervärt. Konsumenten skulle stå för endast en del av förlusten; exakt andel framgår inte av översiktstexten.

**Källa:** [ARN:s vägledande översikt (översiktskälla, inte ärendespecifik länk)](https://www.arn.se/om-arn/vagledande-beslut/)

**Osäkerhet:** Stöld/bedrägerihändelse eller utsatt konsument beskrivs; inte en brottmålsdom. Faktisk identifierbarhet och tillämpligt undantag/derogation är inte automatiskt fastställda.

**Status:** väntar på innehållsbeslut och separat rättslig grund för offentlig sökning/utlämning.

### 23. 2022-03987 — Bank

**Föreslagen text:** Personliga koder skyddades inte tillräckligt i samband med ett bedrägeri. ARN bedömde agerandet som grovt oaktsamt men inte särskilt klandervärt. Konsumenten skulle stå för endast en del av förlusten; exakt andel framgår inte av översiktstexten.

**Källa:** [ARN:s vägledande översikt (översiktskälla, inte ärendespecifik länk)](https://www.arn.se/om-arn/vagledande-beslut/)

**Osäkerhet:** Stöld/bedrägerihändelse eller utsatt konsument beskrivs; inte en brottmålsdom. Faktisk identifierbarhet och tillämpligt undantag/derogation är inte automatiskt fastställda.

**Status:** väntar på innehållsbeslut och separat rättslig grund för offentlig sökning/utlämning.

### 24. 2022-04140 — Bank

**Föreslagen text:** Personliga koder skyddades inte tillräckligt i samband med ett bedrägeri. ARN bedömde agerandet som grovt oaktsamt men inte särskilt klandervärt. Konsumenten skulle stå för endast en del av förlusten; exakt andel framgår inte av översiktstexten.

**Källa:** [ARN:s vägledande översikt (översiktskälla, inte ärendespecifik länk)](https://www.arn.se/om-arn/vagledande-beslut/)

**Osäkerhet:** Stöld/bedrägerihändelse eller utsatt konsument beskrivs; inte en brottmålsdom. Faktisk identifierbarhet och tillämpligt undantag/derogation är inte automatiskt fastställda.

**Status:** väntar på innehållsbeslut och separat rättslig grund för offentlig sökning/utlämning.

### 25. 2022-13993 — Bank

**Föreslagen text:** En konsument godkände en betalning under ett hot som innebar eller framstod som trängande fara. ARN bedömde att godkännandet under dessa omständigheter inte uttryckte samtycke enligt betaltjänstlagen; transaktionen var därmed obehörig. Den offentliga översikten anger klassificeringen men inte separat slutlig ersättningsrekommendation.

**Källa:** [ARN:s vägledande översikt (översiktskälla, inte ärendespecifik länk)](https://www.arn.se/om-arn/vagledande-beslut/)

**Osäkerhet:** Personanknutet hot/tvång vid transaktion; eventuell brottskvalificering måste bedömas.

**Status:** väntar på innehållsbeslut och separat rättslig grund för offentlig sökning/utlämning.

### 26. 2022-21906 — Bank

**Föreslagen text:** Bedrägeriet innefattade flera moment före en obehörig transaktion. ARN bedömde att konsumenten måste ha förstått att det fanns en risk för transaktionen; agerandet bedömdes som särskilt klandervärt. Slutlig ersättningsrekommendation framgår inte i det återgivna översiktsutdraget.

**Källa:** [ARN:s vägledande översikt (översiktskälla, inte ärendespecifik länk)](https://www.arn.se/om-arn/vagledande-beslut/)

**Osäkerhet:** Konkret falsk bankkontakt, fjärrstyrning och kontoöverföringar; inte bara generell rättsregel. Följande fält är inte verifierade i det använda referatet: utfall.

**Status:** väntar på innehållsbeslut och separat rättslig grund för offentlig sökning/utlämning.

### 27. 2022-22360 — Bank

**Föreslagen text:** Ett falskt sms ledde konsumenten till att följa instruktioner om en säkerhetsåtgärd och godkänna ett nytt autentiseringsmoment. ARN bedömde agerandet som grovt oaktsamt men inte särskilt klandervärt, särskilt mot bakgrund av en tydlig och kortfattad varning. Den tillgängliga översiktstexten anger inte slutlig ersättningsfördelning.

**Källa:** [ARN:s vägledande översikt (översiktskälla, inte ärendespecifik länk)](https://www.arn.se/om-arn/vagledande-beslut/)

**Osäkerhet:** Stöld/bedrägerihändelse eller utsatt konsument beskrivs; inte en brottmålsdom. Faktisk identifierbarhet och tillämpligt undantag/derogation är inte automatiskt fastställda. Följande fält är inte verifierade i det använda referatet: utfall.

**Status:** väntar på innehållsbeslut och separat rättslig grund för offentlig sökning/utlämning.

### 28. 2023-00686 — Bank

**Föreslagen text:** En konsument blev vilseledd av personer som utgav sig för att företräda banker; transaktionen föregicks av ett varningsmeddelande och ökad betalgräns. ARN bedömde agerandet som grovt oaktsamt men inte särskilt klandervärt. Även tillämpningen av reglerna på ett konto som öppnats utan samtycke prövades. Den offentliga översikten anger ingen slutlig ersättningsrekommendation.

**Källa:** [ARN:s vägledande översikt (översiktskälla, inte ärendespecifik länk)](https://www.arn.se/om-arn/vagledande-beslut/)

**Osäkerhet:** Konkret falsk bankkontakt och åtgärder för transaktioner; artikel10-kvalificeringen är separat. Följande fält är inte verifierade i det använda referatet: utfall.

**Status:** väntar på innehållsbeslut och separat rättslig grund för offentlig sökning/utlämning.

### 29. 2023-19612 — Motor

**Föreslagen text:** Efter ett distansköp utövades ångerrätten, men den köpta varan förlorades innan den återlämnades. Ångerrätten hindrades inte av att varan förlorats. Efter ånger beskrev ARN en vårdplikt och bedömde att konsumenten inte visat att hanteringen inte varit försumlig. Företaget fick kvitta skadestånd mot återbetalningskravet; konsumentens krav avslogs.

**Källa:** [ARN:s vägledande översikt (översiktskälla, inte ärendespecifik länk)](https://www.arn.se/om-arn/vagledande-beslut/)

**Osäkerhet:** Stöld/bedrägerihändelse eller utsatt konsument beskrivs; inte en brottmålsdom. Faktisk identifierbarhet och tillämpligt undantag/derogation är inte automatiskt fastställda.

**Status:** väntar på innehållsbeslut och separat rättslig grund för offentlig sökning/utlämning.

### Hashregister för de 29 utkasten

| Ärende | Innehåll SHA256 | Föreslagna fält SHA256 |
|---|---|---|
| 2017-07814 | `5278b0f9c710f3fdb70efc44eaa6c89412b24844e5c0b88bf03c791c38da5c5c` | `1beb9d187857c0c84f3c2b05aa93589c393b375a53fc6e7526780c6b938404e7` |
| 2017-10285 | `f13f48f418950b5c331d4fb006394ec4030f69c980dbda0bde5759213c51408c` | `b70b52a33155622653b366e5f1ba70b32ddfa239be6b3bb440c205ba2f6b6d76` |
| 2018-06551 | `4fc6faaf19ede8f4a96bb60a30b129b400034e136197184f19abe3c409e38628` | `28ee2a6ac93d2ed7747b2cfd18cfbb79f953eaf23ebaa7ef476e75cc4d9fbbc3` |
| 2018-12086 | `e81926f73ce3e9f976350d037a8695c5a341abf3a5d6767483876ff214f17d64` | `4c0827a871503baf4dd3cdfc183414d55dec34c4060bd6a6299d5869aa1e29f3` |
| 2019-04475 | `c17352ce4122857075ba2e1ab5a31c00fc2cc37f7dd9d7335239889d7818fa45` | `26bfd4037fa035115a28f66252e1ad7997ef0744a0056fbb9b98fe24f558ddaa` |
| 2019-16037 | `9be11e72dcbdad31de56a5984ecd84530fc6c3ace7ad4b6eb8834c3604bbc0a2` | `fd3eb64b3175ae6553a7c22fe9cfeb22eb0d77582154e6395fe5e96663902042` |
| 2019-19154 | `8ad5019a74e2ad3455208854e5987ff4e910d5918f91eb24f36c18f10be7f07e` | `e0e3425de2ae169f34441d6be4cafdef2d5611785a08bcec315ff4b5cb32bc1b` |
| 2020-02384 | `98dc941b6d1286a39e994d06cf13b4c6727406186476a86fc021c0970a836284` | `3a503c38510bced50a8865bcde0c2d03a32d2dbc9cb7e0fbffdd0be4ec6b09c6` |
| 2020-16821 | `c178b87c0e245d1a8127451af7a0c422f5e3555c4a5521d22076c610c35f4790` | `ae0375d574bcee7f778bb7170c5f85667f9dd621c95e1570cb4ff6bc0d000b5d` |
| 2020-19246 | `7c5adce5d9e51afe9602ada35d5d21b07454bb475839a62f5c20ad213dceafc9` | `c8db870f32ee05b4b035a9de283fc7fbe601b977ea53b8b37be1906451da5850` |
| 2020-21153 | `6bbdb44b31e1846e73f1d89c36f7fbc2df66477636fb36732a041a9b29ddd1f7` | `8cec0679a23bdd338773944fff120a3abc83b5b271f58999abbbc3aeb34b28fd` |
| 2020-21764 | `1a90f53bd46ee2017d0ff6891d1710cf0d58982f749a39343dfad2b3e1b1a6cd` | `394a6152f60ef04e3141bb690106653e6f202d8e973bec5e8239f819f5739c1f` |
| 2021-02178 | `f819074767edad96b03fa1af9fc930e69f9c3f1d603e054d95c60b5f86fb4341` | `872ae50367aa22a6f70aa58ed760734ef940b6041113fcc16217a6396292aaec` |
| 2021-05878 | `6adc08f7f1d1c7838c3e695d905ebe173cdce1e85d118db1fd743ec73975ccdb` | `b03d2af1ab7b1669117ef0192aacd92d86b8797fd4e3db130fd661d6ba2bf6b4` |
| 2021-12666 | `65bf36cd7585fec8f834b2d9aa97091ef9bba4a42632a30be05bcaed725615a4` | `4aa6a9c6d5492114be9ccbb8bf6f0a2d163f0d7090c073b9e75b1a076b37e815` |
| 2021-16194 | `c912a04622ff7766af5f9e4e992b980aef4e06c5065b06b81622c1f52403dc46` | `02994133b41715508d35cc464a027159a5d04edb40254b4f872b37b9f866b201` |
| 2021-18725 | `79d02fb961f655caf54b652a972f3b10caff5d09db5cbd9014688bc12817e921` | `1127bc531175a52f7028724f0d6791f7a2fcba74d7427a02a087149341bd8fa1` |
| 2021-19593 | `bb1347a30caecc84ddf4c4a426ce5481304793a47744de1e1a7c5fdb0f9a9a53` | `80f9992b7921edba62f042abeeed81eb8b1dfb0b96b9f21e8245cf8547830405` |
| 2022-01950 | `13d7493d0aa56faedaaae4cbe44f3b3f3e261caead16d02fbfdce50e25be6bff` | `e0f08906552af6b38a2aceadd0376736232b636bfffea65bcdcba6eac6c2a0eb` |
| 2022-02184 | `7ebc4afefc0ac7c9e73d624840cf19b5401671e4cd11edd60f85d0a433abd18f` | `cb90493ab404bd023c3bc84d1f4c0b4f5a5c416379539e23dcaab70bde8c76e9` |
| 2022-03446 | `12ad70c15ba2d122ee52611dc3baeaad682ce84822098f3be4890511c54809c5` | `739172d96bea1d199e5b1f0f91e44ae8ac8f2474bdc8daee3ae1f83af44a4f8d` |
| 2022-03828 | `693fcf853da07ecc9de3d30fc8ff9f8baf4545c6ccbb03fc717bb721274f9f70` | `80bd81fba8efa7d4b7dfb81b5d10dae6a45944d4ecb3d07aa4fa168158110ab1` |
| 2022-03987 | `b6af9599933f0c9ad8724e3b40dc514069001003461cf37427cdb4bd8442df36` | `d121b76870fcf0d89d5e9ef75e0397ef97ce2b4d2706c10d96e18913a039771c` |
| 2022-04140 | `cd1591ae14d546ab658caf861ed2151d45258bc462941d09900227e1b768bdf5` | `3177dc47e9afa0d9a5803bba3f67bbb7e8f82c224f42b972ef600a8ce38a7dda` |
| 2022-13993 | `3a6d3c7c012e60245e1a02dd5161e075ceaab0f0eccf7cd4b7efded2fb1d2016` | `c7a701b367d774b7b6afa468aee9a7ec4391cd383e73a9c4122afc0009ef0a69` |
| 2022-21906 | `f54b3dd348dd208d4185eb8bc1c7f0702df5d90b6736f5262b7f7d9b924e2267` | `5ee4f5f8795b509939c369a540857183f1ed03f8655a350d3d0f8afe8c86ed2a` |
| 2022-22360 | `3a3830b5f9aea0c47ea5418cfdaf3db4bdb3c8afbdea956758cf35710684f68f` | `c47465bdb082b778d3a631e84809addd46891c610af0554122a18a103e946180` |
| 2023-00686 | `f422b64295b987b1f89fcea2158854072e68a994057cdf45ca0e6c1d0322458d` | `0f9e92ecd3408219ff6bd65b29da8618083bf6d145bcaff399c20b3c37470fb6` |
| 2023-19612 | `75803ffe69bc932e79b385b6819101f26276e39a39047114b8373ae4484069e3` | `b9b52c601438a2acf28927b3d2b9938c3574519d8043e19612e846c364a0f116` |

## B. 8 särskilda minimeringsförslag

| Ärende / kategori | Minimerad text | Utelämnat / kvarstående länkning | Innehåll SHA256 | Fälthash SHA256 | Källa | Status |
|---|---|---|---|---|---|---|
| 2020-08290 / Bank | En bank avslutade tillgången till betalkonton efter transaktioner vars syfte och medlens ursprung enligt banken inte hade klarlagts. Rätten till grundläggande betalkonto är inte ovillkorlig och begränsas av penningtvättsregler. ARN saknade underlag som vägledde om bankens agerande stred mot dessa regler. Kravet avslogs. | Utelämna misstanke om terrorism/penningtvätt riktad mot kontohavaren. Det minskar utlämnat brottspåstående men källreferensen kan fortfarande återkoppla.; ärendenummer/källa kan återidentifiera. | `9ae8984f21bbd39440b19597745acb254c68c84bd8a6b200bc79d4d82cc09a4a` | `a4fe4cde745c264e88aab0611b3c2a990c83ea0d7e1951e1159de055051669b8` | [ARN HTML](https://www.arn.se/vanligafall/4.9.-tillgang-till-betalkonto/) | HOLD – ej godkänd |
| 2020-08400 / Resor | Flygkompensation vid en driftshändelse som inträffat utanför flygbolagets hemmabas. Den offentliga översikten ställer frågan om en omständighet inom verksamhetens drift kan vara extraordinär enligt EU-förordning 261/2004. Den medicinska uppgiften om en person i besättningen återges inte i denna minimerade text. Översikten visar inte den slutliga bedömningen. | Utelämna uppgift om sjukdom och individ; källnumret kan ändå koppla texten till hälsouppgiften.; ärendenummer/källa kan återidentifiera. | `3540804b70a14dd1c8ab77d94696c55c1cb86e2e64a8cc5457b3f553d3fcde7b` | `c42907674d1bbbae243d2229428899e0d1025e67130738afb987cd56774d7bb9` | [ARN HTML](https://www.arn.se/om-arn/vagledande-beslut/) | HOLD – ej godkänd |
| 2020-16845 / Försäkring | Reseförsäkringsvillkor krävde att ett försäkringsfall innebar akut sjukdom eller akut försämring före avresa. ARN ansåg att villkorets tröskel inte var uppfylld i det beskrivna fallet; en allmän försäkringskategori var inte likställd med akut sjukdom. Försäkringskravet avslogs. | Ta bort den personanknutna uppgiften om riskgrupp och smittorisk; ärendenummer/källsida kan fortfarande återidentifiera hälsokontexten.; ärendenummer/källa kan återidentifiera. | `0736a5ccf5ee6a0bac419248af48ea4c492fab096e7629d1b2772a8bbfa917e1` | `1e9e06e0991de78500c614b191b9fa5040c0c9f5bfb9d49db039d78206026858` | [ARN HTML](https://www.arn.se/vanligafall/5.1.-forsakringsfall/) | HOLD – ej godkänd |
| 2020-24389 / Bank | Kontohavaren bestred kort- och kodbaserade transaktioner trots att det fysiska kortet fanns kvar. Den som påstår att transaktioner är obehöriga måste göra detta antagligt. ARN ansåg att redogörelsen inte rimligt förklarade hur kortet kunde ha använts och återlämnats. Kravet avslogs. | Ta bort påståendet om att konsumenten kan ha blivit drogad; det är ett obevisat hälsorelaterat påstående. Källnumret förblir länkande.; ärendenummer/källa kan återidentifiera. | `7c5e5ee87f93e2c49a8fb1c98779f96bdc8c25ed398f332c6773dddf56621fb1` | `34c6d36db82cb4ba8aff1a5297d7afd60a59032133d198cd5330c646da37a3b2` | [ARN HTML](https://www.arn.se/vanligafall/4.2.-uttag-fran-uttagsautomat-med-kort-och-pinkod-trots-att-kontohavaren-har-kortet-kvar/) | HOLD – ej godkänd |
| 2021-01513 / Allmänna | Ett företag utförde en behandlingstjänst och invände att avtalsinformation begränsade ansvaret för det felaktiga resultatet. ARN fann att företagets allmänna förbehåll inte undanröjde ansvar för hur tjänsten utförts och att felet inte visats bero på konsumentens handlande. Företaget rekommenderades återbetala priset och ersätta styrkta kostnader och förluster. | Utelämna behandlingstyp, kroppsdel och skadornas art; källreferensen kan fortfarande koppla till hälsouppgift.; ärendenummer/källa kan återidentifiera. | `4a930b7b4a583d95cdf455699668facb58fad3e84609523b293db154f6dedf9c` | `b9d20224fca195da43871722dad12fb4e254d178e66a548cfe4bb7d042b40e1c` | [ARN HTML](https://www.arn.se/om-arn/vagledande-beslut/) | HOLD – ej godkänd |
| 2022-08567 / Allmänna | Ett krav avsåg skadestånd efter en konsumentbehandling som ARN bedömde som felaktigt utförd. ARN fann att skadan inte visats bero på konsumenten och bedömde att företagets allmänna informationsvillkor inte begränsade ansvaret. Översikten redovisar ersättningskategorier för följder av felet. Företaget rekommenderades betala ersättning för följder av den felaktiga tjänsten. | Utelämna procedur, specifik skada och medicinsk följd; identifierande koppling kan bestå via ärendenummer och originalkälla.; ärendenummer/källa kan återidentifiera. | `fa8ade0bfae52562554e9099d84aceded36b0a201e026e3dea056db6f6cb3821` | `28e69bca1b5c3cd829b25782bf52c87fd47857301ae3f1896069ad421a4b68fd` | [ARN HTML](https://www.arn.se/om-arn/vagledande-beslut/) | HOLD – ej godkänd |
| 2023-24464 / Bank | Referatet gäller om ett godkännande utgör samtycke enligt betaltjänstlagen i särskilda omständigheter. Den offentliga översikten formulerar en fråga om påverkan från ett hälsotillstånd men lämnar inte själva svaret eller närmare fakta. Den minimerade texten återger inte diagnos eller hälsotillstånd. Utfall och motivering utöver den rättsliga frågan är okända från översikten. | Ta bort uttrycklig uppgift om psykisk störning/demens. Ärendenumret och länken kan ändå röja att originalet gäller hälsa.; ärendenummer/källa kan återidentifiera. | `fd3519a7a981d689eb1a72602c224851167daf4136b06f669676ae2ab3bd7823` | `3317065047d8eb74af2330250400abcd631c64a1cee37b5fe7b3dd87f531ca56` | [ARN HTML](https://www.arn.se/om-arn/vagledande-beslut/) | HOLD – ej godkänd |
| 2024-20240 / Allmänna | En tvist gällde ett avtal om en produkt som enligt lagen krävde särskilt försäljningstillstånd. När säljaren saknade tillstånd förelåg rättslig omöjlighet att fullgöra; frågan avsåg därför hävning i stället för fullgörelse. Konsumenten hade inte rätt till fullgörelse men hade rätt att häva köpet. | Utelämna läkemedlets namn och receptstatus; fallreferens och ursprungslänk kan ändå möjliggöra hälsorelaterad inferens.; ärendenummer/källa kan återidentifiera. | `d473a0f8dec02a132871db47d16fd2b9c6b2e37a77229ecfa170cbf22b776144` | `e5283005aef432aaaba154e0f371b75b75986e05cea97c9fd536d958bab9b83a` | [ARN HTML](https://www.arn.se/om-arn/vagledande-beslut/) | HOLD – ej godkänd |

## Verifieringsstatus

- 29 ordinära texter och 8 särskilda minimeringsförslag är placerade i privat staging och nya hashvärden har beräknats.
- 37 tillhörande stagingapproval-rader är fortfarande `pending`; `library/approved.json` och `library/approvals.json` förblir tomma.
- De 146 befintliga ordinära förslagen har den 2026-11-14 hashkontrollerats mot exakt lokal källpost, föreslagna fält, stagingtext/käll-URL och väntande godkännanderad: 146/146 matchar. Detta återanvänder tidigare individuell sakgranskning; det är inte en ny kontroll av live-HTML och inte innehålls-/juridiskt godkännande.
- Inga verkliga ARN-referat har importerats i runtime; ingen installation, push, merge eller publicering har skett.
- Källa: [ARN:s aktuella översikt över vägledande beslut](https://www.arn.se/om-arn/vagledande-beslut/). Vanliga fall är pedagogiska sammanfattningar, inte fullständiga beslutstexter; utkastens källtyp och källa förblir synliga.

### Riktade verifieringar

- Windows: `tests/test_broad_html.py` — 74 passed.
- Linux: hashbunden isolerad körning med Python 3.14.4 och MCP 2.3.0; aktuell runtime-/testdelta (`arn_html_search.py`, `arn_public_responses.py`, `tests/test_broad_html.py`) — 190 passed. Resultatet finns i `review-local/LINUX-LOCAL-INDEX.json`; endast syntetiska tester kördes och ingen produktions-/Auth-data användes.
- Kandidatens privata staging-data: 186 poster strukturellt validerade; samtliga staging- och trace-hashar matchar, 37 nya poster pending, 3 äldre 1.0.4-hashar oförändrade, runtime approved library fortfarande tomt. Denna datavalidering kördes lokalt på Windows; inga verkliga posttexter överfördes till Linux.


## Hashkontinuitet för de 146 kvarvarande förslagen

Kontrollen den 2026-11-14 bekräftade för samtliga 146 `ORDINARY_FIELD_CANDIDATE_NOT_APPROVED`-poster att: (1) canonical SHA256 för den individuella posten i `review-local/INDEX-REVIEW-STAGING.json` matchar `examined_candidate_record_sha256`; (2) canonical SHA256 för `proposed_fields` matchar dess registrerade fälthash; (3) stagingpostens sammanfattning och officiella URL matchar förslaget; (4) approvalraden binder stagingpostens exakta hash och står `pending`; och (5) källhosten är `www.arn.se`. Fördelning: 113 poster från vägledande översikt och 33 från ARN:s vanliga fall. För de 113 verifierade datum/kategorifälten matchar staging förslaget; för de 33 återstående saknas datum och kategori i förslaget och lämnas därför tomma i staging. Stagingens strukturerade utfallsfält är `okant` för samtliga 146; inget okänt utfall har uppfunnits. Inga av dessa 146 har godkänts.

Detta är den uttryckligen tillåtna återanvändningen av tidigare käll-/sakgranskning där hashvärden fortfarande gäller. Eftersom råa live-HTTP-svar inte sparades finns inget live-body-hash; därför styrker kontrollen inte att ARN:s sida oförändrad efter senast dokumenterad kontroll. Före framtida aktivering ska källa och text kontrolleras på nytt och eventuella ändringar ge ny text- och fälthash.

## Tidigare preliminär matris — ersatt av slutlig postprövning

Den preliminära matrisen och frågelistan som tidigare stod här ersattes efter fullständig granskning av exakt innehåll och hash den 2026-11-14. De innehöll dåvarande slutsatser om att artikel 10-klassificering och artikel 14-avvägning återstod; de slutsatserna är historiska. Aktuell och auktoritativ rekommendation finns i avsnittet **Slutlig postprövning** nedan och i maskinläsbara hashposter i [`review-local/INDIVIDUAL-INDEX-DECISIONS.json`](../review-local/INDIVIDUAL-INDEX-DECISIONS.json).

Inget av detta ändrar status: samtliga 175 ordinarie versioner är fortfarande `NOT_APPROVED_OR_ACTIVATED`; åtta särskilda versioner är fortsatt HOLD; de tre 1.0.4-posterna lämnas oförändrade.

## Slutlig postprövning: artikel 6, 10 och 14 — 2026-11-14

### Rekommenderad godkännandeomfattning (inte ett redan fattat godkännande)

Jag rekommenderar att ägaren prövar positivt innehållsgodkännande för de **175 ordinära exakta postversionerna** i `review-local/INDIVIDUAL-INDEX-DECISIONS.json`: 146 tidigare fältversioner (`ORDINARY_FIELD_CANDIDATE_NOT_APPROVED`) och 29 nyminimerade textversioner (`ORDINARY_MINIMIZED_TEXT_DRAFT_NOT_APPROVED`). Den exakta listan och fulla SHA-256 för var och en finns i registret; varje post binder till `proposed_fields_sha256`. Inget approval-statusfält har ändrats och ingen post aktiveras. Tre äldre 1.0.4-inlägg bevaras.

Den fullständiga listan nedan anger exakt vilka 175 innehållsversioner som rekommenderas för innehållsgodkännande. Den är inte ett aktiveringsbeslut. Varje digest ska matcha `proposed_fields_sha256` i registret.

| ARN-referens | Exakt föreslagen fälthash (SHA-256) | Grupp |
|---|---|---|
| 2014-07855 | `72ae5c151eb5a3c1de915f988205fba411cee4e736f2b05d55a4bfcd238f5b86` | common_case_example |
| 2016-05368 | `ae91ddf8cbd2787f9916a2590043f500042eebc5c44becd3b5b743969a067824` | common_case_example |
| 2016-13173 | `4997dee97493c5ad034352b170325e6a213b87fe254712c3bbd85665f8c70c03` | common_case_example |
| 2016-13500 | `0abbae3ca2c8935e79b8248e8f81fa1f5c89c48ab4ae5e699231865d1bd60714` | common_case_example |
| 2017-00202 | `2ea56a671196e9cae371b57de3871604651a5224ccad3e2fe265196898d35b03` | common_case_example |
| 2017-02218 | `83fc771d7b8c2298a3ed7ba345c5a932bd4323a546feac564c48a9cca7a5f980` | common_case_example |
| 2017-03049 | `71072ac88508df3a3c2ae1ebea49283079139ba614092ca1fe9257cd6e4b314f` | guiding_summary |
| 2017-04862 | `4f8467bbe29511c015914a4dd5fca9f9deb85d3680de851ec7f271a3eff0c8ba` | guiding_summary |
| 2017-05137 | `3c28f651da7176ca61faa285412303a23fa6b6862438f5c4806949db8535b524` | guiding_summary |
| 2017-06733 | `91987157387f95e9b95b98fd03bd619ec5fa64c6080e034563c33943fa75405f` | guiding_summary |
| 2017-07814 | `1beb9d187857c0c84f3c2b05aa93589c393b375a53fc6e7526780c6b938404e7` | guiding_summary |
| 2017-07902 | `8624e27a906fca9f608cf8bb556549f60168b2fdec2feadd3a070761fcdcf1d6` | guiding_summary |
| 2017-09822 | `c6a91f3c09c41dd113255bebfd90bc498d66d2c85962a8130273e96fdc38b5f4` | guiding_summary |
| 2017-09834 | `cc27026e9adb0b021d586b68805a5886f3782a9a240006903d7064f555a5b12f` | guiding_summary |
| 2017-10285 | `b70b52a33155622653b366e5f1ba70b32ddfa239be6b3bb440c205ba2f6b6d76` | guiding_summary |
| 2017-13307 | `8da972f72125c558eac6c6c255356a3babe810a3103f1140eb8e78a8a7f9f59e` | guiding_summary |
| 2017-13781 | `0e804b357838c9349c61b5114c81f444096f20d44ba3644b14cc1fb4bf4eddc9` | guiding_summary |
| 2018-01587 | `8ff66231ac89d196e509c279da55f0f6a882d820a6619b3252de075ab87f62a5` | guiding_summary |
| 2018-05453 | `3f84793b2e2152aa241d0f686d7f6b2d74d31e65752500af83822e992fb5007c` | guiding_summary |
| 2018-06551 | `28ee2a6ac93d2ed7747b2cfd18cfbb79f953eaf23ebaa7ef476e75cc4d9fbbc3` | guiding_summary |
| 2018-06637 | `92addf9ed470582466f862aa62fea769390c7cb5c1be424eb5cf65e863d259b3` | common_case_example |
| 2018-10746 | `41765b6e8df73314bcc4a5b63d736163f0e351a927dc7eaca0a646c04c7439fa` | guiding_summary |
| 2018-11707 | `390169daece8190e4c2c2077d93d7759973e966d5507030dc32f863f429d947c` | guiding_summary |
| 2018-12086 | `4c0827a871503baf4dd3cdfc183414d55dec34c4060bd6a6299d5869aa1e29f3` | common_case_example |
| 2018-12962 | `6ed2037222c6140de2ec691ae798c8d2af56f79f25b915b1ae8ecc47cc28c3cb` | guiding_summary |
| 2018-14272 | `4f95a675d45fc04fd243ca94cb7a48ee8657bde998aca9b7216e3fc2e4ec396f` | guiding_summary |
| 2018-16096 | `fbdbae74326220d83fb1224e5d5c3b1be9e011a21f638926c8fb30b27d54d403` | guiding_summary |
| 2019-00739 | `03f0dfb9dc66e19210c4aad94ad89a0d5cd65ee13a44d51c6057c00c3a324759` | common_case_example |
| 2019-00870 | `dd31010db8174c55799c3001a4c6d077293cff112939604fe6a7ee4b03618291` | guiding_summary |
| 2019-01105 | `21414d6c8b74d9ba8a647d7edd015cdc592de0e38e10f49c07d312b94628c0f4` | guiding_summary |
| 2019-02517 | `8d278d76be3160b6fb0edd56b7a9c2659cf5b1243ee2238e5395a5ca74109bef` | guiding_summary |
| 2019-04350 | `a8464c9f98023f6487f67fa523ec75f124916c8ab14fdaff8724d83554ee8b35` | guiding_summary |
| 2019-04475 | `26bfd4037fa035115a28f66252e1ad7997ef0744a0056fbb9b98fe24f558ddaa` | guiding_summary |
| 2019-05176 | `3348ce8d91a12aac7d589a1863408f2f0ccd577bea2a18e11756e452cc9f3865` | guiding_summary |
| 2019-05386 | `1c08fea8a93941327fc10f463723a27503e8ac94ea526b1dee81ae139f4d2e02` | common_case_example |
| 2019-05790 | `c8a4553ed2b1e082e5e42baa4b0ae66325d6ef4c7b5d20d2ade963ca08e7a4f1` | guiding_summary |
| 2019-06075 | `189bf096f029a267513508e339bd138aea7232facd0bf242bae234ff2ea1e0e4` | common_case_example |
| 2019-06722 | `9e636ab03d18571ea92ac617e965af2b6ecbde00d0ce31f4236e9d1d7d04df3a` | guiding_summary |
| 2019-07775 | `0477e6689439225dc8c0ea47215ec86d78df732176033ab81b56e87dc42b1bbf` | guiding_summary |
| 2019-08258 | `34a69495136dce40577180e284ed734e4137ee34ee894a8ce82a3ca6bd0e8806` | guiding_summary |
| 2019-11253 | `f4617457138cc867f9726f8ce9df8db9213dfe867f57d0392054bacc9de3b0a8` | guiding_summary |
| 2019-11341 | `78124e552ff3ba71d995d675f774d3a6c371c419e51af302667ebef212a5c75d` | guiding_summary |
| 2019-11771 | `cc9fd90a27f510e61d075bcf8cbd90c0488ff0e143b617ddeda18ca1149acbcb` | guiding_summary |
| 2019-14354 | `329980952f049aaeb3fe74dc2ba54d7bcbd944d2bcb6467b39c2358b3f405238` | guiding_summary |
| 2019-16037 | `fd3eb64b3175ae6553a7c22fe9cfeb22eb0d77582154e6395fe5e96663902042` | common_case_example |
| 2019-16732 | `80804286379d29e6833caa9fc70014bc8ea0a04829bebdf6247a18c083e0466a` | guiding_summary |
| 2019-17088 | `fada2d23e14dfc7f58c10b25b30ed2def192322dba765e9510b69b9dbf03a214` | guiding_summary |
| 2019-17351 | `5115102b54ea9bd9512352ffec1208cff85ff8ba4b5db873c9509084118c050c` | common_case_example |
| 2019-17538 | `68428b903e2e57dd98d791cf7caa68533bccd0f5a52a5099e46b2bcd2ccad960` | common_case_example |
| 2019-17613 | `72ba007e9929268365cc95065b6711125970b3902fe5403482a38d907bd3f180` | guiding_summary |
| 2019-17639 | `2021ed3e4eca274673bdadb61c405b271f84bec9036180abe299d76f56ced0be` | guiding_summary |
| 2019-17821 | `8de73aa1ac072dd10cd156e96f234aff402763321256339d5aa4ef033a614f0c` | guiding_summary |
| 2019-18386 | `4e8aa681df42d32ae0d083e4732eeff1b93699c66510e6ee007b46291a532b45` | guiding_summary |
| 2019-19154 | `e0e3425de2ae169f34441d6be4cafdef2d5611785a08bcec315ff4b5cb32bc1b` | guiding_summary |
| 2019-19835 | `e1aa0ed82629c3be43d1396f98a9dc7128e189289095dad175c0d79b90310421` | common_case_example |
| 2019-20086 | `1843d71abf3ae9a170e7fda0aaea08b6167e91fcf1d7ed7d9b1ee5f48099bcaf` | common_case_example |
| 2019-20390 | `224ef8f6b687ad9cc64de5ed3fe1d29319dd9625878c45f1f5732f6a186294da` | common_case_example |
| 2020-00455 | `8319893ee512b6ac485354e8d1fb6d2a10659f0d7b7a71d2aba02b1f8b396dbc` | common_case_example |
| 2020-00535 | `3fcfdcea93ab6bd110dd3af26b58a9aa49db3424ae5c8fd4a8bf29238351e136` | common_case_example |
| 2020-02384 | `3a503c38510bced50a8865bcde0c2d03a32d2dbc9cb7e0fbffdd0be4ec6b09c6` | common_case_example |
| 2020-03506 | `2426025a383559589eb0fc0509c1623affae25db518f8c7e370894aa5dfe30c5` | common_case_example |
| 2020-03524 | `1df0281104f79c3a469853b31061815d8a3f80b73b15528a8ff79b94d044d9b3` | guiding_summary |
| 2020-04504 | `c30502593ae6686216c0b2c1bafe0ee97d2167d0c8614cfd805a3343145a2b5e` | guiding_summary |
| 2020-04664 | `902370b2d0ede9ef2ce895783b5415c49ce0d9e2f17680745475f59fe6cb7316` | guiding_summary |
| 2020-04925 | `b7aea8e8fdd0c37fd61693f10b1e3c5c8b9f34af0f9100e555f8e2951a8c21f5` | guiding_summary |
| 2020-05928 | `4597d3a1fa3395fefcde8c0832169726689153697ff328edcf2ad84d57d8b1df` | guiding_summary |
| 2020-06224 | `c37132458058380aba2fcdcf110cd6279923486981ac9e968dcd140847701029` | guiding_summary |
| 2020-06536 | `3cda2007957d414a745789690e5892cb72982b80a7a605f1205d83f1cc4d4303` | common_case_example |
| 2020-06575 | `c4869dd34023ef7e8e23f6f175df0570e87f0b6175e2e862e2f3d0e3e8425faf` | guiding_summary |
| 2020-06881 | `1369f8b76db471b4a0f3b045faf6b47c6af5a238091c31bfbc8ba5a039b36919` | guiding_summary |
| 2020-07299 | `1766c2524bbbd71839be28d5d5eb8a279cd8169ef672d2d7b676c89aa73b4769` | guiding_summary |
| 2020-07802 | `def0ec4cdfc7a758807b41e975bde86427f4bbdf3d3d37607fac14a629b2a34c` | common_case_example |
| 2020-08372 | `c2887033cc600873d027b91f1871db3618f72fa174a5943c97df34a61a2ef208` | guiding_summary |
| 2020-08495 | `dbaf7d7761d51b9edef95eae92d5147e516a779319454376ebef676b551bc65b` | guiding_summary |
| 2020-08566 | `f2c488a525b1500d806f166541076177c8acf3783d24cdcd615a2fe76e8d9b8a` | guiding_summary |
| 2020-09740 | `77cd409cbcba9f38df934efe5f604f362bb74ecdb8d5253c70d1347577b08647` | guiding_summary |
| 2020-09746 | `6fa574607c59f6c202bb0647c0171ef5adddd0052bf87cc034ba6ae3ace15535` | guiding_summary |
| 2020-09902 | `2a19357fd71c4e75fdb8c5c85580af2628af595498fea7b609e90eddb6f53d73` | guiding_summary |
| 2020-09914 | `29d774f47d14caa69e9bc6e55f2b0f5c1878d224641701743223e4d015dd3cbe` | guiding_summary |
| 2020-15371 | `66c1d70565867bf55e6f6a87fa7687524021399793231f412f96bfc8d752621c` | guiding_summary |
| 2020-15809 | `a01c68d8d7cb5811ec76059b280c8f74aab03f6fbbd6a238b6c2ac8003fff4d8` | guiding_summary |
| 2020-16283 | `5ac5de8344aa01a97128356bdf04035c013cde66f862666f4f6b4eeab7a4edbb` | guiding_summary |
| 2020-16821 | `ae0375d574bcee7f778bb7170c5f85667f9dd621c95e1570cb4ff6bc0d000b5d` | common_case_example |
| 2020-18057 | `d8fc2e4b244fb8820e3347f9deb9c4b6d21a6258d15dfe2a505a31f4da3ffdb9` | guiding_summary |
| 2020-19246 | `c8db870f32ee05b4b035a9de283fc7fbe601b977ea53b8b37be1906451da5850` | common_case_example |
| 2020-19405 | `d5804dbb1874336facf470bbb5f082a7cf196c762d7ab857cbb8f478758347f1` | common_case_example |
| 2020-19648 | `dbda2d707667fa272f1e23116a71c9a839412409246e6ed2e4d02081f48786f0` | guiding_summary |
| 2020-21153 | `8cec0679a23bdd338773944fff120a3abc83b5b271f58999abbbc3aeb34b28fd` | common_case_example |
| 2020-21304 | `b7474e4770f39734c1e276b76799589193472ce14224da92701444746839dd6f` | common_case_example |
| 2020-21764 | `394a6152f60ef04e3141bb690106653e6f202d8e973bec5e8239f819f5739c1f` | common_case_example |
| 2020-22881 | `b61cc92df74d25c8313ddd38380e7620dac7b923a9f7659f98b67c5fe698b9d8` | guiding_summary |
| 2020-22979 | `9d7c0966ce54a84821f40d1f32843747aa2d5d391e1ea88643b9daa045e5a0ad` | common_case_example |
| 2020-25502 | `1d2fcce8952a6b6fee114712eb2713373a51bf5476c61a324b05f491b22b708e` | common_case_example |
| 2020-25951 | `0485fd43988ab3c292a2cc129c87a22e4499c60e13f25ac33942b7d3970cc97d` | common_case_example |
| 2020-27482 | `1a9e1f1f3d91ae77ac2d507a266e5f0f78915b607cc9177ac90838e30de6968f` | common_case_example |
| 2021-00114 | `36072af37b70087c8a943a876bcc23f5ddef8c9d4f1b9ad146d092365e715d81` | common_case_example |
| 2021-00847 | `936f6355d8f80c3890388ab0cb366e44f5a357ffd4e4f63d69790c47d7285e1e` | common_case_example |
| 2021-02178 | `872ae50367aa22a6f70aa58ed760734ef940b6041113fcc16217a6396292aaec` | common_case_example |
| 2021-03350 | `ea27ec0993d86b3b0e80fa38c6463469822cdc09f2218b2466786817762e48fd` | common_case_example |
| 2021-05542 | `f221734810a5b47d8bac04e54e93ffca721061f3494b65c4da54fb86ed2a1453` | common_case_example |
| 2021-05878 | `b03d2af1ab7b1669117ef0192aacd92d86b8797fd4e3db130fd661d6ba2bf6b4` | common_case_example |
| 2021-06584 | `99afbe80a155f56a9b8ee800e74dac5fde9f8371a4d9f6ffec91199f0c882cb2` | guiding_summary |
| 2021-06886 | `da8bf1197bc5fa03a0bb59d4d252ad619c2772f5f6e966b789d99a42a757cc9e` | common_case_example |
| 2021-07612 | `adeffe38aefe1232f0f88dad52438ff0a1091adb40d9b3f1636a7617e70ac705` | guiding_summary |
| 2021-07942 | `52cfcc5ed9ba89d689c3067bbdefec5e4ab3384c3d6aca276457b3cb81497332` | common_case_example |
| 2021-08342 | `d8aeb9a3c5f4154ed8c37866394f406579d306390425d7bfefd04e3be6d936f9` | guiding_summary |
| 2021-09060 | `e9bf9ec50e7538ec0ff9b87b2487655fdcd48edbf74395c665af8f73a0ae4571` | guiding_summary |
| 2021-10041 | `e55ee99c7fa27105337af42c423aa22ae7d6ee1899c598c81461dd4b46bd1607` | guiding_summary |
| 2021-12666 | `4aa6a9c6d5492114be9ccbb8bf6f0a2d163f0d7090c073b9e75b1a076b37e815` | guiding_summary |
| 2021-15559 | `b40317345c97920048fda9f4bfb3c7e2b608b4cf10f01faba1c526706e5ab7ca` | common_case_example |
| 2021-16194 | `02994133b41715508d35cc464a027159a5d04edb40254b4f872b37b9f866b201` | guiding_summary |
| 2021-17230 | `c088838fb4c454ccf2643282fb97ee90e61e6f2d20923e14593c9d5a0af41dfd` | guiding_summary |
| 2021-17441 | `51c163f78761b9f14633a2e0d4483aeea9367d124e08839b376ea1d7c2bf5d11` | guiding_summary |
| 2021-18388 | `9e266719c0f92b3e61e336982f805f0050a0f3e1b9e29e2949b0273ad344b59a` | guiding_summary |
| 2021-18725 | `1127bc531175a52f7028724f0d6791f7a2fcba74d7427a02a087149341bd8fa1` | guiding_summary |
| 2021-19593 | `80f9992b7921edba62f042abeeed81eb8b1dfb0b96b9f21e8245cf8547830405` | guiding_summary |
| 2022-00304 | `c7e74874825aa65446c5574e03a796deae01965c19ca9df9f2f207c6ce503ab9` | guiding_summary |
| 2022-01950 | `e0f08906552af6b38a2aceadd0376736232b636bfffea65bcdcba6eac6c2a0eb` | guiding_summary |
| 2022-02184 | `cb90493ab404bd023c3bc84d1f4c0b4f5a5c416379539e23dcaab70bde8c76e9` | guiding_summary |
| 2022-03446 | `739172d96bea1d199e5b1f0f91e44ae8ac8f2474bdc8daee3ae1f83af44a4f8d` | guiding_summary |
| 2022-03728 | `debe14bb8ed0cea156f28ddadfe697449975e2229c5ee553e1b07951246e4dd9` | guiding_summary |
| 2022-03828 | `80bd81fba8efa7d4b7dfb81b5d10dae6a45944d4ecb3d07aa4fa168158110ab1` | guiding_summary |
| 2022-03987 | `d121b76870fcf0d89d5e9ef75e0397ef97ce2b4d2706c10d96e18913a039771c` | guiding_summary |
| 2022-04140 | `3177dc47e9afa0d9a5803bba3f67bbb7e8f82c224f42b972ef600a8ce38a7dda` | guiding_summary |
| 2022-07469 | `33ffa4124ed47da00c280683f8b1a3d9f8bb312d4a157d214ed17286eb90a7cf` | guiding_summary |
| 2022-07578 | `be8847f9eed03ae17f04f31844c81fa1bbcf158abb53b89d907f89f1d3b1b6ef` | guiding_summary |
| 2022-08173 | `b91cac2bff359ddcb7d59495a761beba4c19aa55d342527f3cb8525a567d86ab` | guiding_summary |
| 2022-09243 | `aaff43f23b4547b05f48eae7e5ad4f84d175addc576acf9e40c296d7c48c3a4f` | guiding_summary |
| 2022-10562 | `77e1c7265b4f34db3602de19bc3bb2c04a0daa72fa1bb6415dbb98596f85f437` | guiding_summary |
| 2022-10784 | `15a8e3182662bf0fcb9a66d2e3c85f2fe57e51a99da520c8dd2a2f9c1ba1e21b` | guiding_summary |
| 2022-12169 | `992c4ea0560ff3905bccffb200223681de30e0b2e4b98ee140846e6090564d3c` | guiding_summary |
| 2022-12985 | `39af935aa44ff8a25f7deef1f86b256d2a2d4eaf83df1ef42623eba8136795d2` | guiding_summary |
| 2022-13388 | `f136f012a20b189b6c23ccf10ba06c79c8d7addf96167b0725116ddf9bce0bc1` | guiding_summary |
| 2022-13993 | `c7a701b367d774b7b6afa468aee9a7ec4391cd383e73a9c4122afc0009ef0a69` | guiding_summary |
| 2022-14070 | `075f36a3762b93753fc006e602f68960593b7f0f256e79c6f7dca00896303842` | guiding_summary |
| 2022-14514 | `2733d1ba5a38821ba3367505e3ff40a10812c56b050e11210e1317c417161c4a` | guiding_summary |
| 2022-15488 | `8f4f9136f7ab3b24d9382c57e84ba7304d7db275f4730eb3440c004bd1007a2e` | guiding_summary |
| 2022-17669 | `89e25b0f6e05b6a3cd1a91db67491940dbd053736f1418e899b5d86027edd764` | guiding_summary |
| 2022-17735 | `5a486b482b7394994bd642a93890c38cd64b44c4c269e4136e2ef70d1799b546` | guiding_summary |
| 2022-17839 | `a70856d1afa68c0268df8513d9240c1dcc26978757935e524e367f3165bd2273` | guiding_summary |
| 2022-17895 | `e9194f8425e3894b0e79f4df7ac69e40c6b2279a3fc6b7ec252f05a62f865261` | guiding_summary |
| 2022-18915 | `d46a59127bfb21bbde8a89162bcf989c2c838413cdb168c973a6051f2edd7007` | guiding_summary |
| 2022-21906 | `5ee4f5f8795b509939c369a540857183f1ed03f8655a350d3d0f8afe8c86ed2a` | guiding_summary |
| 2022-22360 | `c47465bdb082b778d3a631e84809addd46891c610af0554122a18a103e946180` | guiding_summary |
| 2022-25660 | `1dd3278936c59ff0d27cb3e1dd8d08a327c40b0bfdf7416cfc52625e59eb4c7e` | guiding_summary |
| 2023-00170 | `bb6787b05dd350339b47e51aaa21815e75d2311fbd38f214ae54bf50f15584c2` | guiding_summary |
| 2023-00384 | `96fa0191c1db6742cfc7e9ab6d6cfb356fed928a32a6aa74013c7d4684e08b1d` | guiding_summary |
| 2023-00686 | `0f9e92ecd3408219ff6bd65b29da8618083bf6d145bcaff399c20b3c37470fb6` | guiding_summary |
| 2023-01361 | `f5bd6a6338da51341e20d4ce1f95f89d8096588c94cd2b5b5087692425853a73` | guiding_summary |
| 2023-04093 | `998b4f6cd170131b660b50a9a457037c6a21c3317f76aa67498458313abb3928` | guiding_summary |
| 2023-04491 | `70547b559e276a33b336a1a6da97f0eec4db5aee25a84151acbf1be877b68142` | guiding_summary |
| 2023-04890 | `bb7a48d149cfdfd14b34238306944f9ec9160a8478da91da00931a53bd8e6f97` | guiding_summary |
| 2023-05704 | `808158a4cd012e879fc04f624b4d7c70da8677befde72ce9b459888f9cf4ad36` | guiding_summary |
| 2023-07552 | `90fdcbca20d8c5a9d3c52dadf1e99305b52f52067059fe2a0306182cdba59a96` | guiding_summary |
| 2023-07964 | `5f9f95adc6b963e00f658fa5cf8da239284fbe1b2323d5f38639ec550aebffb2` | guiding_summary |
| 2023-10393 | `6a3fd440d43f9b2b068cdc848fd542d0a71f1eb88519a9d352a627739630170c` | guiding_summary |
| 2023-13486 | `fca3bbe0f9dcdfa161f4fdde3a249ee682446a898664bb904891119fa8b2599a` | guiding_summary |
| 2023-16889 | `1111a63409057e7a061c6bda584f65f82075ad99ca1445b1fb3e78591819991f` | guiding_summary |
| 2023-17878 | `1063c31298001ebcc435768a7c02fad491e6618abd1319f5a8900888f8de966a` | guiding_summary |
| 2023-19612 | `b9b52c601438a2acf28927b3d2b9938c3574519d8043e19612e846c364a0f116` | guiding_summary |
| 2023-28076 | `4422cce040a5a4a23a6992566c3ebe3ab4671111b39a518914a2505a89fb3572` | guiding_summary |
| 2024-02479 | `44ee54631cbc52c3be3b6860db4ed9d784607ba6fb9d64c2eb45d4e2b43fec73` | guiding_summary |
| 2024-03864 | `06bff4a2d1a9561fb2440536112e62c0a2781211681ed7d66b172ce8d448f4c2` | guiding_summary |
| 2024-14210 | `00cfcd5f9cd5353f52b8561238ca2847f8f09a9cb499a0413edd84320991f178` | guiding_summary |
| 2024-16960 | `26b6a01dd40ed283be4b59bcc8f7c77677d1312d3e005f0be7e252e8201214c3` | guiding_summary |
| 2024-19113 | `07e5ef2b4e09aea0f2afb751f78581400d348aa863e8e4b6badaae1eccdcfe54` | guiding_summary |
| 2024-20746 | `d5df161920232f0fd36b1e33db4d128f14324e28daa7e97996ccbaabc8ca1c5e` | guiding_summary |
| 2024-22797 | `46133dc216fd42dacb59ab2462b8f59a45fc7b3149cdcb755a34fe7afaef6313` | guiding_summary |
| 2024-24471 | `78b3a23356c3acb11e47abc9787bbbadfd3bbba7541dc528f984923bfcf55003` | guiding_summary |
| 2024-24944 | `bd7b911c934ed97aca5857ea10d824b19d95d5437f51f3549b5deb6a09c42d2d` | guiding_summary |
| 2024-25067 | `565f5bd9f7eef895f66a810649aa9fb0c60a35f70ed561d105eb7cd986b0ad27` | guiding_summary |
| 2025-00318 | `908ecb293d3242ab91e1638f255a9ae93d7599065cbe26856313922187b1071d` | guiding_summary |
| 2025-06866 | `9cbccb2a06d4c443b06611d1ca16c293d2ecc10d554075198a2a47295ddd2607` | guiding_summary |
| 2026-01631 | `63e3efe1b84fbc495a5a43c1dcd8fce1f04583fad668ffd97cbef979e65a467f` | guiding_summary |
| 2026-07742 | `9c40b72077d7384689610a5d99cf022304a1442d340bce1dd1aff16f52fc6c7b` | guiding_summary |

### Artikel 6.1 f — slutsats för den ordinära kohorten

**Rekommendation: positiv avvägning för den definierade 175-postskohorten, endast i den minimerade, hashbundna HTML-sammanfattningsformen och runtime som nu är lokalt verifierad.** Ändamålet är konkret konsumentupplysning om ARN:s konsumenträttsliga bedömningar. Rättsfråga, nödvändiga sakförhållanden, bedömning, utgång när verifierad, datum/kategori när tillgängligt och källreferens behövs för att söka och förstå praxis; saknade utfall/datum lämnas uttryckligen okända. Att ta bort alla ärendereferenser skulle försämra verifierbarheten väsentligt. Ingen rå PDF eller livehämtning behövs för denna kandidat.

Avvägningen talar för behandlingen eftersom det gäller korta officiella sammanfattningar som redan publicerats för konsumentvägledning, utan namn, personnummer eller privata kontaktuppgifter i föreslagna fält; den betalda tjänsten lämnar inte ut profil- eller identifieringsregister. Den sökande måste ange en fråga, varje svar begränsas till 20 relevanssorterade träffar och varje sida debiteras enligt befintlig per-anropskvot. Matchning sker i det godkända lokala indexet utan att sökfrågan skickas till ARN eller extern söktjänst.

Motstående faktorer är att ärendenummer/källänk kan återkoppla till en registrerad och att paginering inte förhindrar kumulativt uttag: cursor gör alla matchande godkända poster nåbara och en betalande klient kan göra upprepade anrop. Den samlade risken bedöms ändå proportionerlig för denna avgränsade mängd om exponeringen stannar vid de 175 minimerade fälthasharna, blankfråga fortsätter avvisas, inga bulkexport-/live-/PDF-vägar läggs till, invändningar leder till snabb spärr och varje ny version bedöms på nytt. Det är inte ett godkännande av framtida poster eller av de åtta särskilda fallen.

### Artikel 10 — individuell klassificering av de 22 flaggade versionerna

**Överlapp:** samtliga 22 är delmängd av de 175 ordinära versionerna. Ingen av de 22 överlappar de åtta special-HOLD-posterna. Av de åtta är sju artikel 9-HOLD och en separat artikel 10-HOLD (2020-08290). De 22 ska alltså inte räknas som ytterligare poster.

**Resultat på de exakta föreslagna fälten:** 21 sammanfattningar handlar om konsumenten som utsatt part eller om en okänd/icke identifierad tredje part (betalningsbedrägeri, stöld/inbrott, obehörig användning eller hot); ARN bedömer i huvudsak konsumentens aktsamhet och bankens/försäkringsgivarens civilrättsliga ansvar. Ingen av de 21 identifierar eller konkret pekar ut en naturlig person som gärningsperson, misstänkt, dömd eller föremål för straffprocess. En sammanfattning (2023-19612) gäller en förlorad vara vid återlämnande och innehåller inget påstående om brott.

**Klassificering:** inget av de 22 exakta fältförslagen innehåller enligt den individuella granskningen artikel 10-uppgift om en identifierad/identifierbar gärningsperson. Att en konsument är brottsoffer/utsatt part och att en okänd person generiskt benämns bedragare/stjälande part är inte i sig en uppgift om att konsumenten begått ett brott. Civilrättslig ”grov oaktsamhet” är inte en brottmålsdom eller brottsmisstanke. Den rättsliga ställningstagandepraxis IMY redovisar avser personuppgifter om någon som begått, dömts/friats eller misstänks för ett konkret brott; IMY har samtidigt 2026 begärt EDPB-klargörande om räckvidden för uppgifter utan inlett förfarande. Därför gäller klassificeringen endast dessa anonymiserade/rollbeskrivna fält och inte en personidentifierande källversion. Om ett framtida fält eller källåtergivning pekar ut en person som misstänkt/gärningsperson ska den versionen hållas på HOLD tills artikel 10-stöd enligt GDPR och svensk rätt finns.

Primär vägledning: [IMY, Personuppgifter som rör lagöverträdelser](https://www.imy.se/verksamhet/dataskydd/det-har-galler-enligt-gdpr/personuppgifter-som-ror-lagovertradelser/) och [IMYRS 2021:1](https://www.imy.se/publikationer/rattsligt-stallningstagande-imyrs-20211/). IMY:s [begäran om EDPB-klargörande den 23 september 2026](https://www.imy.se/nyheter/imy-begar-klargorande-om-vilka-brottsuppgifter-som-omfattas-av-artikel-10/) visar att gränsen för brottsmisstankar utan rättsligt förfarande är under klargörande; det ändrar inte observationen att ingen identifierbar misstänkt förekommer i dessa 22 fält.

| Ärende | SHA-256 av exakt föreslagna fält | Individuell artikel 10-klassificering |
|---|---|---|
| 2018-06551 | `28ee2a6ac93d2ed7747b2cfd18cfbb79f953eaf23ebaa7ef476e75cc4d9fbbc3` | Ingen identifierbar misstänkt/gärningsperson i fält |
| 2018-12086 | `4c0827a871503baf4dd3cdfc183414d55dec34c4060bd6a6299d5869aa1e29f3` | Ingen identifierbar misstänkt/gärningsperson i fält |
| 2019-16037 | `fd3eb64b3175ae6553a7c22fe9cfeb22eb0d77582154e6395fe5e96663902042` | Ingen identifierbar misstänkt/gärningsperson i fält |
| 2019-19154 | `e0e3425de2ae169f34441d6be4cafdef2d5611785a08bcec315ff4b5cb32bc1b` | Ingen identifierbar misstänkt/gärningsperson i fält |
| 2020-02384 | `3a503c38510bced50a8865bcde0c2d03a32d2dbc9cb7e0fbffdd0be4ec6b09c6` | Ingen identifierbar misstänkt/gärningsperson i fält |
| 2020-16821 | `ae0375d574bcee7f778bb7170c5f85667f9dd621c95e1570cb4ff6bc0d000b5d` | Ingen identifierbar misstänkt/gärningsperson i fält |
| 2020-19246 | `c8db870f32ee05b4b035a9de283fc7fbe601b977ea53b8b37be1906451da5850` | Ingen identifierbar misstänkt/gärningsperson i fält |
| 2020-21153 | `8cec0679a23bdd338773944fff120a3abc83b5b271f58999abbbc3aeb34b28fd` | Ingen identifierbar misstänkt/gärningsperson i fält |
| 2021-02178 | `872ae50367aa22a6f70aa58ed760734ef940b6041113fcc16217a6396292aaec` | Ingen identifierbar misstänkt/gärningsperson i fält |
| 2021-05878 | `b03d2af1ab7b1669117ef0192aacd92d86b8797fd4e3db130fd661d6ba2bf6b4` | Ingen identifierbar misstänkt/gärningsperson i fält |
| 2021-12666 | `4aa6a9c6d5492114be9ccbb8bf6f0a2d163f0d7090c073b9e75b1a076b37e815` | Ingen identifierbar misstänkt/gärningsperson i fält |
| 2021-16194 | `02994133b41715508d35cc464a027159a5d04edb40254b4f872b37b9f866b201` | Ingen identifierbar misstänkt/gärningsperson i fält |
| 2021-18725 | `1127bc531175a52f7028724f0d6791f7a2fcba74d7427a02a087149341bd8fa1` | Ingen identifierbar misstänkt/gärningsperson i fält |
| 2021-19593 | `80f9992b7921edba62f042abeeed81eb8b1dfb0b96b9f21e8245cf8547830405` | Ingen identifierbar misstänkt/gärningsperson i fält |
| 2022-01950 | `e0f08906552af6b38a2aceadd0376736232b636bfffea65bcdcba6eac6c2a0eb` | Ingen identifierbar misstänkt/gärningsperson i fält |
| 2022-02184 | `cb90493ab404bd023c3bc84d1f4c0b4f5a5c416379539e23dcaab70bde8c76e9` | Ingen identifierbar misstänkt/gärningsperson i fält |
| 2022-03828 | `80bd81fba8efa7d4b7dfb81b5d10dae6a45944d4ecb3d07aa4fa168158110ab1` | Ingen identifierbar misstänkt/gärningsperson i fält |
| 2022-03987 | `d121b76870fcf0d89d5e9ef75e0397ef97ce2b4d2706c10d96e18913a039771c` | Ingen identifierbar misstänkt/gärningsperson i fält |
| 2022-04140 | `3177dc47e9afa0d9a5803bba3f67bbb7e8f82c224f42b972ef600a8ce38a7dda` | Ingen identifierbar misstänkt/gärningsperson i fält |
| 2022-13993 | `c7a701b367d774b7b6afa468aee9a7ec4391cd383e73a9c4122afc0009ef0a69` | Ingen identifierbar misstänkt/gärningsperson i fält |
| 2022-22360 | `c47465bdb082b778d3a631e84809addd46891c610af0554122a18a103e946180` | Ingen identifierbar misstänkt/gärningsperson i fält |
| 2023-19612 | `b9b52c601438a2acf28927b3d2b9938c3574519d8043e19612e846c364a0f116` | Ingen brottsuppgift; falsk positiv flagga |

### Artikel 14.5 b — separat slutsats för samma 175 hashversioner

**Rekommendation: tillämpa artikel 14.5 b på just dessa 175 hashbundna sammanfattningsversioner, inte som generellt undantag för andra källor eller framtida poster.** Skälen är att lokala postfält saknar partsidentiteter och kontaktvärden, att den aggregerade kontrollen av 41 officiella ARN-URL:er inte fann synlig partsspecifik kontakt eller ARN-förmedling, och att Qysley saknar relation till parterna. Individuell information kan därför inte skickas från de uppgifter som behandlas. Att först söka upp eller härleda partidentiteter och kontaktvägar skulle skapa ny personuppgiftsbehandling som inte behövs för söktjänstens ändamål. GDPR artikel 11 innebär att ansvarig inte behöver skaffa ytterligare identifieringsuppgifter enbart för att uppfylla GDPR när ändamålet inte kräver identifiering; det är inte i sig undantaget.

Avvägning av effekten: utebliven individuell avisering innebär att den registrerade kanske inte känner till den nya sökbarheten. Mot detta står att källorna redan är offentliga, referaten saknar direkta identifierare, offentlig notis plus rättighetskanal kan göra behandlingen synlig och invändning/spärr möjlig. Tjänstens högre sökbarhet och möjlig kumulativ hämtning är en verklig kvarstående nackdel; den mildras av innehållsminimering, avvisad blankfråga, 20 resultat per svar, ingen live-/PDF-hämtning och snabb rättelse/spärr. Med denna avgränsning bedöms individuell information vara omöjlig med de faktiskt behandlade uppgifterna och fullständig offentlig information vara lämplig skyddsåtgärd enligt 14.5 b.

**Nödvändigt villkor före första utlämning:** 1.0.5-integritetsinformationen, i full artikel 14-form och lätt att hitta utan konto, måste vara faktiskt publicerad och beskriva dessa 175 sammanfattningar, källa, ändamål, grund, mottagare, retention, rättigheter och invändningskanal. Rättighetskanal/spärrrutin ska vara operativ. Eftersom denna begäran förbjuder publicering/aktivering nu är undantaget rekommenderat men ännu inte operativt åberopat; ingen post är godkänd i runtime. Detta är det enda konkreta kvarvarande förhandsvillkoret för den rekommenderade Art14-vägen; om det inte uppfylls ska de nya 175 inte lämnas ut.

**Beslutsutfall:** Jag rekommenderar innehållsgodkännande av de 175 exakta ordinära hashversionerna enligt annexregistret, inklusive de 22 efter ovanstående artikel 10-klassificering, och rekommenderar artikel 14.5 b för just denna definierade grupp med villkoret om publicerad information/rättighetsrutin. Jag rekommenderar inte godkännande av de åtta HOLD-versionerna. Ingen av dessa rekommendationer ändrar status, aktiverar poster, installerar eller publicerar.


## Slutlig artikel 10-klassificering och tillämpning av ägarbeslut — 2026-11-14

Ägaren har fastställt den dokumenterade artikel 6.1 f-avvägningen och det separata artikel 14.5 b-beslutet för de hashbundna förslag som rekommenderats i registret, med de där angivna villkoren. Det fastställer rättslig grund/informationsväg för den definierade behandlingen; det är inte ett innehållsgodkännande, aktivering, installation eller publicering. Exakt registerfält för innehållsversion är `records[].proposed_fields_sha256`.

**22 brottskontextflaggor, ingen dubbelräkning.** Den befintliga 22-radstabellen ovan är den exakta listan av ärenden och fälthashar. Alla 22 tillhör de ursprungliga 175 ordinära förslagen; ingen tillhör de 8 special-HOLD. Individuella fältklassificeringar identifierade inte artikel 10-uppgift i någon av de 22 exakta föreslagna texterna. Tjugoen beskriver konsumenten som utsatt eller en oidentifierad tredje part utan identifierbar misstänkt/gärningsperson; 2023-19612 är en falsk positiv flagga utan brottspåstående. Detta är inte ett anonymitetsintyg och gäller inte andra källfält eller framtida textversioner. 2019-16037 är fortfarande korrekt klassificerad på sina egna föreslagna textfält men flyttas nedan till källänksgranskning.

**Källänksfynd och tre återförda versioner.** Sidlänksfältet har korrigerats från `case_specific` till `multi_case_page` för de tre versionerna; ny fälthash har beräknats och tidigare hash står kvar som historik i beslutsregistret. Den aktuella officiella ARN-sidan [5.1 Försäkringsfall](https://www.arn.se/vanligafall/5.1.-forsakringsfall/) visar flera separata ärenden på samma sida: 2019-16037, 2020-27482 och 2021-03350 samt det separat HOLD-markerade 2020-16845. Det senare innehåller hälsorelaterad riskgruppskontext. Därför kan den gemensamma sidlänken inte behandlas som en isolerad källhänvisning till de tre ordinära posterna. Följande exakta versioner återförs till källänksgranskning och är inte i den nu rekommenderade mängden; deras föreslagna text/hash har inte ändrats:

| Ärende | SHA-256 föreslagna fält | Status |
|---|---|---|
| 2019-16037 | `fd3eb64b3175ae6553a7c22fe9cfeb22eb0d77582154e6395fe5e96663902042` | Åter till granskning: gemensam källa visar separat HOLD-post |
| 2020-27482 | `1a9e1f1f3d91ae77ac2d507a266e5f0f78915b607cc9177ac90838e30de6968f` | Åter till granskning: gemensam källa visar separat HOLD-post |
| 2021-03350 | `ea27ec0993d86b3b0e80fa38c6463469822cdc09f2218b2466786817762e48fd` | Åter till granskning: gemensam källa visar separat HOLD-post |

**Exakt rekommenderad uppsättning efter källkontrollen: 172 postversioner.** Den fullständiga maskinläsbara listan i ärende-ID + SHA-256-form finns i `review-local/CURRENT-CANDIDATE-MANIFEST.json` under `legal_decision_schedule.recommended_exact_post_versions` och i `review-local/INDIVIDUAL-INDEX-DECISIONS.json` under `owner_article6_article14_decision_2026_11_14.recommended_exact_hash_versions`. Dessa 172 är de ursprungliga 175 minus endast tabellens tre källänksundantag. Alla hashvärden är oförändrade och innehållsgodkännande står fortfarande pending.

**Tillämpning per grupp:**

- För de 172 exakta hashversionerna: ägarens positiva artikel 6.1 f- och separata artikel 14.5 b-beslut tillämpas med deras fastställda villkor. Ingen direkt identifierare/kontaktfält; sökningen använder lokal, minimerad text; ärendenummer/källa medför fortsatt länkbarhet. Före första utlämning krävs 1.0.5-specifik, lättfunnen integritetsinformation och fungerande rättighets-, invändnings-, rättelse- och omedelbar spärrväg.
- För de tre versionerna i tabellen: ingen av de två besluten är tillämplig förrän källänken har godkänts för den isolerade posten eller ersatts med en rättsligt användbar, verifierad ärendespecifik hänvisning och ny hashbunden prövning.
- För de 8 särskilda posterna: 7 artikel 9-risker och 1 separat artikel 10-risk kvarstår på HOLD; de är inte i 172 och får inte ärva gruppbeslutet.
- De 3 befintliga 1.0.4-posterna bevaras oförändrade och är inte del av det nya beslutet.

Den källkontrollen använde renderad officiell webbvy; rå HTML sparades inte och direkt HTTP-svarshash kunde inte erhållas. Den bekräftar sidans sammanblandade ärendeinnehåll men inte en fullständig byte-identisk källsnapshot. Ingen produktion, aktivering eller publicering har skett.
