# Scientific Figure & Table Protocol (RC-09)

## 1. Constitutional Table Protocol

Every table in the research repository must be created via the deterministic `TableBuilder` (`src/research_agent/verification/tables/builder.py`):
1. **Multi-Format Export:** Emits aligned CSV, GitHub Flavored Markdown, and Booktabs LaTeX (`tabular`) representations.
2. **Cell-Level Provenance:** Stores a provenance map associating individual cells $(r, c)$ to exact `SourceID` (for prior art numbers) or `ExperimentRunID` (for empirical results).
3. **Table Comparability Audit:** `TableFairnessAuditor` verifies that compared baselines share identical dataset versions, split strategies, and metric evaluation granularities. If differences exist, `is_directly_comparable` is set to `False` with an explicit reason string.
4. **Cryptographic Hash:** The entire table content is hashed with SHA-256 (`output_sha256`).

---

## 2. Constitutional Figure Protocol

Every scientific plot must adhere to the publication standard (`src/research_agent/verification/figures/`):
1. **Headless Generation:** Rendered using non-interactive Matplotlib backend (`Agg`) at 300 DPI.
2. **Mandatory Companion Data CSV:** Beside each figure `fig-01.png`, a companion `fig-01-data.csv` is written containing the exact raw numerical coordinates used to render the plot points, curves, and error bars.
3. **Figure Metadata JSON:** Companion `fig-01-metadata.json` links the figure to the generation script, source run IDs, SHA-256 hashes of both image and CSV, and uncertainty representation flags (`CI_95`, `ERROR_BARS_SD`, `NONE`).
4. **Manual Edit Audit:** Any external post-processing in image editors sets `manually_edited = True` with mandatory `manual_edit_reason`.

---

## 3. Supported Standard Figure Types

1. **`LINE_PLOT`**: Trajectory and convergence curves.
2. **`SCATTER_PLOT`**: Two-dimensional correlation and latent space projections.
3. **`BAR_PLOT`**: Comparative performance bars with explicit 95% confidence intervals / error caps.
4. **`BOX_PLOT`**: Distribution quartiles and outlier visualizations.
5. **`PR_CURVE`**: Precision-Recall tradeoff curves with trapezoidal PR-AUC computation.
6. **`ROC_CURVE`**: True Positive Rate vs False Positive Rate curves.
7. **`ABLATION_PLOT`**: Component removal performance impact.
8. **`PARETO_FRONTIER`**: Multi-objective trade-off frontiers (e.g. Accuracy vs Latency).
9. **`LATENCY_THROUGHPUT`**: Operational throughput vs P95/P99 latency curves with warmup exclusion.
10. **`ROBUSTNESS_CURVE`**: Performance retention under label noise or missing feature ratios.
