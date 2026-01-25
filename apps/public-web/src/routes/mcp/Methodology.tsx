/**
 * Methodology Page (/mcp/methodology)
 * 
 * Purpose: Explain Trust Score, Evidence Confidence, and how to submit evidence
 * Based on Step 6: MVP PRD + UI Component Spec
 */

// import { DISCLAIMERS } from '../../utils/copy' // Unused for now
import Disclaimer from '../../components/mcp/Disclaimer'
import EvidenceConfidenceBadge from '../../components/mcp/EvidenceConfidenceBadge'
import TierBadge from '../../components/mcp/TierBadge'
import { Link } from 'react-router-dom'

export default function Methodology() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-4xl font-bold text-white mb-2">Methodology</h1>
        <p className="text-slate-400">How we assess MCP server security posture</p>
      </div>

      {/* What is Trust Score */}
      <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6">
        <h2 className="text-2xl font-semibold text-white mb-4">What is Trust Score?</h2>
        <p className="text-slate-300 mb-4">
          Trust Score is a <strong className="text-white">risk posture assessment</strong> (0–100) that evaluates MCP servers across six security domains.
          It is <strong className="text-white">not a certification</strong> and does not guarantee security.
        </p>
        <Disclaimer variant="long" className="mt-4" />
      </div>

      {/* Domain Definitions */}
      <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6">
        <h2 className="text-2xl font-semibold text-white mb-4">Security Domains (D1–D6)</h2>
        <div className="space-y-4">
          <div>
            <h3 className="text-lg font-medium text-white mb-2">D1: Authentication</h3>
            <p className="text-slate-300">How users and systems authenticate to the MCP server. Evaluates OAuth/OIDC, API keys, PAT, mTLS, and authentication best practices.</p>
          </div>
          <div>
            <h3 className="text-lg font-medium text-white mb-2">D2: Authorization</h3>
            <p className="text-slate-300">How permissions and scopes are managed. Evaluates least-privilege principles, scope definitions, and access controls.</p>
          </div>
          <div>
            <h3 className="text-lg font-medium text-white mb-2">D3: Data Protection</h3>
            <p className="text-slate-300">How data is protected in transit and at rest. Evaluates encryption, data residency, retention, and deletion policies.</p>
          </div>
          <div>
            <h3 className="text-lg font-medium text-white mb-2">D4: Audit & Logging</h3>
            <p className="text-slate-300">How actions are logged and audited. Evaluates audit trail availability, log retention, and monitoring capabilities.</p>
          </div>
          <div>
            <h3 className="text-lg font-medium text-white mb-2">D5: Operational Security</h3>
            <p className="text-slate-300">How the service is operated and maintained. Evaluates hosting posture, SBOM availability, vulnerability disclosure, and incident response.</p>
          </div>
          <div>
            <h3 className="text-lg font-medium text-white mb-2">D6: Compliance</h3>
            <p className="text-slate-300">Compliance with security standards and regulations. Evaluates certifications, attestations, and regulatory alignment.</p>
          </div>
        </div>
      </div>

      {/* Evidence Confidence */}
      <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6">
        <h2 className="text-2xl font-semibold text-white mb-4">Evidence Confidence (0–3)</h2>
        <p className="text-slate-300 mb-4">
          Evidence Confidence measures how well-supported the security posture claims are by verifiable evidence.
        </p>
        <div className="space-y-3">
          <div className="flex items-center gap-4 p-3 bg-slate-800/50 rounded-lg">
            <EvidenceConfidenceBadge confidence={0} />
            <div>
              <div className="text-sm font-medium text-white">Unknown — not enough evidence</div>
              <div className="text-xs text-slate-400">No public documentation or evidence found</div>
            </div>
          </div>
          <div className="flex items-center gap-4 p-3 bg-slate-800/50 rounded-lg">
            <EvidenceConfidenceBadge confidence={1} />
            <div>
              <div className="text-sm font-medium text-white">Public claims — self-attested</div>
              <div className="text-xs text-slate-400">Claims found in public documentation</div>
            </div>
          </div>
          <div className="flex items-center gap-4 p-3 bg-slate-800/50 rounded-lg">
            <EvidenceConfidenceBadge confidence={2} />
            <div>
              <div className="text-sm font-medium text-white">Verifiable — artifacts reviewed</div>
              <div className="text-xs text-slate-400">Evidence artifacts reviewed and verified</div>
            </div>
          </div>
          <div className="flex items-center gap-4 p-3 bg-slate-800/50 rounded-lg">
            <EvidenceConfidenceBadge confidence={3} />
            <div>
              <div className="text-sm font-medium text-white">Validated — independent verification</div>
              <div className="text-xs text-slate-400">Independently verified by third party or audit</div>
            </div>
          </div>
        </div>
      </div>

      {/* Tier Definitions */}
      <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6">
        <h2 className="text-2xl font-semibold text-white mb-4">Tier Definitions</h2>
        <div className="space-y-3">
          <div className="flex items-center gap-4 p-3 bg-slate-800/50 rounded-lg">
            <TierBadge tier="A" />
            <div>
              <div className="text-sm font-medium text-white">Strong posture</div>
              <div className="text-xs text-slate-400">Trust Score 80-100, high evidence confidence, minimal risk flags</div>
            </div>
          </div>
          <div className="flex items-center gap-4 p-3 bg-slate-800/50 rounded-lg">
            <TierBadge tier="B" />
            <div>
              <div className="text-sm font-medium text-white">Good posture</div>
              <div className="text-xs text-slate-400">Trust Score 60-79, moderate evidence confidence, some risk flags</div>
            </div>
          </div>
          <div className="flex items-center gap-4 p-3 bg-slate-800/50 rounded-lg">
            <TierBadge tier="C" />
            <div>
              <div className="text-sm font-medium text-white">Mixed/unknown</div>
              <div className="text-xs text-slate-400">Trust Score 40-59, low evidence confidence, multiple risk flags</div>
            </div>
          </div>
          <div className="flex items-center gap-4 p-3 bg-slate-800/50 rounded-lg">
            <TierBadge tier="D" />
            <div>
              <div className="text-sm font-medium text-white">High risk/insufficient evidence</div>
              <div className="text-xs text-slate-400">Trust Score 0-39, very low evidence confidence, fail-fast flags present</div>
            </div>
          </div>
        </div>
      </div>

      {/* How to Submit Evidence */}
      <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6">
        <h2 className="text-2xl font-semibold text-white mb-4">How to Submit Evidence Packs</h2>
        <p className="text-slate-300 mb-4">
          Providers can submit evidence packs to improve their verification and Trust Score.
        </p>
        <div className="space-y-3 mb-4">
          <div className="flex items-start gap-3">
            <span className="text-blue-400 mt-1">1.</span>
            <div>
              <div className="text-sm font-medium text-white">Gather Evidence</div>
              <div className="text-xs text-slate-400">Documentation, security reports, attestations, or other verifiable artifacts</div>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <span className="text-blue-400 mt-1">2.</span>
            <div>
              <div className="text-sm font-medium text-white">Submit via Form</div>
              <div className="text-xs text-slate-400">Use the <Link to="/mcp/submit" className="text-blue-400 hover:text-blue-300">Submit Evidence</Link> page</div>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <span className="text-blue-400 mt-1">3.</span>
            <div>
              <div className="text-sm font-medium text-white">Review Process</div>
              <div className="text-xs text-slate-400">Our team reviews and validates evidence, then updates scores accordingly</div>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <span className="text-blue-400 mt-1">4.</span>
            <div>
              <div className="text-sm font-medium text-white">Response Status</div>
              <div className="text-xs text-slate-400">Provider response status is visible on server detail pages</div>
            </div>
          </div>
        </div>
        <Link
          to="/mcp/submit"
          className="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
        >
          Submit Evidence →
        </Link>
      </div>

      {/* Rubric Changelog */}
      <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6">
        <h2 className="text-2xl font-semibold text-white mb-4">Rubric Changelog</h2>
        <p className="text-slate-300 mb-4">
          We maintain a changelog of rubric changes and methodology updates.
        </p>
        <Link
          to="/mcp/changelog"
          className="text-blue-400 hover:text-blue-300"
        >
          View Changelog →
        </Link>
      </div>

      {/* Disclaimers */}
      <div className="bg-gradient-to-r from-yellow-600/20 to-orange-600/20 border border-yellow-500/30 rounded-xl p-6">
        <h2 className="text-xl font-semibold text-white mb-3">Important Disclaimers</h2>
        <Disclaimer variant="long" className="text-slate-300" />
        <Disclaimer variant="methodology" className="mt-4 text-slate-300" />
      </div>
    </div>
  )
}

