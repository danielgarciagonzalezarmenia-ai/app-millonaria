import { useEffect, useRef } from 'react'

/**
 * Revela en pantalla los elementos con clase `.reveal` del contenedor cuando
 * entran en el viewport (IntersectionObserver).
 *
 * Soporta contenido que se monta de forma asíncrona (ej. pronósticos que
 * llegan tras un fetch): usa un MutationObserver para registrar los nuevos
 * elementos que aparezcan después del primer scan.
 */
export function useReveal<T extends HTMLElement>() {
  const ref = useRef<T | null>(null)

  useEffect(() => {
    const root = ref.current
    if (!root) return

    const pending = new Set<HTMLElement>()

    const observeFresh = () => {
      const fresh = Array.from(root.querySelectorAll<HTMLElement>('.reveal')).filter(
        (el) => !el.classList.contains('visible'),
      )
      fresh.forEach((el) => pending.add(el))
      io?.disconnect()
      io = new IntersectionObserver(onIntersect, {
        threshold: 0.12,
        rootMargin: '0px 0px -40px 0px',
      })
      pending.forEach((el) => io?.observe(el))
    }

    const onIntersect: IntersectionObserverCallback = (entries) => {
      for (const entry of entries) {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible')
          pending.delete(entry.target as HTMLElement)
          io?.unobserve(entry.target)
        }
      }
    }

    let io: IntersectionObserver | null = null

    // Primer scan + re-scan cuando el DOM del contenedor cambie.
    const mo = new MutationObserver(observeFresh)
    observeFresh()
    mo.observe(root, { childList: true, subtree: true })

    return () => {
      mo.disconnect()
      io?.disconnect()
    }
  }, [])

  return ref
}