# STAGE A1 SELF-SUPERVISED TRAINING CONTRACT (LOCKED SPECIFICATION)

**Document Identifier:** `CONTRACT-STAGE-A1-20260822-V1.2`  
**Status:** **LOCKED & CANONICAL (PRE-TRAIN FREEZE)**  
**Target Workload:** Sequence-Only Multi-Task Self-Supervised Pretraining (Stage A1)  
**Execution State:** `ANY_MODEL_TRAINED = NO`, `OPTIMIZER_STEPS = 0`, `TEST_SEALED = YES`  

---

## 1. Scope & Evidential Boundaries

1. **Self-Supervised Pretraining Only:**
   Stage A1 trains the sequence representation backbone using purely self-supervised objectives ($L_{\text{MEP}}$, $L_{\text{MPP}}$, $L_{\text{time}}$).
   - **Zero Downstream Labels:** No anomaly, alert, attack, or probe labels are exposed to the pretraining pipeline.
   - **Zero Graph View / VICReg:** Graph encoders, multi-view alignments ($L_{\text{align}}$), and VICReg loss branches are strictly inactive during Stage A1.
2. **Dataset-Specific Separate Backbones:**
   - `MODEL-A1-HDFS`: Trained exclusively on HDFS Train partition with HDFS-specific fitted vocabulary.
   - `MODEL-A1-BGL`: Trained exclusively on BGL Days 1–150 Train partition with BGL-specific fitted vocabulary.
   - **Strict Isolation:** Vocabularies and models are never concatenated or sequentially cross-trained.

---

## 2. Multi-Task Objective & Loss Weights

The sequence-only self-supervised loss is locked to:
$$L_{\text{seq}} = \lambda_{\text{MEP}} L_{\text{MEP}} + \lambda_{\text{MPP}} L_{\text{MPP}} + \lambda_{\text{time}} L_{\text{time}}$$

| Loss Component | Objective Name | Target Definition | Loss Function | Locked Weight $\lambda$ |
| :--- | :--- | :--- | :--- | :--- |
| **$L_{\text{MEP}}$** | Masked Event Prediction | Rule-based canonical event template classes | Cross-Entropy over masked tokens | $\lambda_{\text{MEP}} = 1.0$ |
| **$L_{\text{MPP}}$** | Masked Parameter Prediction | Multi-parameter slots (`BOUNDED_MULTI_SLOT_TYPED_PARAMETER_SET_K4`, max 4 slots/event) | Cross-Entropy averaged over active masked slots (ignoring `<PAD_PARAM>`) | $\lambda_{\text{MPP}} = 1.0$ |
| **$L_{\text{time}}$** | Event Time Delta Prediction | Real adjacent time interval $\log(1 + \Delta t)$ | Smooth L1 Loss ($\beta = 1.0$) | $\lambda_{\text{time}} = 0.1$ |

---

## 3. Model Architecture & Hyperparameters

| Hyperparameter | Locked Specification |
| :--- | :--- |
| **Architecture Family** | Bidirectional Transformer Encoder |
| **Model Dimension ($d_{\text{model}}$)** | $128$ |
| **Transformer Layers ($L$)** | $4$ |
| **Attention Heads ($H$)** | $4$ |
| **Feedforward Dimension ($d_{\text{ffn}}$)** | $512$ |
| **Dropout Rate** | $0.10$ |
| **Max Sequence Length ($T_{\max}$)** | $128$ tokens |
| **Parameter Representation Mode** | `BOUNDED_MULTI_SLOT_TYPED_PARAMETER_SET_K4` |
| **Max Parameter Slots / Event** | $4$ slots |
| **Masking Probability** | $15\%$ Bernoulli masking ($80\%$ `[MASK]`, $10\%$ random, $10\%$ unchanged) |

---

## 4. Optimization & Training Schedule

| Parameter | Locked Value |
| :--- | :--- |
| **Optimizer** | `AdamW` ($\beta_1 = 0.9$, $\beta_2 = 0.98$, $\epsilon = 10^{-8}$) |
| **Peak Learning Rate** | $5.0 \times 10^{-4}$ |
| **Learning Rate Schedule** | Linear warmup ($5\%$ of total optimizer steps) followed by Cosine Decay to $1.0 \times 10^{-5}$ |
| **Weight Decay** | $0.01$ |
| **Micro-Batch Size** | $16$ sequences |
| **Gradient Accumulation Steps** | $4$ micro-batches |
| **Effective Batch Size** | $64$ sequences |
| **Optimizer Step Cadence** | Every $4$ micro-batches ($1$ optimizer step per $64$ sequences) |
| **Gradient Clipping** | $\text{max\_norm} = 1.0$ (L2 norm) |
| **Max Epochs** | $20$ epochs |
| **Validation Check Frequency** | Exactly once per completed epoch |
| **Early Stopping Criterion** | Validation $L_{\text{seq}}$ non-improving for $3$ consecutive epochs (Patience = $3$) |
| **Checkpoint Selection Rule** | Minimum Validation $L_{\text{seq}}$ checkpoint (`best_val_loss.pt`) |

---

## 5. Canonical Five-Seed Protocol

Pretraining will be executed across exactly five pre-registered seeds:
$$\mathcal{K}_{\text{canonical}} = \{42, 1337, 2024, 7, 999\}$$

- **Role of 5 Seeds:** Evaluates stochastic training stability, initialization sensitivity, and variance dispersion across independent runs.
- **Reporting:** Individual run trajectories and summary $\text{Mean} \pm \text{Standard Deviation}$ across seeds.
- **Inferential Scope:** Five seeds do **NOT** serve as a bootstrap sampling population. No bootstrap confidence interval is computed over the 5 seed runs. Primary confirmatory statistical inference belongs strictly to downstream paired cluster bootstrap ($B=2000$, seed=10007) over evaluation units.
- **Zero Cherry-Picking:** Checkpoints from all 5 seeds are preserved and forwarded to downstream probe evaluations.
