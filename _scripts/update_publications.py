from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import html
import os
import re
import time

import bibtexparser
import yaml
from bibtexparser.bibdatabase import BibDatabase
from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import BibTexWriter


ROOT = Path(__file__).resolve().parents[1]
CONFIG_FILE = ROOT / "scripts" / "publication_config.yml"
MANUAL_BIB = ROOT / "_bibliography" / "paper.bib"
AUTO_BIB = ROOT / "_bibliography" / "auto_papers.bib"

API_URL = "https://api.openalex.org/works"
PER_PAGE = 100


def load_bib(path):
    """Load a BibTeX file, or return an empty database."""
    db = BibDatabase()

    if not path.exists():
        return db

    parser = BibTexParser(common_strings=True)
    return bibtexparser.loads(
        path.read_text(encoding="utf-8"),
        parser=parser,
    )


def clean_doi(value):
    """Normalize a DOI to its identifier."""
    value = (value or "").strip().lower()

    for prefix in (
        "https://doi.org/",
        "http://doi.org/",
        "https://dx.doi.org/",
        "http://dx.doi.org/",
        "doi:",
    ):
        if value.startswith(prefix):
            value = value[len(prefix):]

    return value.strip().rstrip(" .")


def normalize_title(value):
    """Normalize titles for duplicate detection."""
    value = html.unescape(value or "")
    value = re.sub(r"<[^>]+>", "", value)
    value = value.replace("{", "").replace("}", "")
    return re.sub(r"[^a-z0-9]", "", value.lower())


def entry_doi(entry):
    return clean_doi(entry.get("doi", ""))


def entry_title(entry):
    return normalize_title(entry.get("title", ""))


def is_duplicate(candidate, existing_entries):
    """Match DOI first; use title when either record lacks a DOI."""
    doi = entry_doi(candidate)
    title = entry_title(candidate)

    for existing in existing_entries:
        other_doi = entry_doi(existing)
        other_title = entry_title(existing)

        if doi and other_doi and doi == other_doi:
            return True

        if title and title == other_title and (
            not doi or not other_doi
        ):
            return True

    return False


def normalize_author_id(value):
    """Accept an OpenAlex author ID or profile URL."""
    value = (value or "").strip()
    match = re.search(r"(A\d+)$", value)
    return match.group(1) if match else ""


def fetch_author_works(author_id, api_key):
    """Retrieve works associated with one OpenAlex author."""
    all_works = []
    page = 1

    while True:
        params = {
            "filter": f"author.id:{author_id}",
            "per_page": PER_PAGE,
            "page": page,
        }

        if api_key:
            params["api_key"] = api_key

        url = f"{API_URL}?{urlencode(params)}"
        request = Request(
            url,
            headers={"User-Agent": "AI2Lab-Publication-Sync/1.0"},
        )

        with urlopen(request, timeout=60) as response:
            import json
            data = json.loads(response.read().decode("utf-8"))

        works = data.get("results", [])
        if not works:
            break

        all_works.extend(works)

        total = data.get("meta", {}).get("count", 0)

        # Avoid silently generating an incomplete bibliography.
        if total > 10_000:
            raise RuntimeError(
                f"Author {author_id} has {total} works. "
                "This script's page-based retrieval limit was exceeded."
            )

        if page * PER_PAGE >= total or len(works) < PER_PAGE:
            break

        page += 1
        time.sleep(0.2)

    return all_works


def work_to_entry(work):
    """Convert an OpenAlex work to a BibTeX entry."""
    title = work.get("title") or work.get("display_name")
    if not title:
        return None

    authors = []
    for authorship in work.get("authorships", []):
        author = authorship.get("author") or {}
        name = author.get("display_name")
        if name:
            authors.append(name)

    if not authors:
        authors = ["Unknown"]

    year = work.get("publication_year")
    doi = clean_doi(work.get("doi", ""))

    primary = work.get("primary_location") or {}
    open_access = work.get("best_oa_location") or {}

    primary_source = primary.get("source") or {}
    oa_source = open_access.get("source") or {}
    venue = (
        primary_source.get("display_name")
        or oa_source.get("display_name")
        or ""
    )

    # Prefer an open-access location; otherwise use the primary location.
    paper_url = (
        open_access.get("landing_page_url")
        or open_access.get("pdf_url")
        or primary.get("landing_page_url")
        or primary.get("pdf_url")
        or ""
    )

    doi_url = f"https://doi.org/{doi}" if doi else ""

    entry_type_map = {
        "article": "article",
        "book": "book",
        "book-chapter": "incollection",
        "proceedings-article": "inproceedings",
    }
    entry_type = entry_type_map.get(
        work.get("type", ""), "misc"
    )

    first_author = authors[0].split()[-1]
    surname = re.sub(r"[^A-Za-z0-9]", "", first_author) or "paper"
    year_text = str(year) if year else "nd"
    slug = re.sub(
        r"[^a-z0-9]+", "", title.lower()
    )[:30] or "publication"

    entry = {
        "ENTRYTYPE": entry_type,
        "ID": f"{surname.lower()}{year_text}{slug}",
        "title": title,
        "author": " and ".join(authors),
    }

    if year:
        entry["year"] = str(year)

    if doi:
        entry["doi"] = doi

    # Avoid storing a redundant URL when it is just the DOI link.
    if paper_url and paper_url.rstrip("/") != doi_url.rstrip("/"):
        entry["url"] = paper_url

    if venue:
        if entry_type == "article":
            entry["journal"] = venue
        elif entry_type in ("incollection", "inproceedings"):
            entry["booktitle"] = venue

    biblio = work.get("biblio") or {}
    for source_field, bib_field in (
        ("volume", "volume"),
        ("issue", "number"),
        ("first_page", "pages"),
    ):
        value = biblio.get(source_field)
        if value:
            entry[bib_field] = str(value)

    first_page = biblio.get("first_page")
    last_page = biblio.get("last_page")
    if first_page and last_page:
        entry["pages"] = f"{first_page}--{last_page}"

    return entry


def main():
    config = yaml.safe_load(
        CONFIG_FILE.read_text(encoding="utf-8")
    ) or {}

    professors = config.get("professors", [])
    author_ids = [
        normalize_author_id(p.get("openalex_id", ""))
        for p in professors
    ]
    author_ids = list(dict.fromkeys(
        author_id for author_id in author_ids if author_id
    ))

    if not author_ids:
        print(
            "No OpenAlex profile IDs configured. "
            "Nothing changed; add IDs to publication_config.yml later."
        )
        return

    api_key = os.environ.get("OPENALEX_API_KEY", "")

    manual_db = load_bib(MANUAL_BIB)
    previous_auto_db = load_bib(AUTO_BIB)

    manual_entries = manual_db.entries
    used_entries = list(manual_entries)

    # Retain earlier automated records, except ones now covered manually.
    retained_auto = []
    for entry in previous_auto_db.entries:
        if not is_duplicate(entry, manual_entries):
            retained_auto.append(entry)
            used_entries.append(entry)

    fetched_works = []
    seen_work_ids = set()

    for author_id in author_ids:
        print(f"Fetching publications for {author_id}...")
        works = fetch_author_works(author_id, api_key)

        for work in works:
            work_id = work.get("id")
            if work_id and work_id in seen_work_ids:
                continue
            if work_id:
                seen_work_ids.add(work_id)

            fetched_works.append(work)

    new_entries = []
    used_keys = {
        entry.get("ID", "").lower()
        for entry in used_entries
    }

    for work in fetched_works:
        entry = work_to_entry(work)
        if not entry:
            continue

        if is_duplicate(entry, used_entries):
            continue

        base_key = entry["ID"]
        key = base_key
        suffix = 2

        while key.lower() in used_keys:
            key = f"{base_key}{suffix}"
            suffix += 1

        entry["ID"] = key
        used_keys.add(key.lower())
        used_entries.append(entry)
        new_entries.append(entry)

    output_db = BibDatabase()
    output_db.entries = retained_auto + new_entries

    writer = BibTexWriter()
    writer.indent = "  "
    writer.order_entries_by = None

    output_text = (
        "% Automatically generated from OpenAlex.\n"
        "% Do not edit this file manually.\n\n"
        + bibtexparser.dumps(output_db, writer)
    )

    AUTO_BIB.parent.mkdir(parents=True, exist_ok=True)
    AUTO_BIB.write_text(output_text, encoding="utf-8")

    print(f"Profiles checked: {len(author_ids)}")
    print(f"Works retrieved: {len(fetched_works)}")
    print(f"New entries added: {len(new_entries)}")
    print(f"Generated: {AUTO_BIB}")


if __name__ == "__main__":
    main()
