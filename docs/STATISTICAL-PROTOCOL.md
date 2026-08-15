# Scientific Statistical Protocol & Misuse Prevention

## 1. Core Principles

1. **Mandatory Sample Unit:** Every statistical claim and test must declare its explicit unit of analysis (e.g. `Random Seed Run`, `Target Host`, `Evaluation Session`).
2. **Multi-Seed Distribution Reporting:** For all empirical benchmarks, evaluations must be performed over $K \ge 5$ independent random seeds. Authors must report:
   $$\text{Mean} \pm \text{Standard Deviation} \quad \text{or} \quad \text{Median } [\text{IQR}]$$
3. **No p-Value Without Effect Size:** Significance ($p < \alpha$) alone does not measure practical importance. Every hypothesis test must report a standardized effect size (Cohen's $d$, Hedges' $g$, or relative percentage change).

---

## 2. Hypothesis Testing Matrix

| Data Structure | Normality Condition | Test Selected | Effect Size Metric |
| :--- | :--- | :--- | :--- |
| **Matched Seeds / Hosts** ($N \ge 5$) | Normal (Shapiro-Wilk $p \ge 0.05$) | Paired Student's $t$-test | Hedges' $g$ (small-sample corrected) |
| **Matched Seeds / Hosts** ($N \ge 8$) | Non-Normal ($p < 0.05$) | Wilcoxon signed-rank test | Rank-biserial correlation $r_{rb}$ |
| **Independent Partitions** | Normal | Independent two-sample $t$-test | Cohen's $d$ / Hedges' $g$ |
| **Independent Partitions** | Non-Normal / Skewed | Mann-Whitney $U$ test | Rank-biserial correlation $r_{rb}$ |

---

## 3. Standardized Effect Size Formulations

### Cohen's $d$ & Hedges' $g$
$$d = \frac{\bar{x}_1 - \bar{x}_2}{s_{\text{pooled}}}, \quad \text{where } s_{\text{pooled}} = \sqrt{\frac{(n_1-1)s_1^2 + (n_2-1)s_2^2}{n_1 + n_2 - 2}}$$

$$g = d \cdot \left(1 - \frac{3}{4(n_1 + n_2) - 9}\right)$$

### Bootstrap Confidence Intervals
Deterministic non-parametric percentile bootstrap confidence intervals with fixed random seed:
- Resample $B = 2000$ iterations with replacement.
- For $95\%$ confidence level, lower bound is $2.5^{\text{th}}$ percentile and upper bound is $97.5^{\text{th}}$ percentile.

---

## 4. BestRunCherryPickingGuard

The `BestRunCherryPickingGuard` audits experimental reporting to prevent single-run cherry-picking:
- If a reported scalar $V_{\text{rep}}$ equals $\max(V_{\text{seeds}})$ within $10^{-4}$ tolerance while diverging from $\bar{V}_{\text{seeds}}$, the toolchain triggers a `CHERRY_PICKING_DETECTED` warning.
- Writing gates enforce replacing $V_{\text{rep}}$ with $\bar{V} \pm s$ or reporting the full multi-seed distribution.

---

## 5. Statistical Misuse Guardrails

The `StatisticalMisuseAuditor` enforces:
1. **Absence of Evidence Is Not Evidence of Absence:** $p \ge 0.05$ cannot be interpreted as proof that two methods are equivalent without equivalence testing (e.g. Two One-Sided Tests, TOST).
2. **Multiple Comparisons:** When conducting multiple simultaneous statistical comparisons across sub-hypotheses, Bonferroni adjustment ($\alpha' = \alpha / m$) or False Discovery Rate (Benjamini-Hochberg) is required.
3. **Small Sample Warnings:** Parametric assumptions on $N < 5$ trigger explicit small-sample warnings.
