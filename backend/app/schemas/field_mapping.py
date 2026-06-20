from pydantic import BaseModel, ConfigDict, Field


class FieldMappingBase(BaseModel):
    field_key: str
    x: float = Field(ge=0)
    y: float = Field(ge=0)
    width: float = Field(gt=0)
    height: float = Field(gt=0)
    font_family: str | None = "helv"
    font_size: float | None = Field(default=36, gt=0)
    font_color: str | None = "#111827"
    font_weight: str | None = "normal"
    alignment: str | None = "center"
    visible: bool = True


class FieldMappingCreate(FieldMappingBase):
    pass


class FieldMappingUpdate(BaseModel):
    mappings: list[FieldMappingCreate]


class FieldMappingRead(FieldMappingBase):
    id: int
    template_id: int

    model_config = ConfigDict(from_attributes=True)
