"""
MODULE: unified_intersection_schema
VERSION: 2.0.0
TYPE: Database Object Mapping (SQLAlchemy ORM)
USE: Consolidates identity records, multi-type relationship edges, 
     and spatio-temporal/telemetry footprints under one framework.
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import declarative_base, relationship
import uuid

Base = declarative_base()

class IdentityNode(Base):
    """
    [SLOT: UNIFIED_IDENTITY_REGISTRY]
    A polymorphic node representing an individual, organization, or asset.
    """
    __tablename__ = "identity_nodes"

    node_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    display_name = Column(String(150), nullable=False)
    node_type = Column(String(30), default="HUMAN")  # HUMAN, ORGANIZATION, MACHINE_ASSET
    
    # Base Metadata Slots
    birth_or_origin_year = Column(Integer, nullable=True)
    birth_or_origin_place = Column(String(150), nullable=True)
    y_haplogroup = Column(String(30), nullable=True)   # Deep ancestry markers
    mt_haplogroup = Column(String(30), nullable=True)
    
    created_at = Column(DateTime, server_default=func.now())

    # Structural lineages (Strict DAG pointers for ancestry engine)
    father_id = Column(String(36), ForeignKey("identity_nodes.node_id"), nullable=True)
    mother_id = Column(String(36), ForeignKey("identity_nodes.node_id"), nullable=True)


class RelationshipEdge(Base):
    """
    [SLOT: POLYMORPHIC_GRAPH_EDGES]
    Handles directed edges for social networks, ancestry trees, and corporate tenures.
    """
    __tablename__ = "relationship_edges"

    edge_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_id = Column(String(36), ForeignKey("identity_nodes.node_id"), nullable=False)
    destination_id = Column(String(36), ForeignKey("identity_nodes.node_id"), nullable=False)
    
    # Edge Class: SOCIAL, ANCESTRY, INSTITUTIONAL_TENURE
    edge_type = Column(String(30), nullable=False, default="SOCIAL")
    
    # Weighting metrics for social and network topology
    base_weight = Column(Float, default=0.5)
    telemetry_score = Column(Float, default=0.0)
    composite_weight = Column(Float, default=0.5) # Normalized 0.0 to 1.0
    
    # Temporal framing for institutional tenure or historical verification
    time_window_start = Column(Integer, nullable=True) # Year format
    time_window_end = Column(Integer, nullable=True)   # Null indicates active placement
    
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (UniqueConstraint('source_id', 'destination_id', 'edge_type', name='_source_dest_type_uc'),)


class SpatioTemporalTelemetry(Base):
    """
    [SLOT: GEOGRAPHIC_SIGNAL_TELEMETRY]
    Logs metadata bursts, technical footprints, and physical spatial presence profiles.
    """
    __tablename__ = "spatio_temporal_telemetry"

    log_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    node_id = Column(String(36), ForeignKey("identity_nodes.node_id"), nullable=False)
    
    telemetry_class = Column(String(30), nullable=False) # SPATIAL, SIGNAL_BURST, CONFIG_PROFILE
    geocode_cluster = Column(String(50), nullable=True) # Spatial box indexing
    timestamp_marker = Column(DateTime, nullable=True)
    parameter_key = Column(String(100), nullable=True)  # e.g., "software_version", "email_cadence"
    parameter_value = Column(String(250), nullable=True) # e.g., "v3.1.1", "high-frequency"

