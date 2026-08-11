export function LoadingState({ label = 'Loading…' }) {
  return (
    <div className="status-state" role="status">
      <span>{label}</span>
    </div>
  );
}

export function ErrorState({ error }) {
  return (
    <div className="status-state status-state--error" role="alert">
      <span>Couldn't load this data{error?.message ? `: ${error.message}` : '.'}</span>
    </div>
  );
}

export function EmptyState({ children }) {
  return (
    <div className="status-state status-state--empty">
      <span>{children}</span>
    </div>
  );
}
