from sqlalchemy.orm import Session
from backend.app.models.entities import Role, RoleRequirement

SEED_ROLES = [
    {
        "title": "Software Engineer",
        "onet_code": "15-1252.00",
        "description": "Develops, tests, and maintains computer applications and software systems requiring structured problem solving, continuous learning, and high attention to detail.",
        "requirements": [
            {"trait_name": "Conscientiousness", "target_level": 0.85, "weight": 1.2, "source": "ONET"},
            {"trait_name": "Openness", "target_level": 0.80, "weight": 1.1, "source": "ONET"},
            {"trait_name": "Emotional Stability", "target_level": 0.75, "weight": 1.0, "source": "ONET"},
            {"trait_name": "Agreeableness", "target_level": 0.65, "weight": 0.8, "source": "LITERATURE"},
            {"trait_name": "Extraversion", "target_level": 0.50, "weight": 0.6, "source": "LITERATURE"}
        ]
    },
    {
        "title": "Data Analyst",
        "onet_code": "15-2051.00",
        "description": "Analyzes complex datasets to identify trends, draw actionable insights, and build quantitative models demanding analytical rigor and accuracy.",
        "requirements": [
            {"trait_name": "Conscientiousness", "target_level": 0.88, "weight": 1.3, "source": "ONET"},
            {"trait_name": "Openness", "target_level": 0.82, "weight": 1.1, "source": "ONET"},
            {"trait_name": "Emotional Stability", "target_level": 0.78, "weight": 1.0, "source": "ONET"},
            {"trait_name": "Agreeableness", "target_level": 0.60, "weight": 0.7, "source": "EXPERT"},
            {"trait_name": "Extraversion", "target_level": 0.55, "weight": 0.6, "source": "EXPERT"}
        ]
    },
    {
        "title": "Project Manager",
        "onet_code": "11-9199.00",
        "description": "Leads cross-functional project teams, coordinates resources, manages stakeholder expectations, and mitigates delivery risks under high operational pressure.",
        "requirements": [
            {"trait_name": "Extraversion", "target_level": 0.85, "weight": 1.2, "source": "ONET"},
            {"trait_name": "Conscientiousness", "target_level": 0.85, "weight": 1.2, "source": "ONET"},
            {"trait_name": "Agreeableness", "target_level": 0.80, "weight": 1.1, "source": "ONET"},
            {"trait_name": "Emotional Stability", "target_level": 0.82, "weight": 1.1, "source": "ONET"},
            {"trait_name": "Openness", "target_level": 0.70, "weight": 0.8, "source": "LITERATURE"}
        ]
    }
]

def seed_onet_roles(db: Session):
    """Seeds the O*NET role profiles into the database if not present."""
    seeded_count = 0
    for role_data in SEED_ROLES:
        existing = db.query(Role).filter(Role.title == role_data["title"]).first()
        if not existing:
            role = Role(
                title=role_data["title"],
                onet_code=role_data["onet_code"],
                description=role_data["description"]
            )
            db.add(role)
            db.flush()

            for req in role_data["requirements"]:
                requirement = RoleRequirement(
                    role_id=role.id,
                    trait_name=req["trait_name"],
                    target_level=req["target_level"],
                    weight=req["weight"],
                    source=req["source"]
                )
                db.add(requirement)
            seeded_count += 1
    
    db.commit()
    return seeded_count
