#1.0.5 — förberett införande, EJ INSTALLATIONSGODKÄNT

Utgångspunkt: produktion1.0.4 på18e79a0. Ingen push/merge/tagg/installation ingår
i detta uppdrag. Ändra inte1.0.4-taggen, bibliotekets treposter, pin, journal,
ankare, databaser, OAuth, PayPal eller andra tjänster.

## Före ägarens installationsbeslut

1. Granska kandidatens manifest och Windows/Linux-resultat. Ingen GitHub-CI-körning
   påstås för1.0.5: pushmandat saknas. Kontrollera aktiveringsblockerarna i
   105-processing-and-policy.md. Robots-disallow får inte kringgås med UA eller
   config. Accepterad källtäckning måste anges uttryckligen, inte kallas helaARN.
2. Gör en färsk skrivskyddad baslinjekontroll av berörda runtimefiler, Python/SDK,
   ARN ExecStart/UID och kontrollfiler. Använd inte en gammal match som livebevis.
3. Bygg en privat kompatibilitets-/installationspayload från exakt kandidatmanifest.
   Nödvändigt runtimefilurval är ENDAST arn_html_search.py (ny), arn_mcp.py,
   arn_public_responses.py. Övriga runtimekomponenter ska matcha1.0.4-baslinjen.
   README/CHANGELOG/server.json är releaseartefakter, inte serverkonfiguration.
4. Skyddad backup före ändring: dessa två befintliga Python-filer, eventuell tidigare
   arn_html_search.py, den avgränsade systemd-dropin som styr aktivering och
   versions-/hashinventering. Rootägd0700backup/0600filer. Verifiera SHA och
   återläsning till separat temporär katalog innan ändring. Återställ inte databaser.
   Spara kontrollfilsmetadata/hash utan att reinitialisera dem. Ingen full .venv-kopia.

## Planerad ändring efter separat godkännande

- Installera endast de tre hashbundna runtimefilerna atomärt med befintligt
  ägarskap/behörighet; inga paketinstalleringar eller ändringar av låsfiler i drift.
- Separat ARN-dropin får ange ARN_BROAD_HTML_ENABLED=1 endast efter uppfyllda
  sakvillkor. Default är0; en installerad men avstängd kandidat uppfyller inte
  produktmålet och ska inte presenteras som fungerande bred publik sökning.
- Publicera godkänt policydelta före ny personuppgiftsutlämning. Gamla villkor,
  avtalssnapshots och ansvarig-/rättighets-/retentionsinformation bevaras.
- Endast ARN får kort omstart. Auth/Nginx/SMTP/övriga system ska inte ändras.

## Obligatoriska efterkontroller

Verifiera installerade SHA/initialize-version1.0.5; åtta verktygsnamn och samma
argument; OAuth/discovery200 och oautentiseradMCP401Bearer; tre godkända
bibliotekshashar och senastejournal/ankare oförändrade. Ingen riktig betalning.

Verifiera syntetisk nekad admission ger0källanrop, medgiven kombination ger en
kvotoperation, robotsblockeddb ger0form/PDF-anrop, bred verklig HTML-träff utanför
treposter och korrekt källa/länktyp, godkänd biblioteksläsning samt okändreferens/
källfel. Autentiserad wire-kontroll görs med ägarens befintliga klient och
angiven kvotkostnad. Varken intern stub eller tools/list ersätter faktisk wire.
Återkallad referens får inte återkomma via bred källa eller gammal backup.

## Säker rollback

Stoppa endast ARN. Återför exakt de verifierade1.0.4-kodfilerna och tidigare
aktiveringsdropin ur backup (ta bort nytillagd fil/dropin endast om den saknades
före installationen och endast inom exakt dokumenterad målväg). Återför aldrig
äldre kontrolljournal/ankare eller kunddatabaser. Verifiera1.0.4-filer mot backup,
1.0.4:s lokala trepostadapter utan PDF-fallback, och starta ARN först efter
kontroller. Vid osäkerhet håll ARN stoppad; inga andra tjänster påverkas.

Detta är en komplett avgränsning för ett senare hashbundet installationsscript,
inte en procedur som nu körts eller bevis att framtida baslinje fortfarande matchar.
