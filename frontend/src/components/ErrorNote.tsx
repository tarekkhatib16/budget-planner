interface Props {
  message: string;
  onRetry?: () => void;
}

export function ErrorNote({ message, onRetry }: Props) {
  return (
    <div className="error-note" role="alert">
      <span>{message}</span>
      {onRetry && (
        <button type="button" onClick={onRetry}>
          Retry
        </button>
      )}
    </div>
  );
}
