import type { FieldKey, FieldMapping } from "../types/fieldMapping";

interface FieldControlPanelProps {
  mapping: FieldMapping;
  onChangeMapping: (field: FieldKey, updates: Partial<FieldMapping>) => void;
}

export function FieldControlPanel({ mapping, onChangeMapping }: FieldControlPanelProps) {
  function updateNumber(key: keyof FieldMapping, value: string) {
    onChangeMapping(mapping.field_key, { [key]: Number(value) } as Partial<FieldMapping>);
  }

  return (
    <aside className="panel control-panel">
      <h2>Field Controls</h2>
      <p className="muted">{mapping.field_key.replace("_", " ")}</p>
      <label>
        X
        <input type="number" value={Math.round(mapping.x)} onChange={(event) => updateNumber("x", event.target.value)} />
      </label>
      <label>
        Y
        <input type="number" value={Math.round(mapping.y)} onChange={(event) => updateNumber("y", event.target.value)} />
      </label>
      <label>
        Width
        <input
          min="1"
          type="number"
          value={Math.round(mapping.width)}
          onChange={(event) => updateNumber("width", event.target.value)}
        />
      </label>
      <label>
        Height
        <input
          min="1"
          type="number"
          value={Math.round(mapping.height)}
          onChange={(event) => updateNumber("height", event.target.value)}
        />
      </label>
      <label>
        Font family
        <select
          value={mapping.font_family ?? "helv"}
          onChange={(event) => onChangeMapping(mapping.field_key, { font_family: event.target.value })}
        >
          <option value="helv">Helvetica</option>
          <option value="times">Times</option>
          <option value="courier">Courier</option>
          <option value="arial">Arial</option>
          <option value="tahoma">Tahoma Arabic</option>
          <option value="segoe_ui">Segoe UI</option>
          <option value="dejavu_sans">DejaVu Sans</option>
        </select>
      </label>
      <label>
        Font size
        <input
          min="1"
          type="number"
          value={Math.round(mapping.font_size ?? 36)}
          onChange={(event) => updateNumber("font_size", event.target.value)}
        />
      </label>
      <label>
        Font color
        <input
          type="color"
          value={mapping.font_color ?? "#111827"}
          onChange={(event) => onChangeMapping(mapping.field_key, { font_color: event.target.value })}
        />
      </label>
      <label>
        Alignment
        <select
          value={mapping.alignment ?? "center"}
          onChange={(event) =>
            onChangeMapping(mapping.field_key, { alignment: event.target.value as FieldMapping["alignment"] })
          }
        >
          <option value="left">Left</option>
          <option value="center">Center</option>
          <option value="right">Right</option>
        </select>
      </label>
      <label className="checkbox-row">
        <input
          checked={mapping.visible}
          type="checkbox"
          onChange={(event) => onChangeMapping(mapping.field_key, { visible: event.target.checked })}
        />
        Visible
      </label>
    </aside>
  );
}
