export default function LoadingSpinner({ text = 'Loading...' }) {
  return (
    <div className="loading-container">
      <div className="spinner"></div>
      <div className="loading-text">{text}</div>
    </div>
  );
}
