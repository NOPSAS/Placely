from __future__ import annotations
from typing import List, Optional, Literal
from enum import Enum
from pydantic import BaseModel, Field
import uuid
from datetime import datetime


class VersionStatus(str, Enum):
    last_approved = "last_approved"
    as_built      = "as_built"
    current       = "current"
    proposed      = "proposed"


class WallType(str, Enum):
    exterior      = "exterior"
    interior      = "interior"
    load_bearing  = "load_bearing"
    partition     = "partition"
    foundation    = "foundation"


class FloorType(str, Enum):
    basement = "basement"
    ground   = "ground"
    upper    = "upper"
    attic    = "attic"


class RoomType(str, Enum):
    living_room = "living_room"
    kitchen     = "kitchen"
    bedroom     = "bedroom"
    bathroom    = "bathroom"
    toilet      = "toilet"
    hallway     = "hallway"
    utility     = "utility"
    storage     = "storage"
    garage      = "garage"
    office      = "office"
    other       = "other"


class RoofType(str, Enum):
    flat    = "flat"
    shed    = "shed"
    gable   = "gable"
    hip     = "hip"
    mansard = "mansard"
    complex = "complex"


class ConditionGrade(int, Enum):
    not_assessed = 0
    good         = 1
    fair         = 2
    poor         = 3


class SourceInfo(BaseModel):
    source:            str = "manual"
    confidence:        float = Field(default=1.0, ge=0.0, le=1.0)
    measured_at:       Optional[str] = None


class Condition(BaseModel):
    tg:                      Optional[ConditionGrade] = None
    risk:                    Optional[Literal["low", "medium", "high"]] = None
    estimated_lifetime_years: Optional[int] = None
    notes:                   Optional[str] = None


class TopPoint(BaseModel):
    x_m: float
    z_m: float


class Opening(BaseModel):
    id:                    str = Field(default_factory=lambda: f"opening_{uuid.uuid4().hex[:8]}")
    type:                  Literal["opening"] = "opening"
    opening_type:          Literal["door", "window", "garage_door", "hatch"] = "window"
    width_m:               Optional[float] = None
    height_m:              Optional[float] = None
    sill_height_m:         Optional[float] = None
    position_along_wall_m: Optional[float] = None
    year_installed:        Optional[int] = None
    source_info:           Optional[SourceInfo] = None
    condition:             Optional[Condition] = None


class Wall(BaseModel):
    id:              str = Field(default_factory=lambda: f"wall_{uuid.uuid4().hex[:8]}")
    type:            Literal["wall"] = "wall"
    start:           List[float] = Field(..., min_items=3, max_items=3)
    end:             List[float] = Field(..., min_items=3, max_items=3)
    height_left_m:   Optional[float] = None
    height_right_m:  Optional[float] = None
    thickness_m:     float = 0.248
    wall_type:       WallType = WallType.exterior
    is_roof_driver:  bool = False
    top_points:      List[TopPoint] = []
    openings:        List[Opening] = []
    room_id_inside:  Optional[str] = None
    room_id_outside: Optional[str] = None
    source_info:     Optional[SourceInfo] = None
    condition:       Optional[Condition] = None


class Surface(BaseModel):
    id:           str = Field(default_factory=lambda: f"surface_{uuid.uuid4().hex[:8]}")
    type:         Literal["surface"] = "surface"
    surface_type: str = "wall_other"
    area_m2:      Optional[float] = None
    material:     Optional[str] = None
    moisture_pct: Optional[float] = None
    source_info:  Optional[SourceInfo] = None
    condition:    Optional[Condition] = None


class Room(BaseModel):
    id:               str = Field(default_factory=lambda: f"room_{uuid.uuid4().hex[:8]}")
    type:             Literal["room"] = "room"
    room_type:        RoomType = RoomType.other
    name:             Optional[str] = None
    area_m2:          Optional[float] = None
    ceiling_height_m: Optional[float] = None
    is_wet_room:      bool = False
    surfaces:         List[Surface] = []
    source_info:      Optional[SourceInfo] = None
    condition:        Optional[Condition] = None


class Roof(BaseModel):
    id:                   str = Field(default_factory=lambda: f"roof_{uuid.uuid4().hex[:8]}")
    type:                 Literal["roof"] = "roof"
    roof_type:            RoofType = RoofType.gable
    ridge_height_m:       Optional[float] = None
    eave_height_m:        Optional[float] = None
    overhang_m:           Optional[float] = None
    pitch_deg:            Optional[float] = None
    derived_from_walls:   List[str] = []
    source_info:          Optional[SourceInfo] = None


class Floor(BaseModel):
    id:               str = Field(default_factory=lambda: f"floor_{uuid.uuid4().hex[:8]}")
    type:             Literal["floor"] = "floor"
    level_index:      int = 0
    floor_type:       FloorType = FloorType.ground
    floor_height_m:   Optional[float] = None
    ceiling_height_m: Optional[float] = None
    bra_m2:           Optional[float] = None
    rooms:            List[Room] = []
    walls:            List[Wall] = []
    source_info:      Optional[SourceInfo] = None


class Building(BaseModel):
    id:              str = Field(default_factory=lambda: f"bygg_{uuid.uuid4().hex[:8]}")
    type:            Literal["building"] = "building"
    building_type:   Optional[str] = None
    version_status:  VersionStatus = VersionStatus.as_built
    year_built:      Optional[int] = None
    year_approved:   Optional[int] = None
    bra_m2:          Optional[float] = None
    bya_m2:          Optional[float] = None
    floors:          List[Floor] = []
    roof:            Optional[Roof] = None
    origin:          Optional[List[float]] = None
    rotation_deg:    Optional[float] = None
    source_info:     Optional[SourceInfo] = None
    condition:       Optional[Condition] = None


class Property(BaseModel):
    id:                  str = Field(default_factory=lambda: f"prop_{uuid.uuid4().hex[:8]}")
    type:                Literal["property"] = "property"
    address:             str = "Ukjent adresse"
    gnr:                 Optional[int] = None
    bnr:                 Optional[int] = None
    municipality_number: Optional[str] = None
    plot_area_m2:        Optional[float] = None
    buildings:           List[Building] = []
    source_info:         Optional[SourceInfo] = None
    condition:           Optional[Condition] = None


class SlimBIMDocument(BaseModel):
    slimbim_version: str = "1.0.0"
    created_at:      str = Field(default_factory=lambda: datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"))
    created_by:      str = "xdi-v0.1"
    property:        Property
