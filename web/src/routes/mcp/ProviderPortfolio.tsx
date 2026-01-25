import { useParams } from 'react-router-dom'

export default function ProviderPortfolio() {
  const { providerSlug } = useParams()
  return (
    <div className="text-center py-12">
      <h1 className="text-4xl font-bold text-white mb-4">Provider Portfolio</h1>
      <p className="text-slate-400">Provider: {providerSlug}</p>
      <p className="text-sm text-slate-500 mt-4">Coming soon - Will show portfolio metrics, servers, and drift</p>
    </div>
  )
}
