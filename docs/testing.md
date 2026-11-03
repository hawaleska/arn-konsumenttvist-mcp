# Reproducerbara ARN-tester (R6)

Målmiljö: Linux x86-64, CPython **3.14.4**, MCP SDK **2.3.0**. Lokal verifiering 2026-11-03: Windows x86-64, samma Python/SDK. Repo innehåller MCP-komponenten och har privata driftsberoenden; detta är inte en komplett självhostningsguide.

## Ren installation

Kör från projektroten med Python 3.14.4:

```bash
python3.14 -m venv .venv
.venv/bin/python -m pip install --require-hashes --only-binary=:all: -r requirements-test.lock
.venv/bin/python -m pip check
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -B -m pytest -q --tb=short -p no:cacheprovider tests
```

På Windows används `.venv\Scripts\python.exe` och miljövariabeln sätts med `$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'` i PowerShell. Lokal ren installation gjordes med uv 0.13.7 (`uv pip install --python .venv/Scripts/python.exe --require-hashes -r requirements-test.lock`) och konsistens med `uv pip check`; CI använder pip enligt ovan.

`requirements.txt` anger direkta import-/runtimeberoenden med driftversionerna. `requirements.lock` är en konservativ fullständig snapshot av driftmiljöns distributionsversioner, exklusive pip, med SHA-256 från PyPI:s versionsmetadata. Den innehåller även indirekta paket; onödig paketminskning görs inte inom R6. `requirements-test.txt` lägger till pytest; `requirements-test.lock` inkluderar runtime-låset och låser testberoendena. Alla publicerade distributionshashar för respektive version tillåts för att stödja plattformarnas wheels. CI kräver wheels och får inte tyst falla tillbaka till källbyggen. En låsfil ersätter inte verifiering av en ren installation på målplattformen.

Windows kräver dessutom pywin32 312 via SDK; detta paket har explicit Windows-markör i runtime-låset och påverkar inte Linux-produktionen. Testberoendenas versioner är separata från den verifierade Linux-runtime-snapshoten. Inga paket eller konfigurationer på Ubuntu ändras av R6.

## Testomfattning

- Återanvända R3/R4-prov: publika tillåtelselistor, nästlade resultat/licensfält, sessions-/URL-/token-canaries, neutrala fel, referenser och loggutskrifter, adapterfel och syntetiska PayPal-beslut.
- Återanvända ARN-specifika R2-prov: statuskontrakt, timeout/nätverksfel och total deadline fail-closed; API-nyckelns felgräns. Qysley Auths implementation, databas och testnycklar ingår inte.
- R5: komplett AST-jämförelse mot godkänd R4 efter enbart metadatanormalisering; faktiska tools/list-wirefält för alla åtta verktyg jämförs med riktigt SDK. Metadataharnessen använder identitetsdekoratorer för R3/R4; deras beteende täcks separat av fel-/serialiseringstesterna.
- R6: verklig full modulimport och `__main__`-startväg med `streamable-http`, inklusive SDK-importen och riktiga run-parametrar. Endast Uvicorns sista `serve`-steg ersätts: ingen port binds. Faktisk ASGI-app/lifespan och discovery 200 samt oautentiserat MCP 401 kontrolleras.

Startup-testet kopierar källfiler till pytest-tmp, tömmer processkonfigurationen till en uttrycklig syntetisk miljö och skapar endast en tillfällig SQLite-fil där. Ingen .env kopieras. Externa requests/urllib/httpx-transporter stoppas uttryckligen i startup-smoken. Övriga återanvända tester mockar externa gränser och använder ASGI/MockTransport. Inga verkliga ARN-sökningar, betalningar, tokens eller nätverksbaserade verifieringar ska utföras. Tester får aldrig köras i produktionskatalogen.

## Resultat och kvarstående begränsningar

**122 tester passerade** lokalt i den rena Python 3.14.4-miljön. Beroendekontroll: 45 installerade paket kompatibla. Hashkrävande ren installation passerade. Se test-result.txt, dependency-check-result.txt och clean-install-result.txt (lokala granskningsunderlag).

GitHub Actions har **inte körts** för detta förslag: inget har publicerats. Datorn har ingen installerad WSL/Linux och Docker hittades inte, så ren Linux-installation och CI-startup är ännu inte verifierade. Tidigare Linux/SDK-resultat från R3–R5 återanvänds som historiskt stöd, men räknas inte som en ren installation från det nya låset. CI måste visa PASS efter separat GitHub-godkännande innan R6 kan markeras KLAR.

Inga livebetalningar, fullständig privat backendintegration, publik OAuth-klient eller autentiserad tools/list från körande produktion verifieras av denna svit. R5:s återstående produktionskontroll är oförändrad. R2–R5:s godkännanden eller funktioner ändras inte av R6.

## Publiceringsavgränsning

R6-filerna som föreslås versionshanteras är exakt requirements-filerna, `.gitignore`, `.github/workflows/ci.yml`, `docs/testing.md`, `tests/*.py` och de två historiska källfixtures som testerna läser under `baseline/`. Baselinefiler är testunderlag, inte installerbara original. Befintliga Python-moduler i denna lokala kopia är oförändrade snapshots för testning, inte nya R6-kodändringar.

Publicera inte lokala `.tools/`, `.python/`, `.cache/`, `.test-tmp*/`, venv, resultatloggar eller hela arbetskatalogen. Använd en uttrycklig filförteckning vid ett framtida godkänt GitHub-steg. `.gitignore` har endast fått den godkända borttagningen av `test_*.py`; övriga regler och R15-arbete lämnas orörda.


## Isolerad Linux-verifiering 2026-11-03

Utf�rd efter separat godk�nnande p� Ubuntu med /usr/bin/python3.14 (3.14.4). Publika wheels h�mtades med pip --require-hashes till en ny privat tempor�r katalog (0700). Befintlig pip anv�ndes endast som l�sande h�mtningsverktyg; inga paket installerades i befintliga milj�er. D�refter k�rdes Bubblewrap med separat n�tverks-/processnamnrymd, read-only /usr och k�ll-/wheelmontage, egen tmpfs och utan produktionskataloger. Ingen n�tverks�tkomst under installation/test. Gr�nser: en CPU, 1 GiB adressutrymme, 120 CPU-sekunder.

En helt ny venv utan �rvda site-packages skapades inne i isoleringen. Pip 25.1.1 bootstrapades fr�n separat offentlig wheel; samtliga applikations-/testberoenden installerades offline fr�n of�r�ndrade l�sfiler med --require-hashes --only-binary=:all:. Pip sj�lvt �r ett bootstrapverktyg och ing�r inte i applikationsl�set.

Resultat: hashinstallation PASS; pip check: No broken requirements found; Python 3.14.4 / MCP 2.3.0 PASS; **122 tester passerade p� 3,43 sekunder**, inklusive verklig startup och ASGI-smoke. Inga Linux-specifika kod-/l�s�ndringar beh�vdes. Windows-markerade pywin32 hoppades �ver som avsett. Tillf�llig SQLite och syntetisk konfiguration anv�ndes; inga produktionsuppgifter, Auth-filer eller betalningar.

Bubblewrap-tmpfs f�rsvann n�r processen avslutades. Skriptets finally tog bort endast sin egen verifierade /tmp/qysley-r6-check-*-katalog, inklusive nedladdade wheels och k�llkopior. Se linux-test-result.txt och linux-verification-template.py f�r underlag. Detta �r en lokal/SSH-k�rd Linux-verifiering, inte en GitHub Actions-k�rning och inte ett nytt produktionsprov f�r R5.


### Kontaktkommentarer efter Linux-provet

Inf�r publicering ersattes endast en tidigare privat Gmail-kontakt med den redan publika support@qysley.se i arn_mcp.py, arn_license.py och baseline/arn_mcp.py. AST �r identiskt f�re/efter. Samtliga 122 tester passerade p� nytt lokalt med Python 3.14.4/MCP 2.3.0. Den tidigare Linux-k�rningen avser bytes f�re kommentarsbytet; runtime-/testlogiken �r identisk. R12 �r fortfarande inte avslutat.
