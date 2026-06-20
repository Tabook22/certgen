import { useEffect, useState } from "react";

import { getApiErrorMessage } from "../api/client";
import { listAttendeeImports, uploadAttendees } from "../api/attendees";
import { listTemplates, uploadTemplate } from "../api/templates";
import { AttendeeTable } from "../components/AttendeeTable";
import { JobStatusCard } from "../components/JobStatusCard";
import { UploadBox } from "../components/UploadBox";
import type { Attendee, AttendeeImport } from "../types/attendee";
import type { CertificateTemplate } from "../types/template";

interface DashboardPageProps {
  selectedTemplate: CertificateTemplate | null;
  selectedImport: AttendeeImport | null;
  onTemplateSelected: (template: CertificateTemplate) => void;
  onImportSelected: (attendeeImport: AttendeeImport) => void;
}

export function DashboardPage({
  selectedTemplate,
  selectedImport,
  onTemplateSelected,
  onImportSelected,
}: DashboardPageProps) {
  const [attendees, setAttendees] = useState<Attendee[]>([]);
  const [isTemplateUploading, setIsTemplateUploading] = useState(false);
  const [isAttendeeUploading, setIsAttendeeUploading] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadLatestRecords() {
      try {
        const [templates, imports] = await Promise.all([listTemplates(), listAttendeeImports()]);
        if (!selectedTemplate && templates[0]) {
          onTemplateSelected(templates[0]);
        }
        if (!selectedImport && imports[0]) {
          onImportSelected(imports[0]);
        }
      } catch (loadError) {
        setError(getApiErrorMessage(loadError));
      }
    }

    void loadLatestRecords();
  }, [onImportSelected, onTemplateSelected, selectedImport, selectedTemplate]);

  async function handleTemplateUpload(file: File) {
    setIsTemplateUploading(true);
    setError(null);
    setNotice(null);
    try {
      const response = await uploadTemplate(file);
      onTemplateSelected(response.template);
      setNotice(response.message);
    } catch (uploadError) {
      setError(getApiErrorMessage(uploadError));
    } finally {
      setIsTemplateUploading(false);
    }
  }

  async function handleAttendeeUpload(file: File) {
    setIsAttendeeUploading(true);
    setError(null);
    setNotice(null);
    try {
      const response = await uploadAttendees(file);
      onImportSelected(response.attendee_import);
      setAttendees(response.attendees);
      setNotice(response.message);
    } catch (uploadError) {
      setError(getApiErrorMessage(uploadError));
    } finally {
      setIsAttendeeUploading(false);
    }
  }

  return (
    <div className="dashboard">
      {(notice || error) && <div className={error ? "alert error" : "alert success"}>{error ?? notice}</div>}

      <section className="stats-grid">
        <JobStatusCard
          label="Template"
          value={selectedTemplate ? selectedTemplate.name : "None"}
          helper="PDF, PNG, JPG, or JPEG"
        />
        <JobStatusCard
          label="Attendee Import"
          value={selectedImport ? selectedImport.total_rows : 0}
          helper="Rows parsed and stored"
        />
        <JobStatusCard
          label="Valid Attendees"
          value={selectedImport ? selectedImport.valid_rows : 0}
          helper="Ready for generation"
        />
      </section>

      <section className="upload-grid">
        <UploadBox
          title="Upload Certificate Template"
          description="Store a PDF or image certificate design for future field mapping."
          accept=".pdf,.png,.jpg,.jpeg"
          buttonLabel="Upload Template"
          isUploading={isTemplateUploading}
          onUpload={handleTemplateUpload}
        />
        <UploadBox
          title="Upload Attendees"
          description="Import a CSV or Excel file with full_name plus optional email, workshop_title, and certificate_date."
          accept=".csv,.xls,.xlsx"
          buttonLabel="Upload Attendees"
          isUploading={isAttendeeUploading}
          onUpload={handleAttendeeUpload}
        />
      </section>

      <section className="panel">
        <div className="panel-header">
          <div>
            <h2>Attendee Validation Preview</h2>
            <p>Showing the first uploaded rows returned by the backend.</p>
          </div>
        </div>
        <AttendeeTable attendees={attendees} />
      </section>
    </div>
  );
}
