export type FieldKey = "attendee_name" | "workshop_title" | "certificate_date";

export interface FieldMapping {
  id?: number;
  template_id?: number;
  field_key: FieldKey;
  x: number;
  y: number;
  width: number;
  height: number;
  font_family: string | null;
  font_size: number | null;
  font_color: string | null;
  font_weight: string | null;
  alignment: "left" | "center" | "right" | null;
  visible: boolean;
}
