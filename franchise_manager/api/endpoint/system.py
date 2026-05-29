from pathlib import Path

from fastapi import HTTPException
from fastapi.responses import FileResponse

from franchise_manager.api.config import is_develop


# #
# health

def health() -> dict:
    return {"ok": True}


# #
# domain map (dev only)

def domain_map_page() -> FileResponse:
    if not is_develop():
        raise HTTPException(status_code=404)

    return FileResponse("/app/franchise_manager/api/domain/map.html")


def domain_map_data() -> list[dict]:
    if not is_develop():
        raise HTTPException(status_code=404)
    
    raw = []
    for directory in sorted(Path("/app/franchise_manager/api/domain").iterdir()):
        if not directory.is_dir() or directory.name.startswith("__"):
            continue
        
        files = {f.name: f.read_text() for f in sorted(directory.glob("*.py"))}
        if files:
            raw.append({"name": directory.name, "files": files})
            
    return raw