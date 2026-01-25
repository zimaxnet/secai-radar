import { Link } from 'react-router-dom'

interface Breadcrumb {
  label: string
  path?: string
}

interface Props {
  items: Breadcrumb[]
}

export default function Breadcrumbs({ items }: Props) {
  return (
    <nav className="flex items-center space-x-2 text-sm text-gray-600 mb-4">
      {items.map((item, idx) => (
        <span key={idx} className="flex items-center">
          {item.path ? (
            <Link to={item.path} className="hover:text-blue-600 hover:underline">
              {item.label}
            </Link>
          ) : (
            <span className="text-gray-900 font-medium">{item.label}</span>
          )}
          {idx < items.length - 1 && <span className="mx-2 text-gray-400">/</span>}
        </span>
      ))}
    </nav>
  )
}

