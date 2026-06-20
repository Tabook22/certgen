import { useState } from "react";

import { Layout } from "./components/Layout";
import { CertificatesPage } from "./pages/CertificatesPage";
import { DashboardPage } from "./pages/DashboardPage";
import { GeneratePage } from "./pages/GeneratePage";
import { TemplateDesignerPage } from "./pages/TemplateDesignerPage";
import type { AttendeeImport } from "./types/attendee";
import type { CertificateTemplate } from "./types/template";

export function App() {
  const [currentPage, setCurrentPage] = useState("dashboard");
  const [selectedTemplate, setSelectedTemplate] = useState<CertificateTemplate | null>(null);
  const [selectedImport, setSelectedImport] = useState<AttendeeImport | null>(null);

  const page = {
    dashboard: (
      <DashboardPage
        selectedTemplate={selectedTemplate}
        selectedImport={selectedImport}
        onTemplateSelected={setSelectedTemplate}
        onImportSelected={setSelectedImport}
      />
    ),
    designer: <TemplateDesignerPage selectedTemplate={selectedTemplate} onTemplateSelected={setSelectedTemplate} />,
    generate: <GeneratePage selectedTemplate={selectedTemplate} selectedImport={selectedImport} />,
    certificates: <CertificatesPage />,
  }[currentPage];

  return (
    <Layout currentPage={currentPage} onNavigate={setCurrentPage}>
      {page}
    </Layout>
  );
}
