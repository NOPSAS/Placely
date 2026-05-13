"""
XDi IFC Parser
Konverterer IFC-filer til SlimBIM JSON via ifcopenshell.
Krever: pip install ifcopenshell
"""
import io
import tempfile
import os
import uuid
from typing import Optional

from models.slimbim import (
    SlimBIMDocument, Property, Building, Floor, Wall, Room,
    SourceInfo, WallType, FloorType, RoomType
)

try:
    import ifcopenshell
    import ifcopenshell.util.element as ifc_util
    HAS_IFC = True
except ImportError:
    HAS_IFC = False


class IfcParser:
    def __init__(self):
        if not HAS_IFC:
            raise ImportError(
                "ifcopenshell er ikke installert. Kjør: pip install ifcopenshell"
            )

    def parse(self, ifc_bytes: bytes, address: Optional[str] = None) -> SlimBIMDocument:
        # Skriv til tempfil (ifcopenshell trenger filsti)
        with tempfile.NamedTemporaryFile(suffix=".ifc", delete=False) as tmp:
            tmp.write(ifc_bytes)
            tmp_path = tmp.name

        try:
            model = ifcopenshell.open(tmp_path)
            return self._convert(model, address)
        finally:
            os.unlink(tmp_path)

    def _convert(self, model, address: Optional[str]) -> SlimBIMDocument:
        site   = self._get_site(model)
        floors = self._extract_floors(model)
        roof   = self._extract_roof(model)

        building = Building(
            id             = f"bygg_{uuid.uuid4().hex[:8]}",
            building_type  = "detached_house",
            version_status = "as_built",
            floors         = floors,
            roof           = roof,
            source_info    = SourceInfo(source="ifc_parser", confidence=0.95),
        )

        prop = Property(
            id          = f"prop_{uuid.uuid4().hex[:8]}",
            address     = address or self._get_address(model) or "Ukjent adresse",
            buildings   = [building],
            source_info = SourceInfo(source="ifc_parser", confidence=0.95),
        )

        return SlimBIMDocument(
            created_by = "xdi-ifc-parser-v1",
            property   = prop,
        )

    def _get_address(self, model) -> Optional[str]:
        try:
            sites = model.by_type("IfcSite")
            if sites and sites[0].Name:
                return sites[0].Name
        except Exception:
            pass
        return None

    def _get_site(self, model):
        try:
            return model.by_type("IfcSite")[0]
        except Exception:
            return None

    def _extract_floors(self, model) -> list:
        floors = []
        try:
            storeys = model.by_type("IfcBuildingStorey")
            for i, storey in enumerate(storeys):
                elevation = getattr(storey, "Elevation", None) or 0.0
                walls     = self._extract_walls(model, storey)
                rooms     = self._extract_rooms(model, storey)

                floors.append(Floor(
                    id               = f"etg_{i:02d}",
                    level_index      = i - 1 if self._is_basement(storey) else i,
                    floor_type       = FloorType.basement if self._is_basement(storey) else (FloorType.ground if i == 0 else FloorType.upper),
                    floor_height_m   = round(float(elevation), 3),
                    walls            = walls,
                    rooms            = rooms,
                    source_info      = SourceInfo(source="ifc_parser", confidence=0.95),
                ))
        except Exception:
            # Fallback: hent alle vegger uten etasjeskilille
            all_walls = self._extract_all_walls(model)
            floors = [Floor(
                id          = "etg_00",
                level_index = 0,
                floor_type  = FloorType.ground,
                walls       = all_walls,
                source_info = SourceInfo(source="ifc_parser", confidence=0.7),
            )]

        return floors

    def _is_basement(self, storey) -> bool:
        name = (getattr(storey, "Name", "") or "").lower()
        return any(k in name for k in ["kjeller", "basement", "underground", "-1"])

    def _extract_walls(self, model, storey) -> list:
        walls = []
        try:
            ifc_walls = [
                el for el in model.by_type("IfcWall")
                if self._in_storey(el, storey)
            ]
            for w in ifc_walls:
                wall = self._ifc_wall_to_slimbim(w)
                if wall:
                    walls.append(wall)
        except Exception:
            pass
        return walls

    def _extract_all_walls(self, model) -> list:
        walls = []
        for w in model.by_type("IfcWall"):
            wall = self._ifc_wall_to_slimbim(w)
            if wall:
                walls.append(wall)
        return walls

    def _ifc_wall_to_slimbim(self, ifc_wall) -> Optional[Wall]:
        try:
            props    = ifc_util.get_psets(ifc_wall)
            is_ext   = self._is_exterior(props)
            thickness = self._get_thickness(props) or 0.248
            height    = self._get_height(props) or 2.4

            coords = self._get_wall_coords(ifc_wall)
            if not coords:
                return None

            start_m, end_m = coords
            length_m = ((end_m[0]-start_m[0])**2 + (end_m[1]-start_m[1])**2) ** 0.5

            return Wall(
                id          = ifc_wall.GlobalId or f"wall_{uuid.uuid4().hex[:8]}",
                start       = [round(start_m[0], 4), round(start_m[1], 4), round(start_m[2], 4)],
                end         = [round(end_m[0],   4), round(end_m[1],   4), round(end_m[2],   4)],
                thickness_m = round(thickness, 4),
                wall_type   = WallType.exterior if is_ext else WallType.interior,
                top_points  = [
                    {"x_m": 0.0,                  "z_m": round(height, 3)},
                    {"x_m": round(length_m, 3),    "z_m": round(height, 3)},
                ],
                source_info = SourceInfo(source="ifc_parser", confidence=0.90),
            )
        except Exception:
            return None

    def _extract_rooms(self, model, storey) -> list:
        rooms = []
        try:
            spaces = [
                el for el in model.by_type("IfcSpace")
                if self._in_storey(el, storey)
            ]
            for sp in spaces:
                props = ifc_util.get_psets(sp)
                area  = self._get_area(props)
                name  = getattr(sp, "LongName", None) or getattr(sp, "Name", None) or "Rom"
                rooms.append(Room(
                    id          = sp.GlobalId or f"room_{uuid.uuid4().hex[:8]}",
                    name        = name,
                    room_type   = self._guess_room_type(name),
                    area_m2     = round(area, 2) if area else None,
                    source_info = SourceInfo(source="ifc_parser", confidence=0.85),
                ))
        except Exception:
            pass
        return rooms

    def _extract_roof(self, model):
        return None  # TODO: IfcRoof i v0.2

    def _in_storey(self, element, storey) -> bool:
        try:
            for rel in storey.ContainsElements:
                if element in rel.RelatedElements:
                    return True
        except Exception:
            pass
        return False

    def _is_exterior(self, psets: dict) -> bool:
        for pset in psets.values():
            if isinstance(pset, dict):
                v = pset.get("IsExternal") or pset.get("LoadBearing")
                if v is True:
                    return True
        return False

    def _get_thickness(self, psets: dict) -> Optional[float]:
        for pset in psets.values():
            if isinstance(pset, dict):
                v = pset.get("Width") or pset.get("Thickness")
                if v:
                    return float(v)
        return None

    def _get_height(self, psets: dict) -> Optional[float]:
        for pset in psets.values():
            if isinstance(pset, dict):
                v = pset.get("Height") or pset.get("OverallHeight")
                if v:
                    return float(v)
        return None

    def _get_area(self, psets: dict) -> Optional[float]:
        for pset in psets.values():
            if isinstance(pset, dict):
                v = pset.get("NetFloorArea") or pset.get("GrossFloorArea") or pset.get("Area")
                if v:
                    return float(v)
        return None

    def _get_wall_coords(self, ifc_wall):
        try:
            rep = ifc_wall.Representation
            if not rep:
                return None
            for item in rep.Representations:
                for shape in item.Items:
                    if hasattr(shape, "SweptArea"):
                        # IfcExtrudedAreaSolid
                        pos   = ifc_wall.ObjectPlacement
                        start = [0.0, 0.0, 0.0]
                        end   = [1.0, 0.0, 0.0]
                        return start, end
            return None
        except Exception:
            return None

    def _guess_room_type(self, name: str) -> RoomType:
        n = name.lower()
        if any(k in n for k in ["stue", "living", "opphold"]):
            return RoomType.living_room
        if any(k in n for k in ["kjøkken", "kitchen"]):
            return RoomType.kitchen
        if any(k in n for k in ["sov", "bedroom", "rom "]):
            return RoomType.bedroom
        if any(k in n for k in ["bad", "bath", "wc", "toalett"]):
            return RoomType.bathroom
        if any(k in n for k in ["entre", "hall", "gang"]):
            return RoomType.hallway
        if any(k in n for k in ["bod", "lager", "storage"]):
            return RoomType.storage
        if any(k in n for k in ["garasje", "garage"]):
            return RoomType.garage
        return RoomType.other
