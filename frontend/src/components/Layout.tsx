import type { ReactNode } from "react";

interface LayoutProps {
  children: ReactNode;
  currentPage: string;
  onNavigate: (page: string) => void;
}

const navItems = [
  { id: "dashboard", label: "Dashboard" },
  { id: "designer", label: "Designer" },
  { id: "generate", label: "Generate" },
  { id: "certificates", label: "Certificates" },
];

export function Layout({ children, currentPage, onNavigate }: LayoutProps) {
  return (
    <div className="app-shell">
      <nav className="top-nav">
        {navItems.map((item) => (
          <button
            className={currentPage === item.id ? "nav-link active" : "nav-link"}
            key={item.id}
            onClick={() => onNavigate(item.id)}
            type="button"
          >
            {item.label}
          </button>
        ))}
      </nav>
      <header className="hero">
        <div>
          <p className="eyebrow">Certificate Generator</p>
          <h1>Design and generate certificates</h1>
          <p className="hero-copy">
            Upload a template and attendee list, position certificate fields, then generate downloadable PDFs.
          </p>
        </div>
      </header>
      <main>{children}</main>
    </div>
  );
}
