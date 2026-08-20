from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    Boolean,
    DateTime,
    ForeignKey
)

from sqlalchemy.orm import relationship

from app.database import Base


class Contract(Base):

    __tablename__ = "contracts"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    filename = Column(
        String(255),
        nullable=False
    )

    title = Column(
        String(500),
        nullable=True
    )

    extracted_text = Column(
        Text,
        nullable=True
    )

    summary = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    clauses = relationship(
        "Clause",
        back_populates="contract",
        cascade="all, delete-orphan"
    )

    risks = relationship(
        "Risk",
        back_populates="contract",
        cascade="all, delete-orphan"
    )

    obligations = relationship(
        "Obligation",
        back_populates="contract",
        cascade="all, delete-orphan"
    )

    entities = relationship(
        "Entity",
        back_populates="contract",
        cascade="all, delete-orphan"
    )


class Clause(Base):

    __tablename__ = "clauses"

    id = Column(
        Integer,
        primary_key=True
    )

    contract_id = Column(
        Integer,
        ForeignKey("contracts.id"),
        nullable=False
    )

    category = Column(
        String(255),
        nullable=False
    )

    text = Column(
        Text,
        nullable=True
    )

    contract = relationship(
        "Contract",
        back_populates="clauses"
    )


class Risk(Base):

    __tablename__ = "risks"

    id = Column(
        Integer,
        primary_key=True
    )

    contract_id = Column(
        Integer,
        ForeignKey("contracts.id"),
        nullable=False
    )

    category = Column(
        String(255)
    )

    clause = Column(
        Text
    )

    risk_score = Column(
        Float
    )

    risk_level = Column(
        String(50)
    )

    reason = Column(
        Text
    )

    contract = relationship(
        "Contract",
        back_populates="risks"
    )


class Obligation(Base):

    __tablename__ = "obligations"

    id = Column(
        Integer,
        primary_key=True
    )

    contract_id = Column(
        Integer,
        ForeignKey("contracts.id"),
        nullable=False
    )

    obligation = Column(
        Text
    )

    responsible_party = Column(
        String(500)
    )

    deadline = Column(
        String(255)
    )

    frequency = Column(
        String(255)
    )

    trigger = Column(
        Text
    )

    category = Column(
        String(255)
    )

    consequence = Column(
        Text
    )

    evidence = Column(
        Text
    )

    completed = Column(
        Boolean,
        default=False
    )

    contract = relationship(
        "Contract",
        back_populates="obligations"
    )


class Entity(Base):

    __tablename__ = "entities"

    id = Column(
        Integer,
        primary_key=True
    )

    contract_id = Column(
        Integer,
        ForeignKey("contracts.id"),
        nullable=False
    )

    entity_type = Column(
        String(100)
    )

    entity_value = Column(
        Text
    )

    contract = relationship(
        "Contract",
        back_populates="entities"
    )