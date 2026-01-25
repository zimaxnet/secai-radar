/**
 * GK Graph Schema Types (openContextGraph-aligned)
 * Based on Step 4: Data Model + API Spec specification
 */

// ============================================================================
// 2.1 Node Types
// ============================================================================

export type GraphNodeType =
  | 'Provider'
  | 'MCPServer'
  | 'Endpoint'
  | 'Tool'
  | 'PermissionScope'
  | 'DataDomain'
  | 'Hosting'
  | 'EvidenceArtifact'
  | 'ScoreSnapshot'
  | 'DriftEvent'
  | 'Policy' // private
  | 'Approval' // private
  | 'RunEvent' // private
  | 'DailyBrief' // public

export interface GraphNode {
  id: string
  type: GraphNodeType
  label: string
  props: Record<string, any>
  createdAt?: string
  updatedAt?: string
}

// ============================================================================
// 2.2 Edge Types
// ============================================================================

export type GraphEdgeType =
  | 'OWNS' // Provider OWNS MCPServer
  | 'HAS_ENDPOINT' // MCPServer HAS_ENDPOINT Endpoint
  | 'EXPOSES' // MCPServer EXPOSES Tool
  | 'REQUIRES' // Tool REQUIRES PermissionScope
  | 'TOUCHES' // Tool TOUCHES DataDomain
  | 'HOSTED_BY' // MCPServer HOSTED_BY Hosting
  | 'SUPPORTS' // EvidenceArtifact SUPPORTS (MCPServer | Tool | Provider | Policy | ScoreSnapshot)
  | 'HAS_SCORE' // MCPServer HAS_SCORE ScoreSnapshot
  | 'HAS_DRIFT' // MCPServer HAS_DRIFT DriftEvent
  | 'GOVERNS' // Policy GOVERNS (MCPServer | Tool) (private)
  | 'APPROVES' // Approval APPROVES Policy (private)
  | 'INVOKED' // RunEvent INVOKED Tool (private)
  | 'MENTIONS' // DailyBrief MENTIONS (MCPServer | Provider | DriftEvent)

export interface GraphEdge {
  id?: string
  from: string
  to: string
  type: GraphEdgeType
  props?: Record<string, any>
  createdAt?: string
}

// ============================================================================
// 2.3 Node Property Examples
// ============================================================================

export interface MCPServerNodeProps {
  serverId: string
  name: string
  slug: string
  deploymentType: string
  authModel: string
  toolAgency: string
  status: string
  lastAssessedAt: string
  trustScore: number
  evidenceConfidence: number
}

export interface ToolNodeProps {
  toolName: string
  capability: 'Read' | 'Write' | 'Destructive'
  description?: string
}

export interface EvidenceArtifactNodeProps {
  evidenceId: string
  type: string
  url?: string
  confidence: number
  capturedAt: string
  hash: string
}

// ============================================================================
// Graph Query Types
// ============================================================================

export interface GraphQuery {
  nodeIds?: string[]
  nodeTypes?: GraphNodeType[]
  edgeTypes?: GraphEdgeType[]
  fromNode?: string
  toNode?: string
  depth?: number
  limit?: number
}

export interface GraphSubgraph {
  nodes: GraphNode[]
  edges: GraphEdge[]
  metadata?: {
    totalNodes: number
    totalEdges: number
    query: GraphQuery
  }
}
