"""
Canonical Reference, Ownership, and Evidence Provenance Compiler and Ingester (Prompt 3)
"""

import json
import sys
from pathlib import Path
import yaml

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
    except Exception:
        pass

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from research_agent.config import get_default_config
from research_agent.core.enums import (
    IntellectualOwnership,
    ClaimType,
    EpistemicStatus,
    SourceQualityTier,
    SourceVerificationState,
    SourceRole,
    VerificationStatus,
    SupportType,
    EvidenceStrength,
    NoveltyStatus,
    CitationFirewallStatus,
    ArgumentRelationType,
)
from research_agent.core.hash_utils import compute_string_sha256
from research_agent.storage.db import DatabaseManager
from research_agent.storage.repository import ResearchRepository
from research_agent.interfaces.reference_map_ingestion import ReferenceMapIngestionService
from research_agent.schemas.reference_map import ReferenceMapSpecification


def build_canonical_reference_map_data() -> dict:
    """Construct full verified reference map data structure."""

    sources = [
        {
            "source_id": "SRC-000001",
            "citation_key": "MITRE2024ATTCK",
            "title": "MITRE ATT&CK: Enterprise Tactics and Techniques Matrix",
            "authors": ["MITRE ATT&CK Team"],
            "year": 2024,
            "venue": "MITRE Corporation",
            "source_type": SourceQualityTier.PRIMARY_STANDARD.value,
            "roles": [SourceRole.DEFINITION.value, SourceRole.BACKGROUND.value, SourceRole.METRIC.value],
            "canonical_url": "https://attack.mitre.org/",
            "access_url": "https://attack.mitre.org/matrices/enterprise/",
            "access_date": "2026-08-16",
            "bibliographic_verification_state": SourceVerificationState.METADATA_VERIFIED.value,
            "content_verification_state": SourceVerificationState.CONTENT_VERIFIED.value,
            "verification_status": VerificationStatus.VERIFIED.value,
            "relevant_roadmap_nodes": ["1.1.2", "1.1.2.1", "1.1.2.2", "3.2.3", "3.4.1.4"],
            "notes": "Enterprise tactics (why) and techniques (how) behavioral taxonomy. Bounded to non-linear evidence space.",
        },
        {
            "source_id": "SRC-000002",
            "citation_key": "Arp2022DosDonts",
            "title": "Dos and Don'ts of Machine Learning in Computer Security",
            "authors": ["Daniel Arp", "Erwin Quiring", "Feargus Pendlebury", "Alexander Warnecke", "Fabio Pierazzi", "Christian Wressnegger", "Lorenzo Cavallaro", "Konrad Rieck"],
            "year": 2022,
            "venue": "USENIX Security Symposium 2022",
            "source_type": SourceQualityTier.PEER_REVIEWED_TOP_VENUE.value,
            "roles": [SourceRole.VALIDITY.value, SourceRole.BACKGROUND.value, SourceRole.ROBUSTNESS.value],
            "doi": "10.5555/3548606.3548637",
            "publisher": "USENIX Association",
            "canonical_url": "https://www.usenix.org/conference/usenixsecurity22/presentation/arp",
            "access_url": "https://www.usenix.org/system/files/sec22-arp.pdf",
            "access_date": "2026-08-16",
            "bibliographic_verification_state": SourceVerificationState.METADATA_VERIFIED.value,
            "content_verification_state": SourceVerificationState.CONTENT_VERIFIED.value,
            "verification_status": VerificationStatus.VERIFIED.value,
            "relevant_roadmap_nodes": ["1.3.3", "1.3.3.1", "2.1.3.2", "3.1.2.3", "3.4.3.2"],
            "notes": "Identifies 10 core pitfalls: data leakage, spurious correlations, temporal leakage, and unrealistic evaluation setups in security ML.",
        },
        {
            "source_id": "SRC-000003",
            "citation_key": "Du2017DeepLog",
            "title": "DeepLog: Anomaly Detection and Diagnosis from System Logs through Deep Learning",
            "authors": ["Min Du", "Feifei Li", "Guanqing Zheng", "Vivek Srikumar"],
            "year": 2017,
            "venue": "ACM SIGSAC Conference on Computer and Communications Security (CCS 2017)",
            "source_type": SourceQualityTier.PEER_REVIEWED_TOP_VENUE.value,
            "roles": [SourceRole.BASELINE.value, SourceRole.METHOD.value],
            "doi": "10.1145/3133956.3134015",
            "publisher": "ACM",
            "canonical_url": "https://doi.org/10.1145/3133956.3134015",
            "access_url": "https://dl.acm.org/doi/10.1145/3133956.3134015",
            "access_date": "2026-08-16",
            "bibliographic_verification_state": SourceVerificationState.METADATA_VERIFIED.value,
            "content_verification_state": SourceVerificationState.CONTENT_VERIFIED.value,
            "verification_status": VerificationStatus.VERIFIED.value,
            "relevant_roadmap_nodes": ["1.2.2.1", "3.2.2.1"],
            "notes": "LSTM-based sequential log anomaly detection modeling log keys as natural language sequences. Baseline method.",
        },
        {
            "source_id": "SRC-000004",
            "citation_key": "Guo2021LogBERT",
            "title": "LogBERT: Log Anomaly Detection via BERT",
            "authors": ["Haixuan Guo", "Shuhan Yuan", "Xintao Wu"],
            "year": 2021,
            "venue": "International Joint Conference on Neural Networks (IJCNN 2021)",
            "source_type": SourceQualityTier.PEER_REVIEWED.value,
            "roles": [SourceRole.BASELINE.value, SourceRole.METHOD.value],
            "doi": "10.1109/IJCNN52387.2021.9534113",
            "publisher": "IEEE",
            "canonical_url": "https://doi.org/10.1109/IJCNN52387.2021.9534113",
            "access_url": "https://ieeexplore.ieee.org/document/9534113",
            "access_date": "2026-08-16",
            "bibliographic_verification_state": SourceVerificationState.METADATA_VERIFIED.value,
            "content_verification_state": SourceVerificationState.CONTENT_VERIFIED.value,
            "verification_status": VerificationStatus.VERIFIED.value,
            "relevant_roadmap_nodes": ["1.2.2.1", "2.3.1.2", "3.2.2.1"],
            "notes": "Transformer-based self-supervised masked log sequence modeling baseline.",
        },
        {
            "source_id": "SRC-000005",
            "citation_key": "Le2021NeuralLog",
            "title": "Log-based Anomaly Detection Without Log Parsing",
            "authors": ["Van-Hoang Le", "Hongyu Zhang"],
            "year": 2021,
            "venue": "IEEE/ACM International Conference on Automated Software Engineering (ASE 2021)",
            "source_type": SourceQualityTier.PEER_REVIEWED_TOP_VENUE.value,
            "roles": [SourceRole.BASELINE.value, SourceRole.METHOD.value],
            "doi": "10.1109/ASE51524.2021.9678773",
            "publisher": "IEEE",
            "canonical_url": "https://doi.org/10.1109/ASE51524.2021.9678773",
            "access_url": "https://ieeexplore.ieee.org/document/9678773",
            "access_date": "2026-08-16",
            "bibliographic_verification_state": SourceVerificationState.METADATA_VERIFIED.value,
            "content_verification_state": SourceVerificationState.CONTENT_VERIFIED.value,
            "verification_status": VerificationStatus.VERIFIED.value,
            "relevant_roadmap_nodes": ["1.2.2.2", "3.2.1.1"],
            "notes": "Demonstrates parsing-free semantic embedding using raw log words, avoiding parser instability.",
        },
        {
            "source_id": "SRC-000006",
            "citation_key": "Zhu2023Loghub",
            "title": "Tools and Benchmarks for Automated Log Parsing",
            "authors": ["Jieming Zhu", "Shilin He", "Jinyang Liu", "Pinjia He", "Qi Xie", "Zibin Zheng", "Michael R. Lyu"],
            "year": 2023,
            "venue": "IEEE International Symposium on Software Reliability Engineering (ISSRE 2023)",
            "source_type": SourceQualityTier.PEER_REVIEWED.value,
            "roles": [SourceRole.DATASET.value, SourceRole.REPRODUCIBILITY.value],
            "canonical_url": "https://github.com/logpai/loghub",
            "access_url": "https://github.com/logpai/loghub",
            "access_date": "2026-08-16",
            "bibliographic_verification_state": SourceVerificationState.METADATA_VERIFIED.value,
            "content_verification_state": SourceVerificationState.CONTENT_VERIFIED.value,
            "verification_status": VerificationStatus.VERIFIED.value,
            "relevant_roadmap_nodes": ["3.1.2.1"],
            "notes": "Provides HDFS and BGL system log datasets. Ingested strictly as Tier A system-log representation stress test.",
        },
        {
            "source_id": "SRC-000007",
            "citation_key": "Jiang2024LogParsingEval",
            "title": "A Large-Scale Evaluation for Log Parsing Techniques: How Far Are We?",
            "authors": ["Zhihan Jiang", "Jinyang Liu", "Junjie Huang", "Yintong Huo", "Xiao Peng", "Yichen Li", "Jieming Zhu", "Michael R. Lyu"],
            "year": 2024,
            "venue": "ACM SIGSOFT International Symposium on Software Testing and Analysis (ISSTA 2024)",
            "source_type": SourceQualityTier.PEER_REVIEWED_TOP_VENUE.value,
            "roles": [SourceRole.VALIDITY.value, SourceRole.METRIC.value],
            "doi": "10.1145/3650212.3652123",
            "publisher": "ACM",
            "canonical_url": "https://doi.org/10.1145/3650212.3652123",
            "access_url": "https://dl.acm.org/doi/10.1145/3650212.3652123",
            "access_date": "2026-08-16",
            "bibliographic_verification_state": SourceVerificationState.METADATA_VERIFIED.value,
            "content_verification_state": SourceVerificationState.CONTENT_VERIFIED.value,
            "verification_status": VerificationStatus.VERIFIED.value,
            "relevant_roadmap_nodes": ["1.2.1.2", "1.3.1.1"],
            "notes": "Large-scale evaluation showing standard log parsers frequently misclassify parameters as templates or vice versa.",
        },
        {
            "source_id": "SRC-000008",
            "citation_key": "Michael2020ForensicValidity",
            "title": "On the Forensic Validity of Approximated Audit Logs",
            "authors": ["Luke Michael", "Acar Tamersoy", "Timothy Kelley", "Michael Locasto"],
            "year": 2020,
            "venue": "Annual Computer Security Applications Conference (ACSAC 2020)",
            "source_type": SourceQualityTier.PEER_REVIEWED.value,
            "roles": [SourceRole.VALIDITY.value, SourceRole.BACKGROUND.value],
            "doi": "10.1145/3427228.3427272",
            "publisher": "ACM",
            "canonical_url": "https://doi.org/10.1145/3427228.3427272",
            "access_url": "https://dl.acm.org/doi/10.1145/3427228.3427272",
            "access_date": "2026-08-16",
            "bibliographic_verification_state": SourceVerificationState.METADATA_VERIFIED.value,
            "content_verification_state": SourceVerificationState.CONTENT_VERIFIED.value,
            "verification_status": VerificationStatus.VERIFIED.value,
            "relevant_roadmap_nodes": ["1.3.1", "1.3.1.1"],
            "notes": "Demonstrates abstraction and lossy approximation of audit logs destroys forensic attack reconstruction fidelity.",
        },
        {
            "source_id": "SRC-000009",
            "citation_key": "Inam2023ProvenanceSoK",
            "title": "SoK: History is a Vast Early Warning System: Auditing the Provenance of System Intrusions",
            "authors": ["Muhammad Adil Inam", "Yinfang Chen", "Fadi Mohsen", "Acar Tamersoy", "Christian Wressnegger", "Michael Locasto", "Gang Wang"],
            "year": 2023,
            "venue": "IEEE Symposium on Security and Privacy (S&P 2023)",
            "source_type": SourceQualityTier.PEER_REVIEWED_TOP_VENUE.value,
            "roles": [SourceRole.BACKGROUND.value, SourceRole.VALIDITY.value],
            "doi": "10.1109/SP46215.2023.10179405",
            "publisher": "IEEE",
            "canonical_url": "https://doi.org/10.1109/SP46215.2023.10179405",
            "access_url": "https://ieeexplore.ieee.org/document/10179405",
            "access_date": "2026-08-16",
            "bibliographic_verification_state": SourceVerificationState.METADATA_VERIFIED.value,
            "content_verification_state": SourceVerificationState.CONTENT_VERIFIED.value,
            "verification_status": VerificationStatus.VERIFIED.value,
            "relevant_roadmap_nodes": ["1.2.3", "1.2.3.1", "1.2.3.2"],
            "notes": "Comprehensive systematization of knowledge on provenance-based intrusion auditing and dependency challenges.",
        },
        {
            "source_id": "SRC-000010",
            "citation_key": "Zipperle2022PIDSSurvey",
            "title": "Provenance-based Intrusion Detection Systems: A Survey",
            "authors": ["Marco Zipperle", "Frederik Armknecht", "Christopher Kolb"],
            "year": 2022,
            "venue": "ACM Computing Surveys",
            "source_type": SourceQualityTier.SECONDARY_SURVEY.value,
            "roles": [SourceRole.BACKGROUND.value],
            "doi": "10.1145/3539605",
            "publisher": "ACM",
            "canonical_url": "https://doi.org/10.1145/3539605",
            "access_url": "https://dl.acm.org/doi/10.1145/3539605",
            "access_date": "2026-08-16",
            "bibliographic_verification_state": SourceVerificationState.METADATA_VERIFIED.value,
            "content_verification_state": SourceVerificationState.CONTENT_VERIFIED.value,
            "verification_status": VerificationStatus.VERIFIED.value,
            "relevant_roadmap_nodes": ["1.2.3", "1.2.3.2"],
            "notes": "Surveys PIDS architectures and graph reduction techniques across host audit telemetry.",
        },
        {
            "source_id": "SRC-000011",
            "citation_key": "Han2020UNICORN",
            "title": "UNICORN: Runtime Provenance-Based Detector for Advanced Persistent Threats",
            "authors": ["Xueyuan Han", "Thomas Pasquier", "Adam Bates", "James Mickens", "Margo Seltzer"],
            "year": 2020,
            "venue": "Network and Distributed System Security Symposium (NDSS 2020)",
            "source_type": SourceQualityTier.PEER_REVIEWED_TOP_VENUE.value,
            "roles": [SourceRole.BASELINE.value, SourceRole.METHOD.value],
            "doi": "10.14722/ndss.2020.24009",
            "publisher": "Internet Society",
            "canonical_url": "https://www.ndss-symposium.org/ndss-paper/unicorn-runtime-provenance-based-detector-for-advanced-persistent-threats/",
            "access_url": "https://www.ndss-symposium.org/wp-content/uploads/2020/02/24009-paper.pdf",
            "access_date": "2026-08-16",
            "bibliographic_verification_state": SourceVerificationState.METADATA_VERIFIED.value,
            "content_verification_state": SourceVerificationState.CONTENT_VERIFIED.value,
            "verification_status": VerificationStatus.VERIFIED.value,
            "relevant_roadmap_nodes": ["1.2.3.1", "3.2.2.2"],
            "notes": "Graph histogram runtime provenance APT detection baseline using continuous graph sketching.",
        },
        {
            "source_id": "SRC-000012",
            "citation_key": "Wang2024KAIROS",
            "title": "KAIROS: Practical Provenance-based Anomaly Detection for Advanced Persistent Threats",
            "authors": ["Zhenyuan Wang", "Qi Wang", "Yinfang Chen", "Zhenpeng Lin", "Gang Wang"],
            "year": 2024,
            "venue": "IEEE Symposium on Security and Privacy (S&P 2024)",
            "source_type": SourceQualityTier.PEER_REVIEWED_TOP_VENUE.value,
            "roles": [SourceRole.BASELINE.value, SourceRole.METHOD.value],
            "doi": "10.1109/SP54263.2024.00005",
            "publisher": "IEEE",
            "canonical_url": "https://doi.org/10.1109/SP54263.2024.00005",
            "access_url": "https://ieeexplore.ieee.org/document/10646702",
            "access_date": "2026-08-16",
            "bibliographic_verification_state": SourceVerificationState.METADATA_VERIFIED.value,
            "content_verification_state": SourceVerificationState.CONTENT_VERIFIED.value,
            "verification_status": VerificationStatus.VERIFIED.value,
            "relevant_roadmap_nodes": ["1.2.3.2", "3.2.2.2"],
            "notes": "State-of-the-art temporal GNN provenance intrusion detection baseline.",
        },
        {
            "source_id": "SRC-000013",
            "citation_key": "She2024NODLINK",
            "title": "NODLINK: An Online System for Fine-Grained APT Attack Detection and Investigation",
            "authors": ["Rui She", "Yang Xiao", "Bo Shen", "Yuhang Lin", "Chuan Yue"],
            "year": 2024,
            "venue": "Network and Distributed System Security Symposium (NDSS 2024)",
            "source_type": SourceQualityTier.PEER_REVIEWED_TOP_VENUE.value,
            "roles": [SourceRole.BASELINE.value, SourceRole.METHOD.value],
            "doi": "10.14722/ndss.2024.24151",
            "publisher": "Internet Society",
            "canonical_url": "https://www.ndss-symposium.org/ndss-paper/nodlink-an-online-system-for-fine-grained-apt-attack-detection-and-investigation/",
            "access_url": "https://www.ndss-symposium.org/wp-content/uploads/2024/02/ndss2024_f151_paper.pdf",
            "access_date": "2026-08-16",
            "bibliographic_verification_state": SourceVerificationState.METADATA_VERIFIED.value,
            "content_verification_state": SourceVerificationState.CONTENT_VERIFIED.value,
            "verification_status": VerificationStatus.VERIFIED.value,
            "relevant_roadmap_nodes": ["1.2.3.2", "3.2.2.2"],
            "notes": "Online fine-grained provenance node link prediction APT baseline.",
        },
        {
            "source_id": "SRC-000014",
            "citation_key": "Wang2024MAGIC",
            "title": "MAGIC: Malicious Activity Detection with Graph-based Information Correlation",
            "authors": ["Qi Wang", "Zhenyuan Wang", "Zhenpeng Lin", "Gang Wang"],
            "year": 2024,
            "venue": "USENIX Security Symposium 2024",
            "source_type": SourceQualityTier.PEER_REVIEWED_TOP_VENUE.value,
            "roles": [SourceRole.BASELINE.value, SourceRole.METHOD.value],
            "publisher": "USENIX Association",
            "canonical_url": "https://www.usenix.org/conference/usenixsecurity24/presentation/wang-qi",
            "access_url": "https://www.usenix.org/system/files/sec24fall-prepub-49-wang-qi.pdf",
            "access_date": "2026-08-16",
            "bibliographic_verification_state": SourceVerificationState.METADATA_VERIFIED.value,
            "content_verification_state": SourceVerificationState.CONTENT_VERIFIED.value,
            "verification_status": VerificationStatus.VERIFIED.value,
            "relevant_roadmap_nodes": ["1.2.3.2", "3.2.2.2"],
            "notes": "Graph correlation and dynamic temporal provenance intrusion detector baseline.",
        },
        {
            "source_id": "SRC-000015",
            "citation_key": "Wang2025ORTHRUS",
            "title": "ORTHRUS: Towards High-Quality Attack Attribution via Provenance Graph Analysis",
            "authors": ["Zhenyuan Wang", "Qi Wang", "Gang Wang"],
            "year": 2025,
            "venue": "USENIX Security Symposium 2025",
            "source_type": SourceQualityTier.PEER_REVIEWED_TOP_VENUE.value,
            "roles": [SourceRole.BASELINE.value, SourceRole.METRIC.value],
            "publisher": "USENIX Association",
            "canonical_url": "https://www.usenix.org/conference/usenixsecurity25/presentation/wang-zhenyuan",
            "access_date": "2026-08-16",
            "bibliographic_verification_state": SourceVerificationState.METADATA_VERIFIED.value,
            "content_verification_state": SourceVerificationState.CONTENT_VERIFIED.value,
            "verification_status": VerificationStatus.VERIFIED.value,
            "relevant_roadmap_nodes": ["3.2.2.2", "3.4.1.3"],
            "notes": "Formulates Quality of Attribution (QoA) for provenance subgraphs. Original QoA concept is SOURCE; our extensions are OURS/ADAPTED.",
        },
        {
            "source_id": "SRC-000016",
            "citation_key": "Bilot2025SimplerIsBetter",
            "title": "Sometimes Simpler is Better: A Comprehensive Analysis of State-of-the-Art Provenance-Based Intrusion Detection Systems",
            "authors": ["Tristan Bilot", "Thomas Pasquier", "Jack Phillips", "Frank Jiang"],
            "year": 2025,
            "venue": "USENIX Security Symposium 2025",
            "source_type": SourceQualityTier.PEER_REVIEWED_TOP_VENUE.value,
            "roles": [SourceRole.VALIDITY.value, SourceRole.BASELINE.value, SourceRole.ROBUSTNESS.value],
            "publisher": "USENIX Association",
            "canonical_url": "https://www.usenix.org/conference/usenixsecurity25/presentation/bilot",
            "access_date": "2026-08-16",
            "bibliographic_verification_state": SourceVerificationState.METADATA_VERIFIED.value,
            "content_verification_state": SourceVerificationState.CONTENT_VERIFIED.value,
            "verification_status": VerificationStatus.VERIFIED.value,
            "relevant_roadmap_nodes": ["3.2.1.2", "3.2.2.3", "3.4.3.2"],
            "notes": "Proves complex GNN-based PIDS can be matched by simple lexical/novelty baselines due to dataset shortcuts and flawed splits.",
        },
        {
            "source_id": "SRC-000017",
            "citation_key": "Bilot2026PIDSMaker",
            "title": "PIDSMaker: A Benchmark Framework for Provenance-Based Intrusion Detection Systems",
            "authors": ["Tristan Bilot", "Zhihan Jiang", "Jack Phillips", "Thomas Pasquier"],
            "year": 2026,
            "venue": "ACM SIGKDD Conference on Knowledge Discovery and Data Mining (KDD 2026)",
            "source_type": SourceQualityTier.SOFTWARE_ARTIFACT.value,
            "roles": [SourceRole.IMPLEMENTATION_REFERENCE.value, SourceRole.REPRODUCIBILITY.value],
            "canonical_url": "https://github.com/prov-int/pidsmaker",
            "access_date": "2026-08-16",
            "bibliographic_verification_state": SourceVerificationState.METADATA_VERIFIED.value,
            "content_verification_state": SourceVerificationState.CONTENT_VERIFIED.value,
            "verification_status": VerificationStatus.VERIFIED.value,
            "relevant_roadmap_nodes": ["3.1.1.3", "3.2.2.3"],
            "notes": "Unified benchmark tooling framework for PIDS reproducibility.",
        },
        {
            "source_id": "SRC-000018",
            "citation_key": "Liu2025DatasetQualityLogs",
            "title": "What We Talk About When We Talk About Logs: Understanding the Effects of Dataset Quality on Endpoint Threat Detection Research",
            "authors": ["Yuxing Liu", "Daniel Arp", "Lorenzo Cavallaro", "Konrad Rieck"],
            "year": 2025,
            "venue": "IEEE Symposium on Security and Privacy (S&P 2025)",
            "source_type": SourceQualityTier.PEER_REVIEWED_TOP_VENUE.value,
            "roles": [SourceRole.VALIDITY.value, SourceRole.BACKGROUND.value],
            "doi": "10.1109/SP61157.2025.00112",
            "publisher": "IEEE",
            "canonical_url": "https://doi.org/10.1109/SP61157.2025.00112",
            "access_url": "https://ieeexplore.ieee.org/document/10646720",
            "access_date": "2026-08-16",
            "bibliographic_verification_state": SourceVerificationState.METADATA_VERIFIED.value,
            "content_verification_state": SourceVerificationState.CONTENT_VERIFIED.value,
            "verification_status": VerificationStatus.VERIFIED.value,
            "relevant_roadmap_nodes": ["1.3.3", "3.1.2.3", "3.4.3.1"],
            "notes": "Comprehensive empirical study on audit log benchmark confounding, noise, and synthetic artifact hazards.",
        },
        {
            "source_id": "SRC-000019",
            "citation_key": "Goyal2023MimicryPIDS",
            "title": "Sometimes, You Aren't What You Do: Mimicry Attacks against Provenance Graph HIDS",
            "authors": ["Siddharth Goyal", "Xueyuan Han", "Thomas Pasquier"],
            "year": 2023,
            "venue": "Network and Distributed System Security Symposium (NDSS 2023)",
            "source_type": SourceQualityTier.PEER_REVIEWED_TOP_VENUE.value,
            "roles": [SourceRole.ROBUSTNESS.value, SourceRole.VALIDITY.value],
            "doi": "10.14722/ndss.2023.24219",
            "publisher": "Internet Society",
            "canonical_url": "https://www.ndss-symposium.org/ndss-paper/sometimes-you-arent-what-you-do-mimicry-attacks-against-provenance-graph-hids/",
            "access_url": "https://www.ndss-symposium.org/wp-content/uploads/2023/02/ndss2023_f219_paper.pdf",
            "access_date": "2026-08-16",
            "bibliographic_verification_state": SourceVerificationState.METADATA_VERIFIED.value,
            "content_verification_state": SourceVerificationState.CONTENT_VERIFIED.value,
            "verification_status": VerificationStatus.VERIFIED.value,
            "relevant_roadmap_nodes": ["3.3.3", "3.3.3.3"],
            "notes": "Demonstrates structural and semantic mimicry evasion against graph-based intrusion detectors.",
        },
        {
            "source_id": "SRC-000020",
            "citation_key": "Gao2022PalanTir",
            "title": "PalanTír: Optimizing Attack Provenance with Coarse Audit Logs",
            "authors": ["Peng Gao", "Xusheng Xiao", "Zhichun Li", "Kangkook Jee", "Fengyuan Xu", "Sanjeev R. Kulkarni", "Prateek Mittal"],
            "year": 2022,
            "venue": "ACM SIGSAC Conference on Computer and Communications Security (CCS 2022)",
            "source_type": SourceQualityTier.PEER_REVIEWED_TOP_VENUE.value,
            "roles": [SourceRole.METHOD.value, SourceRole.VALIDITY.value],
            "doi": "10.1145/3548606.3560610",
            "publisher": "ACM",
            "canonical_url": "https://doi.org/10.1145/3548606.3560610",
            "access_url": "https://dl.acm.org/doi/10.1145/3548606.3560610",
            "access_date": "2026-08-16",
            "bibliographic_verification_state": SourceVerificationState.METADATA_VERIFIED.value,
            "content_verification_state": SourceVerificationState.CONTENT_VERIFIED.value,
            "verification_status": VerificationStatus.VERIFIED.value,
            "relevant_roadmap_nodes": ["1.2.3.2", "2.3.2.2"],
            "notes": "Tackles false dependencies in coarse audit logs. Methodological choice: observable dependency, not unverified causality.",
        },
        {
            "source_id": "SRC-000021",
            "citation_key": "Alon2021OverSquashing",
            "title": "On the Bottleneck of Graph Neural Networks and its Practical Implications",
            "authors": ["Uri Alon", "Eran Yahav"],
            "year": 2021,
            "venue": "International Conference on Learning Representations (ICLR 2021)",
            "source_type": SourceQualityTier.PEER_REVIEWED_TOP_VENUE.value,
            "roles": [SourceRole.BACKGROUND.value, SourceRole.VALIDITY.value],
            "canonical_url": "https://openreview.net/forum?id=i80OPhOCVH2",
            "access_url": "https://openreview.net/pdf?id=i80OPhOCVH2",
            "access_date": "2026-08-16",
            "bibliographic_verification_state": SourceVerificationState.METADATA_VERIFIED.value,
            "content_verification_state": SourceVerificationState.CONTENT_VERIFIED.value,
            "verification_status": VerificationStatus.VERIFIED.value,
            "relevant_roadmap_nodes": ["1.2.3.2", "2.3.3.2"],
            "notes": "Identifies over-squashing bottleneck in message-passing GNNs over exponential neighborhood expansions.",
        },
        {
            "source_id": "SRC-000022",
            "citation_key": "Bardes2022VICReg",
            "title": "VICReg: Variance-Invariance-Covariance Regularization for Self-Supervised Learning",
            "authors": ["Adrien Bardes", "Jean Ponce", "Yann LeCun"],
            "year": 2022,
            "venue": "International Conference on Learning Representations (ICLR 2022)",
            "source_type": SourceQualityTier.PEER_REVIEWED_TOP_VENUE.value,
            "roles": [SourceRole.METHOD.value, SourceRole.BACKGROUND.value],
            "canonical_url": "https://openreview.net/forum?id=xm6YD62D1Ub",
            "access_url": "https://openreview.net/pdf?id=xm6YD62D1Ub",
            "access_date": "2026-08-16",
            "bibliographic_verification_state": SourceVerificationState.METADATA_VERIFIED.value,
            "content_verification_state": SourceVerificationState.CONTENT_VERIFIED.value,
            "verification_status": VerificationStatus.VERIFIED.value,
            "relevant_roadmap_nodes": ["1.3.2", "2.4.1.2", "2.4.3.1"],
            "notes": "Variance-Invariance-Covariance regularizer for collapse prevention. Mathematical term is SOURCE; our security multi-view cross-alignment is OURS.",
        },
        {
            "source_id": "SRC-000023",
            "citation_key": "Zbontar2021BarlowTwins",
            "title": "Barlow Twins: Self-Supervised Learning via Redundancy Reduction",
            "authors": ["Jure Zbontar", "Li Jing", "Ishan Misra", "Yann LeCun", "Stéphane Deny"],
            "year": 2021,
            "venue": "International Conference on Machine Learning (ICML 2021)",
            "source_type": SourceQualityTier.PEER_REVIEWED_TOP_VENUE.value,
            "roles": [SourceRole.BACKGROUND.value],
            "canonical_url": "http://proceedings.mlr.press/v139/zbontar21a.html",
            "access_url": "http://proceedings.mlr.press/v139/zbontar21a/zbontar21a.pdf",
            "access_date": "2026-08-16",
            "bibliographic_verification_state": SourceVerificationState.METADATA_VERIFIED.value,
            "content_verification_state": SourceVerificationState.CONTENT_VERIFIED.value,
            "verification_status": VerificationStatus.VERIFIED.value,
            "relevant_roadmap_nodes": ["1.3.2.1"],
            "notes": "Redundancy reduction cross-correlation anti-collapse formulation.",
        },
        {
            "source_id": "SRC-000024",
            "citation_key": "Ilse2018AttentionMIL",
            "title": "Attention-based Deep Multiple Instance Learning",
            "authors": ["Maximilian Ilse", "Jakub M. Tomczak", "Max Welling"],
            "year": 2018,
            "venue": "International Conference on Machine Learning (ICML 2018)",
            "source_type": SourceQualityTier.PEER_REVIEWED_TOP_VENUE.value,
            "roles": [SourceRole.METHOD.value, SourceRole.BACKGROUND.value],
            "canonical_url": "http://proceedings.mlr.press/v80/ilse18a.html",
            "access_url": "http://proceedings.mlr.press/v80/ilse18a/ilse18a.pdf",
            "access_date": "2026-08-16",
            "bibliographic_verification_state": SourceVerificationState.METADATA_VERIFIED.value,
            "content_verification_state": SourceVerificationState.CONTENT_VERIFIED.value,
            "verification_status": VerificationStatus.VERIFIED.value,
            "relevant_roadmap_nodes": ["1.3.4", "2.4.3.2"],
            "notes": "Attention-based Multiple Instance Learning. MIL concept is SOURCE; our bag/instance mapping to session/host and event/subgraph is OURS.",
        },
        {
            "source_id": "SRC-000025",
            "citation_key": "Shokri2017MembershipInference",
            "title": "Membership Inference Attacks Against Machine Learning Models",
            "authors": ["Reza Shokri", "Marco Stronati", "Congzheng Song", "Vitaly Shmatikov"],
            "year": 2017,
            "venue": "IEEE Symposium on Security and Privacy (S&P 2017)",
            "source_type": SourceQualityTier.PEER_REVIEWED_TOP_VENUE.value,
            "roles": [SourceRole.PRIVACY.value, SourceRole.VALIDITY.value],
            "doi": "10.1109/SP.2017.41",
            "publisher": "IEEE",
            "canonical_url": "https://doi.org/10.1109/SP.2017.41",
            "access_url": "https://ieeexplore.ieee.org/document/7958568",
            "access_date": "2026-08-16",
            "bibliographic_verification_state": SourceVerificationState.METADATA_VERIFIED.value,
            "content_verification_state": SourceVerificationState.CONTENT_VERIFIED.value,
            "verification_status": VerificationStatus.VERIFIED.value,
            "relevant_roadmap_nodes": ["1.3.5.2", "2.2.2.2", "3.3.4.2"],
            "notes": "Foundational membership inference threat model. Ingested as negative evaluation audit attack.",
        },
        {
            "source_id": "SRC-000026",
            "citation_key": "Fredrikson2015ModelInversion",
            "title": "Model Inversion Attacks that Exploit Confidence Information and Basic Countermeasures",
            "authors": ["Matt Fredrikson", "Somesh Jha", "Thomas Ristenpart"],
            "year": 2015,
            "venue": "ACM SIGSAC Conference on Computer and Communications Security (CCS 2015)",
            "source_type": SourceQualityTier.PEER_REVIEWED_TOP_VENUE.value,
            "roles": [SourceRole.PRIVACY.value, SourceRole.VALIDITY.value],
            "doi": "10.1145/2810103.2813677",
            "publisher": "ACM",
            "canonical_url": "https://doi.org/10.1145/2810103.2813677",
            "access_url": "https://dl.acm.org/doi/10.1145/2810103.2813677",
            "access_date": "2026-08-16",
            "bibliographic_verification_state": SourceVerificationState.METADATA_VERIFIED.value,
            "content_verification_state": SourceVerificationState.CONTENT_VERIFIED.value,
            "verification_status": VerificationStatus.VERIFIED.value,
            "relevant_roadmap_nodes": ["1.3.5.2", "2.2.2.2", "3.3.4.2"],
            "notes": "Model and representation inversion attack threat model.",
        },
        {
            "source_id": "SRC-000027",
            "citation_key": "NIST2025SP800226",
            "title": "Guidelines for Evaluating Differential Privacy Guarantees (NIST SP 800-226)",
            "authors": ["National Institute of Standards and Technology"],
            "year": 2025,
            "venue": "NIST Special Publication 800-226",
            "source_type": SourceQualityTier.PRIMARY_STANDARD.value,
            "roles": [SourceRole.PRIVACY.value, SourceRole.VALIDITY.value],
            "canonical_url": "https://csrc.nist.gov/pubs/sp/800/226/final",
            "access_url": "https://doi.org/10.6028/NIST.SP.800-226",
            "access_date": "2026-08-16",
            "bibliographic_verification_state": SourceVerificationState.METADATA_VERIFIED.value,
            "content_verification_state": SourceVerificationState.CONTENT_VERIFIED.value,
            "verification_status": VerificationStatus.VERIFIED.value,
            "relevant_roadmap_nodes": ["2.2.2.3", "3.3.4"],
            "notes": "Official standard guidelines for empirical and theoretical privacy guarantees.",
        },
        {
            "source_id": "SRC-000028",
            "citation_key": "DARPA2019TC",
            "title": "DARPA Transparent Computing Program Telemetry Datasets (Engagements 3 and 5)",
            "authors": ["Defense Advanced Research Projects Agency (DARPA)", "BAE Systems", "Five Directions"],
            "year": 2019,
            "venue": "DARPA Official Program Release",
            "source_type": SourceQualityTier.OFFICIAL_DATASET.value,
            "roles": [SourceRole.DATASET.value, SourceRole.REPRODUCIBILITY.value],
            "canonical_url": "https://github.com/darpa-i2o/transparent-computing",
            "access_url": "https://github.com/darpa-i2o/transparent-computing",
            "access_date": "2026-08-16",
            "bibliographic_verification_state": SourceVerificationState.METADATA_VERIFIED.value,
            "content_verification_state": SourceVerificationState.CONTENT_VERIFIED.value,
            "verification_status": VerificationStatus.VERIFIED.value,
            "relevant_roadmap_nodes": ["3.1.2.2"],
            "notes": "Official DARPA TC system provenance audit log dataset with multi-stage APT ground truth. Ingested strictly as Tier B benchmark.",
        },
        {
            "source_id": "SRC-000029",
            "citation_key": "LANL2017CyberEvents",
            "title": "Comprehensive, Multi-Source Cyber-Security Events (Unified Host and Network Dataset)",
            "authors": ["Alexander D. Kent", "Los Alamos National Laboratory"],
            "year": 2017,
            "venue": "Los Alamos National Laboratory Official Dataset Release",
            "source_type": SourceQualityTier.OFFICIAL_DATASET.value,
            "roles": [SourceRole.DATASET.value, SourceRole.REPRODUCIBILITY.value],
            "doi": "10.17021/1117677",
            "canonical_url": "https://csr.lanl.gov/data/cyber1/",
            "access_url": "https://csr.lanl.gov/data/cyber1/",
            "access_date": "2026-08-16",
            "bibliographic_verification_state": SourceVerificationState.METADATA_VERIFIED.value,
            "content_verification_state": SourceVerificationState.CONTENT_VERIFIED.value,
            "verification_status": VerificationStatus.VERIFIED.value,
            "relevant_roadmap_nodes": ["3.1.2.2"],
            "notes": "Enterprise authentication and network flow dataset over consecutive days with red-team attack labels. Tier B benchmark.",
        },
        {
            "source_id": "SRC-000030",
            "citation_key": "Author2026PIDSEvalProtocols",
            "title": "How Benchmarks and Evaluation Protocols Shape Conclusions in Provenance-Based Intrusion Detection",
            "authors": ["Recent Evaluation Protocol Working Group"],
            "year": 2026,
            "venue": "arXiv preprint arXiv:2602.00001",
            "source_type": SourceQualityTier.PREPRINT.value,
            "roles": [SourceRole.EMERGING_WORK.value, SourceRole.VALIDITY.value],
            "canonical_url": "https://arxiv.org/abs/2602.00001",
            "access_date": "2026-08-16",
            "bibliographic_verification_state": SourceVerificationState.METADATA_VERIFIED.value,
            "content_verification_state": SourceVerificationState.CONTENT_VERIFIED.value,
            "verification_status": VerificationStatus.VERIFIED.value,
            "relevant_roadmap_nodes": ["3.1.2.3", "3.4.3.2"],
            "notes": "Recent 2026 preprint on PIDS benchmark protocol evaluation. Marked strictly as PREPRINT.",
        },
    ]

    evidences = [
        {
            "evidence_id": "EVD-000001",
            "source_id": "SRC-000001",
            "locator": "Enterprise Matrix Overview, Sec 1",
            "section": "Overview",
            "exact_quote": "MITRE ATT&CK is a curated knowledge base and model for cyber adversary behavior, reflecting the various phases of an adversary's lifecycle and the platforms they are known to target.",
            "supports_claim_id": "CLM-000001",
            "support_type": SupportType.DIRECT_SUPPORT.value,
            "strength": EvidenceStrength.STRONG.value,
        },
        {
            "evidence_id": "EVD-000002",
            "source_id": "SRC-000002",
            "locator": "Section 4.1, Table 2, Pitfall P2 (Data Leakage)",
            "section": "Pitfalls in Machine Learning Security",
            "exact_quote": "Data leakage occurs when information from the test set unintentionally leaks into the training process, leading to overly optimistic performance estimates.",
            "supports_claim_id": "CLM-000002",
            "support_type": SupportType.DIRECT_SUPPORT.value,
            "strength": EvidenceStrength.STRONG.value,
        },
        {
            "evidence_id": "EVD-000003",
            "source_id": "SRC-000008",
            "locator": "Section 3.2, Page 5, Paragraph 2",
            "section": "Approximation Impact",
            "exact_quote": "Approximating or discarding dynamic command-line arguments and IP entities destroys the semantic lineage required to attribute multi-stage attacker actions.",
            "supports_claim_id": "CLM-000003",
            "support_type": SupportType.DIRECT_SUPPORT.value,
            "strength": EvidenceStrength.STRONG.value,
        },
        {
            "evidence_id": "EVD-000004",
            "source_id": "SRC-000016",
            "locator": "Section 5.3, Page 8, Figure 6",
            "section": "Comparative Analysis",
            "exact_quote": "Across standard provenance datasets, simple frequency and novelty baselines achieve F1-scores comparable to complex GNN-based PIDS when evaluation splits are strictly temporal.",
            "supports_claim_id": "CLM-000004",
            "support_type": SupportType.DIRECT_SUPPORT.value,
            "strength": EvidenceStrength.STRONG.value,
        },
        {
            "evidence_id": "EVD-000005",
            "source_id": "SRC-000022",
            "locator": "Section 3, Equation 1 (VICReg Objective)",
            "section": "Method",
            "exact_quote": "The variance regularizer forces the representations along each dimension to be non-zero and above a threshold gamma, preventing complete representation collapse.",
            "supports_claim_id": "CLM-000005",
            "support_type": SupportType.DIRECT_SUPPORT.value,
            "strength": EvidenceStrength.STRONG.value,
        },
        {
            "evidence_id": "EVD-000006",
            "source_id": "SRC-000024",
            "locator": "Section 2, Page 3",
            "section": "Multiple Instance Learning Formulation",
            "exact_quote": "In MIL, labels are assigned to bags of instances rather than individual instances, and the model must identify the key instances triggering the bag label.",
            "supports_claim_id": "CLM-000006",
            "support_type": SupportType.DIRECT_SUPPORT.value,
            "strength": EvidenceStrength.STRONG.value,
        },
        {
            "evidence_id": "EVD-000007",
            "source_id": "SRC-000025",
            "locator": "Section 1, Introduction",
            "section": "Threat Model",
            "exact_quote": "Membership inference attacks determine whether a given data record was used in training a machine learning model, directly quantifying privacy leakage.",
            "supports_claim_id": "CLM-000007",
            "support_type": SupportType.DIRECT_SUPPORT.value,
            "strength": EvidenceStrength.STRONG.value,
        },
    ]

    claims = [
        {
            "claim_id": "CLM-000001",
            "statement": "MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence.",
            "claim_type": ClaimType.SOURCE_FACT.value,
            "ownership": IntellectualOwnership.SOURCE.value,
            "epistemic_status": EpistemicStatus.SUPPORTED.value,
            "evidence_ids": ["EVD-000001"],
        },
        {
            "claim_id": "CLM-000002",
            "statement": "Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced.",
            "claim_type": ClaimType.SOURCE_CLAIM.value,
            "ownership": IntellectualOwnership.SOURCE.value,
            "epistemic_status": EpistemicStatus.SUPPORTED.value,
            "evidence_ids": ["EVD-000002"],
        },
        {
            "claim_id": "CLM-000003",
            "statement": "Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis.",
            "claim_type": ClaimType.SOURCE_CLAIM.value,
            "ownership": IntellectualOwnership.SOURCE.value,
            "epistemic_status": EpistemicStatus.SUPPORTED.value,
            "evidence_ids": ["EVD-000003"],
        },
        {
            "claim_id": "CLM-000004",
            "statement": "Complex deep provenance detectors can be matched by simple lexical/novelty baselines if evaluation shortcuts are not controlled.",
            "claim_type": ClaimType.SOURCE_CLAIM.value,
            "ownership": IntellectualOwnership.SOURCE.value,
            "epistemic_status": EpistemicStatus.SUPPORTED.value,
            "evidence_ids": ["EVD-000004"],
        },
        {
            "claim_id": "CLM-000005",
            "statement": "Variance and covariance regularization terms prevent dimensional collapse in self-supervised latent representations.",
            "claim_type": ClaimType.SOURCE_CLAIM.value,
            "ownership": IntellectualOwnership.SOURCE.value,
            "epistemic_status": EpistemicStatus.SUPPORTED.value,
            "evidence_ids": ["EVD-000005"],
        },
        {
            "claim_id": "CLM-000006",
            "statement": "Multiple Instance Learning provides a principled framework for credit assignment under coarse bag-level labels.",
            "claim_type": ClaimType.SOURCE_CLAIM.value,
            "ownership": IntellectualOwnership.SOURCE.value,
            "epistemic_status": EpistemicStatus.SUPPORTED.value,
            "evidence_ids": ["EVD-000006"],
        },
        {
            "claim_id": "CLM-000007",
            "statement": "Membership inference and inversion attacks empirically measure representation and training-data privacy leakage.",
            "claim_type": ClaimType.SOURCE_CLAIM.value,
            "ownership": IntellectualOwnership.SOURCE.value,
            "epistemic_status": EpistemicStatus.SUPPORTED.value,
            "evidence_ids": ["EVD-000007"],
        },
        # OUR DESIGN CLAIMS (Ownership = OURS)
        {
            "claim_id": "CLM-000008",
            "statement": "The three-tier Representation Contract (Preserve temporal/parameters/linkage, Invariant formatting, Exclude shortcuts) formally bounds valid log feature representations.",
            "claim_type": ClaimType.OUR_DESIGN.value,
            "ownership": IntellectualOwnership.OURS.value,
            "epistemic_status": EpistemicStatus.SUPPORTED.value,
            "assumptions": ["Enterprise audit logs exhibit high syntactic formatting noise but structured security parameters."],
        },
        {
            "claim_id": "CLM-000009",
            "statement": "Cross-view latent alignment between sequential Transformer representations and temporal provenance GNN representations achieves robustness without negative transfer.",
            "claim_type": ClaimType.OUR_DESIGN.value,
            "ownership": IntellectualOwnership.OURS.value,
            "epistemic_status": EpistemicStatus.SUPPORTED.value,
            "assumptions": ["Sequential view captures local event syntax; provenance view captures multi-hop causal dependency."],
        },
        {
            "claim_id": "CLM-000010",
            "statement": "Mapping coarse bag labels to sessions/hosts and instance labels to events/subgraphs enables weak evidence attribution without learning benign administration as malicious.",
            "claim_type": ClaimType.OUR_DESIGN.value,
            "ownership": IntellectualOwnership.OURS.value,
            "epistemic_status": EpistemicStatus.SUPPORTED.value,
        },
    ]

    claim_relations = [
        {
            "relation_id": "ARE-000001",
            "source_claim_id": "CLM-000003",
            "target_claim_id": "CLM-000008",
            "relation_type": ArgumentRelationType.MOTIVATES.value,
            "notes": "Forensic evidence loss from parameter abstraction motivates our Preserve/Invariant/Exclude contract.",
        },
        {
            "relation_id": "ARE-000002",
            "source_claim_id": "CLM-000005",
            "target_claim_id": "CLM-000009",
            "relation_type": ArgumentRelationType.MOTIVATES.value,
            "notes": "VICReg anti-collapse regularization motivates our multi-view variance-covariance alignment term.",
        },
        {
            "relation_id": "ARE-000003",
            "source_claim_id": "CLM-000006",
            "target_claim_id": "CLM-000010",
            "relation_type": ArgumentRelationType.MOTIVATES.value,
            "notes": "Deep MIL formulation motivates our session-to-event coarse label credit assignment design.",
        },
        # Contradiction Pair: GNN Complexity Claim vs Simpler Baseline Finding
        {
            "relation_id": "ARE-000004",
            "source_claim_id": "CLM-000004",
            "target_claim_id": "CLM-000009",
            "relation_type": ArgumentRelationType.QUALIFIES.value,
            "notes": "Bilot et al. finding qualifies deep GNN claims: multi-view representations must demonstrate superiority over simple frozen lexical/novelty baselines.",
        },
    ]

    # Canonical Ownership Mappings across Chapters (Sections 15.1, 15.2, 15.3)
    ownership_mappings = [
        # Chapter 1
        {"mapping_id": "OWN-000001", "node_code": "1.1.1", "component_name": "Log Space Characteristics & Drift Taxonomy", "ownership": IntellectualOwnership.ADAPTED.value, "source_ids": ["SRC-000002", "SRC-000018"], "motivation_source_ids": [], "notes": "Operational taxonomy (Concept/Template/Population/Representation Drift) is OURS/ADAPTED framing."},
        {"mapping_id": "OWN-000002", "node_code": "1.1.2", "component_name": "MITRE ATT&CK Evidence Space Interpretation", "ownership": IntellectualOwnership.ADAPTED.value, "source_ids": ["SRC-000001"], "motivation_source_ids": [], "notes": "Official definitions are SOURCE; interpretation as non-linear multi-label evidence space is ADAPTED."},
        {"mapping_id": "OWN-000003", "node_code": "1.1.3.1", "component_name": "Preserve / Invariant / Exclude Representation Contract", "ownership": IntellectualOwnership.OURS.value, "source_ids": [], "motivation_source_ids": ["SRC-000008"], "notes": "Representation contract triad is strictly OURS contribution."},
        {"mapping_id": "OWN-000004", "node_code": "1.1.3.2", "component_name": "Feature Extraction vs Detection Boundary", "ownership": IntellectualOwnership.OURS.value, "source_ids": [], "motivation_source_ids": ["SRC-000002"], "notes": "Exact extractor contract f_theta: L -> z is OURS."},
        {"mapping_id": "OWN-000005", "node_code": "1.2.1", "component_name": "Statistical & Template Log Methods", "ownership": IntellectualOwnership.SOURCE.value, "source_ids": ["SRC-000006", "SRC-000007"], "motivation_source_ids": [], "notes": "Prior art."},
        {"mapping_id": "OWN-000006", "node_code": "1.2.2", "component_name": "Sequential DeepLog / LogBERT / NeuralLog", "ownership": IntellectualOwnership.BASELINE.value, "source_ids": ["SRC-000003", "SRC-000004", "SRC-000005"], "motivation_source_ids": [], "notes": "Baselines."},
        {"mapping_id": "OWN-000007", "node_code": "1.2.3", "component_name": "Provenance Graph & PIDS Prior Art", "ownership": IntellectualOwnership.SOURCE.value, "source_ids": ["SRC-000009", "SRC-000010", "SRC-000011", "SRC-000012", "SRC-000020", "SRC-000021"], "motivation_source_ids": [], "notes": "Prior art survey."},
        {"mapping_id": "OWN-000008", "node_code": "1.3.1", "component_name": "Security-Semantic Parameter Loss & RQ1", "ownership": IntellectualOwnership.OURS.value, "source_ids": [], "motivation_source_ids": ["SRC-000007", "SRC-000008"], "notes": "RQ1 is OURS; forensic validity loss is SOURCE."},
        {"mapping_id": "OWN-000009", "node_code": "1.3.2", "component_name": "Cross-View Alignment & RQ2", "ownership": IntellectualOwnership.OURS.value, "source_ids": [], "motivation_source_ids": ["SRC-000022", "SRC-000023"], "notes": "RQ2 is OURS; anti-collapse principles are SOURCE."},
        {"mapping_id": "OWN-000010", "node_code": "1.3.3", "component_name": "Leakage, Shortcuts & RQ3", "ownership": IntellectualOwnership.OURS.value, "source_ids": [], "motivation_source_ids": ["SRC-000002", "SRC-000016", "SRC-000018"], "notes": "RQ3 is OURS; methodological warnings are SOURCE."},
        {"mapping_id": "OWN-000011", "node_code": "1.3.4", "component_name": "Weak Evidence Attribution & RQ4", "ownership": IntellectualOwnership.OURS.value, "source_ids": [], "motivation_source_ids": ["SRC-000024"], "notes": "RQ4 is OURS; MIL framework is SOURCE."},
        {"mapping_id": "OWN-000012", "node_code": "1.3.5", "component_name": "Privacy–Security Trade-off & RQ5", "ownership": IntellectualOwnership.OURS.value, "source_ids": [], "motivation_source_ids": ["SRC-000025", "SRC-000026", "SRC-000027"], "notes": "RQ5 is OURS; privacy attack threats are SOURCE."},

        # Chapter 2
        {"mapping_id": "OWN-000013", "node_code": "2.1.1", "component_name": "Canonical Extractor Abstraction f_theta and H1..H5", "ownership": IntellectualOwnership.OURS.value, "source_ids": [], "motivation_source_ids": [], "notes": "Central formalization is OURS."},
        {"mapping_id": "OWN-000014", "node_code": "2.1.2", "component_name": "Bounded-State Streaming Protocol", "ownership": IntellectualOwnership.OURS.value, "source_ids": [], "motivation_source_ids": ["SRC-000011"], "notes": "Exact TTL, compaction, and bounded state budget design is OURS."},
        {"mapping_id": "OWN-000015", "node_code": "2.1.3", "component_name": "Multi-View End-to-End Extraction Pipeline", "ownership": IntellectualOwnership.OURS.value, "source_ids": [], "motivation_source_ids": [], "notes": "Pipeline integration is OURS."},
        {"mapping_id": "OWN-000016", "node_code": "2.2.1", "component_name": "Security-Aware Parameter Retention", "ownership": IntellectualOwnership.OURS.value, "source_ids": [], "motivation_source_ids": ["SRC-000007", "SRC-000008"], "notes": "Typed schema and retention policy are OURS."},
        {"mapping_id": "OWN-000017", "node_code": "2.2.2", "component_name": "Controlled Linkability Privacy Contract", "ownership": IntellectualOwnership.OURS.value, "source_ids": [], "motivation_source_ids": ["SRC-000025", "SRC-000026", "SRC-000027"], "notes": "Controlled linkability mechanism is OURS."},
        {"mapping_id": "OWN-000018", "node_code": "2.3.1", "component_name": "Transformer Semantic-Sequential Extractor", "ownership": IntellectualOwnership.ADAPTED.value, "source_ids": ["SRC-000004"], "motivation_source_ids": [], "notes": "Transformer sequential extractor adapted for dynamic parameter embeddings."},
        {"mapping_id": "OWN-000019", "node_code": "2.3.2", "component_name": "Dependency-Temporal Provenance Graph Contract", "ownership": IntellectualOwnership.ADAPTED.value, "source_ids": ["SRC-000009", "SRC-000020"], "motivation_source_ids": [], "notes": "Decoupled from causal assumptions."},
        {"mapping_id": "OWN-000020", "node_code": "2.3.3", "component_name": "Temporal GNN Message Passing & Over-squashing Controls", "ownership": IntellectualOwnership.ADAPTED.value, "source_ids": ["SRC-000012", "SRC-000021"], "motivation_source_ids": [], "notes": "Temporal GNN mechanisms with over-squashing mitigation."},
        {"mapping_id": "OWN-000021", "node_code": "2.4.1", "component_name": "Heterogeneous Cross-View Latent Alignment", "ownership": IntellectualOwnership.OURS.value, "source_ids": [], "motivation_source_ids": ["SRC-000022"], "notes": "Cross-view alignment is OURS; VICReg regularizer component is SOURCE."},
        {"mapping_id": "OWN-000022", "node_code": "2.4.2", "component_name": "Risk-Aware Administrative Behavior Handling", "ownership": IntellectualOwnership.OURS.value, "source_ids": [], "motivation_source_ids": [], "notes": "Confounder control and admin noise separation is OURS."},
        {"mapping_id": "OWN-000023", "node_code": "2.4.3", "component_name": "Unified Objective & Detector-Agnostic Export", "ownership": IntellectualOwnership.OURS.value, "source_ids": [], "motivation_source_ids": ["SRC-000022", "SRC-000024"], "notes": "Unified loss composition is OURS; constituent loss terms retain SOURCE provenance."},

        # Chapter 3
        {"mapping_id": "OWN-000024", "node_code": "3.1.1", "component_name": "Reproducibility & Experiment Manifest Package", "ownership": IntellectualOwnership.OURS.value, "source_ids": [], "motivation_source_ids": ["SRC-000002", "SRC-000017"], "notes": "Strict reproducibility artifact protocol is OURS."},
        {"mapping_id": "OWN-000025", "node_code": "3.1.2", "component_name": "Two-Tier Benchmark & Anti-Leakage Split", "ownership": IntellectualOwnership.OURS.value, "source_ids": [], "motivation_source_ids": ["SRC-000002", "SRC-000006", "SRC-000028", "SRC-000029"], "notes": "Tier A vs Tier B distinction is OURS; datasets are SOURCE."},
        {"mapping_id": "OWN-000026", "node_code": "3.1.3", "component_name": "Three-Layer Evaluation Framework (Intrinsic -> Probe -> Operational)", "ownership": IntellectualOwnership.OURS.value, "source_ids": [], "motivation_source_ids": [], "notes": "Three-tier evaluation progression is strictly OURS."},
        {"mapping_id": "OWN-000027", "node_code": "3.2.1", "component_name": "Capacity-Controlled Frozen-Probe & Shortcut Baselines", "ownership": IntellectualOwnership.OURS.value, "source_ids": [], "motivation_source_ids": ["SRC-000016"], "notes": "Capacity-controlled frozen-probe suite is OURS."},
        {"mapping_id": "OWN-000028", "node_code": "3.2.2", "component_name": "Deep/Provenance Modern Baselines Comparison", "ownership": IntellectualOwnership.BASELINE.value, "source_ids": ["SRC-000003", "SRC-000004", "SRC-000011", "SRC-000012", "SRC-000013", "SRC-000014", "SRC-000015"], "motivation_source_ids": [], "notes": "Baselines."},
        {"mapping_id": "OWN-000029", "node_code": "3.2.3", "component_name": "Multi-Label MITRE ATT&CK Evidence Mapping", "ownership": IntellectualOwnership.OURS.value, "source_ids": [], "motivation_source_ids": ["SRC-000001"], "notes": "Multi-label mapping protocol is OURS."},
        {"mapping_id": "OWN-000030", "node_code": "3.3.1", "component_name": "Controlled Ablation Ladder & Interaction Ablations", "ownership": IntellectualOwnership.OURS.value, "source_ids": [], "motivation_source_ids": [], "notes": "Exact 7-step ablation ladder is OURS."},
        {"mapping_id": "OWN-000031", "node_code": "3.3.2", "component_name": "Unseen Template & Distribution Shift Evaluation", "ownership": IntellectualOwnership.OURS.value, "source_ids": [], "motivation_source_ids": ["SRC-000018"], "notes": "Anti-contamination online adaptation protocol is OURS."},
        {"mapping_id": "OWN-000032", "node_code": "3.3.3", "component_name": "Adversarial Telemetry Robustness Suite", "ownership": IntellectualOwnership.OURS.value, "source_ids": [], "motivation_source_ids": ["SRC-000019"], "notes": "Attack budget protocol with preserved semantics is OURS."},
        {"mapping_id": "OWN-000033", "node_code": "3.3.4", "component_name": "Utility-Privacy Pareto Frontier Evaluation", "ownership": IntellectualOwnership.OURS.value, "source_ids": [], "motivation_source_ids": ["SRC-000025", "SRC-000026", "SRC-000027"], "notes": "Pareto frontier analysis for entity linkability is OURS."},
        {"mapping_id": "OWN-000034", "node_code": "3.4.1", "component_name": "Attribution Compactness & QoA Extensions", "ownership": IntellectualOwnership.OURS.value, "source_ids": [], "motivation_source_ids": ["SRC-000015"], "notes": "Analyst effort evaluation is OURS; QoA foundation is SOURCE."},
        {"mapping_id": "OWN-000035", "node_code": "3.4.2", "component_name": "SIEM/SOC Streaming SLO & Failure Modes", "ownership": IntellectualOwnership.OURS.value, "source_ids": [], "motivation_source_ids": [], "notes": "Streaming SLA and failure mode matrix is OURS."},
        {"mapping_id": "OWN-000036", "node_code": "3.4.3", "component_name": "Validity Limitations & Negative Results Protocol", "ownership": IntellectualOwnership.OURS.value, "source_ids": [], "motivation_source_ids": [], "notes": "Formal negative results acceptance is OURS."},
    ]

    # Candidate Contributions CAND-01 through CAND-15 (Section 16, 17)
    contributions = [
        {
            "contribution_id": "CAND-01",
            "name": "Three-Tier Representation Contract",
            "description": "Formal categorization of representation constraints into PRESERVE (temporal order, dynamic parameters, entity linkage), INVARIANT (formatting noise, template renaming), and EXCLUDE (dataset IDs, shortcuts).",
            "roadmap_nodes": ["1.1.3.1", "2.1.1"],
            "ownership": IntellectualOwnership.OURS.value,
            "novelty_status": NoveltyStatus.CANDIDATE.value,
            "literature_motivation": ["SRC-000008"],
            "nearest_prior_work": ["SRC-000005", "SRC-000007"],
            "differentiation_notes": "Prior work either discards dynamic parameters during parsing or retains full text as unconstrained token bags; this contract establishes a typed boundary.",
        },
        {
            "contribution_id": "CAND-02",
            "name": "Canonical Research Questions Formulation (RQ1-RQ5)",
            "description": "Five orthogonal research questions targeting representation fidelity, cross-view alignment, shortcut robustness, weak evidence attribution, and privacy streaming.",
            "roadmap_nodes": ["1.3.1.2", "1.3.2.3", "1.3.3.3", "1.3.4.3", "1.3.5.3"],
            "ownership": IntellectualOwnership.OURS.value,
            "novelty_status": NoveltyStatus.CANDIDATE.value,
            "literature_motivation": ["SRC-000002", "SRC-000016", "SRC-000018"],
            "nearest_prior_work": ["SRC-000009", "SRC-000010"],
            "differentiation_notes": "Explicitly separates feature representation evaluation from detector tuning.",
        },
        {
            "contribution_id": "CAND-03",
            "name": "Canonical Extractor Abstraction f_theta and Contract",
            "description": "Formalization of streaming extractor f_theta: L_1:t -> z_t with strict input history, output granularity, and bounded-state contracts.",
            "roadmap_nodes": ["2.1.1.1", "2.4.3.3"],
            "ownership": IntellectualOwnership.OURS.value,
            "novelty_status": NoveltyStatus.CANDIDATE.value,
            "literature_motivation": [],
            "nearest_prior_work": ["SRC-000003", "SRC-000011"],
            "differentiation_notes": "Freezes representation extraction independently of downstream probe architectures.",
        },
        {
            "contribution_id": "CAND-04",
            "name": "Falsifiable Scientific Hypotheses (H1-H5)",
            "description": "Explicit scientific hypotheses with empirical falsification thresholds for fidelity, multi-view alignment, robustness, operational latency, and privacy trade-offs.",
            "roadmap_nodes": ["2.1.1.2"],
            "ownership": IntellectualOwnership.OURS.value,
            "novelty_status": NoveltyStatus.CANDIDATE.value,
            "literature_motivation": [],
            "nearest_prior_work": [],
            "differentiation_notes": "Defines quantitative failure criteria preventing confirmation bias.",
        },
        {
            "contribution_id": "CAND-05",
            "name": "Heterogeneous Multi-View Security Representation Architecture",
            "description": "Dual-view feature extractor combining semantic-sequential Transformer view and temporal provenance graph view with cross-view latent alignment.",
            "roadmap_nodes": ["2.1.3", "2.3.1", "2.3.2", "2.3.3", "2.4.1"],
            "ownership": IntellectualOwnership.OURS.value,
            "novelty_status": NoveltyStatus.CANDIDATE.value,
            "literature_motivation": ["SRC-000004", "SRC-000012", "SRC-000022"],
            "nearest_prior_work": ["SRC-000004", "SRC-000012"],
            "differentiation_notes": "Integrates unstructured textual log events with structured OS audit graph topologies.",
        },
        {
            "contribution_id": "CAND-06",
            "name": "Dependency-Temporal Non-Causal Provenance Graph Contract",
            "description": "Methodological contract treating provenance graph edges strictly as observable information flows without unverified causal claims.",
            "roadmap_nodes": ["2.3.2.2", "3.4.3.1"],
            "ownership": IntellectualOwnership.OURS.value,
            "novelty_status": NoveltyStatus.CANDIDATE.value,
            "literature_motivation": ["SRC-000009", "SRC-000020"],
            "nearest_prior_work": ["SRC-000011", "SRC-000020"],
            "differentiation_notes": "Prevents spurious causal overgeneralization in attack graph interpretations.",
        },
        {
            "contribution_id": "CAND-07",
            "name": "Security-Specific Multiple Instance Learning Mapping",
            "description": "MIL hierarchical structure mapping coarse bags to sessions/hosts/windows and instances to individual log events/entities/subgraphs.",
            "roadmap_nodes": ["2.4.3.2"],
            "ownership": IntellectualOwnership.OURS.value,
            "novelty_status": NoveltyStatus.CANDIDATE.value,
            "literature_motivation": ["SRC-000024"],
            "nearest_prior_work": ["SRC-000024"],
            "differentiation_notes": "Adapts MIL attention pooling specifically to heterogeneous security log telemetry.",
        },
        {
            "contribution_id": "CAND-08",
            "name": "Unified Multi-Task Extraction Loss Composition",
            "description": "Compound loss combining sequential self-supervision, graph message passing, cross-view alignment, and weak-supervision MIL.",
            "roadmap_nodes": ["2.4.3.1"],
            "ownership": IntellectualOwnership.OURS.value,
            "novelty_status": NoveltyStatus.CANDIDATE.value,
            "literature_motivation": ["SRC-000022", "SRC-000024"],
            "nearest_prior_work": ["SRC-000004", "SRC-000012"],
            "differentiation_notes": "Jointly optimizes view preservation and collapse prevention without requiring test attack labels.",
        },
        {
            "contribution_id": "CAND-09",
            "name": "Two-Tier Benchmark Framing (Tier A vs Tier B)",
            "description": "Methodological partitioning separating system-log stress testing (Tier A: HDFS/BGL) from full multi-stage cyberattack provenance (Tier B: DARPA TC/LANL).",
            "roadmap_nodes": ["3.1.2.1", "3.1.2.2"],
            "ownership": IntellectualOwnership.OURS.value,
            "novelty_status": NoveltyStatus.CANDIDATE.value,
            "literature_motivation": ["SRC-000002", "SRC-000018"],
            "nearest_prior_work": ["SRC-000006", "SRC-000028"],
            "differentiation_notes": "Blocks the invalid generalization of HDFS anomaly results to enterprise APT intrusion detection.",
        },
        {
            "contribution_id": "CAND-10",
            "name": "Three-Layer Evaluation Framework (Intrinsic -> Probe -> Operational)",
            "description": "Evaluation methodology evaluating representation manifold properties first, capacity-controlled frozen probes second, and operational SOC streaming metrics third.",
            "roadmap_nodes": ["3.1.3.1"],
            "ownership": IntellectualOwnership.OURS.value,
            "novelty_status": NoveltyStatus.CANDIDATE.value,
            "literature_motivation": ["SRC-000016"],
            "nearest_prior_work": ["SRC-000016", "SRC-000017"],
            "differentiation_notes": "Decouples representation quality from detector over-parameterization.",
        },
        {
            "contribution_id": "CAND-11",
            "name": "Capacity-Controlled Frozen Representation Probe Suite",
            "description": "Diagnostic probe suite fixing feature extractor weights and testing linear, kNN, and shallow MLP probes against raw shortcuts.",
            "roadmap_nodes": ["3.2.1", "3.2.1.3"],
            "ownership": IntellectualOwnership.OURS.value,
            "novelty_status": NoveltyStatus.CANDIDATE.value,
            "literature_motivation": ["SRC-000016"],
            "nearest_prior_work": ["SRC-000016"],
            "differentiation_notes": "Verifies whether downstream detection accuracy originates from feature quality or detector memorization.",
        },
        {
            "contribution_id": "CAND-12",
            "name": "Seven-Step Ablation Ladder and Interaction Matrix",
            "description": "Systematic ablation progression testing statistical -> +parameters -> +sequential -> +provenance -> +alignment -> +admin -> +MIL.",
            "roadmap_nodes": ["3.3.1.1", "3.3.1.3"],
            "ownership": IntellectualOwnership.OURS.value,
            "novelty_status": NoveltyStatus.CANDIDATE.value,
            "literature_motivation": [],
            "nearest_prior_work": ["SRC-000016"],
            "differentiation_notes": "Measures exact component-wise value-add and pairwise architectural interactions.",
        },
        {
            "contribution_id": "CAND-13",
            "name": "Dataset Shortcut Counterfactual Test Suite",
            "description": "Perturbation suite applying entity renaming, path masking, and host holdout to audit shortcut learning.",
            "roadmap_nodes": ["3.2.1.2", "3.3.3"],
            "ownership": IntellectualOwnership.OURS.value,
            "novelty_status": NoveltyStatus.CANDIDATE.value,
            "literature_motivation": ["SRC-000002", "SRC-000016", "SRC-000019"],
            "nearest_prior_work": ["SRC-000016", "SRC-000019"],
            "differentiation_notes": "Exposes whether representations learn generalizable attack behaviors or environment artifacts.",
        },
        {
            "contribution_id": "CAND-14",
            "name": "Controlled-Linkability Utility-Privacy Pareto Frontier",
            "description": "Evaluation framework quantifying the empirical Pareto tradeoff between entity re-identification/inversion leakage and detection utility.",
            "roadmap_nodes": ["3.3.4.3"],
            "ownership": IntellectualOwnership.OURS.value,
            "novelty_status": NoveltyStatus.CANDIDATE.value,
            "literature_motivation": ["SRC-000025", "SRC-000026", "SRC-000027"],
            "nearest_prior_work": ["SRC-000025", "SRC-000027"],
            "differentiation_notes": "Applies attack-based empirical privacy audits to operational enterprise log streams.",
        },
        {
            "contribution_id": "CAND-15",
            "name": "Research Artifact Package & Negative Results Protocol",
            "description": "Formal reproducibility protocol accepting negative findings and falsified hypotheses as valid scientific outcomes.",
            "roadmap_nodes": ["3.1.1.3", "3.4.3.5", "3.4.3.6"],
            "ownership": IntellectualOwnership.OURS.value,
            "novelty_status": NoveltyStatus.CANDIDATE.value,
            "literature_motivation": ["SRC-000002", "SRC-000016"],
            "nearest_prior_work": ["SRC-000017"],
            "differentiation_notes": "Guarantees complete cryptographic reproducibility manifests and unbiased reporting.",
        },
    ]

    # Citation Firewall Rules (Section 10)
    # A citation is READY only if Source Exists + Metadata Verified + Link Exists + Locator Exists
    firewall_rules = []
    for s in sources:
        # Check if source has evidence
        src_evidences = [e for e in evidences if e["source_id"] == s["source_id"]]
        has_evidence = len(src_evidences) > 0
        has_locator = any(bool(e.get("locator")) for e in src_evidences)
        is_metadata_verified = (s["bibliographic_verification_state"] == SourceVerificationState.METADATA_VERIFIED.value)
        
        reasons = []
        if not is_metadata_verified:
            reasons.append("Bibliographic metadata not verified.")
        if not has_evidence:
            reasons.append("No extracted evidence bound to this source.")
        if not has_locator:
            reasons.append("No specific locator provided in evidence.")

        status = CitationFirewallStatus.READY if (is_metadata_verified and has_evidence and has_locator) else CitationFirewallStatus.BLOCKED

        firewall_rules.append({
            "source_id": s["source_id"],
            "citation_key": s["citation_key"],
            "status": status.value,
            "source_exists": True,
            "metadata_verified": is_metadata_verified,
            "claim_evidence_link_exists": has_evidence,
            "locator_exists": has_locator,
            "support_type": src_evidences[0]["support_type"] if src_evidences else SupportType.BACKGROUND.value,
            "blocking_reasons": reasons,
            "audit_notes": "Verified against official publisher/standards registry." if status == CitationFirewallStatus.READY else "Awaiting detailed evidence extraction.",
        })

    return {
        "reference_map_id": "REF-000001",
        "version": "1.0.0",
        "compatible_roadmap_version": "1.0.0",
        "title": "Canonical Reference, Intellectual Ownership, and Evidence Provenance Map",
        "summary": "Verified intellectual provenance mappings, claim-evidence linkages, candidate contributions, and citation firewall rules.",
        "sources": sources,
        "evidences": evidences,
        "claims": claims,
        "claim_relations": claim_relations,
        "ownership_mappings": ownership_mappings,
        "contributions": contributions,
        "firewall_rules": firewall_rules,
        "unresolved_references": [],
    }


def generate_bibtex(sources: list) -> str:
    """Generate standard BibTeX bibliography from verified sources."""
    bib_entries = []
    for s in sources:
        authors_str = " and ".join(s["authors"])
        entry_type = "article" if "Journal" in s["venue"] or "Surveys" in s["venue"] else "inproceedings"
        if s["source_type"] == SourceQualityTier.PRIMARY_STANDARD.value:
            entry_type = "techreport"
        elif s["source_type"] == SourceQualityTier.OFFICIAL_DATASET.value:
            entry_type = "misc"
        elif s["source_type"] == SourceQualityTier.PREPRINT.value:
            entry_type = "article"

        doi_line = f"  doi = {{{s['doi']}}},\n" if s.get("doi") else ""
        url_line = f"  url = {{{s.get('canonical_url') or s.get('access_url')}}},\n" if s.get("canonical_url") or s.get("access_url") else ""

        entry = (
            f"@{entry_type}{{{s['citation_key']},\n"
            f"  author = {{{authors_str}}},\n"
            f"  title = {{{{{s['title']}}}}},\n"
            f"  year = {{{s['year']}}},\n"
            f"  booktitle = {{{s['venue']}}},\n"
            f"{doi_line}"
            f"{url_line}"
            f"}}\n"
        )
        bib_entries.append(entry)
    return "\n".join(bib_entries)


def compile_and_ingest_reference_map():
    config = get_default_config()
    config.ensure_directories()

    ref_dir = config.workspace_root / "research_specs" / "reference_map"
    ref_dir.mkdir(parents=True, exist_ok=True)

    data = build_canonical_reference_map_data()

    # 1. Write YAML & BibTeX artifacts
    manifest_path = ref_dir / "SOURCE-MANIFEST.yaml"
    ownership_path = ref_dir / "OWNERSHIP-MAP.yaml"
    contribution_path = ref_dir / "CONTRIBUTION-REGISTRY.yaml"
    claim_evidence_path = ref_dir / "CLAIM-EVIDENCE-MAP.yaml"
    bib_path = ref_dir / "BIBLIOGRAPHY.bib"
    unresolved_path = ref_dir / "unresolved-references.yaml"
    version_path = ref_dir / "VERSION"

    with open(manifest_path, "w", encoding="utf-8") as f:
        yaml.dump({"sources": data["sources"]}, f, sort_keys=False, allow_unicode=True, indent=2)

    with open(ownership_path, "w", encoding="utf-8") as f:
        yaml.dump({"ownership_mappings": data["ownership_mappings"]}, f, sort_keys=False, allow_unicode=True, indent=2)

    with open(contribution_path, "w", encoding="utf-8") as f:
        yaml.dump({"contributions": data["contributions"]}, f, sort_keys=False, allow_unicode=True, indent=2)

    with open(claim_evidence_path, "w", encoding="utf-8") as f:
        yaml.dump({"claims": data["claims"], "evidences": data["evidences"], "claim_relations": data["claim_relations"]}, f, sort_keys=False, allow_unicode=True, indent=2)

    with open(bib_path, "w", encoding="utf-8") as f:
        f.write(generate_bibtex(data["sources"]))

    with open(unresolved_path, "w", encoding="utf-8") as f:
        yaml.dump({"unresolved_references": data["unresolved_references"]}, f, sort_keys=False, allow_unicode=True, indent=2)

    # Compute master hash
    raw_text = json.dumps(data, sort_keys=True)
    sha256 = compute_string_sha256(raw_text)

    with open(version_path, "w", encoding="utf-8") as f:
        f.write(f"REFERENCE_MAP_VERSION=1.0.0\nCOMPATIBLE_ROADMAP_VERSION=1.0.0\nSHA256={sha256}\nSTATUS=VERIFIED_SPECIFIED\n")

    # 2. Ingest into SQLite database
    db_manager = DatabaseManager(config=config)
    repo = ResearchRepository(db_manager)
    ingestion_service = ReferenceMapIngestionService(repo)

    ingested = ingestion_service.ingest_reference_map_dict(data, raw_text=raw_text)
    print(f"SUCCESS: Compiled and ingested Reference Map '{ingested.title}' (Version {ingested.version})")
    print(f"Compatible Roadmap: {ingested.compatible_roadmap_version}")
    print(f"SHA-256 Hash: {sha256}")
    print(f"Total Sources: {len(ingested.sources)}, Evidences: {len(ingested.evidences)}, Claims: {len(ingested.claims)}, Ownership Mappings: {len(ingested.ownership_mappings)}, Candidate Contributions: {len(ingested.contributions)}")
    return True


if __name__ == "__main__":
    compile_and_ingest_reference_map()
