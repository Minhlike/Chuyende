# LOG ROBUSTNESS & ADVERSARIAL TELEMETRY PERTURBATION PROTOCOL

**Document Identifier:** `PROT-ROBUST-20260821-V1.0`  
**Protocol Version:** 1.0.0  
**Status:** **LOCKED & CANONICAL**  
**Governing Standard:** Research Constitution (`RC-04`, `RC-10`), Roadmap (`AXIS-A3`, `BOUNDARY-05`).  

---

## 1. Perturbation Principles & Semantic Preservation Invariant

To evaluate representation resilience against real-world evasion, log pipeline faults, and environment drift, the system defines 12 deterministic perturbation operators.

### Core Semantic Invariant:
$$\text{Semantics}(T(X)) \equiv \text{Semantics}(X)$$
**Strict Rule:** No perturbation operator shall alter the ground-truth execution semantics of the underlying attack or benign activity. Perturbations simulate realistic adversary evasion tactics, log pipeline dropouts, and benign environment noise without altering actual execution outcomes.

---

## 2. The 12 Pre-Registered Perturbation Operators

| # | Perturbation Operator | Attack Budget / Parameter Scope | Semantic Preservation Condition | Deterministic Generator / Config |
| :--- | :--- | :--- | :--- | :--- |
| **P01** | **Executable Renaming** | Replace attack executable names with benign system names (e.g. `mimikatz.exe` $\to$ `svchost.exe`). | Execution arguments and process parentage remain identical. | Seeded token mapping table. |
| **P02** | **Path Relocation** | Mutate file paths (e.g. `/tmp/payload` $\to$ `/var/log/syslog.1`). | File operations target valid system directories. | Deterministic path substitution engine. |
| **P03** | **Benign Identifier Replacement** | Randomize user IDs (`U1001` $\to$ `U9999`) and hostnames. | Identifier linkage within session preserved; global ID shifted. | Causal identity pseudonymizer. |
| **P04** | **Timestamp Jitter** | Add Gaussian jitter $\Delta t \sim \mathcal{N}(0, \sigma^2)$, $\sigma \in [0.1\text{s}, 5.0\text{s}]$ to timestamps. | Total event causal order strictly preserved ($t_i \le t_{i+1}$). | Seeded noise injector. |
| **P05** | **Benign Event Insertion** | Interleave benign background log events (up to $50\%$ noise ratio). | Benign events sampled from empirical $\mathcal{D}_{\text{train}}$ normal pool. | Poisson process event merger. |
| **P06** | **Telemetry Dropout / Deletion** | Randomly drop $\rho_{\text{drop}} \in [5\%, 30\%]$ of telemetry events (packet loss). | Dropped events cannot include critical primary attack execution tokens. | Uniform Bernoulli mask with fixed seed. |
| **P07** | **Local Event Reordering** | Permute adjacent independent events occurring within $\Delta t \le 500\text{ms}$. | Causal dependencies (e.g. `write` before `read`) cannot be inverted. | Windowed topological permuter. |
| **P08** | **Telemetry Suppression** | Suppress all telemetry from a specific child process branch. | Simulates auditd/Sysmon logging evasion without breaking parent stream. | Process subtree pruning mask. |
| **P09** | **Broken Entity Linkage** | Strip Parent Process ID (PPID) or network socket binding on 20% of events. | Event content preserved; structural provenance pointer set to $\bot$. | Structural pointer nullifier. |
| **P10** | **Missing View Simulation** | Complete dropout of sequential view ($X_{\text{seq}} = \emptyset$) or graph view ($G = \emptyset$). | Simulates collector outage for one logging modality. | Modality dropout switch. |
| **P11** | **Unseen Host / Entity Cold-Start** | Evaluate model on hosts/users never observed during training. | Telemetry conforms to standard OS schema. | Host holdout partition (`SPL-DTC-001`). |
| **P12** | **Mimicry Benign Tool Insertion** | Interleave realistic discovery commands (`whoami`, `dir`, `ping`, `systeminfo`) inside attack chain. | Standard MITRE ATT&CK discovery techniques executed by adversary. | Synthetic ATT&CK discovery sequence injector. |

---

## 3. Robustness Evaluation Metric & Success Criteria

For each perturbation $P_k$ at budget level $\beta$, compute:
$$\Delta \text{PR-AUC}(P_k, \beta) = \text{PR-AUC}(\text{Clean}) - \text{PR-AUC}(P_k(\beta))$$
$$\text{Invariance}(P_k, \beta) = \frac{1}{N} \sum_{i=1}^N \|\mathbf{z}(P_k(X_i)) - \mathbf{z}(X_i)\|_2$$

- **Robustness Pass:** $\Delta \text{PR-AUC} \le 0.15$ across all $P_1 \dots P_{12}$ at standard budget.
- **Robustness Falsified:** $\Delta \text{PR-AUC} > 0.40$ or performance collapses to random guess level under minor syntactic perturbations ($P_1, P_2, P_4$).
