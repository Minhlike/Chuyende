import subprocess, sys, os, pathlib

base_dir = pathlib.Path("D:/Research")
python_exe = base_dir / ".venv-stage-a2-cuda/Scripts/python.exe"
log_dir = base_dir / "logs/stage-a2"
log_dir.mkdir(parents=True, exist_ok=True)

stdout_f = open(log_dir / "seed42.stdout.log", "w", encoding="utf-8")
stderr_f = open(log_dir / "seed42.stderr.log", "w", encoding="utf-8")

env = os.environ.copy()
env["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"
env["PYTHONUNBUFFERED"] = "1"

cmd = [
    str(python_exe),
    "-u",
    str(base_dir / "scripts/run_stage_a2_five_seed_empirical.py"),
    "--seed", "42",
    "--resume", str(base_dir / ".artifacts/stage-a2/HDFS/seed-42/last_checkpoint.pt"),
    "--resume-sha256", "cca63e780d2fc91bc57260cacace37fc5bb1581d0206e4341ccbb26ed10f2a9f",
    "--authorize-real-empirical-execution",
    "--base-dir", str(base_dir),
    "--dataset-path", str(base_dir / "datasets/raw/hdfs/HDFS_1.tar.gz"),
    "--durable-root", str(base_dir / "durable/stage-a2/HDFS"),
    "--plan", str(base_dir / "experiments/plans/STAGE-A2-FIVE-SEED-EXECUTION-PLAN-V1.5.json"),
    "--environment-lock", str(base_dir / "experiments/evidence/stage-a2/preexecution/STAGE-A2-LOCAL-EXECUTION-ENVIRONMENT-V1.5.json"),
    "--authorization", str(base_dir / "experiments/evidence/stage-a2/preexecution/SEED42-LOCAL-LAUNCH-AUTHORIZATION-V1.5.json")
]

p = subprocess.Popen(
    cmd,
    cwd=str(base_dir),
    stdout=stdout_f,
    stderr=stderr_f,
    env=env,
    creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
)

with open(log_dir / "seed42.pid", "w", encoding="utf-8") as f:
    f.write(str(p.pid))

print(f"Spawned truly detached training process PID: {p.pid}")
