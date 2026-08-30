from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from backend.app.db.session import get_db, Base, engine
from backend.app.models.entities import (
    Candidate, Assessment, Scenario, Item, Response, ResponseTime,
    TraitScore, Role, FitScore, FairnessAudit, AuditLog
)
from backend.app.fusion.ablation_runner import AblationEngine
from backend.app.fit_engine.matcher import FitEngine
from backend.app.fit_engine.onet_seeder import seed_onet_roles
from backend.app.anti_gaming.harness import AntiGamingHarness
from backend.app.fairness.audit import FairnessAuditGate
from backend.app.explainability.tracer import ExplainabilityTracer

router = APIRouter()

ablation_engine = AblationEngine()
fit_engine = FitEngine()
anti_gaming_harness = AntiGamingHarness()
fairness_gate = FairnessAuditGate()
explainability_tracer = ExplainabilityTracer()

# --- Pydantic Schemas ---
class CandidateStartRequest(BaseModel):
    consent_given: bool
    domain_variant: str = "corporate"
    age: Optional[int] = None
    gender: Optional[str] = None
    region: Optional[str] = None

class ResponseSubmission(BaseModel):
    item_id: str
    selected_option: str
    latency_ms: float
    answer_change_count: int = 0
    free_text_justification: Optional[str] = None

class AssessmentSubmitRequest(BaseModel):
    assessment_id: str
    responses: List[ResponseSubmission]
    self_report_proxy: Optional[Dict[str, float]] = None

# --- Seed Sample Items ---
def ensure_sample_items_seeded(db: Session):
    if db.query(Item).count() > 0:
        return

    scenario = Scenario(
        title="Software Release Crisis",
        narrative="A critical production bug is detected 1 hour prior to a scheduled client product release. The bug causes intermittent data display errors for 5% of users under heavy load.",
        domain="corporate"
    )
    db.add(scenario)
    db.flush()

    items = [
        Item(
            scenario_id=scenario.id,
            item_type="sjt",
            prompt="What is your immediate priority step?",
            target_trait="Conscientiousness",
            options_json=[
                {"id": "A", "text": "Halt release, fix the bug thoroughly, and notify leadership.", "score": 1.0},
                {"id": "B", "text": "Proceed with release and patch the bug silently in background.", "score": 0.3},
                {"id": "C", "text": "Deploy hotfix without full regression testing.", "score": 0.5},
                {"id": "D", "text": "Pass responsibility to the QA lead.", "score": 0.1}
            ]
        ),
        Item(
            scenario_id=scenario.id,
            item_type="sjt",
            prompt="How do you communicate the delay to cross-functional stakeholders?",
            target_trait="Emotional Stability",
            options_json=[
                {"id": "A", "text": "Send a calm, structured update outlining root cause, fix time, and impact.", "score": 1.0},
                {"id": "B", "text": "Blame the QA team for discovering the bug late.", "score": 0.1},
                {"id": "C", "text": "Minimize the bug's impact and downplay stakeholder concerns.", "score": 0.4},
                {"id": "D", "text": "Wait until asked directly before giving an update.", "score": 0.2}
            ]
        ),
        Item(
            scenario_id=scenario.id,
            item_type="sjt",
            prompt="How do you engage team members during the emergency patch work?",
            target_trait="Agreeableness",
            options_json=[
                {"id": "A", "text": "Collaborate closely, offer support, and check in on team workload.", "score": 1.0},
                {"id": "B", "text": "Issue strict orders and demand immediate completion.", "score": 0.4},
                {"id": "C", "text": "Work independently without consulting others.", "score": 0.5},
                {"id": "D", "text": "Leave the office early once your task is done.", "score": 0.1}
            ]
        )
    ]
    for itm in items:
        db.add(itm)
    db.commit()

# --- Endpoints ---

@router.get("/health")
def health_check():
    return {"status": "ok", "project": "Mapan", "version": "1.0.0"}

@router.get("/roles")
def get_roles(db: Session = Depends(get_db)):
    seed_onet_roles(db)
    roles = db.query(Role).all()
    out = []
    for r in roles:
        reqs = db.query(Role.requirements.property.mapper.class_).filter_by(role_id=r.id).all()
        out.append({
            "id": r.id,
            "title": r.title,
            "onet_code": r.onet_code,
            "description": r.description,
            "requirements": [{"trait": req.trait_name, "target": req.target_level, "weight": req.weight} for req in r.requirements]
        })
    return out

@router.post("/assessment/start")
def start_assessment(payload: CandidateStartRequest, db: Session = Depends(get_db)):
    if not payload.consent_given:
        raise HTTPException(status_code=400, detail="Informed consent is required under DPDP framework.")

    seed_onet_roles(db)
    ensure_sample_items_seeded(db)

    candidate = Candidate(
        consent_given=True,
        age=payload.age,
        gender=payload.gender,
        region=payload.region
    )
    db.add(candidate)
    db.flush()

    assessment = Assessment(
        candidate_id=candidate.id,
        domain_variant=payload.domain_variant,
        status="in_progress"
    )
    db.add(assessment)

    log = AuditLog(
        assessment_id=assessment.id,
        event_type="SESSION_START",
        details_json={"domain_variant": payload.domain_variant, "consent": True}
    )
    db.add(log)
    db.commit()

    return {
        "assessment_id": assessment.id,
        "candidate_id": candidate.id,
        "domain_variant": assessment.domain_variant,
        "status": assessment.status
    }

@router.get("/assessment/items")
def get_assessment_items(db: Session = Depends(get_db)):
    ensure_sample_items_seeded(db)
    items = db.query(Item).all()
    result = []
    for itm in items:
        scen = db.query(Scenario).filter(Scenario.id == itm.scenario_id).first()
        result.append({
            "id": itm.id,
            "scenario_title": scen.title if scen else "Scenario",
            "scenario_narrative": scen.narrative if scen else "",
            "prompt": itm.prompt,
            "target_trait": itm.target_trait,
            "options": itm.options_json
        })
    return result

@router.post("/assessment/submit")
def submit_assessment(payload: AssessmentSubmitRequest, db: Session = Depends(get_db)):
    assessment = db.query(Assessment).filter(Assessment.id == payload.assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    # Record responses
    sjt_scores: Dict[str, List[float]] = {}
    latencies: Dict[str, float] = {}
    free_texts: List[str] = []

    for resp_data in payload.responses:
        itm = db.query(Item).filter(Item.id == resp_data.item_id).first()
        if not itm:
            continue

        resp = Response(
            assessment_id=assessment.id,
            item_id=itm.id,
            selected_option=resp_data.selected_option,
            free_text_justification=resp_data.free_text_justification
        )
        db.add(resp)
        db.flush()

        resp_time = ResponseTime(
            response_id=resp.id,
            latency_ms=resp_data.latency_ms,
            answer_change_count=resp_data.answer_change_count
        )
        db.add(resp_time)

        # Lookup option score
        opt_score = 0.5
        for opt in itm.options_json:
            if opt["id"] == resp_data.selected_option:
                opt_score = float(opt.get("score", 0.5))
                break

        sjt_scores.setdefault(itm.target_trait, []).append(opt_score)
        latencies[itm.id] = resp_data.latency_ms
        if resp_data.free_text_justification:
            free_texts.append(resp_data.free_text_justification)

    # Execute Model 7 (Full Fused Model)
    fusion_payload = {
        "self_report_scores": payload.self_report_proxy or {"Conscientiousness": 0.7, "Emotional Stability": 0.7, "Agreeableness": 0.7, "Extraversion": 0.7, "Openness": 0.7},
        "sjt_item_scores": sjt_scores,
        "response_latencies_ms": latencies,
        "forced_choice_consistency": 0.85,
        "free_text_justifications": free_texts
    }

    trait_estimates = ablation_engine.run_model("model_7", fusion_payload)

    # Store trait scores
    for trait_name, est in trait_estimates.items():
        ts = TraitScore(
            assessment_id=assessment.id,
            trait_name=trait_name,
            point_estimate=est["score"],
            standard_error=est["se"],
            model_config_tag="model_7"
        )
        db.add(ts)

    # Compute fit against all 3 seed roles
    roles = db.query(Role).all()
    fit_outputs = {}

    for r in roles:
        reqs = db.query(Role.requirements.property.mapper.class_).filter_by(role_id=r.id).all()
        req_list = [{"trait_name": req.trait_name, "target_level": req.target_level, "weight": req.weight} for req in r.requirements]

        fit_res = fit_engine.compute_fit(trait_estimates, req_list)
        fs = FitScore(
            assessment_id=assessment.id,
            role_id=r.id,
            overall_fit_score=fit_res["fit_score"],
            confidence_interval_low=fit_res["confidence_interval_low"],
            confidence_interval_high=fit_res["confidence_interval_high"],
            low_evidence_traits_json=fit_res["low_evidence_traits"],
            model_config_tag="model_7"
        )
        db.add(fs)
        fit_outputs[r.title] = fit_res

    # Fairness audit check
    cand = db.query(Candidate).filter(Candidate.id == assessment.candidate_id).first()
    demo = {"gender": cand.gender, "age": cand.age, "region": cand.region} if cand else {}

    audit_res = fairness_gate.run_subgroup_audit([{"demographics": demo, "fit_score": fit_outputs.get("Software Engineer", {}).get("fit_score", 75.0)}])

    fa = FairnessAudit(
        assessment_id=assessment.id,
        subgroup_key="gender",
        subgroup_value=str(demo.get("gender", "Unspecified")),
        metric_name="max_score_gap",
        metric_value=audit_res["subgroup_breakdown"].get("gender", {}).get("max_score_gap", 0.0),
        threshold=5.0,
        passed=audit_res["overall_fairness_passed"]
    )
    db.add(fa)

    assessment.status = "completed"
    db.commit()

    return {
        "assessment_id": assessment.id,
        "status": "completed",
        "trait_estimates": trait_estimates,
        "fit_scores": fit_outputs,
        "fairness_passed": audit_res["overall_fairness_passed"]
    }

@router.post("/eval/ablation")
def run_ablation_eval(payload: Dict[str, Any]):
    return ablation_engine.run_all_models(payload)

@router.post("/eval/anti-gaming")
def run_anti_gaming_eval(payload: Dict[str, Any]):
    return anti_gaming_harness.evaluate_faking_robustness(payload)

@router.get("/reports/{assessment_id}")
def get_assessment_report(assessment_id: str, db: Session = Depends(get_db)):
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment report not found")

    trait_scores = db.query(TraitScore).filter(TraitScore.assessment_id == assessment_id).all()
    fit_scores = db.query(FitScore).filter(FitScore.assessment_id == assessment_id).all()
    audits = db.query(FairnessAudit).filter(FairnessAudit.assessment_id == assessment_id).all()

    traits_map = {t.trait_name: {"score": t.point_estimate, "se": t.standard_error} for t in trait_scores}

    fit_report = []
    for fs in fit_scores:
        role = db.query(Role).filter(Role.id == fs.role_id).first()
        role_title = role.title if role else "Role"
        reqs = db.query(Role.requirements.property.mapper.class_).filter_by(role_id=role.id).all() if role else []
        req_list = [{"trait_name": req.trait_name, "target_level": req.target_level, "weight": req.weight} for req in reqs]

        fit_res = {
            "fit_score": fs.overall_fit_score,
            "confidence_interval_low": fs.confidence_interval_low,
            "confidence_interval_high": fs.confidence_interval_high,
            "low_evidence_traits": fs.low_evidence_traits_json or [],
            "trait_breakdown": fit_engine.compute_fit(traits_map, req_list)["trait_breakdown"]
        }

        explanation = explainability_tracer.generate_explanation(role_title, fit_res, traits_map, [])

        fit_report.append({
            "role_title": role_title,
            "fit_score": fs.overall_fit_score,
            "ci_low": fs.confidence_interval_low,
            "ci_high": fs.confidence_interval_high,
            "low_evidence_traits": fs.low_evidence_traits_json or [],
            "explanation": explanation
        })

    return {
        "assessment_id": assessment.id,
        "domain_variant": assessment.domain_variant,
        "status": assessment.status,
        "traits": traits_map,
        "role_fits": fit_report,
        "fairness_audits": [{"subgroup": a.subgroup_key, "val": a.subgroup_value, "passed": a.passed} for a in audits]
    }
