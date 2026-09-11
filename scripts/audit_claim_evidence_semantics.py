# -*- coding: utf-8 -*-
"""
scripts/audit_claim_evidence_semantics.py

Reproducible Semantic Verifier (Round 4).
Audits content-level factuality, parent_text_hash binding, self-referential locators,
cross-audit consistency, support semantics, and privacy execution guarantees.

Inputs:
  - experiments/evidence/citation-audit/SCIENTIFIC-CLAIM-AUDIT.json
  - experiments/evidence/citation-audit/SCIENTIFIC-CLAIM-DETECTION.json
  - experiments/evidence/citation-audit/CLAIM-SOURCE-AUDIT.json
  - experiments/evidence/citation-audit/EVIDENCE-LOCATOR-AUDIT.json

Output:
  - experiments/evidence/citation-audit/CLAIM-EVIDENCE-SEMANTIC-AUDIT.json
"""

import sys, json, re, hashlib
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')

def run_semantic_audit():
    repo_root = Path(__file__).resolve().parent.parent

    sci_audit_path = repo_root / "experiments/evidence/citation-audit/SCIENTIFIC-CLAIM-AUDIT.json"
    detection_path = repo_root / "experiments/evidence/citation-audit/SCIENTIFIC-CLAIM-DETECTION.json"
    source_audit_path = repo_root / "experiments/evidence/citation-audit/CLAIM-SOURCE-AUDIT.json"
    locator_audit_path = repo_root / "experiments/evidence/citation-audit/EVIDENCE-LOCATOR-AUDIT.json"
    out_semantic_path = repo_root / "experiments/evidence/citation-audit/CLAIM-EVIDENCE-SEMANTIC-AUDIT.json"

    assert sci_audit_path.exists(), f"Missing {sci_audit_path}"
    assert detection_path.exists(), f"Missing {detection_path}"
    assert source_audit_path.exists(), f"Missing {source_audit_path}"
    assert locator_audit_path.exists(), f"Missing {locator_audit_path}"

    with open(sci_audit_path, "r", encoding="utf-8") as f:
        sci_claims = json.load(f)

    with open(detection_path, "r", encoding="utf-8") as f:
        detection = json.load(f)

    with open(source_audit_path, "r", encoding="utf-8") as f:
        src_claims = {c["claim_id"]: c for c in json.load(f)}

    with open(locator_audit_path, "r", encoding="utf-8") as f:
        locator_claims = {c["claim_id"]: c for c in json.load(f)}

    candidates = {c["detected_id"]: c for c in detection.get("detected_candidates", [])}

    # Gate accumulators
    parent_text_hash_mismatches = 0
    privacy_contradictions = 0
    privacy_exp_without_artifact = 0
    self_referential_locators = 0
    external_fact_disguised = 0
    factual_none_evidence = 0
    false_direct_support = 0
    cross_audit_mismatches = 0

    # Factuality counts
    ext_tech_facts = 0
    ext_emp_facts = 0
    ext_facts_with_evidence = 0
    auth_taxonomies = 0
    auth_specifications = 0
    auth_proposals = 0
    doc_descriptions = 0
    lit_interpretations = 0

    per_claim_records = []

    for a in sci_claims:
        cid = a["claim_id"]
        pid = a.get("parent_detected_id", "")
        c_class = a.get("claim_class", "")
        f_class = a.get("factuality_class", "")
        e_class = a.get("evidence_class", "")
        s_status = a.get("support_status", "")
        cits = a.get("citation_numbers", [])
        src = a.get("source_locator", "")
        code = a.get("code_locator", "")
        art = a.get("artifact_locator", "")
        txt = a.get("atomic_claim", "")
        loc = a.get("document_location", "")

        violations = []

        # 1. Verify parent_text_hash
        cand = candidates.get(pid)
        exp_hash = cand.get("text_hash", "") if cand else ""
        obs_hash = a.get("parent_text_hash", "")
        if not cand:
            violations.append(f"Nonexistent parent_detected_id: {pid}")
        elif exp_hash != obs_hash:
            violations.append(f"parent_text_hash mismatch: expected {exp_hash}, observed {obs_hash}")
            parent_text_hash_mismatches += 1

        # 2. Count factuality
        if f_class == "EXTERNAL_TECHNICAL_FACT":
            ext_tech_facts += 1
        elif f_class == "EXTERNAL_EMPIRICAL_FACT":
            ext_emp_facts += 1
        elif f_class == "LITERATURE_INTERPRETATION":
            lit_interpretations += 1
        elif f_class == "AUTHOR_TAXONOMY":
            auth_taxonomies += 1
        elif f_class == "AUTHOR_SPECIFICATION":
            auth_specifications += 1
        elif f_class == "AUTHOR_PROPOSAL":
            auth_proposals += 1
        elif f_class == "DOCUMENT_DESCRIPTION":
            doc_descriptions += 1
        else:
            violations.append(f"Unknown factuality_class: {f_class}")

        # Check evidence for external facts
        is_external_fact = f_class in ["EXTERNAL_TECHNICAL_FACT", "EXTERNAL_EMPIRICAL_FACT"]
        if is_external_fact:
            has_valid_evid = (
                (e_class == "PRIMARY_PAPER" and len(cits) > 0 and len(src) > 0) or
                (e_class == "CODEBASE" and len(code) > 0) or
                (e_class == "EXPERIMENT_ARTIFACT" and len(art) > 0)
            )
            if has_valid_evid:
                ext_facts_with_evidence += 1
            else:
                violations.append(f"External fact without valid evidence: factuality={f_class}, evidence={e_class}")
                factual_none_evidence += 1

            # Check if disguised as author synthesis without evidence
            if c_class == "AUTHOR_SYNTHESIS" and not has_valid_evid:
                violations.append(f"External fact disguised as AUTHOR_SYNTHESIS without valid evidence")
                external_fact_disguised += 1

        # 3. Disallow evidence_class == NONE for external facts
        if e_class == "NONE":
            if is_external_fact:
                violations.append(f"evidence_class=NONE not allowed for external fact ({f_class})")

        # 4. Check self-referential source_locator
        p_matches = re.findall(r"P(\d+)", loc) + re.findall(r"P(\d+)", pid)
        p_nums = set(int(p) for p in p_matches)
        for p in p_nums:
            if re.search(r"\bP0*" + str(p) + r"\b", src) or re.search(r"Đoạn\s+P?0*" + str(p) + r"\b", src):
                violations.append(f"Self-referential source_locator: references own paragraph P{p}")
                self_referential_locators += 1
                break
        if cid in src:
            violations.append(f"Self-referential source_locator: references own claim_id {cid}")
            self_referential_locators += 1

        # 5. Check Privacy Execution Contradictions
        privacy_terms = ["mia", "membership inference", "model inversion", "tấn công nghịch đảo", "privacy attack"]
        if any(term in txt.lower() for term in privacy_terms):
            if any(term in txt.lower() for term in ["đã kiểm chứng", "đánh giá tại chương 3", "xây dựng đường biên"]) and "chưa thực thi" not in txt.lower() and "hạ nguồn" not in txt.lower():
                if not art:
                    violations.append(f"Privacy attack implies execution without empirical artifact evidence")
                    privacy_contradictions += 1
                    privacy_exp_without_artifact += 1

        # 6. Support-status rule matrix
        if c_class in ["AUTHOR_SYNTHESIS", "AUTHOR_SPECIFICATION", "AUTHOR_PROPOSAL", "AUTHOR_MATHEMATICAL_SPECIFICATION"]:
            if s_status == "DIRECT_SUPPORT":
                violations.append(f"Contradiction: {c_class} cannot have support_status=DIRECT_SUPPORT")
                false_direct_support += 1

        if c_class == "LITERATURE_DIRECT":
            if e_class != "PRIMARY_PAPER":
                violations.append(f"LITERATURE_DIRECT requires evidence_class=PRIMARY_PAPER (got {e_class})")
            if not src:
                violations.append(f"LITERATURE_DIRECT requires source_locator")

        if c_class == "IMPLEMENTATION_VERIFIED":
            if not code:
                violations.append(f"IMPLEMENTATION_VERIFIED requires code_locator")

        if c_class == "EXPERIMENT_ARTIFACT_VERIFIED":
            if not art:
                violations.append(f"EXPERIMENT_ARTIFACT_VERIFIED requires artifact_locator")

        # 7. Cross-audit consistency
        if cid in src_claims:
            sc = src_claims[cid]
            fields_to_check = [
                ("claim_text", txt),
                ("claim_class", c_class),
                ("factuality_class", f_class),
                ("evidence_class", e_class),
                ("support_status", s_status),
                ("citation_numbers", cits),
            ]
            for f_name, f_val in fields_to_check:
                if sc.get(f_name) != f_val:
                    violations.append(f"Cross-audit mismatch for field '{f_name}': SCI='{f_val}' vs SRC='{sc.get(f_name)}'")
                    cross_audit_mismatches += 1

        claim_status = "PASS" if len(violations) == 0 else "FAIL"
        per_claim_records.append({
            "claim_id": cid,
            "parent_detected_id": pid,
            "parent_text_hash_expected": exp_hash,
            "parent_text_hash_observed": obs_hash,
            "claim_class": c_class,
            "factuality_class": f_class,
            "evidence_class": e_class,
            "support_status": s_status,
            "citation_numbers": cits,
            "source_locator": src,
            "code_locator": code,
            "artifact_locator": art,
            "violations": violations,
            "status": claim_status
        })

    unsupported_ext_facts = (ext_tech_facts + ext_emp_facts) - ext_facts_with_evidence

    total_violations = (
        parent_text_hash_mismatches +
        privacy_contradictions +
        privacy_exp_without_artifact +
        self_referential_locators +
        external_fact_disguised +
        factual_none_evidence +
        false_direct_support +
        cross_audit_mismatches +
        unsupported_ext_facts
    )

    overall_status = "PASS" if total_violations == 0 else "FAIL"

    semantic_result = {
        "status": overall_status,
        "gate_title": "CLAIM_EVIDENCE_SEMANTIC_AUDIT",
        "detector_version": "4.0.0-forensic-truth-repair-round-4",
        "reproducible": True,
        "total_claims": len(sci_claims),
        "violations_count": total_violations,
        "gates": {
            "SEMANTIC_AUDIT_REPRODUCIBLE": "YES",
            "PARENT_TEXT_HASH_MISMATCH": parent_text_hash_mismatches,
            "PRIVACY_EXECUTION_CONTRADICTIONS": privacy_contradictions,
            "PRIVACY_EXPERIMENT_WITHOUT_ARTIFACT": privacy_exp_without_artifact,
            "SELF_REFERENTIAL_SOURCE_LOCATORS": self_referential_locators,
            "EXTERNAL_FACT_DISGUISED_AS_AUTHOR_SYNTHESIS": external_fact_disguised,
            "FACTUAL_NONE_EVIDENCE": factual_none_evidence,
            "FALSE_DIRECT_SUPPORT": false_direct_support,
            "CROSS_AUDIT_SEMANTIC_MISMATCH": cross_audit_mismatches,
            "UNSUPPORTED_EXTERNAL_FACTS": unsupported_ext_facts
        },
        "breakdown": {
            "TOTAL_ATOMIC_CLAIMS": len(sci_claims),
            "EXTERNAL_TECHNICAL_FACTS": ext_tech_facts,
            "EXTERNAL_EMPIRICAL_FACTS": ext_emp_facts,
            "EXTERNAL_FACTS_WITH_VALID_EVIDENCE": ext_facts_with_evidence,
            "LITERATURE_INTERPRETATIONS": lit_interpretations,
            "AUTHOR_TAXONOMIES": auth_taxonomies,
            "AUTHOR_SPECIFICATIONS": auth_specifications,
            "AUTHOR_PROPOSALS": auth_proposals,
            "DOCUMENT_DESCRIPTIONS": doc_descriptions,
            "UNSUPPORTED_EXTERNAL_FACTS": unsupported_ext_facts
        },
        "per_claim_records": per_claim_records
    }

    # Fail before mutation: Assert PASS before writing authoritative output
    assert overall_status == "PASS", (
        f"[FAIL-BEFORE-MUTATION] Semantic verification FAILED with {total_violations} violations: "
        f"parent_hash_mismatch={parent_text_hash_mismatches}, "
        f"privacy_contradictions={privacy_contradictions}, "
        f"self_ref={self_referential_locators}, "
        f"disguised={external_fact_disguised}, "
        f"factual_none={factual_none_evidence}, "
        f"cross_mismatch={cross_audit_mismatches}, "
        f"unsupported_ext={unsupported_ext_facts}. "
        f"Output file NOT modified."
    )

    tmp_out = out_semantic_path.with_suffix(".tmp")
    with open(tmp_out, "w", encoding="utf-8") as f:
        json.dump(semantic_result, f, ensure_ascii=False, indent=2)
    tmp_out.replace(out_semantic_path)

    print("\n==================================================")
    print("CLAIM EVIDENCE SEMANTIC VERIFICATION SUMMARY (ROUND 4)")
    print("==================================================")
    print(f"Status:                                       {overall_status}")
    print(f"SEMANTIC_AUDIT_REPRODUCIBLE:                  YES")
    print(f"PARENT_TEXT_HASH_MISMATCH:                    {parent_text_hash_mismatches}")
    print(f"PRIVACY_EXECUTION_CONTRADICTIONS:             {privacy_contradictions}")
    print(f"PRIVACY_EXPERIMENT_WITHOUT_ARTIFACT:          {privacy_exp_without_artifact}")
    print(f"SELF_REFERENTIAL_SOURCE_LOCATORS:             {self_referential_locators}")
    print(f"EXTERNAL_FACT_DISGUISED_AS_AUTHOR_SYNTHESIS:  {external_fact_disguised}")
    print(f"FACTUAL_NONE_EVIDENCE:                        {factual_none_evidence}")
    print(f"FALSE_DIRECT_SUPPORT:                         {false_direct_support}")
    print(f"CROSS_AUDIT_SEMANTIC_MISMATCH:                {cross_audit_mismatches}")
    print(f"UNSUPPORTED_EXTERNAL_FACTS:                   {unsupported_ext_facts}")
    print("--------------------------------------------------")
    print(f"TOTAL_ATOMIC_CLAIMS:                          {len(sci_claims)}")
    print(f"EXTERNAL_TECHNICAL_FACTS:                     {ext_tech_facts}")
    print(f"EXTERNAL_EMPIRICAL_FACTS:                     {ext_emp_facts}")
    print(f"EXTERNAL_FACTS_WITH_VALID_EVIDENCE:           {ext_facts_with_evidence}")
    print(f"LITERATURE_INTERPRETATIONS:                   {lit_interpretations}")
    print(f"AUTHOR_TAXONOMIES:                            {auth_taxonomies}")
    print(f"AUTHOR_SPECIFICATIONS:                        {auth_specifications}")
    print(f"AUTHOR_PROPOSALS:                             {auth_proposals}")
    print(f"DOCUMENT_DESCRIPTIONS:                        {doc_descriptions}")
    print(f"UNSUPPORTED_EXTERNAL_FACTS:                   {unsupported_ext_facts}")
    print("==================================================")
    return semantic_result

if __name__ == "__main__":
    try:
        run_semantic_audit()
        sys.exit(0)
    except AssertionError as e:
        print(f"\n[FAIL-CLOSED ASSERTION ERROR] {e}", file=sys.stderr)
        sys.exit(1)
