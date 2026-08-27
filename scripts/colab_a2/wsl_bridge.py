# -*- coding: utf-8 -*-
"""
WSL Bridge Module for Google Colab CLI.
Provides seamless execution of `colab` commands from both Windows host and native Linux environments.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

DEFAULT_SESSION_NAME = "stage-a2"
DEFAULT_GPU_TYPE = os.environ.get("A2_GPU", "T4")

class ColabCLIBridge:
    def __init__(self, session_name: str = DEFAULT_SESSION_NAME, gpu_type: str = DEFAULT_GPU_TYPE):
        self.session_name = session_name
        self.gpu_type = gpu_type
        self.is_windows = (sys.platform == "win32")
        self.colab_bin = self._find_colab_bin()

    def _find_colab_bin(self) -> List[str]:
        if not self.is_windows:
            which_colab = shutil.which("colab")
            if which_colab:
                return [which_colab]
            local_bin = Path.home() / ".local" / "bin" / "colab"
            if local_bin.exists():
                return [str(local_bin)]
            return ["colab"]
        else:
            return ["wsl", "-e", "/home/minh123/.local/bin/colab"]

    def run_colab_raw(self, args: List[str], capture_output: bool = True, text: bool = True, check: bool = False) -> subprocess.CompletedProcess:
        """Executes a colab command directly."""
        cmd = self.colab_bin + args
        return subprocess.run(cmd, capture_output=capture_output, text=text, check=check)

    def is_authenticated(self) -> bool:
        """Checks if Colab CLI credentials exist and can query sessions."""
        res = self.run_colab_raw(["sessions"], capture_output=True, text=True)
        return res.returncode == 0 and "Enter the authorization code:" not in (res.stdout + res.stderr)

    def list_sessions(self) -> List[Dict[str, str]]:
        """Lists active Colab sessions."""
        res = self.run_colab_raw(["sessions"], capture_output=True, text=True)
        if res.returncode != 0:
            return []
        sessions = []
        for line in res.stdout.splitlines():
            line = line.strip()
            if not line or line.startswith("Session") or line.startswith("---") or line.startswith("Usage:"):
                continue
            parts = line.split()
            if parts:
                sessions.append({"name": parts[0], "raw": line})
        return sessions

    def get_session_status(self, session_name: Optional[str] = None) -> Dict[str, Any]:
        """Queries status of a specific session."""
        sname = session_name or self.session_name
        res = self.run_colab_raw(["status", "-s", sname], capture_output=True, text=True)
        return {
            "session": sname,
            "exists": res.returncode == 0,
            "status_output": res.stdout.strip(),
            "returncode": res.returncode
        }

    def create_session(self, session_name: Optional[str] = None, gpu_type: Optional[str] = None) -> bool:
        """Creates a named persistent GPU Colab session."""
        sname = session_name or self.session_name
        gpu = gpu_type or self.gpu_type
        print(f"[COLAB-CLI] Creating session '{sname}' with GPU '{gpu}'...")
        res = self.run_colab_raw(["new", "-s", sname, "--gpu", gpu], capture_output=True, text=True)
        print(res.stdout)
        if res.returncode != 0:
            print(f"[COLAB-CLI ERROR] {res.stderr}")
            return False
        return True

    def mount_drive(self, session_name: Optional[str] = None) -> bool:
        """Mounts Google Drive on the remote session."""
        sname = session_name or self.session_name
        print(f"[COLAB-CLI] Mounting Google Drive in session '{sname}'...")
        res = self.run_colab_raw(["drivemount", "-s", sname], capture_output=True, text=True)
        print(res.stdout)
        return res.returncode == 0

    def exec_code(self, code_snippet: str, session_name: Optional[str] = None) -> Tuple[int, str, str]:
        """Executes a Python / bash code snippet inside the remote session."""
        sname = session_name or self.session_name
        res = self.run_colab_raw(["exec", "-s", sname, code_snippet], capture_output=True, text=True)
        return res.returncode, res.stdout, res.stderr

    def stop_session(self, session_name: Optional[str] = None) -> bool:
        """Stops a named session."""
        sname = session_name or self.session_name
        print(f"[COLAB-CLI] Stopping session '{sname}'...")
        res = self.run_colab_raw(["stop", "-s", sname], capture_output=True, text=True)
        print(res.stdout)
        return res.returncode == 0
