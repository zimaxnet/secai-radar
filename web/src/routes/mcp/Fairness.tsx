/**
 * Fairness and right-to-respond (T-134): process, provider contact, dispute steps.
 */
export default function Fairness() {
  return (
    <div className="max-w-3xl mx-auto space-y-8">
      <h1 className="text-3xl font-bold text-white">Fairness &amp; right to respond</h1>
      <p className="text-slate-400">
        SecAI Radar aims to be transparent and fair to MCP server providers. This page describes how we handle
        assessments, how you can submit evidence or corrections, and how disputes are handled.
      </p>

      <section>
        <h2 className="text-xl font-semibold text-white mb-2">Assessment process</h2>
        <p className="text-slate-300 text-sm">
          Scores are produced by an automated pipeline using public evidence (docs, repos, reports) and our
          methodology. We do not guarantee that every provider has been manually reviewed. You can improve your
          standing by submitting evidence or clarifications (see below).
        </p>
      </section>

      <section>
        <h2 className="text-xl font-semibold text-white mb-2">Provider submission and contact</h2>
        <p className="text-slate-300 text-sm mb-2">
          If you are a provider and want to submit evidence, correct information, or request a review:
        </p>
        <ul className="list-disc list-inside text-slate-300 text-sm space-y-1">
          <li>Use the <strong>Submit Evidence</strong> flow linked from the main nav.</li>
          <li>Or contact us at the address listed on the <strong>About</strong> page.</li>
          <li>Include your server ID/slug, the type of submission (evidence, correction, dispute), and clear details.</li>
        </ul>
      </section>

      <section>
        <h2 className="text-xl font-semibold text-white mb-2">Dispute handling</h2>
        <ol className="list-decimal list-inside text-slate-300 text-sm space-y-2">
          <li>Submit a clear description of the dispute and the outcome you believe is correct.</li>
          <li>We will acknowledge receipt and triage within a defined window (e.g. 5 business days).</li>
          <li>Where appropriate, we will re-run evidence collection or review the methodology application.</li>
          <li>We will respond with the result or next steps; repeated or abusive disputes may be handled under a separate policy.</li>
        </ol>
      </section>

      <p className="text-slate-500 text-xs pt-4">
        This page is part of our commitment to transparency. Methodology details are in the Methodology section.
      </p>
    </div>
  )
}
