import datetime
import uuid
from sqlalchemy import (
    Column, String, Float, Integer, Boolean, DateTime, ForeignKey, Text, JSON
)
from sqlalchemy.orm import relationship
from backend.app.db.session import Base

def generate_uuid():
    return str(uuid.uuid4())

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(String, primary_key=True, default=generate_uuid)
    external_id = Column(String, nullable=True, index=True)
    consent_given = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Optional demographic fields for fairness audit (not mandatory)
    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)
    region = Column(String, nullable=True)

    assessments = relationship("Assessment", back_populates="candidate", cascade="all, delete-orphan")

class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(String, primary_key=True, default=generate_uuid)
    candidate_id = Column(String, ForeignKey("candidates.id"), nullable=False)
    domain_variant = Column(String, default="corporate", nullable=False) # 'corporate' or 'military'
    status = Column(String, default="in_progress") # 'in_progress', 'completed'
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    candidate = relationship("Candidate", back_populates="assessments")
    responses = relationship("Response", back_populates="assessment", cascade="all, delete-orphan")
    trait_scores = relationship("TraitScore", back_populates="assessment", cascade="all, delete-orphan")
    fit_scores = relationship("FitScore", back_populates="assessment", cascade="all, delete-orphan")
    fairness_audits = relationship("FairnessAudit", back_populates="assessment", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="assessment", cascade="all, delete-orphan")

class Scenario(Base):
    __tablename__ = "scenarios"

    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String, nullable=False)
    narrative = Column(Text, nullable=False)
    domain = Column(String, default="corporate")

    items = relationship("Item", back_populates="scenario")

class Item(Base):
    __tablename__ = "items"

    id = Column(String, primary_key=True, default=generate_uuid)
    scenario_id = Column(String, ForeignKey("scenarios.id"), nullable=True)
    item_type = Column(String, nullable=False) # 'sjt', 'forced_choice', 'likert'
    prompt = Column(Text, nullable=False)
    target_trait = Column(String, nullable=False) # e.g. 'Conscientiousness', 'Emotional Stability'
    options_json = Column(JSON, nullable=False) # list of options with score mappings

    scenario = relationship("Scenario", back_populates="items")
    responses = relationship("Response", back_populates="item")

class Response(Base):
    __tablename__ = "responses"

    id = Column(String, primary_key=True, default=generate_uuid)
    assessment_id = Column(String, ForeignKey("assessments.id"), nullable=False)
    item_id = Column(String, ForeignKey("items.id"), nullable=False)
    selected_option = Column(String, nullable=False)
    free_text_justification = Column(Text, nullable=True)

    assessment = relationship("Assessment", back_populates="responses")
    item = relationship("Item", back_populates="responses")
    response_time = relationship("ResponseTime", uselist=False, back_populates="response", cascade="all, delete-orphan")

class ResponseTime(Base):
    __tablename__ = "response_times"

    id = Column(String, primary_key=True, default=generate_uuid)
    response_id = Column(String, ForeignKey("responses.id"), nullable=False)
    latency_ms = Column(Float, nullable=False) # Latency in milliseconds
    answer_change_count = Column(Integer, default=0, nullable=False)

    response = relationship("Response", back_populates="response_time")

class TraitScore(Base):
    __tablename__ = "trait_scores"

    id = Column(String, primary_key=True, default=generate_uuid)
    assessment_id = Column(String, ForeignKey("assessments.id"), nullable=False)
    trait_name = Column(String, nullable=False) # Big Five / Facet name
    point_estimate = Column(Float, nullable=False)
    standard_error = Column(Float, nullable=False)
    model_config_tag = Column(String, nullable=False) # 'model_1' .. 'model_7'

    assessment = relationship("Assessment", back_populates="trait_scores")

class Role(Base):
    __tablename__ = "roles"

    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String, nullable=False, unique=True)
    onet_code = Column(String, nullable=True)
    description = Column(Text, nullable=True)

    requirements = relationship("RoleRequirement", back_populates="role", cascade="all, delete-orphan")
    fit_scores = relationship("FitScore", back_populates="role")

class RoleRequirement(Base):
    __tablename__ = "role_requirements"

    id = Column(String, primary_key=True, default=generate_uuid)
    role_id = Column(String, ForeignKey("roles.id"), nullable=False)
    trait_name = Column(String, nullable=False)
    target_level = Column(Float, nullable=False) # Normalized 0 to 1 scale
    weight = Column(Float, default=1.0)
    source = Column(String, default="ONET") # 'ONET', 'EXPERT', 'LITERATURE'

    role = relationship("Role", back_populates="requirements")

class FitScore(Base):
    __tablename__ = "fit_scores"

    id = Column(String, primary_key=True, default=generate_uuid)
    assessment_id = Column(String, ForeignKey("assessments.id"), nullable=False)
    role_id = Column(String, ForeignKey("roles.id"), nullable=False)
    overall_fit_score = Column(Float, nullable=False) # 0 - 100 fit index
    confidence_interval_low = Column(Float, nullable=False)
    confidence_interval_high = Column(Float, nullable=False)
    low_evidence_traits_json = Column(JSON, nullable=True) # Array of low reliability trait names
    model_config_tag = Column(String, default="model_7")

    assessment = relationship("Assessment", back_populates="fit_scores")
    role = relationship("Role", back_populates="fit_scores")

class FairnessAudit(Base):
    __tablename__ = "fairness_audits"

    id = Column(String, primary_key=True, default=generate_uuid)
    assessment_id = Column(String, ForeignKey("assessments.id"), nullable=False)
    subgroup_key = Column(String, nullable=False) # e.g. 'gender', 'age_bracket'
    subgroup_value = Column(String, nullable=False)
    metric_name = Column(String, nullable=False) # e.g. 'mean_fit_score_gap'
    metric_value = Column(Float, nullable=False)
    threshold = Column(Float, nullable=False)
    passed = Column(Boolean, nullable=False)

    assessment = relationship("Assessment", back_populates="fairness_audits")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=generate_uuid)
    assessment_id = Column(String, ForeignKey("assessments.id"), nullable=False)
    event_type = Column(String, nullable=False) # 'SESSION_START', 'SUBMISSION', 'FAIRNESS_CHECK'
    details_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    assessment = relationship("Assessment", back_populates="audit_logs")
