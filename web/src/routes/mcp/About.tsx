export default function About() {
  return (
    <div className="space-y-6">
      <h1 className="text-4xl font-bold text-white mb-4">About SecAI Radar</h1>
      <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6 space-y-4">
        <p className="text-slate-300">
          SecAI Radar is a transparent trust authority for MCP (Model Context Protocol) security posture.
        </p>
        <div>
          <h2 className="text-xl font-semibold text-white mb-2">Links</h2>
          <ul className="space-y-2 text-slate-400">
            <li><a href="https://zimax.net" target="_blank" rel="noopener noreferrer" className="hover:text-white">Zimax</a></li>
            <li><a href="https://ctxeco.com" target="_blank" rel="noopener noreferrer" className="hover:text-white">CtxEco</a></li>
            <li><a href="https://github.com/derekbmoore/openContextGraph" target="_blank" rel="noopener noreferrer" className="hover:text-white">OSS Engine</a></li>
          </ul>
        </div>
      </div>
    </div>
  )
}
