import re
from collections import defaultdict
from io import BytesIO
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader
from common_cases import ARNCommonCases


class ARNClient:
    BASE_URL = "https://adokweb.arn.se/referatwebb"

    SEARCH_FIELD = "4C5522ED0901C217D45C196C0444E23FBAA3FCA8"
    FROM_YEAR_FIELD = "A9D34C2F3FCFF47AF546517E34D21ABA050E4C9F"
    TO_YEAR_FIELD = "88D755E882BFAE1CE5C04BE95CF6CC1552BA6878"
    CATEGORY_FIELD = "AE745AA845CEAF87776C5AC14600B6C55BA2E391"
    OUTCOME_FIELD = "3A0C59291BEE588B73A5346390A045DB8504101C"
    FROM_DATE_FIELD = "FF1F3F9D936F77066EE7BA36F4B684873511426A"
    TO_DATE_FIELD = "67BEEAC89226A371B9B6A2D2BFBEC427B519B206"

    CATEGORY_VALUES = {
        "alla": "alla",
        "allmänna": "Allm",
        "allm": "Allm",
        "bank": "Bank",
        "boende": "Bo",
        "båt": "Båt",
        "el": "El",
        "försäkring": "Förs",
        "motor": "Motor",
        "möbler": "Möbler",
        "resor": "Resor",
        "sko": "Sko",
        "textil": "Textil",
        "tvätt": "Tvätt",
        "elektronik": "El",
    }

    OUTCOME_VALUES = {
        "obegransad": "obegransad",
        "bifall": "bifall",
        "avslag": "avslag",
        "annat": "annat",
    }

    KNOWN_CATEGORIES = [
        "Allmänna",
        "Bank",
        "Boende",
        "Båt",
        "Elektronik",
        "El",
        "Försäkring",
        "Motor",
        "Möbler",
        "Resor",
        "Sko",
        "Textil",
        "Tvätt",
    ]

    def __init__(self):
        self.session = requests.Session()
        self.common_cases = ARNCommonCases()
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (X11; Linux x86_64) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/155.0.0.0 Safari/537.36"
                )
            }
        )

    @staticmethod
    def _normalize(text):
        if not text:
            return ""
        return re.sub(r"\s+", " ", text.strip())

    @staticmethod
    def _contains_term(text, term):
        if not text or not term:
            return False

        text = text.lower()
        term = term.lower().strip()

        if len(term) <= 3:
            return bool(
                re.search(
                    r"\b" + re.escape(term) + r"\b",
                    text,
                    flags=re.IGNORECASE,
                )
            )

        return term in text

    @staticmethod
    def _safe_int(value, default):
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def _extract_form_data(self, form):
        data = {}

        for element in form.find_all(
            ["input", "select", "textarea"]
        ):
            name = element.get("name")

            if not name:
                continue

            if element.has_attr("disabled"):
                continue

            element_type = element.get(
                "type",
                "",
            ).lower()

            if element_type in [
                "submit",
                "button",
                "file",
            ]:
                continue

            if element_type in [
                "radio",
                "checkbox",
            ]:
                if not element.has_attr("checked"):
                    continue

            if element.name == "select":
                option = element.find(
                    "option",
                    selected=True,
                )

                if not option:
                    option = element.find("option")

                if option:
                    data[name] = option.get(
                        "value",
                        "",
                    )

            else:
                data[name] = element.get(
                    "value",
                    "",
                )

        return data

    def search(
        self,
        query,
        category="alla",
        outcome="obegransad",
        from_year="",
        to_year="",
    ):
        query = (query or "").strip()

        response = self.session.get(
            self.BASE_URL,
            timeout=30,
        )
        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

        form = soup.find("form")

        if not form:
            raise RuntimeError(
                "Hittade inget ARN-sökformulär"
            )

        action = form.get("action")

        if not action:
            raise RuntimeError(
                "ARN-formuläret saknar action"
            )

        post_url = urljoin(
            response.url,
            action,
        )

        search_input = form.find(
            "input",
            {"id": "input-search-referatwebb"},
        )

        if not search_input:
            raise RuntimeError(
                "Hittade inte ARN:s sökfält"
            )

        search_name = search_input.get("name")

        if not search_name:
            raise RuntimeError(
                "ARN:s sökfält saknar name"
            )

        search_button = form.find(
            "button",
            {"id": "btn-search"},
        )

        if not search_button:
            raise RuntimeError(
                "Hittade inte ARN:s SÖK-knapp"
            )

        onclick = search_button.get(
            "onclick",
            "",
        )

        command_match = re.search(
            r"submitCmd\('([^']+)'\)",
            onclick,
        )

        if not command_match:
            raise RuntimeError(
                "Kunde inte hitta ARN:s sökkommando"
            )

        command_name = command_match.group(1)

        data = self._extract_form_data(form)

        data[search_name] = query

        category_key = (
            str(category or "alla")
            .strip()
            .lower()
        )

        outcome_key = (
            str(outcome or "obegransad")
            .strip()
            .lower()
        )

        category_value = self.CATEGORY_VALUES.get(
            category_key,
            category,
        )

        outcome_value = self.OUTCOME_VALUES.get(
            outcome_key,
            outcome,
        )

        data[self.CATEGORY_FIELD] = category_value
        data[self.OUTCOME_FIELD] = outcome_value

        if from_year:
            data[self.FROM_YEAR_FIELD] = str(
                from_year
            )

        if to_year:
            data[self.TO_YEAR_FIELD] = str(
                to_year
            )

        data[command_name] = "submit"

        result = self.session.post(
            post_url,
            data=data,
            timeout=30,
            allow_redirects=True,
        )

        result.raise_for_status()

        result_soup = BeautifulSoup(
            result.text,
            "html.parser",
        )

        results = []

        for container in result_soup.select(
            "div.case-container"
        ):
            text = self._normalize(
                container.get_text(
                    " ",
                    strip=True,
                )
            )

            if not text:
                continue

            case_match = re.search(
                r"\b(\d{4}-\d{5})\b",
                text,
            )

            if not case_match:
                continue

            case_number = case_match.group(1)

            date_match = re.search(
                r"\b(\d{4}-\d{2}-\d{2})\b",
                text,
            )

            date = (
                date_match.group(1)
                if date_match
                else ""
            )

            button = container.find("button")

            if not button:
                continue

            onclick = button.get(
                "onclick",
                "",
            )

            file_match = re.search(
                r"fileId=(\d+)",
                onclick,
            )

            if not file_match:
                continue

            file_id = file_match.group(1)

            session_match = re.search(
                r"xsessiontag=(\d+)",
                onclick,
            )

            xsessiontag = (
                session_match.group(1)
                if session_match
                else ""
            )

            category_text = ""

            for possible_category in self.KNOWN_CATEGORIES:
                if self._contains_term(
                    text,
                    possible_category,
                ):
                    category_text = (
                        possible_category
                    )
                    break

            summary = text

            summary = re.sub(
                r"^\s*"
                + re.escape(case_number)
                + r"\s*",
                "",
                summary,
            )

            if date:
                summary = re.sub(
                    r"^\s*"
                    + re.escape(date)
                    + r"\s*",
                    "",
                    summary,
                )

            results.append(
                {
                    "case_number": case_number,
                    "date": date,
                    "category": category_text,
                    "summary": summary,
                    "file_id": file_id,
                    "xsessiontag": xsessiontag,
                }
            )

        return results

    def get_decision(
        self,
        case_number,
        file_id=None,
        xsessiontag=None,
    ):
        case_number = (
            case_number or ""
        ).strip()

        if not case_number:
            raise ValueError(
                "case_number måste anges"
            )

        source_result = None

        if not file_id:
            results = self.search(
                query=case_number
            )

            source_result = next(
                (
                    item
                    for item in results
                    if item.get(
                        "case_number"
                    ) == case_number
                ),
                None,
            )

            if not source_result:
                raise RuntimeError(
                    f"Hittade inte ARN-ärendet "
                    f"{case_number}"
                )

            file_id = source_result[
                "file_id"
            ]

            xsessiontag = (
                source_result.get(
                    "xsessiontag"
                )
            )

        pdf_url = (
            "https://adokweb.arn.se/"
            "digiforms/"
            "sessionInitializer"
            "?processName="
            "ViewDocumentProcess"
            "&_dfPmid=2387"
            "&keepCache=new"
        )

        if xsessiontag:
            pdf_url += (
                "&xsessiontag="
                + str(xsessiontag)
            )

        pdf_url += (
            "&action=showDocumentContent"
            "&fileId="
            + str(file_id)
        )

        response = self.session.get(
            pdf_url,
            timeout=30,
        )

        response.raise_for_status()

        content_type = response.headers.get(
            "Content-Type",
            "",
        ).lower()

        if (
            "pdf" not in content_type
            and not response.content.startswith(
                b"%PDF"
            )
        ):
            raise RuntimeError(
                "ARN returnerade inte en PDF"
            )

        reader = PdfReader(
            BytesIO(response.content)
        )

        pages = []

        for page in reader.pages:
            try:
                page_text = page.extract_text()
            except Exception:
                page_text = ""

            if page_text:
                pages.append(page_text)

        text = "\n".join(pages).strip()

        result = {
            "case_number": case_number,
            "file_id": str(file_id),
            "xsessiontag": (
                str(xsessiontag)
                if xsessiontag
                else ""
            ),
            "text": text,
            "pages": len(reader.pages),
            "pdf_url": pdf_url,
        }

        if source_result:
            result.update(
                {
                    "date": source_result.get(
                        "date",
                        "",
                    ),
                    "category": source_result.get(
                        "category",
                        "",
                    ),
                    "summary": source_result.get(
                        "summary",
                        "",
                    ),
                }
            )

        else:
            lookup = self.search(
                query=case_number
            )

            match = next(
                (
                    item
                    for item in lookup
                    if item.get(
                        "case_number"
                    ) == case_number
                ),
                None,
            )

            if match:
                result.update(
                    {
                        "date": match.get(
                            "date",
                            "",
                        ),
                        "category": match.get(
                            "category",
                            "",
                        ),
                        "summary": match.get(
                            "summary",
                            "",
                        ),
                    }
                )

        return result

    def _extract_concepts(self, problem):
        text = (
            problem or ""
        ).lower()

        concepts = []

        concept_rules = {
            "tv": [
                "tv",
                "television",
                "tv-apparat",
                "smart-tv",
                "smart tv",
            ],
            "elektronik": [
                "elektronik",
                "elektronikvara",
                "elektronikprodukt",
                "surfplatta",
                "hörlurar",
            ],
            "dator": [
                "dator",
                "laptop",
                "bärbar dator",
                "stationär dator",
            ],
            "mobiltelefon": [
                "mobiltelefon",
                "mobil",
                "smartphone",
                "smarttelefon",
            ],
            "ångerrätt": [
                "ångerrätt",
                "ångra",
                "ångrade",
                "ångrat",
            ],
            "återbetalning": [
                "återbetalning",
                "återbetala",
                "pengarna tillbaka",
                "få tillbaka pengarna",
            ],
            "distansköp": [
                "internet",
                "online",
                "på nätet",
                "webb",
                "distansköp",
                "distansavtal",
            ],
            "reklamation": [
                "reklamation",
                "reklamera",
                "felaktig",
                "fel på",
                "defekt",
            ],
            "garanti": [
                "garanti",
                "garantitid",
                "garantireparation",
            ],
            "reparation": [
                "reparation",
                "reparera",
                "avhjälpa",
                "avhjälpande",
                "lagning",
            ],
            "leverans": [
                "leverans",
                "försenad",
                "försening",
            ],
            "avtal": [
                "avtal",
                "abonnemang",
                "häva",
                "hävning",
            ],
        }

        for concept, terms in concept_rules.items():
            if any(
                self._contains_term(text, term)
                for term in terms
            ):
                concepts.append(concept)

        return concepts

    def _concept_search_terms(
        self,
        problem,
        concepts,
    ):
        terms = []

        if "tv" in concepts:
            terms.extend(
                [
                    "tv",
                    "television",
                    "tv-apparat",
                    "smart-tv",
                ]
            )

        if "elektronik" in concepts:
            terms.extend(
                [
                    "elektronik",
                    "elektronikvara",
                    "elektronikprodukt",
                ]
            )

        if "dator" in concepts:
            terms.extend(
                [
                    "dator",
                    "laptop",
                    "bärbar dator",
                    "stationär dator",
                ]
            )

        if "mobiltelefon" in concepts:
            terms.extend(
                [
                    "mobiltelefon",
                    "smartphone",
                    "smarttelefon",
                ]
            )

        if "ångerrätt" in concepts:
            terms.extend(
                [
                    "ångerrätt",
                    "ånger",
                ]
            )

        if "återbetalning" in concepts:
            terms.extend(
                [
                    "återbetalning",
                    "återbetala",
                ]
            )

        if "distansköp" in concepts:
            terms.extend(
                [
                    "distansavtal",
                    "distansköp",
                ]
            )

        if "reklamation" in concepts:
            terms.extend(
                [
                    "reklamation",
                    "felaktig",
                ]
            )

        if "garanti" in concepts:
            terms.extend(
                [
                    "garanti",
                    "garantireparation",
                ]
            )

        if "reparation" in concepts:
            terms.extend(
                [
                    "reparation",
                    "reparera",
                    "avhjälpa",
                ]
            )

        if "leverans" in concepts:
            terms.extend(
                [
                    "leverans",
                    "försenad",
                ]
            )

        if "avtal" in concepts:
            terms.extend(
                [
                    "avtal",
                    "abonnemang",
                ]
            )

        words = re.findall(
            r"[A-Za-zÅÄÖåäöÉé0-9-]+",
            (problem or "").lower(),
        )

        stopwords = {
            "jag",
            "har",
            "och",
            "att",
            "en",
            "ett",
            "den",
            "det",
            "de",
            "som",
            "på",
            "av",
            "för",
            "med",
            "till",
            "efter",
            "innan",
            "inom",
            "inte",
            "mig",
            "min",
            "mitt",
            "mina",
            "köpt",
            "köpte",
            "köpa",
            "köpet",
            "företaget",
            "företag",
            "vägrar",
            "vill",
            "kan",
            "ska",
            "måste",
            "få",
            "får",
            "något",
            "någon",
            "pengarna",
        }

        for word in words:
            if (
                len(word) >= 5
                and word not in stopwords
            ):
                terms.append(word)

        unique = []

        for term in terms:
            if term not in unique:
                unique.append(term)

        return unique[:20]

    @staticmethod
    def _score_text(
        text,
        concepts,
        problem,
        summary=False,
    ):
        if not text:
            return 0

        searchable = text.lower()

        def has(term):
            return ARNClient._contains_term(
                searchable,
                term,
            )

        score = 0

        concept_terms = {
            "tv": [
                "tv",
                "television",
                "tv-apparat",
                "tv apparat",
                "tv:n",
                "smart-tv",
                "smart tv",
            ],
            "elektronik": [
                "elektronik",
                "elektronikprodukt",
                "elektronikvara",
            ],
            "mobiltelefon": [
                "mobiltelefon",
                "smartphone",
                "smarttelefon",
                "mobil",
            ],
            "ångerrätt": [
                "ångerrätt",
                "ångra",
                "ångrat",
                "ångrade",
                "distansavtalslagen",
            ],
            "återbetalning": [
                "återbetalning",
                "återbetala",
                "återfå",
                "pengarna tillbaka",
            ],
            "distansköp": [
                "distansavtal",
                "distansköp",
                "internet",
                "webbplats",
                "på nätet",
                "online",
            ],
            "reklamation": [
                "reklamation",
                "reklamera",
                "felaktig",
                "fel på",
                "defekt",
            ],
            "garanti": [
                "garanti",
                "garantitid",
                "garantireparation",
            ],
            "reparation": [
                "reparation",
                "reparera",
                "avhjälpa",
                "avhjälpande",
                "lagning",
            ],
            "leverans": [
                "leverans",
                "försenad",
                "försening",
            ],
            "avtal": [
                "avtal",
                "abonnemang",
                "häva",
                "hävning",
            ],
        }

        concept_weights = {
            "tv": 24,
            "elektronik": 10,
            "mobiltelefon": 14,
            "ångerrätt": 4,
            "återbetalning": 4,
            "distansköp": 3,
            "reklamation": 4,
            "garanti": 6,
            "reparation": 7,
            "leverans": 2,
            "avtal": 2,
        }

        for concept in concepts:
            matches = 0

            for term in concept_terms.get(
                concept,
                [],
            ):
                if has(term):
                    matches += 1

            if matches:
                base = concept_weights.get(
                    concept,
                    2,
                )

                if summary:
                    score += min(
                        matches * 2,
                        base,
                    )
                else:
                    score += min(
                        matches * 4,
                        base * 2,
                    )

        useful_words = []

        words = re.findall(
            r"[A-Za-zÅÄÖåäöÉé0-9-]+",
            (problem or "").lower(),
        )

        stopwords = {
            "jag",
            "har",
            "och",
            "att",
            "en",
            "ett",
            "den",
            "det",
            "de",
            "som",
            "på",
            "av",
            "för",
            "med",
            "till",
            "efter",
            "innan",
            "inom",
            "inte",
            "mig",
            "min",
            "mitt",
            "mina",
            "köpt",
            "köpte",
            "köpa",
            "köpet",
            "företaget",
            "företag",
            "vägrar",
            "vill",
            "kan",
            "ska",
            "måste",
            "få",
            "får",
            "något",
            "någon",
            "pengarna",
        }

        for word in words:
            if (
                len(word) >= 5
                and word not in stopwords
            ):
                useful_words.append(word)

        for word in useful_words:
            if has(word):
                score += (
                    1
                    if summary
                    else 2
                )

        combinations = [
            (
                ["tv", "ångerrätt"],
                8,
            ),
            (
                ["tv", "reklamation"],
                10,
            ),
            (
                ["tv", "distansköp"],
                8,
            ),
            (
                ["tv", "återbetalning"],
                8,
            ),

            # Elektronik + reklamation är vanligt, men specifika
            # produkt-/garantiärenden ska väga betydligt tyngre.
            (
                ["elektronik", "reklamation"],
                6,
            ),
            (
                ["elektronik", "ångerrätt"],
                5,
            ),
            (
                ["elektronik", "garanti"],
                12,
            ),

            (
                ["mobiltelefon", "garanti"],
                20,
            ),
            (
                ["mobiltelefon", "reparation"],
                20,
            ),
            (
                ["mobiltelefon", "reklamation"],
                14,
            ),
            (
                ["dator", "garanti"],
                20,
            ),
            (
                ["dator", "reparation"],
                20,
            ),
            (
                ["dator", "reklamation"],
                14,
            ),
            (
                ["garanti", "reparation"],
                14,
            ),

            # Mobiltelefon + garanti/reparation är ett mycket
            # specifikt ärende och ska slå generella elektronikfall.
            # Återbetalning efter retur/distansköp.
            (
                ["ångerrätt", "återbetalning"],
                8,
            ),
            (
                ["ångerrätt", "distansavtal"],
                4,
            ),
            (
                ["återbetalning", "distansköp"],
                8,
            ),

            # Begagnad bil + fel/reklamation.
            (
                ["begagnad", "reklamation"],
                10,
            ),
            (
                ["begagnad", "felaktig"],
                10,
            ),
        ]

        for terms, points in combinations:
            if all(
                has(term)
                for term in terms
            ):
                score += (
                    points // 2
                    if summary
                    else points
                )

        return score

    def _category_relevance(
        self,
        result,
        concepts,
        requested_category,
    ):
        result_category = (
            result.get(
                "category",
                "",
            )
            or ""
        ).lower()

        summary = (
            result.get(
                "summary",
                "",
            )
            or ""
        ).lower()

        score = 0

        requested_category = (
            requested_category or "alla"
        ).lower()

        if requested_category != "alla":
            category_map = {
                "elektronik": [
                    "elektronik",
                    "el",
                ],
                "motor": [
                    "motor",
                ],
                "bank": [
                    "bank",
                ],
                "boende": [
                    "boende",
                ],
                "resor": [
                    "resor",
                ],
                "textil": [
                    "textil",
                ],
                "sko": [
                    "sko",
                ],
                "försäkring": [
                    "försäkring",
                ],
                "båt": [
                    "båt",
                ],
                "möbler": [
                    "möbler",
                ],
            }

            wanted = category_map.get(
                requested_category,
                [requested_category],
            )

            if any(
                value in result_category
                for value in wanted
            ):
                score += 40
            else:
                score -= 30

        if "tv" in concepts:
            physical_tv_terms = [
                "köpt en tv",
                "köpte en tv",
                "köpt tv",
                "köpte tv",
                "tv-apparat",
                "tv apparat",
                "television",
                "smart-tv",
                "smart tv",
                "samsung-tv",
                "philips-tv",
                "lg-tv",
                "sony-tv",
            ]

            streaming_terms = [
                "streamingtjänst",
                "streamingtjänsten",
                "tv-abonnemang",
                "tv abonnemang",
                "abonnemang",
                "digital tjänst",
                "digitala tjänsten",
                "streaming",
            ]

            # TV-relevans ska bedömas mot hela beslutstexten,
            # inte bara sammanfattningen.
            decision_text = (
                result.get("text", "")
                or result.get("summary", "")
                or ""
            )

            physical_tv = any(
                self._contains_term(
                    decision_text,
                    term,
                )
                for term in physical_tv_terms
            )

            streaming_case = any(
                self._contains_term(
                    summary,
                    term,
                )
                for term in streaming_terms
            )

            if physical_tv:
                score += 300

            if streaming_case and not physical_tv:
                score -= 250

            if not physical_tv:
                score -= 75

            if (
                "elektronik"
                in result_category
                and physical_tv
            ):
                score += 45

            unrelated_categories = {
                "textil",
                "motor",
                "sko",
                "resor",
                "möbler",
                "båt",
                "bank",
                "försäkring",
                "boende",
            }

            if any(
                item in result_category
                for item in unrelated_categories
            ):
                score -= 100

        if "elektronik" in concepts:
            if "elektronik" in result_category:
                score += 25

            electronics_terms = [
                "elektronik",
                "elektronikvara",
                "elektronikprodukt",
                "tv",
                "television",
                "dator",
                "telefon",
                "mobil",
                "surfplatta",
                "hörlurar",
            ]

            if any(
                self._contains_term(
                    summary,
                    term,
                )
                for term in electronics_terms
            ):
                score += 15

            unrelated = {
                "textil",
                "motor",
                "sko",
                "resor",
                "möbler",
                "båt",
            }

            if any(
                item in result_category
                for item in unrelated
            ):
                score -= 35

        return score

    def similar_cases(
        self,
        problem,
        category="alla",
        outcome="obegransad",
        from_year="",
        to_year="",
        max_results=10,
    ):
        problem = (
            problem or ""
        ).strip()

        if not problem:
            return {
                "problem": problem,
                "concepts": [],
                "search_terms": [],
                "count": 0,
                "results": [],
                "common_cases": [],
            }

        max_results = self._safe_int(
            max_results,
            10,
        )

        max_results = max(
            1,
            min(
                max_results,
                20,
            ),
        )

        concepts = self._extract_concepts(
            problem
        )

        # Common cases används även för produktspecifika frågor,
        # men filtreras så att deras egen beskrivning måste innehålla
        # den efterfrågade produkten.
        try:
            common_cases = self.common_cases.search(
                query=problem,
                max_results=max_results,
            )
        except Exception:
            common_cases = []

        product_terms_common = {
            "tv": [
                "tv",
                "television",
                "tv-apparat",
            ],
            "mobiltelefon": [
                "mobiltelefon",
                "smartphone",
                "smarttelefon",
            ],
            "dator": [
                "dator",
                "laptop",
                "bärbar dator",
            ],
        }

        required_common_products = [
            product
            for product in product_terms_common
            if product in concepts
        ]

        if required_common_products:
            filtered_common_cases = []

            for common in common_cases:
                common_text = " ".join([
                    common.get("category", ""),
                    common.get("area", ""),
                    common.get("description", ""),
                ]).lower()

                valid = True

                for product in required_common_products:
                    if not any(
                        self._contains_term(common_text, term)
                        for term in product_terms_common[product]
                    ):
                        valid = False
                        break

                if valid:
                    filtered_common_cases.append(common)

            common_cases = filtered_common_cases

        search_terms = (
            self._concept_search_terms(
                problem,
                concepts,
            )
        )

        # Lägg till kombinationer av produkt + juridiskt problem.
        # Exempel: "tv garanti", "tv reparation", "dator garanti".
        product_concepts = [
            "tv",
            "mobiltelefon",
            "dator",
        ]

        issue_concepts = [
            "garanti",
            "reparation",
            "reklamation",
            "ångerrätt",
            "återbetalning",
            "leverans",
        ]

        combination_queries = []

        for product in product_concepts:
            if product in concepts:
                for issue in issue_concepts:
                    if issue in concepts:
                        combination_queries.append(
                            f"{product} {issue}"
                        )

        # Sök på hela problemformuleringen också.
        if problem.strip() and problem not in search_terms:
            search_terms.insert(0, problem)

        # Lägg kombinationerna tidigt i söklistan.
        for combination in reversed(combination_queries):
            if combination not in search_terms:
                search_terms.insert(1, combination)

        if not search_terms:
            search_terms = [problem]

        candidates = defaultdict(
            lambda: {
                "result": None,
                "score": 0,
                "matched_queries": [],
                "common_case": False,
            }
        )

        # Vanliga ARN-fall är semantiskt relevanta kandidater och ska
        # behandlas som riktiga kandidater i rankningen.
        for common in common_cases:
            case_number = common.get("case_number")
            if not case_number:
                continue

            entry = candidates[case_number]

            entry["result"] = {
                "case_number": case_number,
                "category": common.get("category", ""),
                "summary": common.get("description", ""),
                "file_id": "",
                "xsessiontag": "",
            }

            entry["score"] += 100
            entry["common_case"] = True

            if "common_case" not in entry["matched_queries"]:
                entry["matched_queries"].append("common_case")

        for search_query in search_terms:
            try:
                results = self.search(
                    query=search_query,
                    category=category,
                    outcome=outcome,
                    from_year=from_year,
                    to_year=to_year,
                )
            except Exception:
                continue

            for result in results:
                case_number = result.get(
                    "case_number"
                )

                if not case_number:
                    continue

                entry = candidates[
                    case_number
                ]

                entry["result"] = result

                if (
                    search_query
                    not in entry[
                        "matched_queries"
                    ]
                ):
                    entry[
                        "matched_queries"
                    ].append(
                        search_query
                    )

                    # Specifika sökord väger tyngre än breda sökningar.
                    # Det gör att relevanta kandidater kommer med
                    # till fulltextanalysen.
                    query_weight = 3

                    specific_queries = {
                        "mobiltelefon": 14,
                        "smartphone": 14,
                        "smarttelefon": 14,
                        "dator": 14,
                        "laptop": 14,
                        "bärbar dator": 14,
                        "stationär dator": 14,
                        "reparation": 12,
                        "reparera": 12,
                        "avhjälpa": 12,
                        "garanti": 10,
                        "garantireparation": 12,
                        "reklamation": 7,
                        "begagnad": 7,
                        "felaktig": 7,
                        "ångerrätt": 7,
                        "återbetalning": 7,
                    }

                    if search_query.lower() in specific_queries:
                        query_weight = specific_queries[
                            search_query.lower()
                        ]

                    entry["score"] += query_weight

        for entry in candidates.values():
            result = entry["result"]

            summary = " ".join(
                [
                    result.get(
                        "summary",
                        "",
                    ),
                    result.get(
                        "category",
                        "",
                    ),
                ]
            )

            entry["score"] += (
                self._score_text(
                    summary,
                    concepts,
                    problem,
                    summary=True,
                )
            )

            entry["score"] += (
                self._category_relevance(
                    result,
                    concepts,
                    category,
                )
            )

            # Intent-filter för specifika problem.
            # Ett ärende som inte ens verkar handla om den
            # centrala produkten eller åtgärden ska inte få
            # tränga undan relevanta kandidater innan fulltexten
            # läses.
            summary_lower = summary.lower()

            if "mobiltelefon" in concepts:
                # Undvik falska träffar som "telefonbolag",
                # "telefonbank" och "mobila BankID".
                # Generiskt "telefon" får därför inte ensam
                # räknas som en mobiltelefonträff.
                explicit_phone_terms = [
                    "mobiltelefon",
                    "smartphone",
                    "smarttelefon",
                    "mobiltelefonen",
                    "smartphonen",
                ]

                generic_phone_terms = [
                    "telefon",
                    "mobil",
                ]

                repair_terms = [
                    "reparation",
                    "reparera",
                    "reparerat",
                    "avhjälpa",
                    "avhjälpande",
                    "lagning",
                    "slutade fungera",
                    "fungerar inte",
                    "går inte att använda",
                    "ur funktion",
                    "garanti",
                    "garantireparation",
                ]

                has_explicit_phone = any(
                    self._contains_term(
                        summary_lower,
                        term,
                    )
                    for term in explicit_phone_terms
                )

                has_repair = any(
                    self._contains_term(
                        summary_lower,
                        term,
                    )
                    for term in repair_terms
                )

                # Ett explicit mobiltelefonord är stark evidens.
                generic_phone = any(
                    self._contains_term(
                        summary_lower,
                        term,
                    )
                    for term in generic_phone_terms
                )

                if has_explicit_phone and has_repair:
                    entry["score"] += 80
                elif has_explicit_phone:
                    entry["score"] += 20
                elif generic_phone and has_repair:
                    entry["score"] += 35
                else:
                    entry["score"] -= 80

                if "reparation" in concepts:
                    if has_repair:
                        entry["score"] += 25
                    else:
                        entry["score"] -= 30

        ranked_candidates = sorted(
            candidates.values(),
            key=lambda item: (
                item["score"],
                len(
                    item[
                        "matched_queries"
                    ]
                ),
            ),
            reverse=True,
        )

        read_limit = min(
            max(
                max_results * 3,
                20,
            ),
            50,
        )

        output = []

        for entry in ranked_candidates[
            :read_limit
        ]:
            result = entry["result"]

            try:
                if entry.get("common_case"):
                    decision = self.get_decision(
                        case_number=result["case_number"]
                    )
                else:
                    decision = self.get_decision(
                        case_number=result["case_number"],
                        file_id=result.get("file_id"),
                        xsessiontag=result.get("xsessiontag"),
                    )

                full_text = decision.get(
                    "text",
                    "",
                )

                entry["score"] += (
                    self._score_text(
                        full_text,
                        concepts,
                        problem,
                        summary=False,
                    )
                )

                lower_text = (
                    full_text.lower()
                )

                if "tv" in concepts:
                    physical_tv = any(
                        self._contains_term(
                            lower_text,
                            term,
                        )
                        for term in [
                            "köpt en tv",
                            "köpte en tv",
                            "tv-apparat",
                            "tv apparat",
                            "television",
                            "smart-tv",
                            "smart tv",
                            "samsung-tv",
                            "philips-tv",
                            "lg-tv",
                            "sony-tv",
                        ]
                    )

                    streaming_case = any(
                        self._contains_term(
                            lower_text,
                            term,
                        )
                        for term in [
                            "streamingtjänst",
                            "tv-abonnemang",
                            "digital tjänst",
                            "digitala tjänsten",
                        ]
                    )

                    if physical_tv:
                        entry["score"] += 350

                        # Matcha den faktiska frågan, inte bara objektet.
                        # Ett TV-fall med garanti/reparation ska väga
                        # betydligt tyngre för sådana sökningar.
                        if "garanti" in concepts:
                            if any(
                                self._contains_term(
                                    lower_text,
                                    term,
                                )
                                for term in [
                                    "garanti",
                                    "garantitid",
                                    "garantireparation",
                                ]
                            ):
                                entry["score"] += 180

                        if "reparation" in concepts:
                            if any(
                                self._contains_term(
                                    lower_text,
                                    term,
                                )
                                for term in [
                                    "reparation",
                                    "reparera",
                                    "reparerat",
                                    "avhjälpa",
                                    "avhjälpande",
                                    "lagning",
                                    "lagade",
                                    "slutade fungera",
                                    "fungerar inte",
                                    "ur funktion",
                                ]
                            ):
                                entry["score"] += 180

                    if (
                        streaming_case
                        and not physical_tv
                    ):
                        entry["score"] -= 300

                result_category = (
                    result.get(
                        "category",
                        "",
                    )
                    or ""
                )

                # Hård relevansregel för TV-frågor:
                # ett beslut som inte faktiskt nämner fysisk TV
                # ska inte kunna rankas före ett beslut som gör det.
                if "tv" in concepts:
                    if physical_tv:
                        entry["score"] += 500
                    else:
                        # Hård filtrering: ett TV-resultat måste faktiskt
                        # handla om en fysisk TV.
                        continue

                if "tv" in concepts:
                    tv_warranty_terms = [
                        "garanti",
                        "garantitid",
                        "garantireparation",
                    ]

                    tv_repair_terms = [
                        "reparation",
                        "reparera",
                        "reparerat",
                        "reparerades",
                        "avhjälpa",
                        "avhjälpande",
                        "lagning",
                        "lagade",
                        "slutade fungera",
                        "fungerar inte",
                        "går inte att använda",
                        "ur funktion",
                    ]

                    has_tv_warranty = any(
                        self._contains_term(lower_text, term)
                        for term in tv_warranty_terms
                    )

                    has_tv_repair = any(
                        self._contains_term(lower_text, term)
                        for term in tv_repair_terms
                    )

                    # TV-intent används som ranking, inte hård filtrering.
                    # Produktfiltret nedan säkerställer redan att beslutet
                    # faktiskt handlar om en TV.
                    if has_tv_warranty and "garanti" in concepts:
                        entry["score"] += 220

                    if has_tv_repair and "reparation" in concepts:
                        entry["score"] += 220

                # Generellt produktfilter.
                # Om användaren uttryckligen söker en specifik produkt
                # måste beslutets fulltext faktiskt handla om produkten.

                product_terms = {
                    "tv": [
                        "tv",
                        "television",
                        "tv-apparat",
                        "tv apparat",
                        "smart-tv",
                        "smart tv",
                    ],
                    "mobiltelefon": [
                        "mobiltelefon",
                        "smartphone",
                        "smarttelefon",
                    ],
                    "dator": [
                        "dator",
                        "laptop",
                        "bärbar dator",
                        "stationär dator",
                    ],
                }

                required_products = [
                    product
                    for product in product_terms
                    if product in concepts
                ]

                if required_products:
                    all_products_present = all(
                        any(
                            self._contains_term(lower_text, term)
                            for term in product_terms[product]
                        )
                        for product in required_products
                    )

                    if not all_products_present:
                        continue

                    # Produktordet måste också finnas i början av
                    # själva beslutet, där yrkande och sakförhållande
                    # normalt beskrivs. Detta hindrar generella
                    # juridiska vägledningar från att skapa falska
                    # produktträffar.
                    product_intro_limits = {
                        "tv": 5000,
                        "mobiltelefon": 5000,
                        "dator": 5000,
                    }

                    product_intro_valid = True

                    for product in required_products:
                        intro_limit = product_intro_limits.get(
                            product,
                            5000,
                        )

                        intro_text = lower_text[:intro_limit]

                        intro_present = any(
                            self._contains_term(
                                intro_text,
                                term,
                            )
                            for term in product_terms[product]
                        )

                        if not intro_present:
                            product_intro_valid = False
                            break

                    if not product_intro_valid:
                        continue

                    # En produktterm ensam räcker inte.
                    # Exempelvis ska ett bankbedrägeri där en bedragare
                    # fjärrstyr konsumentens dator inte räknas som ett
                    # datorärende.
                    product_context_terms = [
                        "köpt",
                        "köpte",
                        "köpa",
                        "köparen",
                        "köpet",
                        "inköp",
                        "beställde",
                        "beställt",
                        "säljaren",
                        "säljare",
                        "vara",
                        "produkt",
                        "fel på",
                        "felaktig",
                        "defekt",
                        "reklamation",
                        "garanti",
                        "garantireparation",
                        "reparation",
                        "reparera",
                        "avhjälpa",
                        "avhjälpande",
                        "återbetalning",
                        "hävning",
                    ]

                    for product in required_products:
                        product_found_in_context = False

                        for product_term in product_terms[product]:
                            start = 0

                            while True:
                                pos = lower_text.find(
                                    product_term.lower(),
                                    start,
                                )

                                if pos == -1:
                                    break

                                # Produktordet måste stå i samma mening
                                # som ett kommersiellt/produktrelaterat
                                # sammanhang. Detta filtrerar bort
                                # perifera omnämnanden som "låna en dator"
                                # eller "fjärrstyra datorn".
                                sentence_start = lower_text.rfind(
                                    ".",
                                    0,
                                    pos,
                                ) + 1

                                sentence_end = lower_text.find(
                                    ".",
                                    pos,
                                )

                                if sentence_end == -1:
                                    sentence_end = len(lower_text)

                                sentence = lower_text[
                                    sentence_start:sentence_end
                                ]

                                if any(
                                    self._contains_term(
                                        sentence,
                                        context_term,
                                    )
                                    for context_term in product_context_terms
                                ):
                                    product_found_in_context = True
                                    break

                                start = pos + len(product_term)

                            if product_found_in_context:
                                break

                        if not product_found_in_context:
                            continue

                # Hårt relevansfilter för uttryckligen efterfrågade problem.
                # Om användaren anger en specifik produkt + ett specifikt problem
                # måste varje efterfrågat problem faktiskt förekomma i beslutets
                # fulltext.
                issue_terms_fulltext = {
                    "garanti": [
                        "garanti",
                        "garantin",
                        "garantitid",
                        "garantireparation",
                    ],
                    "reparation": [
                        "reparation",
                        "reparera",
                        "reparerat",
                        "reparerades",
                        "reparations",
                        "avhjälpa",
                        "avhjälpande",
                        "lagning",
                        "laga",
                        "lagade",
                    ],
                    "reklamation": [
                        "reklamation",
                        "reklamera",
                        "reklamerade",
                        "felaktig",
                        "defekt",
                    ],
                    "ångerrätt": [
                        "ångerrätt",
                        "ånger",
                        "ångra",
                        "ångrade",
                        "ångrat",
                    ],
                    "återbetalning": [
                        "återbetalning",
                        "återbetala",
                        "pengarna tillbaka",
                        "få tillbaka pengarna",
                    ],
                    "leverans": [
                        "leverans",
                        "leverera",
                        "försenad",
                        "försening",
                        "dröjsmål",
                    ],
                }

                required_issues = [
                    issue
                    for issue in issue_terms_fulltext
                    if issue in concepts
                ]

                # Gate endast när användaren samtidigt har specificerat
                # en produkt och ett eller flera specifika problem.
                if required_products and required_issues:
                    product_issue_match = True

                    product_context_terms = [
                        "köpt",
                        "köpte",
                        "köpa",
                        "köparen",
                        "köpet",
                        "inköp",
                        "beställde",
                        "beställt",
                        "säljaren",
                        "säljare",
                        "vara",
                        "produkt",
                        "fel på",
                        "felaktig",
                        "defekt",
                        "reklamation",
                        "garanti",
                        "garantireparation",
                        "reparation",
                        "reparera",
                        "avhjälpa",
                        "avhjälpande",
                        "återbetalning",
                        "hävning",
                        "leverans",
                    ]

                    for product in required_products:
                        product_terms_for_case = final_product_terms.get(
                            product,
                            product_terms.get(product, [])
                        )

                        product_found_with_issue = False

                        for product_term in product_terms_for_case:
                            start = 0

                            while True:
                                pos = lower_text.find(product_term.lower(), start)

                                if pos == -1:
                                    break

                                sentence_start = lower_text.rfind(".", 0, pos) + 1
                                sentence_end = lower_text.find(".", pos)

                                if sentence_end == -1:
                                    sentence_end = len(lower_text)

                                sentence = lower_text[sentence_start:sentence_end]

                                issue_match = all(
                                    any(
                                        self._contains_term(sentence, issue_term)
                                        for issue_term in issue_terms_fulltext[issue]
                                    )
                                    for issue in required_issues
                                )

                                context_match = any(
                                    self._contains_term(sentence, context_term)
                                    for context_term in product_context_terms
                                )

                                if issue_match and context_match:
                                    product_found_with_issue = True
                                    break

                                start = pos + len(product_term)

                            if product_found_with_issue:
                                break

                        if not product_found_with_issue:
                            product_issue_match = False
                            break

                    if not product_issue_match:
                        continue

                # Generellt intent-filter för åtgärder/problem.
                # Produktkravet hanteras separat ovan.
                # Garanti/reparation används som relevanssignal
                # och ska inte ensamt kasta bort ett relevant
                # produktärende.

                generic_intent_score = 0

                if "garanti" in concepts:
                    generic_warranty_terms = [
                        "garanti",
                        "garantitid",
                        "garantireparation",
                        "garantiansvar",
                    ]

                    if any(
                        self._contains_term(summary_lower, term)
                        for term in generic_warranty_terms
                    ):
                        generic_intent_score += 30

                if "reparation" in concepts:
                    generic_repair_terms = [
                        "reparation",
                        "reparera",
                        "reparerat",
                        "reparerades",
                        "avhjälpa",
                        "avhjälpande",
                        "lagning",
                        "lagade",
                        "slutade fungera",
                        "fungerar inte",
                        "går inte att använda",
                        "ur funktion",
                    ]

                    if any(
                        self._contains_term(summary_lower, term)
                        for term in generic_repair_terms
                    ):
                        generic_intent_score += 30

                entry["score"] += generic_intent_score

                if "mobiltelefon" in concepts:
                    explicit_phone_terms = [
                        "mobiltelefon",
                        "smartphone",
                        "smarttelefon",
                        "mobiltelefonen",
                        "smartphonen",
                    ]

                    repair_terms_fulltext = [
                        "reparation",
                        "reparera",
                        "reparerat",
                        "reparerades",
                        "avhjälpa",
                        "avhjälpande",
                        "lagning",
                        "lagade",
                        "slutade fungera",
                        "fungerar inte",
                        "går inte att använda",
                        "ur funktion",
                        "garanti",
                        "garantireparation",
                    ]

                    has_phone_fulltext = any(
                        self._contains_term(lower_text, term)
                        for term in explicit_phone_terms
                    )

                    has_repair_fulltext = any(
                        self._contains_term(lower_text, term)
                        for term in repair_terms_fulltext
                    )

                    # Hård filtrering: mobilfrågor ska inte kunna ge
                    # telefonbolag, BankID, telefonbedrägerier osv.
                    if not (has_phone_fulltext and has_repair_fulltext):
                        continue

                # Returnera inte kandidater som efter all relevansanalys
                # fortfarande har negativ score.
                if entry["score"] < 0:
                    continue

                output.append(
                    {
                        **result,
                        "score": entry[
                            "score"
                        ],
                        "matched_queries": entry[
                            "matched_queries"
                        ],
                        "text": full_text,
                        "pages": decision.get(
                            "pages"
                        ),
                        "pdf_url": decision.get(
                            "pdf_url"
                        ),
                        "category": (
                            result_category
                            or decision.get(
                                "category",
                                "",
                            )
                        ),
                        "summary": (
                            result.get(
                                "summary",
                                "",
                            )
                            or decision.get(
                                "summary",
                                "",
                            )
                        ),
                    }
                )

            except Exception as exc:
                output.append(
                    {
                        **result,
                        "score": entry[
                            "score"
                        ],
                        "matched_queries": entry[
                            "matched_queries"
                        ],
                        "error": str(exc),
                    }
                )

        # Slutligt relevansfilter för kombinationer av produkt + problem.
        # Produkten och problemet måste förekomma i samma mening,
        # tillsammans med tydlig produkt-/köpkontext.
        final_product_terms = {
            "tv": ["tv", "television", "tv-apparat", "smart-tv", "smart tv"],
            "mobiltelefon": ["mobiltelefon", "smartphone", "smarttelefon"],
            "dator": ["dator", "laptop", "bärbar dator", "stationär dator"],
        }

        final_issue_terms = {
            "garanti": [
                "garanti", "garantin", "garantitid", "garantireparation"
            ],
            "reparation": [
                "reparation", "reparera", "reparerat", "reparerades",
                "reparations", "avhjälpa", "avhjälpande",
                "lagning", "laga", "lagade"
            ],
            "reklamation": [
                "reklamation", "reklamera", "reklamerade",
                "felaktig", "defekt"
            ],
            "ångerrätt": [
                "ångerrätt", "ånger", "ångra", "ångrade", "ångrat"
            ],
            "återbetalning": [
                "återbetalning", "återbetala",
                "pengarna tillbaka", "få tillbaka pengarna"
            ],
            "leverans": [
                "leverans", "leverera", "försenad",
                "försening", "dröjsmål"
            ],
        }

        final_products = [
            product for product in final_product_terms
            if product in concepts
        ]

        final_issues = [
            issue for issue in final_issue_terms
            if issue in concepts
        ]

        if final_products and final_issues:
            filtered_output = []

            product_context_terms = [
                "köpt", "köpte", "köpa", "köparen", "köpet",
                "säljaren", "säljare", "vara", "produkt",
                "fel på", "felaktig", "defekt", "reklamation",
                "garanti", "garantireparation", "reparation",
                "reparera", "avhjälpa", "avhjälpande",
                "återbetalning", "hävning", "leverans",
            ]

            for item in output:
                item_text = " ".join(
                    str(item.get(key, ""))
                    for key in (
                        "description",
                        "text",
                        "content",
                        "summary",
                    )
                ).lower()

                match_found = False

                for product in final_products:
                    product_terms = final_product_terms[product]

                    for product_term in product_terms:
                        search_start = 0

                        while True:
                            pos = item_text.find(product_term, search_start)

                            if pos == -1:
                                break

                            sentence_start = item_text.rfind(".", 0, pos) + 1
                            sentence_end = item_text.find(".", pos)

                            if sentence_end == -1:
                                sentence_end = len(item_text)

                            sentence = item_text[sentence_start:sentence_end]

                            product_ok = any(
                                self._contains_term(sentence, context_term)
                                for context_term in product_context_terms
                            )

                            issues_ok = all(
                                any(
                                    self._contains_term(sentence, issue_term)
                                    for issue_term in final_issue_terms[issue]
                                )
                                for issue in final_issues
                            )

                            if product_ok and issues_ok:
                                match_found = True
                                break

                            search_start = pos + len(product_term)

                        if match_found:
                            break

                    if match_found:
                        break

                if match_found:
                    filtered_output.append(item)

            output = filtered_output

        # Produkt-only-sökningar ska inte acceptera fall där produkten
        # bara nämns perifert, t.ex. en dator som används för BankID.
        if final_products and not final_issues:
            filtered_output = []

            product_only_context_terms = [
                "köpt",
                "köpte",
                "köparen",
                "köpet",
                "inköp",
                "beställde",
                "beställt",
                "säljaren",
                "säljare",
                "fel på",
                "felaktig",
                "defekt",
                "reklamation",
                "garanti",
                "reparation",
                "reparera",
                "avhjälpa",
                "avhjälpande",
                "återbetalning",
                "hävning",
                "leverans",
            ]

            for item in output:
                item_text = " ".join(
                    str(item.get(key, ""))
                    for key in (
                        "description",
                        "text",
                        "content",
                        "summary",
                    )
                ).lower()

                product_match = False

                for product in final_products:
                    for product_term in final_product_terms[product]:
                        search_start = 0

                        while True:
                            pos = item_text.find(product_term, search_start)

                            if pos == -1:
                                break

                            sentence_start = item_text.rfind(".", 0, pos) + 1
                            sentence_end = item_text.find(".", pos)

                            if sentence_end == -1:
                                sentence_end = len(item_text)

                            sentence = item_text[sentence_start:sentence_end]

                            if any(
                                self._contains_term(sentence, context_term)
                                for context_term in product_only_context_terms
                            ):
                                product_match = True
                                break

                            search_start = pos + len(product_term)

                        if product_match:
                            break

                    if product_match:
                        break

                if product_match:
                    filtered_output.append(item)

            output = filtered_output

        output.sort(
            key=lambda item: (
                item.get(
                    "score",
                    0,
                ),
                len(
                    item.get(
                        "matched_queries",
                        [],
                    )
                ),
            ),
            reverse=True,
        )

        output = output[:max_results]

        return {
            "problem": problem,
            "concepts": concepts,
            "search_terms": search_terms,
            "count": len(output),
            "results": output,
            "common_cases": common_cases,
        }
