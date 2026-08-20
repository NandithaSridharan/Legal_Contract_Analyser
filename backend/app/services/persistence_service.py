from typing import Any

from sqlalchemy.orm import Session

from app.models import Contract, Clause, Risk, Entity, Obligation


def _unwrap(value: Any, key: str, default: Any) -> Any:
    if isinstance(value, dict) and key in value:
        return value[key]
    return value if value is not None else default


def _save_clause_rows(db: Session, contract_id: int, clauses: Any) -> None:
    clauses = _unwrap(clauses, "clauses", {})
    if isinstance(clauses, list):
        rows = ((item.get("category", "Other"), item.get("text") or item.get("clause") or item.get("content", "")) for item in clauses if isinstance(item, dict))
    elif isinstance(clauses, dict):
        rows = ((category, item.get("text") or item.get("clause") or item.get("content", "") if isinstance(item, dict) else item) for category, item in clauses.items())
    else:
        rows = ()
    for category, text in rows:
        if text is not None and str(text).strip():
            db.add(Clause(contract_id=contract_id, category=str(category), text=str(text)))


def _save_risk_rows(db: Session, contract_id: int, risks: Any) -> None:
    risks = _unwrap(risks, "risks", [])
    if not isinstance(risks, list):
        return
    for item in risks:
        if isinstance(item, dict):
            db.add(Risk(contract_id=contract_id, category=item.get("category"), clause=item.get("clause"), risk_score=item.get("risk_score", 0), risk_level=item.get("risk_level"), reason=item.get("reason")))


def _save_entity_rows(db: Session, contract_id: int, entities: Any) -> None:
    entities = _unwrap(entities, "entities", {})
    if isinstance(entities, list):
        entities = {item.get("entity_type", item.get("type", "Other")): item.get("entity_value", item.get("value")) for item in entities if isinstance(item, dict)}
    if not isinstance(entities, dict):
        return
    for entity_type, value in entities.items():
        values = value if isinstance(value, list) else [value]
        for item in values:
            if item is not None and str(item).strip():
                db.add(Entity(contract_id=contract_id, entity_type=str(entity_type), entity_value=str(item)))


def _save_obligation_rows(db: Session, contract_id: int, obligations: Any) -> None:
    obligations = _unwrap(obligations, "obligations", [])
    if not isinstance(obligations, list):
        return
    for item in obligations:
        if not isinstance(item, dict):
            continue
        db.add(Obligation(contract_id=contract_id, obligation=item.get("obligation"), responsible_party=item.get("responsible_party"), deadline=item.get("deadline"), frequency=item.get("frequency"), trigger=item.get("trigger"), category=item.get("category"), consequence=item.get("consequence"), evidence=item.get("evidence"), completed=bool(item.get("completed", False))))


def save_complete_analysis(db: Session, contract_id: int, summary: Any, clauses: Any, risks: Any, entities: Any, obligations: Any):
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise ValueError("Contract not found.")

    contract.summary = summary.get("summary", "") if isinstance(summary, dict) else str(summary or "")
    for model in (Clause, Risk, Entity, Obligation):
        db.query(model).filter(model.contract_id == contract_id).delete(synchronize_session=False)
    _save_clause_rows(db, contract_id, clauses)
    _save_risk_rows(db, contract_id, risks)
    _save_entity_rows(db, contract_id, entities)
    _save_obligation_rows(db, contract_id, obligations)
    db.commit()
    db.refresh(contract)
    return contract
