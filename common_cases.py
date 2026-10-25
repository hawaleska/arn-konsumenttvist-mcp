import html
import re
import requests
from bs4 import BeautifulSoup


class ARNCommonCases:
    URL = "https://www.arn.se/vanligafall/"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/155.0 Safari/537.36"
        })

    def fetch(self):
        response = self.session.get(self.URL, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")
        cases = []

        for article in soup.select("div.accordion > article.accordion-item"):

            heading = article.select_one("h3.accordion-header")
            if not heading:
                continue

            category = heading.get_text(" ", strip=True)
            category = re.sub(r"\s+", " ", category)

            content = article.select_one(".expandable--content")
            if not content:
                continue

            paragraphs = [
                p.get_text(" ", strip=True)
                for p in content.select("p")
                if p.get_text(" ", strip=True)
            ]

            if not paragraphs:
                continue

            case_number = ""
            area = ""

            for paragraph in paragraphs:
                match = re.search(
                    r"Änr\s+([0-9]{4}-[0-9]+)",
                    paragraph,
                    flags=re.IGNORECASE,
                )
                if match:
                    case_number = match.group(1)
                    break

            second = content.select_one(".expandable--content-second")
            if second:
                area = second.get_text(" ", strip=True)

            description_parts = []
            for paragraph in paragraphs:
                if re.search(r"Änr\s+[0-9]{4}-[0-9]+", paragraph, re.IGNORECASE):
                    continue
                description_parts.append(paragraph)

            description = "\n\n".join(description_parts)

            if not description and not case_number:
                continue

            if case_number and any(
                item.get("case_number") == case_number
                for item in cases
            ):
                continue

            cases.append({
                "case_number": case_number,
                "category": category,
                "area": area,
                "description": html.unescape(description),
                "source": self.URL,
            })

        return cases

    def search(self, query, max_results=10):
        query = query.strip().lower()

        if not query:
            return []

        cases = self.fetch()

        terms = [
            term
            for term in re.findall(r"\w+", query, flags=re.UNICODE)
            if len(term) >= 2
        ]

        scored = []

        for case in cases:
            text = " ".join([
                case.get("category", ""),
                case.get("area", ""),
                case.get("description", ""),
                case.get("case_number", ""),
            ]).lower()

            score = 0

            for term in terms:
                if re.search(
                    r"(?<!\w)" + re.escape(term) + r"(?!\w)",
                    text,
                    flags=re.IGNORECASE,
                ):
                    score += 10

            # Starkare vikt för kombinationer som beskriver samma typ av tvist.
            object_groups = {
                "mobiltelefon": [
                    "mobiltelefon",
                    "smartphone",
                    "smarttelefon",
                ],
                "bil": [
                    "bil",
                    "bilen",
                    "bilar",
                    "bilköp",
                    "bilverkstad",
                ],
                "tv": [
                    "tv",
                    "television",
                    "tv-apparat",
                ],
                "dator": [
                    "dator",
                    "laptop",
                    "bärbar dator",
                ],
                "telefon": [
                    "telefon",
                ],
            }

            query_objects = []

            for object_name, object_terms in object_groups.items():
                for term in object_terms:
                    if term in terms:
                        query_objects.append(object_name)
                        break

            case_objects = []

            def has_object(object_terms):
                for term in object_terms:
                    if term == "tv":
                        # "tv" måste vara ett eget ord.
                        # Detta förhindrar t.ex. att "högtryckstvätt"
                        # klassas som TV.
                        tv_patterns = [
                            r"(köpte|köpt|köpa|köpet).{0,100}(?<!\w)(tv|television|tv-apparat)(?!\w)",
                            r"(?<!\w)(tv|television|tv-apparat)(?!\w).{0,100}(köpte|köpt|köpa|köpet)",
                            r"(?<!\w)(tv|television|tv-apparat)(?!\w).{0,100}(garanti|reparation|reparera|avhjälp|fel|säljare)",
                            r"(garanti|reparation|reparera|avhjälp|fel|säljare).{0,100}(?<!\w)(tv|television|tv-apparat)(?!\w)",
                        ]

                        for pattern in tv_patterns:
                            if re.search(
                                pattern,
                                text,
                                flags=re.IGNORECASE,
                            ):
                                return True

                        continue

                    if re.search(
                        r"(?<!\w)" + re.escape(term) + r"(?!\w)",
                        text,
                        flags=re.IGNORECASE,
                    ):
                        return True

                return False

            for object_name, object_terms in object_groups.items():
                if has_object(object_terms):
                    case_objects.append(object_name)

            if query_objects:
                matched_object = False

                for object_name in query_objects:
                    if object_name in case_objects:
                        matched_object = True
                        score += 40

                if not matched_object:
                    score -= 100

                # Vid en specifik mobiltelefonfråga måste fallet
                # faktiskt handla om en mobiltelefon som vara/tvist,
                # inte bara nämna mobiltelefonen som exempelvis
                # mottagare av en SMS-kod.
                if "mobiltelefon" in query_objects:
                    if "mobiltelefon" not in case_objects:
                        continue

                    mobile_context = False

                    context_patterns = [
                        r"köpte.{0,100}mobiltelefon",
                        r"köpt.{0,100}mobiltelefon",
                        r"köpa.{0,100}mobiltelefon",
                        r"mobiltelefon.{0,100}garanti",
                        r"mobiltelefon.{0,100}repar",
                        r"mobiltelefon.{0,100}avhjälp",
                        r"mobiltelefon.{0,100}fel",
                        r"mobiltelefon.{0,100}säljare",
                    ]

                    for pattern in context_patterns:
                        if re.search(
                            pattern,
                            text,
                            flags=re.IGNORECASE,
                        ):
                            mobile_context = True
                            break

                    if not mobile_context:
                        continue

            # Vid en specifik TV-fråga måste fallet faktiskt handla
            # om en TV, inte bara råka innehålla ordet "tv".
            if "tv" in query_objects:
                if "tv" not in case_objects:
                    continue

                tv_context = False

                context_patterns = [
                    r"köpte.{0,100}(tv|television)",
                    r"köpt.{0,100}(tv|television)",
                    r"köpa.{0,100}(tv|television)",
                    r"(tv|television).{0,100}(garanti|reparation|reparera|avhjälp|fel|säljare)",
                    r"(garanti|reparation|reparera|avhjälp|fel|säljare).{0,100}(tv|television)",
                ]

                for pattern in context_patterns:
                    if re.search(
                        pattern,
                        text,
                        flags=re.IGNORECASE,
                    ):
                        tv_context = True
                        break

                if not tv_context:
                    continue

            # Ett mobiltelefonfall ska aldrig rankas som TV-fall.
            if "tv" in query_objects and "mobiltelefon" in text:
                tv_real_case = re.search(
                    r"(tv|television|tv-apparat).{0,120}"
                    r"(köpte|köpt|köpa|garanti|reparation|reparera|avhjälp|fel|säljare)"
                    r"|"
                    r"(köpte|köpt|köpa|garanti|reparation|reparera|avhjälp|fel|säljare).{0,120}"
                    r"(tv|television|tv-apparat)",
                    text,
                    flags=re.IGNORECASE,
                )

                if not tv_real_case:
                    continue

            if (
                "mobiltelefon" in terms
                and "mobiltelefon" in case_objects
                and "garanti" in terms
                and "garanti" in text
            ):
                score += 35

            if (
                "mobiltelefon" in terms
                and "mobiltelefon" in case_objects
                and "reparation" in terms
                and (
                    "reparation" in text
                    or "reparera" in text
                    or "reparations" in text
                )
            ):
                score += 35

            if "tv" in terms and "tv" in text:
                score += 40

            if query in text:
                score += 25

            if score > 0:
                scored.append((score, case))

        scored.sort(key=lambda item: item[0], reverse=True)

        results = []

        for score, case in scored[:max_results]:
            result = dict(case)
            result["score"] = score
            results.append(result)

        return results


if __name__ == "__main__":
    client = ARNCommonCases()

    cases = client.search(
        "mobiltelefon garanti reparation",
        max_results=5,
    )

    for index, case in enumerate(cases, 1):
        print()
        print(index, "|", case["score"], "|", case["case_number"])
        print(case["category"], "|", case["area"])
        print(case["description"][:500])
