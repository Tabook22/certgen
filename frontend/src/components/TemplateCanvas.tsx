import type { PointerEvent } from "react";

import { getTemplatePreviewUrl } from "../api/templates";
import type { FieldKey, FieldMapping } from "../types/fieldMapping";
import type { CertificateTemplate } from "../types/template";

interface TemplateCanvasProps {
  template: CertificateTemplate;
  mappings: FieldMapping[];
  selectedField: FieldKey;
  onSelectField: (field: FieldKey) => void;
  onChangeMapping: (field: FieldKey, updates: Partial<FieldMapping>) => void;
}

export function TemplateCanvas({
  template,
  mappings,
  selectedField,
  onSelectField,
  onChangeMapping,
}: TemplateCanvasProps) {
  const templateWidth = template.page_width ?? 1000;
  const templateHeight = template.page_height ?? 700;

  function handlePointerMove(event: PointerEvent<HTMLButtonElement>, mapping: FieldMapping) {
    if (event.buttons !== 1) {
      return;
    }

    const bounds = event.currentTarget.getBoundingClientRect();
    const scaleX = templateWidth / bounds.width;
    const scaleY = templateHeight / bounds.height;
    onChangeMapping(mapping.field_key, {
      x: Math.max(0, (event.clientX - bounds.left) * scaleX - mapping.width / 2),
      y: Math.max(0, (event.clientY - bounds.top) * scaleY - mapping.height / 2),
    });
  }

  return (
    <section className="panel">
      <h2>Template Designer</h2>
      <p>Drag fields on the preview, then save the mapping.</p>
      <div className="template-stage" style={{ aspectRatio: `${templateWidth} / ${templateHeight}` }}>
        <img alt={`${template.name} preview`} src={getTemplatePreviewUrl(template.id)} />
        <div className="field-layer">
          {mappings
            .filter((mapping) => mapping.visible)
            .map((mapping) => (
              <button
                className={selectedField === mapping.field_key ? "field-box active" : "field-box"}
                key={mapping.field_key}
                onClick={() => onSelectField(mapping.field_key)}
                onPointerMove={(event) => handlePointerMove(event, mapping)}
                style={{
                  left: `${(mapping.x / templateWidth) * 100}%`,
                  top: `${(mapping.y / templateHeight) * 100}%`,
                  width: `${(mapping.width / templateWidth) * 100}%`,
                  height: `${(mapping.height / templateHeight) * 100}%`,
                  fontSize: `${Math.max((mapping.font_size ?? 24) / 3, 10)}px`,
                  fontFamily: previewFontFamily(mapping.font_family),
                }}
                type="button"
              >
                {mapping.field_key.replace("_", " ")}
              </button>
            ))}
        </div>
      </div>
    </section>
  );
}

function previewFontFamily(fontFamily: string | null): string {
  const fonts: Record<string, string> = {
    arial: "Arial, sans-serif",
    tahoma: "Tahoma, Arial, sans-serif",
    segoe_ui: "'Segoe UI', Tahoma, sans-serif",
    dejavu_sans: "'DejaVu Sans', Arial, sans-serif",
    times: "'Times New Roman', serif",
    courier: "'Courier New', monospace",
    helv: "Arial, sans-serif",
  };
  return fonts[fontFamily ?? "helv"] ?? fonts.helv;
}
