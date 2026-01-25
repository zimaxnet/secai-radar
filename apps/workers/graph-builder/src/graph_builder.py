"""
Graph Builder Worker - Builds per-server graph snapshots
"""

import os
import psycopg2
import json
from datetime import datetime
from typing import Dict, Any, List

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://secairadar:password@localhost:5432/secairadar"
)


def build_server_graph(db, server_id: str) -> Dict[str, Any]:
    """
    Build graph for a server: Server → Tools → Scopes → DataDomains → Evidence → Flags
    """
    with db.cursor() as cur:
        # Get server info
        cur.execute("""
            SELECT server_id, server_name, auth_model, tool_agency
            FROM mcp_servers
            WHERE server_id = %s
        """, (server_id,))
        server_row = cur.fetchone()
        
        if not server_row:
            return None
        
        # Get evidence items
        cur.execute("""
            SELECT evidence_id, type, url, confidence
            FROM evidence_items
            WHERE server_id = %s
        """, (server_id,))
        evidence_items = [
            {"evidence_id": row[0], "type": row[1], "url": row[2], "confidence": row[3]}
            for row in cur.fetchall()
        ]
        
        # Get claims
        evidence_ids = [e["evidence_id"] for e in evidence_items]
        claims = []
        if evidence_ids:
            cur.execute("""
                SELECT claim_type, value_json
                FROM evidence_claims
                WHERE evidence_id = ANY(%s)
            """, (evidence_ids,))
            claims = [
                {"claim_type": row[0], "value": row[1]}
                for row in cur.fetchall()
            ]
        
        # Get latest score
        cur.execute("""
            SELECT tier, trust_score, fail_fast_flags, risk_flags
            FROM score_snapshots
            WHERE server_id = %s
            ORDER BY assessed_at DESC
            LIMIT 1
        """, (server_id,))
        score_row = cur.fetchone()
        
        # Build graph structure
        graph = {
            "nodes": [],
            "edges": []
        }
        
        # Server node
        graph["nodes"].append({
            "id": server_id,
            "type": "Server",
            "label": server_row[1],
            "properties": {
                "authModel": server_row[2],
                "toolAgency": server_row[3]
            }
        })
        
        # Evidence nodes
        for evidence in evidence_items:
            graph["nodes"].append({
                "id": evidence["evidence_id"],
                "type": "Evidence",
                "label": evidence["type"],
                "properties": {
                    "confidence": evidence["confidence"],
                    "url": evidence["url"]
                }
            })
            graph["edges"].append({
                "from": server_id,
                "to": evidence["evidence_id"],
                "type": "hasEvidence"
            })
        
        # Claim nodes
        for claim in claims:
            claim_id = f"{server_id}-{claim['claim_type']}"
            graph["nodes"].append({
                "id": claim_id,
                "type": "Claim",
                "label": claim["claim_type"],
                "properties": claim["value"]
            })
            graph["edges"].append({
                "from": evidence_items[0]["evidence_id"] if evidence_items else server_id,
                "to": claim_id,
                "type": "hasClaim"
            })
        
        # Score node
        if score_row:
            score_id = f"{server_id}-score"
            graph["nodes"].append({
                "id": score_id,
                "type": "Score",
                "label": f"Trust Score: {score_row[1]}",
                "properties": {
                    "tier": score_row[0],
                    "trustScore": float(score_row[1]),
                    "failFastFlags": json.loads(score_row[2] or "[]"),
                    "riskFlags": json.loads(score_row[3] or "[]")
                }
            })
            graph["edges"].append({
                "from": server_id,
                "to": score_id,
                "type": "hasScore"
            })
        
        return graph


def store_graph_snapshot(db, server_id: str, graph: Dict[str, Any]):
    """Store graph snapshot"""
    graph_id = hashlib.sha256(
        f"{server_id}|{datetime.utcnow().isoformat()}".encode()
    ).hexdigest()[:16]
    
    with db.cursor() as cur:
        # Check if table exists (would be created by migration)
        cur.execute("""
            INSERT INTO server_graph_snapshots (
                graph_id, server_id, graph_json, assessed_at
            ) VALUES (%s, %s, %s, %s)
            ON CONFLICT (server_id, assessed_at) DO UPDATE SET
                graph_json = EXCLUDED.graph_json
        """, (
            graph_id,
            server_id,
            json.dumps(graph),
            datetime.utcnow()
        ))
        db.commit()


def run_graph_builder():
    """Main graph builder function"""
    conn = psycopg2.connect(DATABASE_URL)
    
    try:
        # Get all active servers
        with conn.cursor() as cur:
            cur.execute("""
                SELECT server_id FROM mcp_servers
                WHERE status = 'Active'
            """)
            server_ids = [row[0] for row in cur.fetchall()]
        
        graphs_built = 0
        for server_id in server_ids:
            graph = build_server_graph(conn, server_id)
            if graph:
                store_graph_snapshot(conn, server_id, graph)
                graphs_built += 1
        
        return {
            "success": True,
            "serversProcessed": len(server_ids),
            "graphsBuilt": graphs_built,
            "completedAt": datetime.utcnow().isoformat()
        }
    except Exception as e:
        print(f"Graph builder error: {e}")
        return {
            "success": False,
            "error": str(e),
            "completedAt": datetime.utcnow().isoformat()
        }
    finally:
        conn.close()


if __name__ == "__main__":
    import hashlib
    result = run_graph_builder()
    print(json.dumps(result, indent=2, default=str))
