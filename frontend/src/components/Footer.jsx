export default function Footer() {
  return (
    <footer className="footer">
      <div className="container">
        <p>
          © {new Date().getFullYear()} <span className="footer-brand">Krishiv</span> — Intelligent Greenhouse Monitoring Platform
        </p>
      </div>
    </footer>
  );
}
