"""
MODULE: unified_intersection_api
VERSION: 2.0.0
TYPE: Central Control Router & Engine Pipeline (FastAPI)
USE: Computes cross-sections across Social, Ancestral, and Telemetric datasets.
"""

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Set, Any, Optional
import math

app = FastAPI(title="Unified Intersection Detection Framework", version="2.0.0")

# --- Consolidated Pydantic Transport Models ---
class OverlapMetricSummary(BaseModel):
    mode: str
    match_count: int
    primary_index: float  # Kinship Coeff, Jaccard Index, or Temporal Sync score
    summary_text: str

class DiscrepancyLog(BaseModel):
    parameter: str
    origin_tree_val: str
    target_tree_val: str
    severity: str

class IntersectedNodeDetail(BaseModel):
    node_id: str
    display_name: str
    mode_specific_metrics: Dict[str, Any]

class UnifiedIntersectionResponse(BaseModel):
    status: str
    origin_id: str
    target_id: str
    metrics: OverlapMetricSummary
    shared_neighborhood: List[IntersectedNodeDetail]
    data_discrepancies: List[DiscrepancyLog]
    spatio_temporal_overlaps: List[Dict[str, Any]]

# --- Comprehensive Graph Dataset Mock Loader ---
def load_unified_mock_environment() -> Dict[str, Any]:
    return {
        "nodes": {
            "id_brad": {"name": "Brad Geiger", "born": 1980, "place": "Ohio", "y_hap": "R1b-M269", "father": "id_anc_father", "mother": None},
            "id_target": {"name": "Target Node", "born": 1982, "place": "Kentucky", "y_hap": "R1b-M269", "father": "id_anc_uncle", "mother": None},
            "id_anc_father": {"name": "Arthur Geiger", "born": 1950, "place": "Ohio", "father": "id_gfa_shared", "mother": None},
            "id_anc_uncle": {"name": "Barnaby Geiger", "born": 1953, "place": "Frankfurt", "father": "id_gfa_shared", "mother": None},
            "id_gfa_shared": {"name": "George Root", "born": 1920, "place": "Ohio", "father": None, "mother": None},
            "id_proxy_social": {"name": "Sarah Connor", "born": None, "place": None},
            "id_org_unit": {"name": "Strategic Ops Command", "born": None, "place": None}
        },
        "social_edges": {
            "id_brad": {"id_proxy_social": 0.90, "id_target": 0.10},
            "id_target": {"id_proxy_social": 0.85, "id_brad": 0.10}
        },
        "tenure_edges": {
            "id_brad": [{"org": "id_org_unit", "start": 2018, "end": 2022, "role": "Manager"}],
            "id_target": [{"org": "id_org_unit", "start": 2020, "end": 2024, "role": "Analyst"}]
        },
        "telemetry": [
            {"node_id": "id_brad", "class": "SPATIAL", "loc": "Zone-US-VA", "start": 2021, "end": 2022},
            {"node_id": "id_target", "class": "SPATIAL", "loc": "Zone-US-VA", "start": 2021, "end": 2023}
        ]
    }

# --- Ancestry Lineage Traversal Engine with Loop Protection ---
def trace_lineage_recursive(node_id: str, nodes_data: Dict[str, Any], depth: int, max_depth: int, visited_path: List[str], profile: Dict[str, List[int]]) -> Dict[str, List[int]]:
    if not node_id or node_id not in nodes_data or depth > max_depth:
        return profile
    
    # Loop Protection / Pedigree Collapse Detection
    if node_id in visited_path:
        # Loop detected within this trace path branch
        return profile
        
    if node_id not in profile:
        profile[node_id] = []
    profile[node_id].append(depth)
    
    extended_path = visited_path + [node_id]
    node = nodes_data[node_id]
    
    if node.get("father"):
        trace_lineage_recursive(node["father"], nodes_data, depth + 1, max_depth, extended_path, profile)
    if node.get("mother"):
        trace_lineage_recursive(node["mother"], nodes_data, depth + 1, max_depth, extended_path, profile)
        
    return profile

# --- Router Execution Endpoint ---
@app.get("/api/v2/network/intersect", response_model=UnifiedIntersectionResponse)
async def execute_unified_intersection(
    origin_id: str = Query(..., description="Origin node identifier"),
    target_id: str = Query(..., description="Target node identifier"),
    processing_mode: str = Query("SOCIAL", description="Processing modes: SOCIAL, ANCESTRY, INSTITUTIONAL")
):
    env = load_unified_mock_environment()
    nodes = env["nodes"]
    
    if origin_id not in nodes or target_id not in nodes:
        raise HTTPException(status_code=404, detail="Origin or Target identifier not found inside system repository.")

    shared_neighborhood: List[IntersectedNodeDetail] = []
    discrepancy_logs: List[DiscrepancyLog] = []
    spatial_overlaps: List[Dict[str, Any]] = []
    
    # Default metric slots
    match_count = 0
    primary_index_val = 0.0
    summary = "No intersections mapped."

    # ==========================================================================
    # MODE A: ANCESTRY PIPELINE
    # ==========================================================================
    if processing_mode.upper() == "ANCESTRY":
        # Trace family trees backward with absolute depth cap
        origin_profile = trace_lineage_recursive(origin_id, nodes, 0, 8, [], {})
        target_profile = trace_lineage_recursive(target_id, nodes, 0, 8, [], {})
        
        origin_profile.pop(origin_id, None)
        target_profile.pop(target_id, None)
        
        overlaps = set(origin_profile.keys()).intersection(set(target_profile.keys()))
        match_count = len(overlaps)
        
        calculated_kinship = 0.0
        for anc_id in overlaps:
            # Handle shortest generational route for calculating coefficient matrices
            g_orig = min(origin_profile[anc_id])
            g_targ = min(target_profile[anc_id])
            
            # Wright's Kinship Coefficient element tracking: 0.5 ^ (steps)
            calculated_kinship += (0.5) ** (g_orig + g_targ)
            
            # Check for pedigree collapse inside the isolated matching nodes
            collapse_flag = len(origin_profile[anc_id]) > 1 or len(target_profile[anc_id]) > 1
            
            shared_neighborhood.append(IntersectedNodeDetail(
                node_id=anc_id,
                display_name=nodes[anc_id]["name"],
                mode_specific_metrics={
                    "origin_generations_removed": g_orig,
                    "target_generations_removed": g_targ,
                    "pedigree_collapse_detected": collapse_flag
                }
            ))
            
            # Discrepancy checking algorithms
            f_node = nodes.get(nodes[origin_id]["father"], {})
            u_node = nodes.get(nodes[target_id]["father"], {})
            if f_node and u_node and f_node.get("place") != u_node.get("place"):
                # Flag down-funnel geographical record variances between related paths
                discrepancy_logs.append(DiscrepancyLog(
                    parameter="father_birth_place",
                    origin_tree_val=str(f_node.get("place")),
                    target_tree_val=str(u_node.get("place")),
                    severity="MEDIUM"
                ))

        # Deep genetic markers fallback evaluation
        if match_count == 0 and nodes[origin_id]["y_hap"] == nodes[target_id]["y_hap"]:
            summary = f"Macro-lineage connection verified via shared Y-DNA Haplogroup: {nodes[origin_id]['y_hap']}"
            primary_index_val = 0.001
        else:
            primary_index_val = calculated_kinship
            summary = f"Kinship configuration resolved. Total ancestral intersection count: {match_count}"

    # ==========================================================================
    # MODE B: SOCIAL PIPELINE
    # ==========================================================================
    elif processing_mode.upper() == "SOCIAL":
        s_graph = env["social_edges"]
        orig_friends = set(s_graph.get(origin_id, {}).keys())
        targ_friends = set(s_graph.get(target_id, {}).keys())
        
        overlaps = orig_friends.intersection(targ_friends)
        match_count = len(overlaps)
        
        for mid in overlaps:
            w_orig = s_graph[origin_id][mid]
            w_targ = s_graph[target_id][mid]
            comp_affinity = (w_orig * w_targ) ** 0.5 # Geometric mean scaling
            
            shared_neighborhood.append(IntersectedNodeDetail(
                node_id=mid,
                display_name=nodes[mid]["name"],
                mode_specific_metrics={
                    "origin_affinity": w_orig,
                    "target_affinity": w_targ,
                    "composite_closeness": round(comp_affinity, 4)
                }
            ))
            
        union_count = len(orig_friends.union(targ_friends))
        primary_index_val = round(match_count / max(1, union_count), 4) # Jaccard Overlap Matrix
        summary = f"Social graph network mapping complete. Overlap Index verified."

    # ==========================================================================
    # MODE C: INSTITUTIONAL / TELEMETRY OVERLAPS
    # ==========================================================================
    else:
        # Match institutional tenures & geographic clusters
        t_graph = env["tenure_edges"]
        brad_tenures = t_graph.get(origin_id, [])
        targ_tenures = t_graph.get(target_id, [])
        
        for bt in brad_tenures:
            for tt in targ_tenures:
                if bt["org"] == tt["org"]: # Institutional Intersection
                    # Calculate overlapping operational window
                    overlap_start = max(bt["start"], tt["start"])
                    overlap_end = min(bt["end"], tt["end"])
                    
                    if overlap_start <= overlap_end:
                        match_count += 1
                        shared_neighborhood.append(IntersectedNodeDetail(
                            node_id=bt["org"],
                            display_name=nodes[bt["org"]]["name"],
                            mode_specific_metrics={
                                "sync_window_start": overlap_start,
                                "sync_window_end": overlap_end,
                                "duration_years": (overlap_end - overlap_start)
                            }
                        ))
        
        # Spatial Telemetry Co-burst Extraction
        telemetry_logs = env["telemetry"]
        orig_logs = [l for l in telemetry_logs if l["node_id"] == origin_id]
        targ_logs = [l for l in telemetry_logs if l["node_id"] == target_id]
        
        for ol in orig_logs:
            for tl in targ_logs:
                if ol["class"] == "SPATIAL" and ol["loc"] == tl["loc"]:
                    # Isolate parallel tracking intervals
                    s_max = max(ol["start"], tl["start"])
                    e_min = min(ol["end"], tl["end"])
                    if s_max <= e_min:
                        spatial_overlaps.append({
                            "location_cluster": ol["loc"],
                            "synchronized_window": f"{s_max}-{e_min}",
                            "type_flag": "CO-BURST_SITUATIONAL_PROXIMITY"
                        })
                        
        primary_index_val = float(match_count)
        summary = "Institutional tenure cross-sections compiled successfully."

    return UnifiedIntersectionResponse(
        status="SUCCESS",
        origin_id=origin_id,
        target_id=target_id,
        metrics=OverlapMetricSummary(
            mode=processing_mode.upper(),
            match_count=match_count,
            primary_index=primary_index_val,
            summary_text=summary
        ),
        shared_neighborhood=shared_neighborhood,
        data_discrepancies=discrepancy_logs,
        spatio_temporal_overlaps=spatial_overlaps
      )
  
