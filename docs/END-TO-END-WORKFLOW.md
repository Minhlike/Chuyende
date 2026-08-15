# End-to-End Scientific Research Workflow

## Complete System Lifecycle

```mermaid
flowchart TD
    A[PROMPT 1: Research Constitution] --> B[PROMPT 2: Canonical Roadmap]
    B --> C[PROMPT 3: Verified Reference Map & Ownership]
    C --> D[PROMPT 4: Long-Term Memory & Hybrid Retrieval]
    D --> E[PROMPT 5: Scientific Reasoning & Argumentation]
    E --> F[PROMPT 6: Verification Toolchain & Statistics]
    F --> G[PROMPT 7: Academic Composition & Thesis Auditor]
    G --> H[Final Defensible Thesis Artifact Package]
```

## Step-by-Step Operator Guide

1. **Bootstrap & Health Check:**
   ```bash
   python -m research_agent.cli doctor
   ```
2. **Inspect Epistemic Node Status:**
   ```bash
   python -m research_agent.cli thesis node 1.3.3
   ```
3. **Execute Scientific Verification:**
   ```bash
   python -m research_agent.cli verify equation "(x + 1)**2" "x**2 + 2*x + 1"
   python -m research_agent.cli verify cm "[1, 0, 1, 0]" "[1, 0, 0, 0]"
   ```
4. **Draft Subsection:**
   ```bash
   python -m research_agent.cli thesis compose 1.3.3 --mode provisional
   ```
5. **Run Thesis-Wide Epistemic Audit:**
   ```bash
   python -m research_agent.cli thesis audit --mode provisional
   ```
6. **Compile Complete Publication & Thesis Build:**
   ```bash
   python -m research_agent.cli thesis build --mode provisional
   ```
7. **Trace Provenance Chain:**
   ```bash
   python -m research_agent.cli trace P-1.3.3-01
   ```
