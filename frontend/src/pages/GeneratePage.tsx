import { useEffect, useState } from "react";

import { listAttendeeImports } from "../api/attendees";
import { getApiErrorMessage } from "../api/client";
import { createGenerationJob, getJobZipUrl, listGenerationJobs } from "../api/generation";
import { listTemplates } from "../api/templates";
import type { AttendeeImport } from "../types/attendee";
import type { GenerationJob } from "../types/generation";
import type { CertificateTemplate } from "../types/template";

interface GeneratePageProps {
  selectedTemplate: CertificateTemplate | null;
  selectedImport: AttendeeImport | null;
}

export function GeneratePage({ selectedTemplate, selectedImport }: GeneratePageProps) {
  const [templates, setTemplates] = useState<CertificateTemplate[]>([]);
  const [imports, setImports] = useState<AttendeeImport[]>([]);
  const [jobs, setJobs] = useState<GenerationJob[]>([]);
  const [templateId, setTemplateId] = useState<number | "">(selectedTemplate?.id ?? "");
  const [importId, setImportId] = useState<number | "">(selectedImport?.id ?? "");
  const [workshopTitle, setWorkshopTitle] = useState("");
  const [certificateDate, setCertificateDate] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        const [templateList, importList, jobList] = await Promise.all([
          listTemplates(),
          listAttendeeImports(),
          listGenerationJobs(),
        ]);
        setTemplates(templateList);
        setImports(importList);
        setJobs(jobList);
        setTemplateId((current) => current || selectedTemplate?.id || templateList[0]?.id || "");
        setImportId((current) => current || selectedImport?.id || importList[0]?.id || "");
      } catch (loadError) {
        setError(getApiErrorMessage(loadError));
      }
    }

    void loadData();
  }, [selectedImport, selectedTemplate]);

  async function handleGenerate() {
    if (!templateId || !importId) {
      setError("Choose both a template and attendee import before generating.");
      return;
    }

    setIsGenerating(true);
    setError(null);
    setNotice(null);
    try {
      const job = await createGenerationJob(Number(templateId), Number(importId), workshopTitle, certificateDate);
      setJobs((current) => [job, ...current]);
      setNotice(`Generated ${job.success_count} certificates.`);
    } catch (generateError) {
      setError(getApiErrorMessage(generateError));
    } finally {
      setIsGenerating(false);
    }
  }

  return (
    <div className="dashboard">
      {(notice || error) && <div className={error ? "alert error" : "alert success"}>{error ?? notice}</div>}
      <section className="panel generation-form">
        <h2>Generate Certificates</h2>
        <label>
          Template
          <select value={templateId} onChange={(event) => setTemplateId(Number(event.target.value))}>
            <option value="">Choose template</option>
            {templates.map((template) => (
              <option key={template.id} value={template.id}>
                {template.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          Attendee Import
          <select value={importId} onChange={(event) => setImportId(Number(event.target.value))}>
            <option value="">Choose attendee import</option>
            {imports.map((attendeeImport) => (
              <option key={attendeeImport.id} value={attendeeImport.id}>
                {attendeeImport.original_filename} ({attendeeImport.valid_rows} valid)
              </option>
            ))}
          </select>
        </label>
        <label>
          Workshop Title
          <input
            placeholder="Example: JavaScript Fundamentals Workshop"
            type="text"
            value={workshopTitle}
            onChange={(event) => setWorkshopTitle(event.target.value)}
          />
        </label>
        <label>
          Certificate Date
          <input type="date" value={certificateDate} onChange={(event) => setCertificateDate(event.target.value)} />
        </label>
        <button disabled={isGenerating} type="button" onClick={handleGenerate}>
          {isGenerating ? "Generating..." : "Generate PDFs"}
        </button>
      </section>

      <section className="panel">
        <h2>Generation Jobs</h2>
        {jobs.length === 0 ? (
          <p className="muted">No generation jobs yet.</p>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Job</th>
                  <th>Status</th>
                  <th>Success</th>
                  <th>Failed</th>
                  <th>Download</th>
                </tr>
              </thead>
              <tbody>
                {jobs.map((job) => (
                  <tr key={job.id}>
                    <td>#{job.id}</td>
                    <td>{job.status}</td>
                    <td>{job.success_count}</td>
                    <td>{job.failed_count}</td>
                    <td>
                      {job.success_count > 0 && (
                        <a className="download-link" href={getJobZipUrl(job.id)}>
                          ZIP
                        </a>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
