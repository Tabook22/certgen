import { useEffect, useState } from "react";

import { getApiErrorMessage } from "../api/client";
import { getCertificateDownloadUrl, listCertificates } from "../api/certificates";
import type { GeneratedCertificate } from "../types/generation";

export function CertificatesPage() {
  const [certificates, setCertificates] = useState<GeneratedCertificate[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadCertificates() {
      try {
        setCertificates(await listCertificates());
      } catch (loadError) {
        setError(getApiErrorMessage(loadError));
      }
    }

    void loadCertificates();
  }, []);

  return (
    <section className="panel">
      <h2>Certificates</h2>
      {error && <div className="alert error">{error}</div>}
      {certificates.length === 0 ? (
        <p className="muted">No generated certificates yet.</p>
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Job</th>
                <th>Status</th>
                <th>Download</th>
              </tr>
            </thead>
            <tbody>
              {certificates.map((certificate) => (
                <tr key={certificate.id}>
                  <td>#{certificate.id}</td>
                  <td>#{certificate.generation_job_id}</td>
                  <td>{certificate.status}</td>
                  <td>
                    {certificate.status === "generated" && (
                      <a className="download-link" href={getCertificateDownloadUrl(certificate.id)}>
                        PDF
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
  );
}
