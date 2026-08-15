"""
Deterministic Roadmap Specification Compiler and Ingester
Compiles canonical research roadmap data structures into versioned YAML files and ingests into SQLite.
"""

import json
import sys
from pathlib import Path
import yaml

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from research_agent.config import get_default_config
from research_agent.core.hash_utils import compute_string_sha256
from research_agent.schemas.roadmap import (
    ResearchRoadmap,
    ResearchNode,
    ResearchQuestion,
    Hypothesis,
    ResearchAxis,
    RepresentationContract,
    NegativeControl,
    ResearchBoundary,
    DefensibilityQuestion,
    TraceabilityEntry,
)
from research_agent.storage.db import DatabaseManager
from research_agent.storage.repository import ResearchRepository
from research_agent.interfaces.roadmap_ingestion import RoadmapIngestionService


def build_canonical_roadmap_data() -> dict:
    """Build the complete canonical roadmap data structure."""
    
    questions = [
        {
            "rq_id": "RQ-000001",
            "code": "RQ1",
            "title": "REPRESENTATION FIDELITY",
            "canonical_wording_en": "Can a log representation remove syntactic noise while preserving security-critical dynamic parameters?",
            "canonical_wording_vi": "Có thể xây dựng representation loại bỏ nhiễu cú pháp nhưng vẫn bảo toàn các dynamic parameters có ý nghĩa an toàn quan trọng hay không?",
            "target_representation_aspect": "Security-semantic parameter retention vs syntactic noise abstraction",
        },
        {
            "rq_id": "RQ-000002",
            "code": "RQ2",
            "title": "CROSS-VIEW ALIGNMENT",
            "canonical_wording_en": "Can heterogeneous views be aligned without representation collapse or negative transfer while preserving useful view-specific information?",
            "canonical_wording_vi": "Có thể căn chỉnh các view dị thể mà không gây representation collapse, negative transfer, đồng thời vẫn bảo toàn thông tin hữu ích đặc thù của từng view hay không?",
            "target_representation_aspect": "Sequential-provenance cross-view latent alignment and collapse prevention",
        },
        {
            "rq_id": "RQ-000003",
            "code": "RQ3",
            "title": "VALIDITY WITHOUT SHORTCUTS",
            "canonical_wording_en": "Does the representation remain useful after removing dataset shortcuts and under distribution shift?",
            "canonical_wording_vi": "Representation có còn hữu ích sau khi loại bỏ shortcut của dataset và khi phân phối dữ liệu thay đổi hay không?",
            "target_representation_aspect": "Robustness under shortcut removal, OOV templates, and temporal distribution shift",
        },
        {
            "rq_id": "RQ-000004",
            "code": "RQ4",
            "title": "WEAK EVIDENCE ATTRIBUTION",
            "canonical_wording_en": "Can attack evidence be assigned under coarse labels without learning benign administrative behavior as inherently malicious?",
            "canonical_wording_vi": "Có thể gán đúng attack evidence dưới coarse labels mà không học nhầm các hành vi quản trị hợp pháp thành malicious hay không?",
            "target_representation_aspect": "Multiple instance learning and risk-aware administrative confounder control",
        },
        {
            "rq_id": "RQ-000005",
            "code": "RQ5",
            "title": "PRIVACY-SECURITY TRADE-OFF",
            "canonical_wording_en": "What balance between entity continuity and privacy leakage yields useful security representations?",
            "canonical_wording_vi": "Đâu là sự cân bằng chấp nhận được giữa entity continuity và privacy leakage để representation vẫn hữu ích cho phân tích an toàn?",
            "target_representation_aspect": "Controlled linkability vs re-identification and inversion attacks",
        },
    ]

    hypotheses = [
        {
            "hyp_id": "HYP-000001",
            "code": "H1",
            "rq_id": "RQ-000001",
            "title": "FIDELITY",
            "statement": "Parameter-aware representation provides greater security-semantic fidelity than template-only representation.",
            "falsification_criteria": "Frozen probe detection PR-AUC and attribution accuracy on dynamic parameter attacks do not exceed parser-based baseline by statistical significance (p > 0.05).",
        },
        {
            "hyp_id": "HYP-000002",
            "code": "H2",
            "rq_id": "RQ-000002",
            "title": "MULTI-VIEW",
            "statement": "Controlled cross-view alignment improves representation quality without inducing collapse or destructive negative transfer.",
            "falsification_criteria": "Aligned multi-view representation exhibits lower PR-AUC or higher representation variance collapse than the best single-view representation under identical probe capacity.",
        },
        {
            "hyp_id": "HYP-000003",
            "code": "H3",
            "rq_id": "RQ-000003",
            "title": "ROBUSTNESS",
            "statement": "The proposed representation retains useful performance after shortcut removal and under distribution shift.",
            "falsification_criteria": "Representation performance drops to random or lexical-baseline level when dataset shortcuts (host, process, path) are held out or perturbed.",
        },
        {
            "hyp_id": "HYP-000004",
            "code": "H4",
            "rq_id": "RQ-000004",
            "title": "OPERATIONAL",
            "statement": "Any representation-quality improvement must remain within explicit latency, throughput, memory and bounded-state constraints.",
            "falsification_criteria": "Peak memory exceeds stream buffer budget (>500MB/host) or p95 extraction latency exceeds 10ms per event window.",
        },
        {
            "hyp_id": "HYP-000005",
            "code": "H5",
            "rq_id": "RQ-000005",
            "title": "PRIVACY",
            "statement": "Controlled linkability can yield a superior Utility-Privacy trade-off compared with both raw identifiers and extreme anonymization.",
            "falsification_criteria": "Empirical Pareto frontier of Utility vs Re-identification/Inversion risk is strictly dominated by either raw identifiers or complete pseudonymization.",
        },
    ]

    axes = [
        {
            "axis_id": "AXIS-A1",
            "code": "A1",
            "name": "REPRESENTATION FIDELITY",
            "problem_summary": "Security-semantic information loss during dynamic parameter abstraction.",
            "path_nodes": ["1.3.1", "2.2.1", "2.3", "3.2.1", "3.3.1"],
            "core_question": "Can a log representation remove syntactic noise while preserving security-critical dynamic parameters?",
            "core_risks": ["Parameter loss", "Template collision", "Parser instability", "Unseen templates"],
        },
        {
            "axis_id": "AXIS-A2",
            "code": "A2",
            "name": "MULTI-VIEW REPRESENTATION",
            "problem_summary": "Cross-view misalignment, representation collapse, and negative transfer.",
            "path_nodes": ["1.3.2", "2.4", "3.3.1"],
            "core_question": "Can heterogeneous views be aligned without representation collapse or negative transfer?",
            "core_risks": ["Representation collapse", "Negative transfer", "Missing view", "Partial correspondence"],
        },
        {
            "axis_id": "AXIS-A3",
            "code": "A3",
            "name": "VALIDITY UNDER SHIFT",
            "problem_summary": "Pipeline leakage, shortcut learning, and non-stationary distribution drift.",
            "path_nodes": ["1.3.3", "2.1", "2.2", "3.1.2", "3.3.2", "3.3.3"],
            "core_question": "Does the representation remain useful after removing dataset shortcuts and under distribution shift?",
            "core_risks": ["Pipeline leakage", "Dataset shortcuts", "Concept/Template drift", "Adversarial telemetry"],
        },
        {
            "axis_id": "AXIS-A4",
            "code": "A4",
            "name": "WEAK EVIDENCE ATTRIBUTION",
            "problem_summary": "Coarse labels, credit assignment ambiguity, and admin-noise confusion.",
            "path_nodes": ["1.3.4", "2.4.2", "2.4.3", "3.2.3", "3.4.1"],
            "core_question": "Can attack evidence be assigned under coarse labels without learning benign administration as malicious?",
            "core_risks": ["Granularity mismatch", "Wrong credit assignment", "Benign administration confused with attack"],
        },
        {
            "axis_id": "AXIS-A5",
            "code": "A5",
            "name": "PRIVACY-AWARE OPERATIONAL STREAMING",
            "problem_summary": "Entity continuity vs privacy leakage under bounded streaming budgets.",
            "path_nodes": ["1.3.5", "2.1.2", "2.2.2", "3.3.4", "3.4.2"],
            "core_question": "What balance between entity continuity and privacy leakage yields useful security representations?",
            "core_risks": ["Re-identification", "Membership inference", "State explosion", "Excessive latency"],
        },
    ]

    rep_contract = {
        "preserve": [
            "Temporal order of log events",
            "Security-relevant dynamic parameters (IP, path, user, privilege, command arguments)",
            "Entity linkage across log streams",
            "Dependency context and information flows",
        ],
        "invariant": [
            "Benign formatting changes",
            "Template renaming and syntactic noise",
            "Non-semantic identifiers",
        ],
        "exclude": [
            "Dataset IDs and environment artifacts",
            "Campaign IDs and scenario identifiers",
            "Split-specific identifiers",
            "Leakage-derived information",
            "Shortcuts without general security value",
        ],
    }

    controls = [
        {
            "control_id": "CTRL-LEAK-001",
            "category": "LEAKAGE",
            "name": "Anti-Leakage Temporal Split",
            "description": "Strict causal-time split (Train < Val < Test); no random temporal shuffling; preprocessors fit only on Train/Val.",
            "target_nodes": ["1.3.3.1", "2.1.3.2", "2.2.1.3", "3.1.2.3"],
        },
        {
            "control_id": "CTRL-SHORTCUT-001",
            "category": "SHORTCUT",
            "name": "Shortcut Removal & Lexical Baselines",
            "description": "Explicit simple lexical, path, host, and novelty baselines to verify representation learns security semantics rather than environment artifacts.",
            "target_nodes": ["1.3.3.2", "3.2.1.2", "3.2.1.3"],
        },
        {
            "control_id": "CTRL-PROBE-001",
            "category": "PROBE",
            "name": "Capacity-Controlled Frozen Probes",
            "description": "Evaluate representation with frozen extractor using linear/logistic probes, kNN, and shallow MLP without end-to-end retraining.",
            "target_nodes": ["1.1.3.2", "2.4.3.3", "3.1.3.1.2", "3.2.1.3"],
        },
        {
            "control_id": "CTRL-PRIV-001",
            "category": "PRIVACY",
            "name": "Attack-Based Privacy Leakage Audit",
            "description": "Empirical re-identification, linkage, membership inference, and model inversion attack benchmarks.",
            "target_nodes": ["1.3.5.2", "2.2.2.3", "3.3.4.1", "3.3.4.2"],
        },
        {
            "control_id": "CTRL-ADMIN-001",
            "category": "ADMIN_NOISE",
            "name": "Administrative Behavior Confounder Control",
            "description": "Benign-but-risky admin operations (PowerShell, admin tools) explicitly evaluated without username/role shortcuts.",
            "target_nodes": ["1.3.4.2", "2.4.2.1", "2.4.2.2", "3.3.1.1"],
        },
        {
            "control_id": "CTRL-DRIFT-001",
            "category": "DRIFT",
            "name": "Unseen Template and Entity Shift Stress Test",
            "description": "Evaluation under unseen log templates, new hosts, new entities, and novel attack campaigns.",
            "target_nodes": ["1.1.1.2.1", "2.3.2.4", "3.3.2.1", "3.3.2.2"],
        },
        {
            "control_id": "CTRL-ADAPT-001",
            "category": "ADAPTATION",
            "name": "Online Adaptation Contamination Verification",
            "description": "Verify online adaptation mechanisms do not contaminate representation by learning attack labels from test streams.",
            "target_nodes": ["3.3.2.3", "3.3.2.4"],
        },
    ]

    boundaries = [
        {
            "boundary_id": "BOUNDARY-01",
            "title": "Tier A Insufficiency for Attack Semantics",
            "statement": "HDFS/BGL Tier A benchmark alone is insufficient evidence for cyberattack semantics.",
            "rationale": "System logs evaluate parsing and novelty separation, but lack rich entity provenance and multi-stage cyberattack tactics.",
            "affected_sections": ["3.1.2.1", "3.4.3.1"],
        },
        {
            "boundary_id": "BOUNDARY-02",
            "title": "ATT&CK as Evidence Space, Not Linear State Machine",
            "statement": "MITRE ATT&CK tactics and techniques constitute an evidence and behavioral taxonomy, not a mandatory linear state sequence.",
            "rationale": "Real-world multi-stage campaigns exhibit concurrency, backtracking, and technique hopping.",
            "affected_sections": ["1.1.2.1", "3.2.3.2", "3.4.1.4"],
        },
        {
            "boundary_id": "BOUNDARY-03",
            "title": "Dependency Does Not Equal Causality",
            "statement": "Provenance graph dependency does not automatically imply causal relationship without explicit identification assumptions.",
            "rationale": "Observable information flow and OS event sequences must not be claimed as causal mechanisms without causal proof.",
            "affected_sections": ["1.2.3.2", "2.3.2.2"],
        },
        {
            "boundary_id": "BOUNDARY-04",
            "title": "Detector Score Does Not Prove Representation Quality",
            "statement": "High detector accuracy does not automatically prove high-quality feature representation.",
            "rationale": "An over-parameterized downstream detector can compensate for degraded features by learning downstream shortcuts.",
            "affected_sections": ["1.1.3.2", "2.1.1.1", "3.2.1"],
        },
        {
            "boundary_id": "BOUNDARY-05",
            "title": "Deep Architecture Does Not Guarantee Superiority Over Simple Baseline",
            "statement": "High-dimensional or deep neural methods do not automatically outperform well-designed simple baselines.",
            "rationale": "Simple lexical/path/count baselines must be rigorously evaluated to rule out benchmark artifacts.",
            "affected_sections": ["3.2.1.2", "3.4.3.5"],
        },
        {
            "boundary_id": "BOUNDARY-06",
            "title": "Privacy Claim Requires Attack-Based Empirical Evaluation",
            "statement": "A mechanism cannot be claimed as privacy-preserving without empirical leakage evaluation under realistic threat models.",
            "rationale": "Theoretical pseudonymization frequently fails under linkage and membership inference attacks.",
            "affected_sections": ["2.2.2.3", "3.3.4.3"],
        },
        {
            "boundary_id": "BOUNDARY-07",
            "title": "Explanation Plausibility Does Not Equal Fidelity",
            "statement": "Post-hoc explanations do not equal true representation fidelity unless proven to directly govern model predictions.",
            "rationale": "Attribution subgraphs must be quantitatively verified for prediction influence and completeness.",
            "affected_sections": ["3.4.1.1", "3.4.1.2"],
        },
        {
            "boundary_id": "BOUNDARY-08",
            "title": "Offline Metric Does Not Prove Operational Feasibility",
            "statement": "High offline F1-score does not demonstrate operational deployability in SOC/SIEM streaming environments.",
            "rationale": "Operational constraints require bounded state size, low latency (p95), high throughput, and manageable alert burden.",
            "affected_sections": ["2.1.2", "3.1.3.3", "3.4.2"],
        },
        {
            "boundary_id": "BOUNDARY-09",
            "title": "Online Adaptation Must Not Ingest Test Attack Information",
            "statement": "Online stream adaptation cannot learn from test attack events and label that adaptation as generalization.",
            "rationale": "Test stream contamination violates foundational machine learning evaluation contracts.",
            "affected_sections": ["2.1.3.2", "3.3.2.4"],
        },
        {
            "boundary_id": "BOUNDARY-10",
            "title": "Negative Results Are Valid Scientific Outcomes",
            "statement": "Negative results, refuted hypotheses, and failed representations are valid scientific assets, not pipeline failures.",
            "rationale": "Falsification is a core pillar of the scientific method and prevents biased reporting.",
            "affected_sections": ["3.4.3.5"],
        },
    ]

    defensibility_questions = [
        {"question_id": "DQ-01", "question_text": "What exactly is learned?", "target_audit_scope": "Feature manifold z structure and information preservation"},
        {"question_id": "DQ-02", "question_text": "Why should it work?", "target_audit_scope": "Theoretical motivation, loss formulations, and inductive biases"},
        {"question_id": "DQ-03", "question_text": "Could a simpler method obtain the same result?", "target_audit_scope": "Lexical, statistical, and count baseline comparisons"},
        {"question_id": "DQ-04", "question_text": "Could the result be caused by leakage or shortcut learning?", "target_audit_scope": "Anti-leakage splits and shortcut removal controls"},
        {"question_id": "DQ-05", "question_text": "Does it survive distribution shift?", "target_audit_scope": "Unseen templates, unseen hosts, and concept/template drift"},
        {"question_id": "DQ-06", "question_text": "If privacy is claimed, has privacy leakage been measured through attacks?", "target_audit_scope": "ReID, linkage, membership inference, and inversion attacks"},
        {"question_id": "DQ-07", "question_text": "Does the claimed benefit remain under a frozen downstream probe?", "target_audit_scope": "Independent frozen representation evaluation"},
        {"question_id": "DQ-08", "question_text": "What does it cost in latency, throughput, memory and state?", "target_audit_scope": "Operational streaming complexity and bounded state benchmarks"},
        {"question_id": "DQ-09", "question_text": "What fails?", "target_audit_scope": "Error analysis, negative results, and operational edge cases"},
        {"question_id": "DQ-10", "question_text": "Can an independent researcher reproduce it without asking the author?", "target_audit_scope": "Reproducibility artifacts, seeds, manifests, and environment specs"},
    ]

    traceability = [
        {
            "rq_id": "RQ-000001",
            "code": "RQ1",
            "chapter1_gap_nodes": ["1.3.1", "1.3.1.1", "1.3.1.2"],
            "chapter2_mechanism_nodes": ["2.2.1", "2.2.1.1", "2.2.1.2", "2.3.1", "2.3.1.1"],
            "chapter3_evaluation_nodes": ["3.2.1", "3.2.1.1", "3.3.1", "3.3.1.1"],
            "hypothesis_ids": ["HYP-000001"],
            "controls": ["CTRL-SHORTCUT-001", "CTRL-PROBE-001"],
        },
        {
            "rq_id": "RQ-000002",
            "code": "RQ2",
            "chapter1_gap_nodes": ["1.3.2", "1.3.2.1", "1.3.2.2", "1.3.2.3"],
            "chapter2_mechanism_nodes": ["2.4.1", "2.4.1.1", "2.4.1.2", "2.4.1.3", "2.4.3.1"],
            "chapter3_evaluation_nodes": ["3.3.1", "3.3.1.2", "3.3.1.3"],
            "hypothesis_ids": ["HYP-000002"],
            "controls": ["CTRL-PROBE-001"],
        },
        {
            "rq_id": "RQ-000003",
            "code": "RQ3",
            "chapter1_gap_nodes": ["1.3.3", "1.3.3.1", "1.3.3.2", "1.3.3.3"],
            "chapter2_mechanism_nodes": ["2.1.1", "2.1.3.2", "2.2.1.3"],
            "chapter3_evaluation_nodes": ["3.1.2", "3.1.2.3", "3.3.2", "3.3.3"],
            "hypothesis_ids": ["HYP-000003"],
            "controls": ["CTRL-LEAK-001", "CTRL-SHORTCUT-001", "CTRL-DRIFT-001", "CTRL-ADAPT-001"],
        },
        {
            "rq_id": "RQ-000004",
            "code": "RQ4",
            "chapter1_gap_nodes": ["1.3.4", "1.3.4.1", "1.3.4.2", "1.3.4.3"],
            "chapter2_mechanism_nodes": ["2.4.2", "2.4.2.1", "2.4.2.2", "2.4.3.2"],
            "chapter3_evaluation_nodes": ["3.2.3", "3.2.3.2", "3.4.1", "3.4.1.1"],
            "hypothesis_ids": ["HYP-000004"],
            "controls": ["CTRL-ADMIN-001"],
        },
        {
            "rq_id": "RQ-000005",
            "code": "RQ5",
            "chapter1_gap_nodes": ["1.3.5", "1.3.5.1", "1.3.5.2", "1.3.5.3"],
            "chapter2_mechanism_nodes": ["2.1.2", "2.2.2", "2.2.2.1", "2.2.2.2", "2.2.2.3"],
            "chapter3_evaluation_nodes": ["3.3.4", "3.3.4.1", "3.3.4.2", "3.3.4.3", "3.4.2"],
            "hypothesis_ids": ["HYP-000005"],
            "controls": ["CTRL-PRIV-001"],
        },
    ]

    # Build All Hierarchical Roadmap Nodes
    nodes = [
        # --- CHAPTER 1 ---
        {"node_id": "NOD-000001", "parent_node_id": None, "level": 1, "order_index": 1, "code": "1.0", "title": "CHAPTER 1. TỔNG QUAN VỀ PHƯƠNG PHÁP TRÍCH XUẤT ĐẶC TRƯNG DỮ LIỆU LOG VÀ THÁCH THỨC BẢO TOÀN NGỮ CẢNH AN TOÀN", "expected_role": "BACKGROUND", "expected_outputs": ["Định nghĩa bài toán biểu diễn log và bộ tiêu chí đặc trưng"]},
        {"node_id": "NOD-000002", "parent_node_id": "NOD-000001", "level": 2, "order_index": 1, "code": "1.1", "title": "1.1. Bài toán biểu diễn log trong phát hiện tấn công đa giai đoạn", "expected_role": "PROBLEM_DEFINITION"},
        {"node_id": "NOD-000003", "parent_node_id": "NOD-000002", "level": 3, "order_index": 1, "code": "1.1.1", "title": "1.1.1. Không gian dữ liệu log doanh nghiệp: tốc độ cao, mất cân bằng cực đoan và phân phối biến đổi", "expected_role": "PROBLEM_DEFINITION"},
        {"node_id": "NOD-000004", "parent_node_id": "NOD-000003", "level": 4, "order_index": 1, "code": "1.1.1.1", "title": "1.1.1.1. Nguồn log, đơn vị quan sát và tính dị thể", "expected_role": "PROBLEM_DEFINITION"},
        {"node_id": "NOD-000005", "parent_node_id": "NOD-000003", "level": 4, "order_index": 2, "code": "1.1.1.2", "title": "1.1.1.2. Phụ thuộc thời gian, mất cân bằng và các dạng drift", "expected_role": "PROBLEM_DEFINITION", "research_axes": ["A3"]},
        {"node_id": "NOD-000006", "parent_node_id": "NOD-000005", "level": 5, "order_index": 1, "code": "1.1.1.2.1", "title": "1.1.1.2.1. Phân biệt: Concept Drift, Template Drift, Population Drift, Representation Drift", "expected_role": "PROBLEM_DEFINITION", "research_axes": ["A3"]},
        {"node_id": "NOD-000007", "parent_node_id": "NOD-000002", "level": 3, "order_index": 2, "code": "1.1.2", "title": "1.1.2. Hành vi tấn công đa giai đoạn và ánh xạ đa nhãn MITRE ATT&CK tactic/technique", "expected_role": "PROBLEM_DEFINITION"},
        {"node_id": "NOD-000008", "parent_node_id": "NOD-000007", "level": 4, "order_index": 1, "code": "1.1.2.1", "title": "1.1.2.1. ATT&CK như không gian bằng chứng hành vi, không phải chuỗi trạng thái tuyến tính", "expected_role": "PROBLEM_DEFINITION", "methodological_constraints": ["ATT&CK taxonomy is non-linear evidence space"]},
        {"node_id": "NOD-000009", "parent_node_id": "NOD-000007", "level": 4, "order_index": 2, "code": "1.1.2.2", "title": "1.1.2.2. Ground truth, quy tắc ánh xạ và bất định chú thích", "expected_role": "PROBLEM_DEFINITION"},
        {"node_id": "NOD-000010", "parent_node_id": "NOD-000002", "level": 3, "order_index": 3, "code": "1.1.3", "title": "1.1.3. Các mức Token–Event–Sequence/Session–Entity–Graph và Representation Contract", "expected_role": "PROBLEM_DEFINITION"},
        {"node_id": "NOD-000011", "parent_node_id": "NOD-000010", "level": 4, "order_index": 1, "code": "1.1.3.1", "title": "1.1.3.1. Preserve / Invariant / Exclude", "expected_role": "SPECIFICATION"},
        {"node_id": "NOD-000012", "parent_node_id": "NOD-000010", "level": 4, "order_index": 2, "code": "1.1.3.2", "title": "1.1.3.2. Phân biệt: feature extraction, representation learning, detection", "expected_role": "SPECIFICATION", "methodological_constraints": ["Output is feature representation z; detector must not do extractor's job"]},
        {"node_id": "NOD-000013", "parent_node_id": "NOD-000001", "level": 2, "order_index": 2, "code": "1.2", "title": "1.2. Phân tích so sánh các nhóm phương pháp hiện đại", "expected_role": "BACKGROUND"},
        {"node_id": "NOD-000014", "parent_node_id": "NOD-000013", "level": 3, "order_index": 1, "code": "1.2.1", "title": "1.2.1. Phương pháp thống kê/cú pháp: Event Count / Frequency / Entropy / Template Features", "expected_role": "BACKGROUND"},
        {"node_id": "NOD-000015", "parent_node_id": "NOD-000014", "level": 4, "order_index": 1, "code": "1.2.1.1", "title": "1.2.1.1. Cơ chế, ưu điểm và độ phức tạp", "expected_role": "BACKGROUND"},
        {"node_id": "NOD-000016", "parent_node_id": "NOD-000014", "level": 4, "order_index": 2, "code": "1.2.1.2", "title": "1.2.1.2. Mất thông tin do abstraction và phụ thuộc parser", "expected_role": "GAP", "research_axes": ["A1"]},
        {"node_id": "NOD-000017", "parent_node_id": "NOD-000013", "level": 3, "order_index": 2, "code": "1.2.2", "title": "1.2.2. Phương pháp semantic–sequential: embeddings, self-supervised, Transformer, parsing-free", "expected_role": "BACKGROUND"},
        {"node_id": "NOD-000018", "parent_node_id": "NOD-000017", "level": 4, "order_index": 1, "code": "1.2.2.1", "title": "1.2.2.1. DeepLog/LSTM, semantic embedding, masked/self-supervised learning, Transformer, LogBERT và các phương pháp kế tiếp", "expected_role": "BACKGROUND"},
        {"node_id": "NOD-000019", "parent_node_id": "NOD-000017", "level": 4, "order_index": 2, "code": "1.2.2.2", "title": "1.2.2.2. So sánh parser-based, parser-free, pretrained; kiểm soát external information và pretraining-data advantage", "expected_role": "BACKGROUND"},
        {"node_id": "NOD-000020", "parent_node_id": "NOD-000013", "level": 3, "order_index": 3, "code": "1.2.3", "title": "1.2.3. Provenance graph và graph representation learning", "expected_role": "BACKGROUND"},
        {"node_id": "NOD-000021", "parent_node_id": "NOD-000020", "level": 4, "order_index": 1, "code": "1.2.3.1", "title": "1.2.3.1. Các thực thể (process, file, socket, user, host) và edge type, direction, time", "expected_role": "BACKGROUND"},
        {"node_id": "NOD-000022", "parent_node_id": "NOD-000020", "level": 4, "order_index": 2, "code": "1.2.3.2", "title": "1.2.3.2. Các thách thức: dependency explosion, false dependency, long-range dependency, over-smoothing, over-squashing", "expected_role": "GAP", "methodological_constraints": ["dependency != causal effect"]},
        {"node_id": "NOD-000023", "parent_node_id": "NOD-000001", "level": 2, "order_index": 3, "code": "1.3", "title": "1.3. Các khoảng trống nghiên cứu cốt lõi", "expected_role": "GAP"},
        {"node_id": "NOD-000024", "parent_node_id": "NOD-000023", "level": 3, "order_index": 1, "code": "1.3.1", "title": "1.3.1. Mất thông tin security-semantic khi abstraction dynamic parameters", "expected_role": "GAP", "research_axes": ["A1"], "rq_ids": ["RQ-000001"], "hyp_ids": ["HYP-000001"]},
        {"node_id": "NOD-000025", "parent_node_id": "NOD-000024", "level": 4, "order_index": 1, "code": "1.3.1.1", "title": "1.3.1.1. Template equivalence không đồng nghĩa với security semantic equivalence", "expected_role": "GAP", "research_axes": ["A1"]},
        {"node_id": "NOD-000026", "parent_node_id": "NOD-000024", "level": 4, "order_index": 2, "code": "1.3.1.2", "title": "1.3.1.2. RQ1: Có thể loại bỏ syntactic noise nhưng vẫn bảo toàn security-critical dynamic parameters hay không?", "expected_role": "GAP", "research_axes": ["A1"], "rq_ids": ["RQ-000001"]},
        {"node_id": "NOD-000027", "parent_node_id": "NOD-000023", "level": 3, "order_index": 2, "code": "1.3.2", "title": "1.3.2. Cross-view alignment", "expected_role": "GAP", "research_axes": ["A2"], "rq_ids": ["RQ-000002"], "hyp_ids": ["HYP-000002"]},
        {"node_id": "NOD-000028", "parent_node_id": "NOD-000027", "level": 4, "order_index": 1, "code": "1.3.2.1", "title": "1.3.2.1. Các vấn đề: identifiability, representation collapse, negative transfer", "expected_role": "GAP", "research_axes": ["A2"]},
        {"node_id": "NOD-000029", "parent_node_id": "NOD-000027", "level": 4, "order_index": 2, "code": "1.3.2.2", "title": "1.3.2.2. Missing-view và partial correspondence", "expected_role": "GAP", "research_axes": ["A2"]},
        {"node_id": "NOD-000030", "parent_node_id": "NOD-000027", "level": 4, "order_index": 3, "code": "1.3.2.3", "title": "1.3.2.3. RQ2: Có thể align các view mà không collapse/negative transfer, đồng thời giữ thông tin hữu ích đặc thù từng view hay không?", "expected_role": "GAP", "research_axes": ["A2"], "rq_ids": ["RQ-000002"]},
        {"node_id": "NOD-000031", "parent_node_id": "NOD-000023", "level": 3, "order_index": 3, "code": "1.3.3", "title": "1.3.3. Pipeline/Temporal/Identity Leakage, Shortcut Learning và Representation Drift", "expected_role": "GAP", "research_axes": ["A3"], "rq_ids": ["RQ-000003"], "hyp_ids": ["HYP-000003"]},
        {"node_id": "NOD-000032", "parent_node_id": "NOD-000031", "level": 4, "order_index": 1, "code": "1.3.3.1", "title": "1.3.3.1. Các leakage paths: parser/vocabulary, normalization/statistics, host/entity/campaign, threshold/hyperparameter, pretraining, future information", "expected_role": "GAP", "research_axes": ["A3"]},
        {"node_id": "NOD-000033", "parent_node_id": "NOD-000031", "level": 4, "order_index": 2, "code": "1.3.3.2", "title": "1.3.3.2. Dataset shortcut: executable, path, host, template IDs", "expected_role": "GAP", "research_axes": ["A3"]},
        {"node_id": "NOD-000034", "parent_node_id": "NOD-000031", "level": 4, "order_index": 3, "code": "1.3.3.3", "title": "1.3.3.3. RQ3: Representation có còn hữu ích sau khi loại bỏ shortcut hay không?", "expected_role": "GAP", "research_axes": ["A3"], "rq_ids": ["RQ-000003"]},
        {"node_id": "NOD-000035", "parent_node_id": "NOD-000023", "level": 3, "order_index": 4, "code": "1.3.4", "title": "1.3.4. Coarse labels, credit assignment và admin-noise", "expected_role": "GAP", "research_axes": ["A4"], "rq_ids": ["RQ-000004"], "hyp_ids": ["HYP-000004"]},
        {"node_id": "NOD-000036", "parent_node_id": "NOD-000035", "level": 4, "order_index": 1, "code": "1.3.4.1", "title": "1.3.4.1. Label/evidence granularity mismatch", "expected_role": "GAP", "research_axes": ["A4"]},
        {"node_id": "NOD-000037", "parent_node_id": "NOD-000035", "level": 4, "order_index": 2, "code": "1.3.4.2", "title": "1.3.4.2. Benign-but-risky administrative activity không tự thân đồng nghĩa malicious", "expected_role": "GAP", "research_axes": ["A4"]},
        {"node_id": "NOD-000038", "parent_node_id": "NOD-000035", "level": 4, "order_index": 3, "code": "1.3.4.3", "title": "1.3.4.3. RQ4: Có thể assign evidence mà không học benign administrative activity thành malicious hay không?", "expected_role": "GAP", "research_axes": ["A4"], "rq_ids": ["RQ-000004"]},
        {"node_id": "NOD-000039", "parent_node_id": "NOD-000023", "level": 3, "order_index": 5, "code": "1.3.5", "title": "1.3.5. Privacy–Security trade-off", "expected_role": "GAP", "research_axes": ["A5"], "rq_ids": ["RQ-000005"], "hyp_ids": ["HYP-000005"]},
        {"node_id": "NOD-000040", "parent_node_id": "NOD-000039", "level": 4, "order_index": 1, "code": "1.3.5.1", "title": "1.3.5.1. Controlled linkability versus re-identification", "expected_role": "GAP", "research_axes": ["A5"]},
        {"node_id": "NOD-000041", "parent_node_id": "NOD-000039", "level": 4, "order_index": 2, "code": "1.3.5.2", "title": "1.3.5.2. Threats: membership inference, representation/model inversion", "expected_role": "GAP", "research_axes": ["A5"]},
        {"node_id": "NOD-000042", "parent_node_id": "NOD-000039", "level": 4, "order_index": 3, "code": "1.3.5.3", "title": "1.3.5.3. RQ5: Đâu là cân bằng chấp nhận được giữa entity continuity và privacy leakage?", "expected_role": "GAP", "research_axes": ["A5"], "rq_ids": ["RQ-000005"]},

        # --- CHAPTER 2 ---
        {"node_id": "NOD-000043", "parent_node_id": None, "level": 1, "order_index": 2, "code": "2.0", "title": "CHAPTER 2. ĐỀ XUẤT PHƯƠNG PHÁP TRÍCH XUẤT ĐẶC TRƯNG ĐA VIEW BẢO TOÀN NGỮ CẢNH VÀ NHẬN THỨC QUYỀN RIÊNG TƯ", "expected_role": "METHOD", "expected_outputs": ["Extractor contract, multi-view representation architecture, export z"]},
        {"node_id": "NOD-000044", "parent_node_id": "NOD-000043", "level": 2, "order_index": 1, "code": "2.1", "title": "2.1. Phát biểu bài toán và giới hạn streaming", "expected_role": "METHOD"},
        {"node_id": "NOD-000045", "parent_node_id": "NOD-000044", "level": 3, "order_index": 1, "code": "2.1.1", "title": "2.1.1. Multi-view representation, Representation Contract và extractor–detector boundary", "expected_role": "METHOD"},
        {"node_id": "NOD-000046", "parent_node_id": "NOD-000045", "level": 4, "order_index": 1, "code": "2.1.1.1", "title": "2.1.1.1. Canonical abstraction: f_theta: L_{1:t} -> z_t", "expected_role": "SPECIFICATION"},
        {"node_id": "NOD-000047", "parent_node_id": "NOD-000045", "level": 4, "order_index": 2, "code": "2.1.1.2", "title": "2.1.1.2. Hypotheses (H1..H5)", "expected_role": "SPECIFICATION", "hyp_ids": ["HYP-000001", "HYP-000002", "HYP-000003", "HYP-000004", "HYP-000005"]},
        {"node_id": "NOD-000048", "parent_node_id": "NOD-000044", "level": 3, "order_index": 2, "code": "2.1.2", "title": "2.1.2. Bounded-State Streaming Complexity", "expected_role": "MECHANISM", "research_axes": ["A5"], "hyp_ids": ["HYP-000004"]},
        {"node_id": "NOD-000049", "parent_node_id": "NOD-000048", "level": 4, "order_index": 1, "code": "2.1.2.1", "title": "2.1.2.1. State lifecycle: TTL, eviction, compaction/sketching, maximum memory", "expected_role": "MECHANISM", "research_axes": ["A5"]},
        {"node_id": "NOD-000050", "parent_node_id": "NOD-000048", "level": 4, "order_index": 2, "code": "2.1.2.2", "title": "2.1.2.2. Event-time: late events, out-of-order events, missing events, backpressure", "expected_role": "MECHANISM", "research_axes": ["A5"]},
        {"node_id": "NOD-000051", "parent_node_id": "NOD-000048", "level": 4, "order_index": 3, "code": "2.1.2.3", "title": "2.1.2.3. Trade-off: long-horizon APT context vs bounded state", "expected_role": "MECHANISM", "research_axes": ["A5"]},
        {"node_id": "NOD-000052", "parent_node_id": "NOD-000044", "level": 3, "order_index": 3, "code": "2.1.3", "title": "2.1.3. Kiến trúc và I/O", "expected_role": "METHOD"},
        {"node_id": "NOD-000053", "parent_node_id": "NOD-000052", "level": 4, "order_index": 1, "code": "2.1.3.1", "title": "2.1.3.1. Pipeline: Raw logs -> Parsing/Canonicalization -> Context -> Views -> Alignment -> z", "expected_role": "METHOD"},
        {"node_id": "NOD-000054", "parent_node_id": "NOD-000052", "level": 4, "order_index": 2, "code": "2.1.3.2", "title": "2.1.3.2. Phân biệt Training Plane và Inference Plane", "expected_role": "SPECIFICATION", "methodological_constraints": ["No future or test information in streaming inference"]},
        {"node_id": "NOD-000055", "parent_node_id": "NOD-000043", "level": 2, "order_index": 2, "code": "2.2", "title": "2.2. Tiền xử lý và bảo vệ dynamic parameters", "expected_role": "MECHANISM"},
        {"node_id": "NOD-000056", "parent_node_id": "NOD-000055", "level": 3, "order_index": 1, "code": "2.2.1", "title": "2.2.1. Parsing, Typed Canonicalization, Entity Resolution và Security-aware Parameter Retention", "expected_role": "MECHANISM", "research_axes": ["A1"], "rq_ids": ["RQ-000001"], "hyp_ids": ["HYP-000001"]},
        {"node_id": "NOD-000057", "parent_node_id": "NOD-000056", "level": 4, "order_index": 1, "code": "2.2.1.1", "title": "2.2.1.1. Typed schema: timestamp, event type, actor/entity, object, action, dynamic parameters", "expected_role": "MECHANISM", "research_axes": ["A1"]},
        {"node_id": "NOD-000058", "parent_node_id": "NOD-000056", "level": 4, "order_index": 2, "code": "2.2.1.2", "title": "2.2.1.2. Giữ security-semantic parameters, chuẩn hóa formatting noise", "expected_role": "MECHANISM", "research_axes": ["A1"]},
        {"node_id": "NOD-000059", "parent_node_id": "NOD-000056", "level": 4, "order_index": 3, "code": "2.2.1.3", "title": "2.2.1.3. Leakage-safe preprocessing (Train/Val causal-time order)", "expected_role": "MECHANISM", "research_axes": ["A3"]},
        {"node_id": "NOD-000060", "parent_node_id": "NOD-000055", "level": 3, "order_index": 2, "code": "2.2.2", "title": "2.2.2. Privacy Threat Model + Controlled Linkability", "expected_role": "MECHANISM", "research_axes": ["A5"], "rq_ids": ["RQ-000005"], "hyp_ids": ["HYP-000005"]},
        {"node_id": "NOD-000061", "parent_node_id": "NOD-000060", "level": 4, "order_index": 1, "code": "2.2.2.1", "title": "2.2.2.1. Data/entity adversary: linkage, re-identification", "expected_role": "MECHANISM", "research_axes": ["A5"]},
        {"node_id": "NOD-000062", "parent_node_id": "NOD-000060", "level": 4, "order_index": 2, "code": "2.2.2.2", "title": "2.2.2.2. Model adversary: membership inference, representation/model inversion", "expected_role": "MECHANISM", "research_axes": ["A5"]},
        {"node_id": "NOD-000063", "parent_node_id": "NOD-000060", "level": 4, "order_index": 3, "code": "2.2.2.3", "title": "2.2.2.3. Mechanism contract: pseudonymization, tokenization, controlled linkability", "expected_role": "MECHANISM", "research_axes": ["A5"]},
        {"node_id": "NOD-000064", "parent_node_id": "NOD-000055", "level": 3, "order_index": 3, "code": "2.2.3", "title": "2.2.3. Đồng bộ thời gian và multi-scale temporal windows", "expected_role": "MECHANISM"},
        {"node_id": "NOD-000065", "parent_node_id": "NOD-000064", "level": 4, "order_index": 1, "code": "2.2.3.1", "title": "2.2.3.1. Event-time alignment: clock skew, watermark, late tolerance", "expected_role": "MECHANISM"},
        {"node_id": "NOD-000066", "parent_node_id": "NOD-000064", "level": 4, "order_index": 2, "code": "2.2.3.2", "title": "2.2.3.2. Context: short, medium, long/state-summary", "expected_role": "MECHANISM"},
        {"node_id": "NOD-000067", "parent_node_id": "NOD-000043", "level": 2, "order_index": 3, "code": "2.3", "title": "2.3. Multi-view Feature Extraction", "expected_role": "METHOD", "research_axes": ["A1"]},
        {"node_id": "NOD-000068", "parent_node_id": "NOD-000067", "level": 3, "order_index": 1, "code": "2.3.1", "title": "2.3.1. Transformer Semantic–Sequential Extractor", "expected_role": "METHOD", "research_axes": ["A1"], "rq_ids": ["RQ-000001"], "hyp_ids": ["HYP-000001"]},
        {"node_id": "NOD-000069", "parent_node_id": "NOD-000068", "level": 4, "order_index": 1, "code": "2.3.1.1", "title": "2.3.1.1. Event representation: embedding, dynamic parameters, position/time, entity context", "expected_role": "METHOD", "research_axes": ["A1"]},
        {"node_id": "NOD-000070", "parent_node_id": "NOD-000068", "level": 4, "order_index": 2, "code": "2.3.1.2", "title": "2.3.1.2. Self-supervised objectives: masked event, masked parameter, temporal context, contrastive", "expected_role": "METHOD", "research_axes": ["A1"], "methodological_constraints": ["No downstream test labels used in training"]},
        {"node_id": "NOD-000071", "parent_node_id": "NOD-000068", "level": 4, "order_index": 3, "code": "2.3.1.3", "title": "2.3.1.3. Output: z_seq", "expected_role": "SPECIFICATION", "research_axes": ["A1"]},
        {"node_id": "NOD-000072", "parent_node_id": "NOD-000067", "level": 3, "order_index": 2, "code": "2.3.2", "title": "2.3.2. Dependency–Temporal Provenance Graph Construction và Graph Fidelity", "expected_role": "METHOD"},
        {"node_id": "NOD-000073", "parent_node_id": "NOD-000072", "level": 4, "order_index": 1, "code": "2.3.2.1", "title": "2.3.2.1. Typed: nodes, edges, temporal attributes", "expected_role": "METHOD"},
        {"node_id": "NOD-000074", "parent_node_id": "NOD-000072", "level": 4, "order_index": 2, "code": "2.3.2.2", "title": "2.3.2.2. Observable dependency / information flow", "expected_role": "METHOD", "methodological_constraints": ["No causal claim without formal causal assumptions"]},
        {"node_id": "NOD-000075", "parent_node_id": "NOD-000072", "level": 4, "order_index": 3, "code": "2.3.2.3", "title": "2.3.2.3. Kiểm soát: false dependency, long-lived entity contamination, edge pruning, aggregation", "expected_role": "METHOD"},
        {"node_id": "NOD-000076", "parent_node_id": "NOD-000072", "level": 4, "order_index": 4, "code": "2.3.2.4", "title": "2.3.2.4. Cold-start: unseen entities, sparse neighborhoods, new hosts, new processes", "expected_role": "METHOD", "research_axes": ["A3"]},
        {"node_id": "NOD-000077", "parent_node_id": "NOD-000067", "level": 3, "order_index": 3, "code": "2.3.3", "title": "2.3.3. Temporal GNN", "expected_role": "METHOD"},
        {"node_id": "NOD-000078", "parent_node_id": "NOD-000077", "level": 4, "order_index": 1, "code": "2.3.3.1", "title": "2.3.3.1. Typed temporal message passing: edge type, direction, relative time, entity state", "expected_role": "METHOD"},
        {"node_id": "NOD-000079", "parent_node_id": "NOD-000077", "level": 4, "order_index": 2, "code": "2.3.3.2", "title": "2.3.3.2. Kiểm soát: over-smoothing, over-squashing", "expected_role": "METHOD"},
        {"node_id": "NOD-000080", "parent_node_id": "NOD-000077", "level": 4, "order_index": 3, "code": "2.3.3.3", "title": "2.3.3.3. Output: z_graph", "expected_role": "SPECIFICATION"},
        {"node_id": "NOD-000081", "parent_node_id": "NOD-000043", "level": 2, "order_index": 4, "code": "2.4", "title": "2.4. Alignment, objective và administrative behavior", "expected_role": "METHOD", "research_axes": ["A2"], "rq_ids": ["RQ-000002"], "hyp_ids": ["HYP-000002"]},
        {"node_id": "NOD-000082", "parent_node_id": "NOD-000081", "level": 3, "order_index": 1, "code": "2.4.1", "title": "2.4.1. Heterogeneous Cross-view Latent Alignment", "expected_role": "METHOD", "research_axes": ["A2"], "rq_ids": ["RQ-000002"], "hyp_ids": ["HYP-000002"]},
        {"node_id": "NOD-000083", "parent_node_id": "NOD-000082", "level": 4, "order_index": 1, "code": "2.4.1.1", "title": "2.4.1.1. Positive correspondence, hard negatives, partial correspondence", "expected_role": "METHOD", "research_axes": ["A2"]},
        {"node_id": "NOD-000084", "parent_node_id": "NOD-000082", "level": 4, "order_index": 2, "code": "2.4.1.2", "title": "2.4.1.2. Kiểm soát collapse, negative transfer", "expected_role": "METHOD", "research_axes": ["A2"]},
        {"node_id": "NOD-000085", "parent_node_id": "NOD-000082", "level": 4, "order_index": 3, "code": "2.4.1.3", "title": "2.4.1.3. Missing-view modes: semantic-only, graph-only, full multi-view", "expected_role": "METHOD", "research_axes": ["A2"]},
        {"node_id": "NOD-000086", "parent_node_id": "NOD-000081", "level": 3, "order_index": 2, "code": "2.4.2", "title": "2.4.2. Risk-aware Administrative Behavior", "expected_role": "METHOD", "research_axes": ["A4"], "rq_ids": ["RQ-000004"], "hyp_ids": ["HYP-000004"]},
        {"node_id": "NOD-000087", "parent_node_id": "NOD-000086", "level": 4, "order_index": 1, "code": "2.4.2.1", "title": "2.4.2.1. Nguyên tắc: unusual != malicious (privilege, tool, role, context)", "expected_role": "METHOD", "research_axes": ["A4"]},
        {"node_id": "NOD-000088", "parent_node_id": "NOD-000086", "level": 4, "order_index": 2, "code": "2.4.2.2", "title": "2.4.2.2. Confounder control: no privileged test knowledge, username/role shortcut", "expected_role": "METHOD", "research_axes": ["A4"]},
        {"node_id": "NOD-000089", "parent_node_id": "NOD-000081", "level": 3, "order_index": 3, "code": "2.4.3", "title": "2.4.3. Unified Objective + Multiple Instance Learning", "expected_role": "METHOD", "research_axes": ["A4"]},
        {"node_id": "NOD-000090", "parent_node_id": "NOD-000089", "level": 4, "order_index": 1, "code": "2.4.3.1", "title": "2.4.3.1. Canonical high-level objective: L = lambda1 L_seq + lambda2 L_graph + lambda3 L_align + lambda4 L_MIL + lambda5 R", "expected_role": "METHOD"},
        {"node_id": "NOD-000091", "parent_node_id": "NOD-000089", "level": 4, "order_index": 2, "code": "2.4.3.2", "title": "2.4.3.2. Coarse-label credit assignment: bags, instances, evidence score", "expected_role": "METHOD", "research_axes": ["A4"], "rq_ids": ["RQ-000004"]},
        {"node_id": "NOD-000092", "parent_node_id": "NOD-000089", "level": 4, "order_index": 3, "code": "2.4.3.3", "title": "2.4.3.3. Detector-agnostic Export: freeze extractor -> export z -> fixed interface -> downstream evaluation", "expected_role": "SPECIFICATION"},

        # --- CHAPTER 3 ---
        {"node_id": "NOD-000093", "parent_node_id": None, "level": 1, "order_index": 3, "code": "3.0", "title": "CHAPTER 3. THỰC NGHIỆM, ĐÁNH GIÁ VÀ ỨNG DỤNG", "expected_role": "EXPERIMENT", "expected_outputs": ["Benchmark results, ablation ladder, robustness stress tests, reproducibility package"]},
        {"node_id": "NOD-000094", "parent_node_id": "NOD-000093", "level": 2, "order_index": 1, "code": "3.1", "title": "3.1. Thiết lập thực nghiệm và dữ liệu", "expected_role": "EXPERIMENT"},
        {"node_id": "NOD-000095", "parent_node_id": "NOD-000094", "level": 3, "order_index": 1, "code": "3.1.1", "title": "3.1.1. Environment, repeated runs, statistical uncertainty và reproducibility", "expected_role": "EXPERIMENT"},
        {"node_id": "NOD-000096", "parent_node_id": "NOD-000095", "level": 4, "order_index": 1, "code": "3.1.1.1", "title": "3.1.1.1. Experimental manifest: hardware, OS, libraries, model version, dataset hash, config", "expected_role": "EXPERIMENT"},
        {"node_id": "NOD-000097", "parent_node_id": "NOD-000095", "level": 4, "order_index": 2, "code": "3.1.1.2", "title": "3.1.1.2. Repeated seeds, report mean +/- SD, CI/bootstrap", "expected_role": "EXPERIMENT"},
        {"node_id": "NOD-000098", "parent_node_id": "NOD-000095", "level": 4, "order_index": 3, "code": "3.1.1.3", "title": "3.1.1.3. Reproducibility artifact: source code, configs, seeds, split manifest, lock, eval scripts", "expected_role": "EXPERIMENT"},
        {"node_id": "NOD-000099", "parent_node_id": "NOD-000094", "level": 3, "order_index": 2, "code": "3.1.2", "title": "3.1.2. Two-tier Benchmark + Anti-leakage Split", "expected_role": "EXPERIMENT", "research_axes": ["A3"], "rq_ids": ["RQ-000003"], "hyp_ids": ["HYP-000003"]},
        {"node_id": "NOD-000100", "parent_node_id": "NOD-000099", "level": 4, "order_index": 1, "code": "3.1.2.1", "title": "3.1.2.1. TIER A: HDFS / BGL (System-log representation stress test)", "expected_role": "EXPERIMENT", "methodological_constraints": ["Tier A alone is not full proof of attack semantics"]},
        {"node_id": "NOD-000101", "parent_node_id": "NOD-000099", "level": 4, "order_index": 2, "code": "3.1.2.2", "title": "3.1.2.2. TIER B: DARPA TC / LANL hoặc suitable provenance benchmark", "expected_role": "EXPERIMENT"},
        {"node_id": "NOD-000102", "parent_node_id": "NOD-000099", "level": 4, "order_index": 3, "code": "3.1.2.3", "title": "3.1.2.3. Temporal split: Train < Validation < Test (No random temporal shuffling)", "expected_role": "EXPERIMENT", "research_axes": ["A3"]},
        {"node_id": "NOD-000103", "parent_node_id": "NOD-000099", "level": 4, "order_index": 4, "code": "3.1.2.4", "title": "3.1.2.4. Holdout: host, entity, user, campaign, scenario", "expected_role": "EXPERIMENT", "research_axes": ["A3"]},
        {"node_id": "NOD-000104", "parent_node_id": "NOD-000099", "level": 4, "order_index": 5, "code": "3.1.2.5", "title": "3.1.2.5. Validation-only model selection", "expected_role": "EXPERIMENT"},
        {"node_id": "NOD-000105", "parent_node_id": "NOD-000094", "level": 3, "order_index": 3, "code": "3.1.3", "title": "3.1.3. Metrics và evaluation units", "expected_role": "EVALUATION"},
        {"node_id": "NOD-000106", "parent_node_id": "NOD-000105", "level": 4, "order_index": 1, "code": "3.1.3.1", "title": "3.1.3.1. Ba tầng đánh giá: Intrinsic -> Probe -> Operational", "expected_role": "EVALUATION", "methodological_constraints": ["Preserve Intrinsic -> Probe -> Operational evaluation order"]},
        {"node_id": "NOD-000107", "parent_node_id": "NOD-000106", "level": 5, "order_index": 1, "code": "3.1.3.1.1", "title": "3.1.3.1.1. Intrinsic: variance, collapse, cross-view consistency, temporal/entity preservation, stability", "expected_role": "EVALUATION"},
        {"node_id": "NOD-000108", "parent_node_id": "NOD-000106", "level": 5, "order_index": 2, "code": "3.1.3.1.2", "title": "3.1.3.1.2. Probe: Frozen features với linear/logistic probe, distance/kNN, shallow MLP", "expected_role": "EVALUATION"},
        {"node_id": "NOD-000109", "parent_node_id": "NOD-000106", "level": 5, "order_index": 3, "code": "3.1.3.1.3", "title": "3.1.3.1.3. Operational: detection, delay, throughput, latency, memory/state, alert burden", "expected_role": "EVALUATION"},
        {"node_id": "NOD-000110", "parent_node_id": "NOD-000105", "level": 4, "order_index": 2, "code": "3.1.3.2", "title": "3.1.3.2. Metrics: Precision, Recall, F1, PR-AUC, FPR, Recall@fixed FPR, Recall@alert budget", "expected_role": "EVALUATION"},
        {"node_id": "NOD-000111", "parent_node_id": "NOD-000105", "level": 4, "order_index": 3, "code": "3.1.3.3", "title": "3.1.3.3. Operational metrics: delay, events/s, p95 latency, peak/steady memory, state size, alerts/day", "expected_role": "EVALUATION"},
        {"node_id": "NOD-000112", "parent_node_id": "NOD-000093", "level": 2, "order_index": 2, "code": "3.2", "title": "3.2. Kết quả và Benchmarking", "expected_role": "EXPERIMENT"},
        {"node_id": "NOD-000113", "parent_node_id": "NOD-000112", "level": 3, "order_index": 1, "code": "3.2.1", "title": "3.2.1. Independent Representation Quality bằng Capacity-controlled Probe Suite", "expected_role": "EXPERIMENT", "research_axes": ["A1"], "rq_ids": ["RQ-000001"], "hyp_ids": ["HYP-000001"]},
        {"node_id": "NOD-000114", "parent_node_id": "NOD-000113", "level": 4, "order_index": 1, "code": "3.2.1.1", "title": "3.2.1.1. Traditional baselines: statistical, TF-IDF, template/count, LogCluster/equivalent", "expected_role": "EXPERIMENT"},
        {"node_id": "NOD-000115", "parent_node_id": "NOD-000113", "level": 4, "order_index": 2, "code": "3.2.1.2", "title": "3.2.1.2. Simple shortcut baselines: lexical, path, process-name, frequency, novelty", "expected_role": "EXPERIMENT", "research_axes": ["A3"]},
        {"node_id": "NOD-000116", "parent_node_id": "NOD-000113", "level": 4, "order_index": 3, "code": "3.2.1.3", "title": "3.2.1.3. Fair conditions: frozen representation, same probe family, same information, validation threshold", "expected_role": "EXPERIMENT"},
        {"node_id": "NOD-000117", "parent_node_id": "NOD-000112", "level": 3, "order_index": 2, "code": "3.2.2", "title": "3.2.2. Deep/Provenance Modern Baselines", "expected_role": "EXPERIMENT"},
        {"node_id": "NOD-000118", "parent_node_id": "NOD-000117", "level": 4, "order_index": 1, "code": "3.2.2.1", "title": "3.2.2.1. System-log: DeepLog, LogBERT, reproducible recent parser-free/self-supervised methods", "expected_role": "EXPERIMENT"},
        {"node_id": "NOD-000119", "parent_node_id": "NOD-000117", "level": 4, "order_index": 2, "code": "3.2.2.2", "title": "3.2.2.2. Provenance/PIDS: KAIROS, NODLINK, MAGIC, ORTHRUS", "expected_role": "EXPERIMENT"},
        {"node_id": "NOD-000120", "parent_node_id": "NOD-000117", "level": 4, "order_index": 3, "code": "3.2.2.3", "title": "3.2.2.3. Fair comparison: same data, same split, information budget, validation tuning, compute/memory/latency", "expected_role": "EXPERIMENT"},
        {"node_id": "NOD-000121", "parent_node_id": "NOD-000112", "level": 3, "order_index": 3, "code": "3.2.3", "title": "3.2.3. Multi-label MITRE ATT&CK Evidence", "expected_role": "EXPERIMENT", "research_axes": ["A4"], "rq_ids": ["RQ-000004"], "hyp_ids": ["HYP-000004"]},
        {"node_id": "NOD-000122", "parent_node_id": "NOD-000121", "level": 4, "order_index": 1, "code": "3.2.3.1", "title": "3.2.3.1. Ground truth, mapping rules, uncertainty, independent review/inter-annotator agreement", "expected_role": "EXPERIMENT"},
        {"node_id": "NOD-000123", "parent_node_id": "NOD-000121", "level": 4, "order_index": 2, "code": "3.2.3.2", "title": "3.2.3.2. Multi-label mapping: event/entity/subgraph -> Technique/Tactic evidence", "expected_role": "EXPERIMENT", "methodological_constraints": ["Do not collapse ATT&CK into single linear attack stage"]},
        {"node_id": "NOD-000124", "parent_node_id": "NOD-000093", "level": 2, "order_index": 3, "code": "3.3", "title": "3.3. Ablation, Generalization, Robustness và Privacy", "expected_role": "EXPERIMENT"},
        {"node_id": "NOD-000125", "parent_node_id": "NOD-000124", "level": 3, "order_index": 1, "code": "3.3.1", "title": "3.3.1. Controlled Ablation", "expected_role": "EXPERIMENT", "research_axes": ["A1", "A2"], "rq_ids": ["RQ-000001", "RQ-000002"], "hyp_ids": ["HYP-000001", "HYP-000002"]},
        {"node_id": "NOD-000126", "parent_node_id": "NOD-000125", "level": 4, "order_index": 1, "code": "3.3.1.1", "title": "3.3.1.1. Ablation ladder: statistical -> +param -> +seq -> +provenance -> +alignment -> +admin -> +MIL", "expected_role": "EXPERIMENT", "research_axes": ["A1"]},
        {"node_id": "NOD-000127", "parent_node_id": "NOD-000125", "level": 4, "order_index": 2, "code": "3.3.1.2", "title": "3.3.1.2. Unified setup: data, probe, search budget, compute, memory", "expected_role": "EXPERIMENT"},
        {"node_id": "NOD-000128", "parent_node_id": "NOD-000125", "level": 4, "order_index": 3, "code": "3.3.1.3", "title": "3.3.1.3. Interaction ablations: Seq x Graph, Alignment x MIL, Parameter x Privacy", "expected_role": "EXPERIMENT", "research_axes": ["A2"]},
        {"node_id": "NOD-000129", "parent_node_id": "NOD-000124", "level": 3, "order_index": 2, "code": "3.3.2", "title": "3.3.2. Unseen Templates / Cross-domain / Drift", "expected_role": "EXPERIMENT", "research_axes": ["A3"], "rq_ids": ["RQ-000003"], "hyp_ids": ["HYP-000003"]},
        {"node_id": "NOD-000130", "parent_node_id": "NOD-000129", "level": 4, "order_index": 1, "code": "3.3.2.1", "title": "3.3.2.1. Test: unseen templates, hosts, entities, campaigns, scenarios", "expected_role": "EXPERIMENT", "research_axes": ["A3"]},
        {"node_id": "NOD-000131", "parent_node_id": "NOD-000129", "level": 4, "order_index": 2, "code": "3.3.2.2", "title": "3.3.2.2. Drift: Concept, Template, Population, Representation Drift", "expected_role": "EXPERIMENT", "research_axes": ["A3"]},
        {"node_id": "NOD-000132", "parent_node_id": "NOD-000129", "level": 4, "order_index": 3, "code": "3.3.2.3", "title": "3.3.2.3. Compare: frozen vs online adaptation", "expected_role": "EXPERIMENT", "research_axes": ["A3"]},
        {"node_id": "NOD-000133", "parent_node_id": "NOD-000129", "level": 4, "order_index": 4, "code": "3.3.2.4", "title": "3.3.2.4. Adaptation contamination check", "expected_role": "EXPERIMENT", "research_axes": ["A3"], "methodological_constraints": ["Verify model did not learn attack events from test stream"]},
        {"node_id": "NOD-000134", "parent_node_id": "NOD-000124", "level": 3, "order_index": 3, "code": "3.3.3", "title": "3.3.3. Adversarial Telemetry / Log Robustness", "expected_role": "EXPERIMENT", "research_axes": ["A3"], "rq_ids": ["RQ-000003"], "hyp_ids": ["HYP-000003"]},
        {"node_id": "NOD-000135", "parent_node_id": "NOD-000134", "level": 4, "order_index": 1, "code": "3.3.3.1", "title": "3.3.3.1. Semantic-preserving perturbations: rename ID/path, token jitter, timing jitter", "expected_role": "EXPERIMENT", "research_axes": ["A3"]},
        {"node_id": "NOD-000136", "parent_node_id": "NOD-000134", "level": 4, "order_index": 2, "code": "3.3.3.2", "title": "3.3.3.2. Structural perturbations: event insertion, deletion, reordering, suppression, broken link", "expected_role": "EXPERIMENT", "research_axes": ["A3"]},
        {"node_id": "NOD-000137", "parent_node_id": "NOD-000134", "level": 4, "order_index": 3, "code": "3.3.3.3", "title": "3.3.3.3. Mimicry: benign-looking behavior inserted in attack graph", "expected_role": "EXPERIMENT", "research_axes": ["A3"]},
        {"node_id": "NOD-000138", "parent_node_id": "NOD-000134", "level": 4, "order_index": 4, "code": "3.3.3.4", "title": "3.3.3.4. Attack budget protocol with preserved attack semantics", "expected_role": "EXPERIMENT", "research_axes": ["A3"]},
        {"node_id": "NOD-000139", "parent_node_id": "NOD-000124", "level": 3, "order_index": 4, "code": "3.3.4", "title": "3.3.4. Privacy Leakage–Utility", "expected_role": "EXPERIMENT", "research_axes": ["A5"], "rq_ids": ["RQ-000005"], "hyp_ids": ["HYP-000005"]},
        {"node_id": "NOD-000140", "parent_node_id": "NOD-000139", "level": 4, "order_index": 1, "code": "3.3.4.1", "title": "3.3.4.1. Entity privacy: re-identification success, linkage success", "expected_role": "EXPERIMENT", "research_axes": ["A5"]},
        {"node_id": "NOD-000141", "parent_node_id": "NOD-000139", "level": 4, "order_index": 2, "code": "3.3.4.2", "title": "3.3.4.2. Model privacy: membership-inference advantage, inversion leakage", "expected_role": "EXPERIMENT", "research_axes": ["A5"]},
        {"node_id": "NOD-000142", "parent_node_id": "NOD-000139", "level": 4, "order_index": 3, "code": "3.3.4.3", "title": "3.3.4.3. Utility–Privacy frontier: Maximize U(z) while minimizing L_privacy(z)", "expected_role": "EXPERIMENT", "research_axes": ["A5"]},
        {"node_id": "NOD-000143", "parent_node_id": "NOD-000093", "level": 2, "order_index": 4, "code": "3.4", "title": "3.4. Ứng dụng, giải thích và tính hợp lệ", "expected_role": "APPLICATION"},
        {"node_id": "NOD-000144", "parent_node_id": "NOD-000143", "level": 3, "order_index": 1, "code": "3.4.1", "title": "3.4.1. Explanation Fidelity, Evidence Quality và Attribution", "expected_role": "APPLICATION", "research_axes": ["A4"], "rq_ids": ["RQ-000004"]},
        {"node_id": "NOD-000145", "parent_node_id": "NOD-000144", "level": 4, "order_index": 1, "code": "3.4.1.1", "title": "3.4.1.1. Fidelity: Explained evidence must actually affect prediction", "expected_role": "APPLICATION", "research_axes": ["A4"]},
        {"node_id": "NOD-000146", "parent_node_id": "NOD-000144", "level": 4, "order_index": 2, "code": "3.4.1.2", "title": "3.4.1.2. Completeness: Recover relevant attack entities and events", "expected_role": "APPLICATION", "research_axes": ["A4"]},
        {"node_id": "NOD-000147", "parent_node_id": "NOD-000144", "level": 4, "order_index": 3, "code": "3.4.1.3", "title": "3.4.1.3. Compactness / QoA: Analyst effort vs attribution subgraph size", "expected_role": "APPLICATION", "research_axes": ["A4"]},
        {"node_id": "NOD-000148", "parent_node_id": "NOD-000144", "level": 4, "order_index": 4, "code": "3.4.1.4", "title": "3.4.1.4. ATT&CK mapping with uncertainty", "expected_role": "APPLICATION", "research_axes": ["A4"]},
        {"node_id": "NOD-000149", "parent_node_id": "NOD-000143", "level": 3, "order_index": 2, "code": "3.4.2", "title": "3.4.2. SIEM/SOC Streaming Integration", "expected_role": "APPLICATION", "research_axes": ["A5"], "rq_ids": ["RQ-000005"], "hyp_ids": ["HYP-000004"]},
        {"node_id": "NOD-000150", "parent_node_id": "NOD-000149", "level": 4, "order_index": 1, "code": "3.4.2.1", "title": "3.4.2.1. Pipeline: Collectors -> Parser/Normalizer -> State Store -> Extractor -> Detector -> View", "expected_role": "APPLICATION", "research_axes": ["A5"]},
        {"node_id": "NOD-000151", "parent_node_id": "NOD-000149", "level": 4, "order_index": 2, "code": "3.4.2.2", "title": "3.4.2.2. SLO: throughput, p95, memory, state TTL, backpressure", "expected_role": "APPLICATION", "research_axes": ["A5"]},
        {"node_id": "NOD-000152", "parent_node_id": "NOD-000149", "level": 4, "order_index": 3, "code": "3.4.2.3", "title": "3.4.2.3. Failure modes: disconnect, skew, missing telemetry, eviction, parser fail, explosion", "expected_role": "APPLICATION", "research_axes": ["A5"]},
        {"node_id": "NOD-000153", "parent_node_id": "NOD-000143", "level": 3, "order_index": 3, "code": "3.4.3", "title": "3.4.3. Limitations / Threats / Future Work", "expected_role": "LIMITATION"},
        {"node_id": "NOD-000154", "parent_node_id": "NOD-000153", "level": 4, "order_index": 1, "code": "3.4.3.1", "title": "3.4.3.1. Construct validity: anomaly dataset vs cyberattack semantics; ATT&CK ground truth", "expected_role": "LIMITATION"},
        {"node_id": "NOD-000155", "parent_node_id": "NOD-000153", "level": 4, "order_index": 2, "code": "3.4.3.2", "title": "3.4.3.2. Internal validity: leakage, shortcut, hyperparameter selection, threshold, tuning", "expected_role": "LIMITATION"},
        {"node_id": "NOD-000156", "parent_node_id": "NOD-000153", "level": 4, "order_index": 3, "code": "3.4.3.3", "title": "3.4.3.3. External validity: dataset age, synthetic benign data, domain transfer", "expected_role": "LIMITATION"},
        {"node_id": "NOD-000157", "parent_node_id": "NOD-000153", "level": 4, "order_index": 4, "code": "3.4.3.4", "title": "3.4.3.4. Statistical validity: seed instability, confidence intervals, multiple comparisons", "expected_role": "LIMITATION"},
        {"node_id": "NOD-000158", "parent_node_id": "NOD-000153", "level": 4, "order_index": 5, "code": "3.4.3.5", "title": "3.4.3.5. Failure / Negative Results: Falsification and negative outcomes allowed", "expected_role": "LIMITATION", "methodological_constraints": ["Negative results are valid scientific outcomes"]},
        {"node_id": "NOD-000159", "parent_node_id": "NOD-000153", "level": 4, "order_index": 6, "code": "3.4.3.6", "title": "3.4.3.6. Research Artifact Package: source, hashes, split manifests, configs, reproduction steps", "expected_role": "SPECIFICATION"},
    ]

    return {
        "roadmap_id": "ROD-000001",
        "version": "1.0.0",
        "title": "Nghiên cứu phương pháp trích xuất đặc trưng đối với dữ liệu log trong phát hiện tấn công",
        "summary": "Canonical 3-Chapter Research Roadmap and Execution Graph for feature representation z.",
        "central_object": "feature representation z (f_theta: L_{1:t} -> z_t)",
        "questions": questions,
        "hypotheses": hypotheses,
        "axes": axes,
        "representation_contract": rep_contract,
        "controls": controls,
        "boundaries": boundaries,
        "defensibility_questions": defensibility_questions,
        "traceability_matrix": traceability,
        "nodes": nodes,
    }


def compile_and_ingest_roadmap():
    config = get_default_config()
    config.ensure_directories()
    
    spec_dir = config.roadmap_specs_dir
    spec_dir.mkdir(parents=True, exist_ok=True)
    
    roadmap_data = build_canonical_roadmap_data()
    
    # 1. Write structured YAML files
    roadmap_yaml_path = spec_dir / "roadmap.yaml"
    traceability_yaml_path = spec_dir / "traceability.yaml"
    rq_hyp_yaml_path = spec_dir / "rq-hypothesis.yaml"
    axes_yaml_path = spec_dir / "research-axes.yaml"
    controls_yaml_path = spec_dir / "controls.yaml"
    boundaries_yaml_path = spec_dir / "boundaries.yaml"
    version_file_path = spec_dir / "VERSION"

    # YAML serialization
    with open(roadmap_yaml_path, "w", encoding="utf-8") as f:
        yaml.dump(roadmap_data, f, sort_keys=False, allow_unicode=True, indent=2)

    with open(traceability_yaml_path, "w", encoding="utf-8") as f:
        yaml.dump({"traceability_matrix": roadmap_data["traceability_matrix"]}, f, sort_keys=False, allow_unicode=True, indent=2)

    with open(rq_hyp_yaml_path, "w", encoding="utf-8") as f:
        yaml.dump({"questions": roadmap_data["questions"], "hypotheses": roadmap_data["hypotheses"]}, f, sort_keys=False, allow_unicode=True, indent=2)

    with open(axes_yaml_path, "w", encoding="utf-8") as f:
        yaml.dump({"axes": roadmap_data["axes"]}, f, sort_keys=False, allow_unicode=True, indent=2)

    with open(controls_yaml_path, "w", encoding="utf-8") as f:
        yaml.dump({"controls": roadmap_data["controls"]}, f, sort_keys=False, allow_unicode=True, indent=2)

    with open(boundaries_yaml_path, "w", encoding="utf-8") as f:
        yaml.dump({"boundaries": roadmap_data["boundaries"]}, f, sort_keys=False, allow_unicode=True, indent=2)

    # Compute hash of roadmap.yaml
    with open(roadmap_yaml_path, "r", encoding="utf-8") as f:
        raw_text = f.read()
    sha256 = compute_string_sha256(raw_text)
    
    with open(version_file_path, "w", encoding="utf-8") as f:
        f.write(f"VERSION=1.0.0\nSHA256={sha256}\nSTATUS=CANONICAL_SPECIFIED\n")

    # 2. Ingest into Database idempotently
    db_manager = DatabaseManager(config=config)
    repo = ResearchRepository(db_manager)
    ingestion_service = RoadmapIngestionService(repo)
    
    ingested = ingestion_service.ingest_roadmap_dict(roadmap_data, raw_text=raw_text)
    print(f"SUCCESS: Compiled and ingested Canonical Roadmap '{ingested.title}' (Version {ingested.version})")
    print(f"Hash: {sha256}")
    print(f"Total Nodes: {len(ingested.nodes)}, RQs: {len(ingested.questions)}, Hypotheses: {len(ingested.hypotheses)}, Axes: {len(ingested.axes)}")
    return True


if __name__ == "__main__":
    compile_and_ingest_roadmap()
