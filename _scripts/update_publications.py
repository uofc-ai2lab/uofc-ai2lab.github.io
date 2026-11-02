
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import html
import json
import os
import re
import time

import bibtexparser
import yaml
from bibtexparser.bibdatabase import BibDatabase
from bibtexparser.bwriter import BibTexWriter


ROOT = Path(__file__).resolve().parents[1]
CONFIG_FILE = ROOT / "_scripts" / "publication_config.yml"
AUTO_BIB = ROOT / "_bibliography" / "auto_papers.bib"

API_URL = "https://api.openalex.org/works"
PER_PAGE = 100


def normalize_author_id(value):
    """Accept an OpenAlex author ID or profile URL."""
    value = (value or "").strip().rstrip("/")
    match = re.search(r"(A\d+)$", value)
    return match.group(1) if match else ""


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


def is_duplicate(candidate, existing_entries):
    """Identify duplicate works using DOI or title."""
    doi = clean_doi(candidate.get("doi", ""))
    title = normalize_title(candidate.get("title", ""))

    for existing in existing_entries:
        other_doi = clean_doi(existing.get("doi", ""))
        other_title = normalize_title(existing.get("title", ""))

        if doi and other_doi and doi == other_doi:
            return True

        if title and title == other_title and (
            not doi or not other_doi
        ):
            return True

    return False


def fetch_author_works(author_id, api_key):
    """Retrieve all indexed works for one author using cursor pagination."""
    all_works = []
    cursor = "*"
    seen_cursors = set()

    while cursor:
        if cursor in seen_cursors:
            raise RuntimeError(
                f"Repeated pagination cursor for {author_id}. "
                "Stopping to avoid incomplete retrieval."
            )

        seen_cursors.add(cursor)

        params = {
            "filter": f"authorships.author.id:{author_id}",
            "per_page": PER_PAGE,
            "cursor": cursor,
        }

        if api_key:
            params["api_key"] = api_key

        url = f"{API_URL}?{urlencode(params)}"

        request = Request(
            url,
            headers={
                "User-Agent": "AI2Lab-Publication-Sync/1.0"
            },
        )

        with urlopen(request, timeout=90) as response:
            data = json.loads(
                response.read().decode("utf-8")
            )

        works = data.get("results", [])
        all_works.extend(works)

        next_cursor = data.get("meta", {}).get("next_cursor")

        print(
            f"  Retrieved {len(all_works)} works so far "
            f"for {author_id}..."
        )

        if not works or not next_cursor:
            break

        cursor = next_cursor
        time.sleep(0.2)

    return all_works


def work_to_entry(work):
    """Convert an OpenAlex work into a BibTeX entry."""
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

    # Prefer an open-access landing page or PDF.
    paper_url = (
        open_access.get("landing_page_url")
        or open_access.get("pdf_url")
        or primary.get("landing_page_url")
        or primary.get("pdf_url")
        or ""
    )

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
    surname = re.sub(
        r"[^A-Za-z0-9]", "", first_author
    ) or "paper"

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

    if paper_url:
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
    ):
        value = biblio.get(source_field)

        if value:
            entry[bib_field] = str(value)

    first_page = biblio.get("first_page")
    last_page = biblio.get("last_page")

    if first_page and last_page:
        entry["pages"] = f"{first_page}--{last_page}"
    elif first_page:
        entry["pages"] = str(first_page)

    return entry


def main():
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {CONFIG_FILE}"
        )

    config = yaml.safe_load(
        CONFIG_FILE.read_text(encoding="utf-8")
    ) or {}

    professors = config.get("professors", [])

    if not professors:
        raise RuntimeError(
            "No professors configured in publication_config.yml."
        )

    configured_authors = []

    for professor in professors:
        author_id = normalize_author_id(
            professor.get("openalex_id", "")
        )

        if not author_id:
            raise RuntimeError(
                f"Invalid or missing OpenAlex ID for "
                f"{professor.get('name', 'an unnamed professor')}."
            )

        configured_authors.append({
            "name": professor.get("name", author_id),
            "id": author_id,
        })

    # Avoid retrieving the same profile twice.
    unique_authors = []
    seen_author_ids = set()

    for professor in configured_authors:
        if professor["id"] not in seen_author_ids:
            unique_authors.append(professor)
            seen_author_ids.add(professor["id"])

    api_key = os.environ.get("OPENALEX_API_KEY", "")

    if not api_key:
        print(
            "Warning: OPENALEX_API_KEY is not set. "
            "The request will use unauthenticated access."
        )

    all_works = []
    seen_work_ids = set()

    # Fetch publications for every configured professor.
    for professor in unique_authors:
        author_id = professor["id"]

        print(
            f"\nFetching publications for "
            f"{professor['name']} ({author_id})..."
        )

        works = fetch_author_works(author_id, api_key)

        # Fail safely instead of replacing the bibliography
        # if a configured author returns no records.
        if not works:
            raise RuntimeError(
                f"No works were returned for {author_id}. "
                "The existing bibliography was not changed."
            )

        for work in works:
            work_id = work.get("id")

            if work_id and work_id in seen_work_ids:
                continue

            if work_id:
                seen_work_ids.add(work_id)

            all_works.append(work)

    # Convert works and remove duplicates.
    new_entries = []
    used_entries = []
    used_keys = set()

    for work in all_works:
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

    if not new_entries:
        raise RuntimeError(
            "No valid BibTeX entries were generated. "
            "The existing bibliography was not changed."
        )

    # Generate a completely fresh bibliography.
    output_db = BibDatabase()
    output_db.entries = new_entries

    writer = BibTexWriter()
    writer.indent = "  "
    writer.order_entries_by = None

    output_text = (
        "% Automatically generated from OpenAlex.\n"
        "% Do not edit this file manually.\n\n"
        + bibtexparser.dumps(output_db, writer)
    )

    AUTO_BIB.parent.mkdir(parents=True, exist_ok=True)

    AUTO_BIB.write_text(
        output_text,
        encoding="utf-8"
    )

    print("\n========== PUBLICATION UPDATE SUMMARY ==========")
    print(f"Profiles checked: {len(unique_authors)}")
    print(f"Works retrieved: {len(all_works)}")
    print(f"Unique BibTeX entries: {len(new_entries)}")
    print(f"Generated file: {AUTO_BIB}")
    print("================================================")


if __name__ == "__main__":
    main()
