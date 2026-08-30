# Research Package v1 — Pre-Writing Consolidation
## "Towards AI-Driven Personality Assessment: Trait Modelling and Occupational Fit Prediction for Defence and Corporate Domains"

Status: Research/design phase complete enough to begin drafting. This document consolidates everything established across prior sessions (Phase 1, locked) and this session (architecture selection, novelty, ablation design, item generation). It is written so you can go straight from this into an IEEE paper draft.

---

## 1. PROBLEM DEFINITION (locked)

Conventional self-report personality assessment (Likert-scale Big Five, NEO-type inventories) is vulnerable to socially desirable responding and impression management, particularly in high-stakes contexts (defence selection, hiring, founder evaluation). The research question is NOT "can AI replace psychometrics" — it is:

**"Can AI-driven, scenario-based, behavioral and adaptive personality assessment improve resistance to socially desirable responding and provide more useful occupational-fit predictions than conventional self-report assessment, while remaining psychometrically defensible?"**

Governing constraint carried through every design decision: harder-to-fake is not automatically better-validated. Every proposed mechanism must be checked against construct validity, reliability, and fairness — not just gaming-resistance.

### Sub-questions this package answers or scopes:
- RQ1 (self-report vulnerability) — answered via literature (Section 3)
- RQ2 (SJT vs direct rating) — answered via literature (Section 3)
- RQ3 (response time/consistency as signal) — answered via literature + own design (Section 3, 5)
- RQ4 (AI trait inference from behavioral data) — addressed via architecture design (Section 5)
- RQ5/RQ6 (occupational fit prediction) — addressed via architecture design (Section 5) and dataset catalog (Section 6)
- RQ7 (adaptive testing efficiency) — scoped as a secondary/future-work extension (Section 8)
- RQ8 (detecting manipulated responses) — addressed via ablation design (Section 5)
- RQ9 (cross-domain generalization) — **partially open** — see Section 8 (Scope Recommendation)

---

## 2. RESEARCH GAP MAP (locked + this session's additions)

**Already-closed gaps (established in Phase 1, carry into paper as background):**
- Assessment Centre validity is 0.29, not the older 0.37 figure — structured interviews now top-ranked at 0.42 (Sackett et al. correction to Schmidt & Hunter, 1998). *[Carried from Phase 1 — verify original DOI before final submission, as this session did not re-fetch it.]*
- Cronbach & Meehl (1955) nomological network remains the correct theoretical frame for critiquing construct validity of any multi-dimensional trait framework (used for SSB's OLQs, transferable to any occupational trait framework).
- IRT/CAT applies cleanly to item-based instruments (WAT/SRT-style) but has **no established equivalent for group-task/observational assessment** (GTO-style) — this remains an open methodological gap, not solved by this project, but explicitly nameable as a limitation/future-work item.
- Dimensions-vs-exercises paradox (Arthur et al., 2003) is an **active, unresolved debate** in assessment-center literature (per Hoffman, Melchers, Blair, Kleinmann, and Ladd & Dewberry 2024) — must not be presented as settled.

**Gaps identified/closed this session (verified via live search):**
- LLM-based SJT item generation is **no longer a novelty claim** — Krumm et al. (2024) validated GPT-3.5-generated SJT items against human-written ones (comparable internal consistency, ω = 0.82 vs 0.68, convergent validity r = 0.64 vs 0.69); a 2025/2026 HEXACO-SJT study extended this with systematic prompt/temperature optimization across GPT-4 and multiple LLMs. **Implication: do not claim "AI generates the scenarios" as your contribution.**
- Person-job-fit prediction via embeddings is a **saturated field — but only on the resume/skills-matching side** (ConFit v3, Person-Job-Fit joint representation learning, O*NET-transformer matching, TalentCLEF 2025). None of this work does trait-based occupational fit with calibrated uncertainty. **This remains a genuine, citable gap.**
- No public dataset exists with genuine high-stakes applicant faking labels on SJT-format items. Existing faking-condition datasets are Likert-format, lab-instructed (MacCann et al. 2017 on HEXACO; Hendy 2021 bifactor faking study), or purpose-built by individual research teams (a 2025 mouse-dynamics study built and published its own honest-vs-fake-good BFI-2 dataset because none existed). **This is a real, statable data limitation for your experimental design, not a solvable one with public data alone.**
- Forced-choice/quasi-ipsative formats have documented, meta-analytically quantified faking resistance (Martínez & Salgado, 2021: FC inventories show faking resistance; quasi-ipsative more resistant than other FC formats; effect sizes smaller in real applicant samples than lab studies — δ = 0.49 vs 1.27 for conscientiousness across formats).
- Response latency and faking are linked with an existing dedicated meta-analysis (Sagar & colleagues-type work indexed at Hogrefe, EJPA Vol 35 No 1) — response time is not a fabricated construct for this project, it has independent empirical grounding.
- Instructed-faking effect sizes on Big Five are moderate-to-large (51-study meta-analysis on dark triad/Big Five faking) — this is your **benchmark number** for sanity-checking any synthetic faking simulation you build.

---

## 3. TAXONOMY / METHOD COMPARISON (condensed for paper Table 1)

| Method | Construct validity | Faking resistance | Scalability | AI-automation fit |
|---|---|---|---|---|
| Big Five Likert self-report | Strong (decades of data) | Weak — the core problem | High | High (but pointless — automates the weak point) |
| Forced-choice / ipsative | Strong | Moderate–strong (meta-analytically supported) | Medium | High |
| SJT (human-written) | Moderate, varies by trait/study | Moderate | Low (expensive to author) | Medium |
| SJT (LLM-generated) | Comparable to human-written per Krumm et al. (2024) | Untested independently of item-writing method | High | High — but not novel anymore |
| Response-latency-augmented | N/A alone — always a supplement | Moderate, evidence-backed | High | High |
| TAT / projective | Weak, contested reliability | Claimed strong, evidence thin | Low | Low — explicitly not recommended (Phase 3 finding) |
| Multimodal/biometric | Unestablished cross-culturally | Unknown | Low legally | Excluded by your own design rules (bias/legal exposure) |
| Assessment centre (holistic) | 0.29 validity (corrected), dimensions-vs-exercises debate unresolved | Low-moderate | Low (resource-heavy) | Low |

---

## 4. CANDIDATE ARCHITECTURES A–H (from this session, unchanged — see prior message for full table)

Selected: **Candidate H** — SJT + forced-choice/ipsative scoring + response latency + NLP embeddings + confidence/uncertainty output, domain-weighted for cross-occupation fit. This is a **fusion and framing contribution**, not a from-scratch algorithmic invention — state this honestly in the paper's contribution claims.

Excluded: Candidate G (multimodal/biometric) — excluded per your own Phase 18 fairness/legal-exposure design rule (ACLU v. Intuit/HireVue precedent), not per lack of technical feasibility.

---

## 5. ABLATION DESIGN — MODELS 1–7 (from this session)

| Model | Composition | Primary data source |
|---|---|---|
| 1 | Big Five self-report only | Open-Source Psychometrics Project dataset (n≈1,015,342, includes response time) |
| 2 | Big Five + SJT | Above + SJT proxy bank (Section 7) |
| 3 | SJT only | SJT proxy bank |
| 4 | SJT + response time | SJT proxy bank + own timing capture |
| 5 | SJT + response time + forced-choice consistency | Own instrument |
| 6 | SJT + linguistic embeddings | PANDORA Reddit corpus / Big Five essay corpus |
| 7 | Full hybrid (proposed system) | All of the above, fused, + confidence/uncertainty layer |

Faking-robustness testing across all 7 models uses a **synthetic instructed-fake-good perturbation**, calibrated against the published moderate-to-large effect-size benchmark from the 51-study dark-triad/Big-Five faking meta-analysis — labeled explicitly as synthetic in the paper, not real faking behavior, per your own Rule 8/14.

---

## 6. DATASET CATALOG (verified this session + carried from Phase 1)

| Dataset | Size/pop. | Contains response time? | Contains occupational data? | Status |
|---|---|---|---|---|
| Open-Source Psychometrics Project Big Five set | n = 1,015,342, 50-item Likert | **Yes** — completion time, repeat-attempt count | No | Public, usable for Models 1 & 4 |
| PANDORA Reddit corpus | Large, self-report labeled | No | No | Public, usable for Model 6 (Phase 1 carryover) |
| Big Five essay corpora (Pennebaker/Mairesse-style) | ~2,400 essays typical | No | No | Public, usable for Model 6 (Phase 1 carryover) |
| Honest-vs-fake-good instructed datasets (MacCann 2017-style, Hendy 2021, 2025 mouse-dynamics study) | Small, study-specific | Some (mouse dynamics study) | No | **Availability not fully verified — check OSF/supplementary links directly before relying on any one of these; do not assume downloadable without confirming** |
| O*NET | Full US occupational database | N/A | **Yes** — this is the standard source for role-requirement profiles | Public, use for Section 10 role-requirement structuring |

**Explicit limitation to state in the paper:** no public dataset combines (a) SJT-format items, (b) response time, AND (c) genuine high-stakes faking labels. Any faking-robustness claim in this paper is necessarily based on synthetic perturbation and/or a small primary pilot — not large-scale public ground truth. This must be stated plainly, not hedged.

---

## 7. SJT ITEM BANK — STATUS

- 20 seed items generated this session (5 facets × generic + 3 domain variants: military/corporate/founder). **Explicitly unvalidated** — generated, not rater-checked at scale.
- One item (CONS-01-military) walked through a 10-rater mock validation this session:
  - Trait-match: strong pass (10/10 converged on the construct)
  - Single-dimensionality: majority pass, but 2/10 raters independently flagged an adjacent second dimension ("judgment"/"obedience") — worth checking whether this is domain-specific to the military framing (a genuine measurement-invariance finding either way)
  - Option-order: passed unanimously, BUT flagged as **too transparent** — an item this easy to rank correctly is also trivially easy for a real candidate to reverse-engineer and fake. This is a documented finding in itself: content-validity ease and faking-resistance can trade off against each other, which is a citable nuance extending your Phase 3 principle.
- **Action before paper-writing can cite empirical item results**: run the full rater-check protocol (instructions + response sheet already drafted) across all 20 seed items with a real rater panel (3–5 people minimum), and confirm response-option randomization was actually implemented per rater — this was flagged as unconfirmed in the mock walkthrough.

---

## 8. SCOPE RECOMMENDATION (answers Phase 23/Phase 27 of the original brief)

**Core domain for the paper:** Corporate occupational fit, using the hybrid architecture (Candidate H) validated against Open-Psychometrics + SJT proxy + essay/Reddit corpora.

**Secondary validation domain:** Defence screening — using the SJT domain-recontextualization approach (Section 7) as the bridge, framed around the already-identified GTO/IRT gap and the dimensions-vs-exercises debate, NOT as a full SSB redesign.

**Explicitly future work, not this paper:** Founder/VC assessment and sports domains. Neither has had a literature pass in this project yet (Phases 8 and 9 of the original brief remain genuinely undone), and neither has a public dataset identified. Cross-domain generalization (RQ9) should be stated as a **design property to test in future work**, not a claim this paper proves.

**Why this scope, not broader:** your own dataset constraint (no proprietary data, public data only) rules out a defensible founder/sports experimental section right now. Claiming a 4-domain framework without 4-domain data would violate Rule 13 ("do not overfit the research to available datasets" — here inverted: do not claim scope beyond available datasets).

---

## 9. NOVELTY CLAIMS FOR THE PAPER (revised, defensible)

1. Fusion of the two meta-analytically strongest faking-resistance mechanisms (forced-choice/quasi-ipsative + response latency) with NLP-based trait inference — validated individually in the literature, not previously fused for occupational-fit prediction.
2. Uncertainty-quantified occupational fit output (fit score + confidence + evidence + flagged gaps) rather than point-estimate trait-matching — addresses a real gap in the person-job-fit literature, which optimizes ranking accuracy, not calibrated uncertainty.
3. Cross-domain scenario recontextualization tested for measurement invariance (same latent trait across military/corporate/founder framings) — not attempted in the existing LLM-SJT literature, which stays domain-general.

**Explicitly dropped as non-novel:** "AI generates adaptive scenarios" (saturated, Krumm et al. 2024 onward), bare "embeddings for occupational fit" (saturated on the resume-matching side).

---

## 10. LIMITATIONS TO STATE EXPLICITLY IN THE PAPER

- No proprietary or large-scale primary data; all training/validation is on public proxies plus a small pilot.
- No public ground-truth dataset for high-stakes SJT-format faking; faking-robustness results are necessarily synthetic-perturbation-based and/or small-N primary pilot-based.
- Long-horizon criterion validity (does the fit score predict actual job/role performance years later) is a structural limitation of any single-project timeline — cannot be resolved here, must be named as future work.
- The GTO/group-observation IRT gap is not solved by this project — the paper only addresses item-based (SJT/WAT/SRT-style) assessment.
- The dimensions-vs-exercises debate is unresolved in the field; this paper's design choices should be framed as one defensible position within that debate, not as resolving it.
- Item transparency vs. content-validity tradeoff (found in the CONS-01-military walkthrough) should be reported as a finding, with a stated mitigation approach (surface-language obfuscation while preserving trait order) flagged as untested at time of writing unless you run it.

---

## 11. PRELIMINARY IEEE PAPER OUTLINE (mapped to what's ready to write NOW vs. what needs the pilot first)

- **I. Introduction** — ready to draft now (Section 1 of this doc)
- **II. Related Work** — ready to draft now (Sections 2–3), citations listed in Section 12 below
- **III. Problem Formulation** — ready to draft now (Section 1)
- **IV. Datasets** — ready to draft now (Section 6), with limitation explicitly stated
- **V. Methodology**
  - A. Assessment Design — ready (Section 7, item generation pipeline)
  - B. Psychometric Trait Modelling — ready (CTT/IRT framing from Phase 1)
  - C. NLP Feature Extraction — ready (Model 6 design)
  - D. Behavioral Feature Extraction — ready (Model 4/5 design)
  - E. Personality Prediction — ready (fusion architecture, Candidate H)
  - F–G. Occupational Role Modelling / Fit Prediction — ready (Section 8 scope, O*NET-based)
  - H. Confidence and Calibration — ready (novelty claim 2)
  - I. Anti-Gaming/Robustness — **partially ready** — synthetic perturbation design is ready, but real numbers require running the ablation
- **VI. Experimental Setup** — ready to draft now (Section 5, ablation table)
- **VII. Results** — **BLOCKED until rater validation + ablation runs are actually executed**
- **VIII. Ablation Study** — **BLOCKED**, same reason
- **IX. Fairness and Limitations** — ready to draft now (Section 10), results portion blocked
- **X. Discussion / XI. Future Work / XII. Conclusion** — draftable in skeleton form now, finalized after results

**Practical implication: you can draft roughly half the paper (I–VI, IX's limitations half) right now without running anything further. Sections VII–VIII need the rater validation pass and at least Models 1, 4, and 6 run against the public datasets before they can contain real numbers.**

---

## 12. REFERENCE LIST (verified via live search this session — DOIs/URLs included; Phase 1 carryover citations flagged for DOI re-verification before submission)

**Verified this session:**
- Krumm, S., Thiel, A. M., Reznik, N., Freudenstein, J.-P., Schäpers, P., & Mussel, P. (2024). Creating a Psychological Test in a Few Seconds: Can ChatGPT Develop a Psychometrically Sound Situational Judgment Test? *European Journal of Psychological Assessment*. https://doi.org/10.1027/1015-5759/a000878
- Martínez, A., & Salgado, J. F. (2021). A Meta-Analysis of the Faking Resistance of Forced-Choice Personality Inventories. *Frontiers in Psychology*, 12, 732241. https://doi.org/10.3389/fpsyg.2021.732241
- Hendy, N. et al. (2021). Using bifactor models to identify faking on Big Five questionnaires. *International Journal of Selection and Assessment*. Wiley Online Library.
- Seitz, T., Spengler, M., & Meiser, T. (2025). "What If Applicants Fake Their Responses?": Modeling Faking and Response Styles in High-Stakes Assessments Using the Multidimensional Nominal Response Model. https://doi.org/10.1177/00131644241307560
- Automatic Item Generation for Personality Situational Judgment Tests with Large Language Models. arXiv:2412.12144.
- Automated item generation for personality assessment: development and validation of large-language-model-derived HEXACO situational judgment tests. ScienceDirect, S0092656625001126.
- Faking on personality assessments in high-stakes settings: A critical review. ScienceDirect, S2352250X25000703.
- The Relationship Between Faking and Response Latencies: A Meta-Analysis. *European Journal of Psychological Assessment*, 35(1). Hogrefe. https://doi.org/10.1027/1015-5759/a000361
- How much can people fake on the dark triad? A meta-analysis and systematic review of instructed faking. ScienceDirect, S019188692200126X.
- Machine learning in recruiting: predicting personality from CVs and short text responses. *Frontiers*, 10.3389/frsps.2023.1290295.
- Driving Generative Agents With Their Personality (describes Open-Source Psychometrics Project dataset, n=1,015,342). arXiv:2402.14879.
- Detecting faking-good response style in personality questionnaires with four choice alternatives. *Psychological Research*. https://doi.org/10.1007/s00426-020-01473-3
- User modeling for detecting faking-good intent in online personality questionnaires in the wild based on mouse dynamics. *Multimedia Tools and Applications*, Springer, 2025.
- Quantifying and Mitigating Socially Desirable Responding in LLMs: A Desirability-Matched Graded Forced-Choice Psychometric Study. arXiv:2602.17262.
- ConFit v3: Improving Resume-Job Matching with LLM-based Re-Ranking. arXiv:2605.09760. (person-job-fit saturation evidence)
- Zhu, C. et al. (2018). Person-Job Fit: Adapting the Right Talent for the Right Job with Joint Representation Learning. arXiv:1810.04040.

**Carried from Phase 1 (locked, but re-verify exact DOI/citation before final submission — not re-fetched this session):**
- Sackett, P. R., et al. (2022). Correction to assessment-center validity estimates (0.29 vs. 0.37), structured interviews at 0.42.
- Cronbach, L. J., & Meehl, P. E. (1955). Construct validity in psychological tests.
- Arthur, W., et al. (2003). Dimensions-vs-exercises paradox in assessment centers.
- Ladd & Dewberry (2024) — unresolved status of dimensions-vs-exercises debate.
- ACLU v. Intuit / HireVue (2025) — multimodal/affective-computing bias and legal exposure precedent.

---

## 13. IMMEDIATE NEXT ACTIONS (in order)

1. Confirm rater response-option randomization method, then run the full 20-item rater-check protocol with 3–5 real raters.
2. Pull Open-Source Psychometrics Project dataset + PANDORA/essay corpora; run Models 1, 4, 6 to get real baseline numbers (these don't require the SJT bank to be finalized).
3. Once SJT items pass rater-check, run Models 2, 3, 5, 7.
4. Build and calibrate the synthetic faking perturbation against the 51-study meta-analytic effect-size benchmark.
5. Draft Sections I–VI and IX (limitations half) of the paper now, in parallel with steps 1–4.
6. Fill Sections VII–VIII once ablation results exist.
