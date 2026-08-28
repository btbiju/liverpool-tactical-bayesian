import { useEffect, useState } from 'react';

// Runs `loader()` once on mount and exposes { data, error, loading }.
export function useAsync(loader) {
  const [state, setState] = useState({ data: null, error: null, loading: true });

  useEffect(() => {
    let cancelled = false;
    setState({ data: null, error: null, loading: true });
    loader()
      .then((data) => {
        if (!cancelled) setState({ data, error: null, loading: false });
      })
      .catch((error) => {
        if (!cancelled) setState({ data: null, error, loading: false });
      });
    return () => {
      cancelled = true;
    };
  }, [loader]);

  return state;
}
