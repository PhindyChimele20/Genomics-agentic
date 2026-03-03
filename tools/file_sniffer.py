import os
from typing import List, Dict, Any

def save_uploads_to_tempdir(uploads, tmpdir: str) -> List[Dict[str, Any]]:
    manifest = []
    for up in uploads:
        out_path = os.path.join(tmpdir, up.name)
        with open(out_path, "wb") as f:
            f.write(up.getbuffer())
        manifest.append({
            "name": up.name,
            "path": out_path,
            "size": os.path.getsize(out_path),
        })
    return manifest
