# PRD — PsychoNet Node A
## AI-Assisted, Scenario-Based Occupational Fit Assessment Prototype

Version 1.0 | Status: Draft for implementation planning

---

## 1. Summary

Node A is the buildable prototype arm of the broader PsychoNet research project. It implements a scenario-based (SJT), behaviorally-augmented personality assessment pipeline that produces **confidence-scored occupational fit predictions** for corporate roles, with defence-domain scenarios as a secondary validation track. It exists to (a) generate the empirical results the research paper needs, and (b) stand alone as a demoable, pitchable prototype for corporate/VC audiences.

This is decision-support software. It does not make hiring/selection decisions. Every output includes a confidence/uncertainty statement and is explicitly framed as one input to a human decision-maker.

---

## 2. Problem statement

Self-report personality assessments used in hiring and selection are vulnerable to socially desirable responding, which degrades their usefulness in exactly the high-stakes settings where accuracy matters most. Existing AI-driven alternatives (LLM-generated SJTs, embedding-based person-job-fit models) each solve part of the problem but not the fusion: none combine meta-analytically-validated faking-resistance mechanisms (forced-choice, response latency) with NLP trait inference AND calibrated occupational-fit uncertainty in one system.

---

## 3. Goals

**Primary (research-gating) goals:**
- G1: Produce a working assessment pipeline that can generate real numbers for Models 1–7 of the ablation study.
- G2: Produce trait estimates with reported reliability (Cronbach's α / McDonald's ω) and convergent validity against a self-report proxy.
- G3: Produce occupational fit scores with confidence intervals, mapped against O*NET-derived role profiles.

**Secondary (product-facing) goals:**
- G4: A demoable web interface a non-technical evaluator (corporate HR, VC, professor) can walk through in under 10 minutes.
- G5: A defensible fairness/audit report generated per assessment run (subgroup performance breakdown where demographic data is available).

**Explicit non-goals for v1:**
- Not building adaptive/CAT item selection yet (future work — see Section 8).
- Not building the founder/VC or sports domain scoring (future work).
- Not building multimodal/biometric input of any kind (permanently excluded per design rules, not just deferred).
- Not making autonomous hire/no-hire decisions.

---

## 4. Users / stakeholders

| User | Need |
|---|---|
| Researcher (you) | Run assessments against public + pilot data, extract metrics for the paper |
| Pilot respondent (small-N primary data collection) | Take the assessment, understand what's being measured, trust it isn't a black box |
| Corporate/HR evaluator (demo audience) | See a role, see a candidate profile, see a fit score with reasoning |
| VC/patent reviewer (demo audience) | Understand the stability-audit/fairness-gate mechanism specifically — this is your strongest patent claim |

---

## 5. Functional requirements

### FR1 — Assessment delivery
- Present SJT items (from the validated item bank) in sequence.
- Capture: selected option, response latency per item, any answer changes before submission.
- Support forced-choice/graded response format per item design (Section 7 of Research Package v1).
- Support domain variant selection (corporate / military-framed) at assessment configuration time — not user-selectable mid-assessment.

### FR2 — Trait estimation
- Combine item-level responses into facet/domain-level trait estimates using the chosen psychometric model (CTT baseline, IRT where item bank supports it).
- Output includes point estimate + standard error / confidence band, not just a single number.
- Must run all 7 ablation model configurations against the same input where applicable, for comparability.

### FR3 — NLP feature extraction (where free-text responses exist)
- Sentence embeddings on any free-text justification fields.
- Feed into the fusion model as an additional feature block, not a replacement for structured response coding.

### FR4 — Occupational fit engine
- Role profiles stored as structured trait-requirement vectors (seeded from O*NET where available, supplemented by expert/literature-derived weights per Section 10 of the original research brief).
- Fit computation returns: fit score, confidence, per-trait evidence, and explicitly flagged low-evidence traits (traits the assessment didn't measure with enough reliability to weigh in).
- Must support at least corporate role profiles at launch; defence role profile as secondary.

### FR5 — Anti-gaming / robustness layer
- Apply the synthetic instructed-fake-good perturbation pipeline (calibrated against the meta-analytic benchmark effect size) as a test harness, not a live production feature — this is for generating the faking-robustness ablation numbers, not for detecting real users faking in production (v1 has no real faking-detection deployment target).
- Log response-consistency metrics (e.g., contradictory choices across construct-matched items) for later analysis.

### FR6 — Fairness/audit gate
- Generate a subgroup performance breakdown wherever demographic fields are present in the input data (age, gender, region — matching Open-Psychometrics dataset fields for early testing).
- This is the component most likely to anchor the patent's strongest claim — build it as a distinct, inspectable module, not an inline afterthought bolted onto the scoring engine.

### FR7 — Reporting/dashboard
- Per-assessment report: trait profile, fit score(s) against selected role(s), confidence bands, evidence summary, fairness-audit flag status.
- Exportable (PDF/JSON) for both research use and demo use.

### FR8 — Explainability
- Every fit score must be traceable to which items/traits drove it — no unexplained black-box number in the demo path.

---

## 6. Non-functional requirements

- **Privacy**: Design around India's DPDP framework — informed consent screen before assessment start, explicit data retention statement, no assessment data used for anything beyond stated research/demo purpose without re-consent.
- **No irreversible automation**: system never outputs a binary accept/reject; only scores + confidence + evidence.
- **Explainability over raw accuracy**: if a more accurate model is less explainable, default to the explainable one for v1 — this is a research-credibility project, not a production HR tool competing on leaderboard accuracy.
- **Reproducibility**: every ablation run must be logged (model version, dataset snapshot, random seed) — this feeds directly into the paper's experimental section.

---

## 7. Success metrics (research-facing, tie directly to paper sections)

- Internal consistency of the SJT item bank ≥ published Krumm et al. (2024) benchmark (ω ≈ 0.82) — if lower, item bank needs another generation/validation pass before results are usable.
- Convergent validity of SJT-derived traits vs. self-report proxy, r in the range already demonstrated achievable (~0.6+) — flag results far outside this range as a pipeline bug, not a discovery.
- Faking-robustness: measurable reduction in synthetic-fake-good score shift for Model 7 (fusion) vs. Model 1 (self-report baseline) — this is the single number that justifies the whole project if it holds.
- Fairness: no subgroup with a fit-score error-rate gap exceeding a threshold you set and justify explicitly in the paper (don't borrow a number from a different domain's fairness literature without checking it applies).

---

## 8. Phased delivery plan

| Phase | Scope | Blocks paper section |
|---|---|---|
| P0 (now) | Finalize SJT seed item bank + run rater validation | Blocks item bank being citable at all |
| P1 | Build assessment delivery + trait estimation for Models 1, 4, 6 (public-data-only models) | Unblocks partial Results |
| P2 | Build occupational fit engine against O*NET-seeded corporate role profiles | Unblocks Methodology F/G |
| P3 | Build forced-choice + latency capture, run Models 2, 3, 5, 7 | Unblocks full Ablation Study section |
| P4 | Build fairness/audit module, run subgroup breakdown | Unblocks Fairness/Limitations section |
| P5 (future work, not v1) | Adaptive/CAT item selection, defence GTO-equivalent research, founder/sports domains | Explicitly out of scope for this paper |

---

## 9. Risks

- SJT item bank fails validation (low ω, high multidimensionality flags) — mitigation: budget for at least one full regeneration cycle, don't assume first pass survives.
- No real faking-condition data available for final validation, only synthetic — mitigation: this is a stated limitation, not a fixable risk; do not let it block delivery, just be honest about it in the paper.
- Small pilot sample size limits statistical power for CFA-level psychometric claims — mitigation: report exploratory-level statistics honestly, don't overclaim confirmatory results from an undergraduate-scale N.
- Patent strategy depends on the fairness/audit gate being genuinely novel and CRI-compliant — mitigation: keep this module architecturally distinct (FR6) so it can be described/filed as a standalone mechanism if the rest of the system doesn't clear the software-patent bar.
