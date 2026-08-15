# SKL-000001: Verified Paper Ingestion Protocol (v1.0)

## Purpose
Standardized protocol for ingesting scientific literature into the Canonical Source Registry with DOI validation and Citation Firewall compliance.

## Preconditions
1. Source must have official publication metadata (DOI, venue, authors, year).
2. Document payload must be placed within `D:\Research` or fetched from legal open-access endpoints.

## Invariants
1. Do not fabricate DOIs or URLs.
2. Distinguish preprints (`PREPRINT`) from peer-reviewed publications (`PEER_REVIEWED_TOP_VENUE`).
3. Exact locators (Section, Page, Paragraph) are mandatory for all extracted evidence units.

## Checklist
- [ ] Verify DOI resolution via CrossRef / official publisher.
- [ ] Compute SHA-256 hash of PDF/source artifact.
- [ ] Extract atomic claims and classify ownership (`SOURCE`).
- [ ] Record exact quote and locator in Evidence Store.
- [ ] Initialize Citation Firewall status as `READY` once evidence is linked.
