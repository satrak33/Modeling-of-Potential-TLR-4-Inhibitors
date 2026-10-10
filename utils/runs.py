import hashlib
import json
import shutil
from pathlib import Path
from contextlib import contextmanager
from datetime import datetime, timezone
from uuid import uuid4

from utils.logging import close_logging, configure_logging
from utils.paths import DATA, STAGES, stage_path


def signature(path):
    path = path.resolve()
    if not path.exists():
        raise FileNotFoundError(f"Input does not exist: {path}")
    files = sorted(path.rglob("*")) if path.is_dir() else [path]
    digest = hashlib.sha256()
    for item in files:
        if item.is_file():
            digest.update(str(item.relative_to(path) if path.is_dir() else item.name).encode())
            with item.open("rb") as stream:
                for block in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(block)
    return digest.hexdigest()


def require_stage(stage, _seen=None):
    seen = set() if _seen is None else _seen
    if stage in seen:
        raise RuntimeError(f"Circular stage dependency: {stage}")
    seen.add(stage)
    folder = stage_path(stage)
    manifest = folder / "run.json"
    if not manifest.is_file():
        raise RuntimeError(f"Run stage {stage} first; no run manifest found")
    state = json.loads(manifest.read_text(encoding="utf-8"))
    if state["status"] != "completed":
        raise RuntimeError(f"Stage {stage} is {state['status']}; rerun it first")
    for name, fingerprint in state.get("inputs", {}).items():
        path = Path(name)
        for upstream in STAGES:
            upstream_folder = stage_path(upstream)
            if path == upstream_folder or upstream_folder in path.parents:
                require_stage(upstream, seen.copy())
                break
        if signature(path) != fingerprint:
            raise RuntimeError(f"Stage {stage} is stale: input changed: {name}")
    return folder


@contextmanager
def stage_run(stage, inputs, parameters=None):
    fingerprints = {str(p.resolve()): signature(p) for p in inputs}
    folder = stage_path(stage)
    logs = DATA / "logs" / stage
    close_logging()
    if folder.exists() or logs.exists():
        old_manifest = folder / "run.json"
        old = json.loads(old_manifest.read_text(encoding="utf-8")) if old_manifest.exists() else {}
        archive = DATA / "archive" / stage / (old.get("run_id", "legacy") + "_" + uuid4().hex[:8])
        archive.mkdir(parents=True)
        if folder.exists():
            shutil.move(str(folder), str(archive / "results"))
        if logs.exists():
            shutil.move(str(logs), str(archive / "logs"))
    folder.mkdir(parents=True)
    logs.mkdir(parents=True)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ") + "_" + uuid4().hex[:8]
    state = dict(run_id=run_id, stage=stage, status="running", inputs=fingerprints, parameters=parameters or {})
    manifest = folder / "run.json"

    def save():
        manifest.write_text(json.dumps(state, indent=2), encoding="utf-8")

    save()
    log = configure_logging(logs / "pipeline.log", stage, run_id)
    log.info("Starting {}", stage)
    try:
        yield folder
    except BaseException as exc:
        state.update(status="failed", error=str(exc))
        log.exception("Stage failed")
        raise
    else:
        state["status"] = "completed"
        log.success("Stage completed: {}", folder)
    finally:
        state["finished_at"] = datetime.now(timezone.utc).isoformat()
        save()
        close_logging()
