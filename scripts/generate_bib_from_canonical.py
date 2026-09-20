import json
from pathlib import Path

def generate_bib():
    repo_root = Path(__file__).resolve().parent.parent
    canonical_path = repo_root / "research_specs" / "reference_map" / "CANONICAL-SOURCES.json"
    bib_path = repo_root / "research_specs" / "reference_map" / "BIBLIOGRAPHY.bib"

    with open(canonical_path, "r", encoding="utf-8") as f:
        sources = json.load(f)

    lines = []
    lines.append("% Canonical Bibliography for Chuyen de chuyen sau")
    lines.append(f"% Generated from CANONICAL-SOURCES.json ({len(sources)} sources)")
    lines.append("% Source of Truth: research_specs/reference_map/CANONICAL-SOURCES.json")
    lines.append("")

    for s in sources:
        key = s["source_key"]
        title = s["canonical_title"]
        authors = " and ".join(s["canonical_authors"])
        year = s["year"]
        ptype = s["publication_type"]
        venue = s.get("venue", "")
        doi = s.get("doi")
        url = s.get("url")

        # Determine BibTeX entry type
        if ptype == "PEER_REVIEWED":
            if "Conference" in venue or "Symposium" in venue or "Proceedings" in venue or "Workshop" in venue:
                entry_type = "inproceedings"
                venue_field = "booktitle"
            else:
                entry_type = "article"
                venue_field = "journal"
        elif ptype == "PREPRINT":
            entry_type = "article"
            venue_field = "journal"
        elif ptype == "WEB_ARTICLE":
            entry_type = "article"
            venue_field = "journal"
        elif ptype == "DATASET":
            entry_type = "misc"
            venue_field = "howpublished"
        elif ptype == "OFFICIAL_SOURCE":
            if "NIST" in title or "Special Publication" in venue:
                entry_type = "techreport"
                venue_field = "institution"
            else:
                entry_type = "misc"
                venue_field = "howpublished"
        else:
            entry_type = "misc"
            venue_field = "howpublished"

        lines.append(f"@{entry_type}{{{key},")
        lines.append(f"  author = {{{authors}}},")
        lines.append(f"  title = {{{{{title}}}}},")
        lines.append(f"  year = {{{year}}},")
        if venue:
            lines.append(f"  {venue_field} = {{{venue}}},")
        if doi:
            lines.append(f"  doi = {{{doi}}},")
        if url:
            lines.append(f"  url = {{{url}}},")
        lines.append(f"  note = {{Classification: {ptype}}}")
        lines.append("}")
        lines.append("")

    bib_content = "\n".join(lines)
    with open(bib_path, "w", encoding="utf-8") as f:
        f.write(bib_content)

    print(f"Successfully generated {bib_path} with {len(sources)} entries.")

if __name__ == "__main__":
    generate_bib()
