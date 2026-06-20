import { useEffect, useMemo, useState } from "react";

import { getApiErrorMessage } from "../api/client";
import { listFieldMappings, saveFieldMappings } from "../api/fieldMappings";
import { listTemplates } from "../api/templates";
import { FieldControlPanel } from "../components/FieldControlPanel";
import { TemplateCanvas } from "../components/TemplateCanvas";
import type { FieldKey, FieldMapping } from "../types/fieldMapping";
import type { CertificateTemplate } from "../types/template";

const fieldLabels: Record<FieldKey, string> = {
  attendee_name: "Attendee name",
  workshop_title: "Workshop title",
  certificate_date: "Certificate date",
};

interface TemplateDesignerPageProps {
  selectedTemplate: CertificateTemplate | null;
  onTemplateSelected: (template: CertificateTemplate) => void;
}

export function TemplateDesignerPage({ selectedTemplate, onTemplateSelected }: TemplateDesignerPageProps) {
  const [templates, setTemplates] = useState<CertificateTemplate[]>([]);
  const [mappings, setMappings] = useState<FieldMapping[]>([]);
  const [selectedField, setSelectedField] = useState<FieldKey>("attendee_name");
  const [notice, setNotice] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadTemplates() {
      try {
        const templateList = await listTemplates();
        setTemplates(templateList);
        if (!selectedTemplate && templateList[0]) {
          onTemplateSelected(templateList[0]);
        }
      } catch (loadError) {
        setError(getApiErrorMessage(loadError));
      }
    }

    void loadTemplates();
  }, [onTemplateSelected, selectedTemplate]);

  useEffect(() => {
    async function loadMappings() {
      if (!selectedTemplate) {
        return;
      }

      try {
        const savedMappings = await listFieldMappings(selectedTemplate.id);
        setMappings(savedMappings.length > 0 ? savedMappings : createDefaultMappings(selectedTemplate));
      } catch (loadError) {
        setError(getApiErrorMessage(loadError));
      }
    }

    void loadMappings();
  }, [selectedTemplate]);

  const selectedMapping = useMemo(
    () => mappings.find((mapping) => mapping.field_key === selectedField) ?? mappings[0],
    [mappings, selectedField],
  );

  function handleChangeMapping(field: FieldKey, updates: Partial<FieldMapping>) {
    setMappings((current) =>
      current.map((mapping) => (mapping.field_key === field ? { ...mapping, ...updates } : mapping)),
    );
  }

  async function handleSaveMappings() {
    if (!selectedTemplate) {
      return;
    }

    setNotice(null);
    setError(null);
    try {
      const savedMappings = await saveFieldMappings(selectedTemplate.id, mappings);
      setMappings(savedMappings);
      setNotice("Field mappings saved successfully.");
    } catch (saveError) {
      setError(getApiErrorMessage(saveError));
    }
  }

  if (!selectedTemplate) {
    return <section className="panel">Upload a certificate template before opening the designer.</section>;
  }

  return (
    <div className="dashboard">
      {(notice || error) && <div className={error ? "alert error" : "alert success"}>{error ?? notice}</div>}
      <section className="panel designer-toolbar">
        <label>
          Template
          <select
            value={selectedTemplate.id}
            onChange={(event) => {
              const nextTemplate = templates.find((template) => template.id === Number(event.target.value));
              if (nextTemplate) {
                onTemplateSelected(nextTemplate);
              }
            }}
          >
            {templates.map((template) => (
              <option key={template.id} value={template.id}>
                {template.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          Field
          <select value={selectedField} onChange={(event) => setSelectedField(event.target.value as FieldKey)}>
            {Object.entries(fieldLabels).map(([field, label]) => (
              <option key={field} value={field}>
                {label}
              </option>
            ))}
          </select>
        </label>
        <button type="button" onClick={handleSaveMappings}>
          Save Field Mapping
        </button>
      </section>
      <div className="designer-grid">
        <TemplateCanvas
          mappings={mappings}
          onChangeMapping={handleChangeMapping}
          onSelectField={setSelectedField}
          selectedField={selectedField}
          template={selectedTemplate}
        />
        {selectedMapping && <FieldControlPanel mapping={selectedMapping} onChangeMapping={handleChangeMapping} />}
      </div>
    </div>
  );
}

function createDefaultMappings(template: CertificateTemplate): FieldMapping[] {
  const width = template.page_width ?? 1000;
  const height = template.page_height ?? 700;
  return [
    createMapping("attendee_name", width * 0.2, height * 0.4, width * 0.6, height * 0.1, 42),
    createMapping("workshop_title", width * 0.25, height * 0.55, width * 0.5, height * 0.08, 28),
    createMapping("certificate_date", width * 0.35, height * 0.68, width * 0.3, height * 0.06, 22),
  ];
}

function createMapping(field: FieldKey, x: number, y: number, width: number, height: number, fontSize: number): FieldMapping {
  return {
    field_key: field,
    x,
    y,
    width,
    height,
    font_family: "helv",
    font_size: fontSize,
    font_color: "#111827",
    font_weight: "normal",
    alignment: "center",
    visible: true,
  };
}
