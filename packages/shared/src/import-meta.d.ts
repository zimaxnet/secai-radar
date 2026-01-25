/** Ambient declaration for import.meta.env (Vite / environment variables) when not using Vite client types */
interface ImportMeta {
  env: Record<string, string | boolean | undefined>
}
