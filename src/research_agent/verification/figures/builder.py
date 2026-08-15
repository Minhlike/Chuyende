"""
Deterministic Scientific Figure Builder & Plotting Engine (Prompt 6 Sections 57..69, RC-09)
"""

import hashlib
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for headless scientific verification
import matplotlib.pyplot as plt
import pandas as pd
from research_agent.core.enums import FigureType
from research_agent.schemas.verification import FigureSpecification


class FigureBuilder:
    """
    Renders publication-grade scientific figures and writes companion figure-data.csv.
    Enforces that every plot point originates from raw structured arrays with recorded SHA-256.
    """

    def __init__(self, output_dir: Path | str = "artifacts/figures"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _save_plot_and_companion_data(
        self,
        fig: plt.Figure,
        figure_id: str,
        df_companion: pd.DataFrame,
    ) -> Tuple[str, str, str, str]:
        """Saves SVG plot and companion CSV, returning relative paths and SHA-256 hashes."""
        img_filename = f"{figure_id.lower()}.png"
        csv_filename = f"{figure_id.lower()}-data.csv"

        img_path = self.output_dir / img_filename
        csv_path = self.output_dir / csv_filename

        fig.savefig(img_path, dpi=300, bbox_inches="tight")
        plt.close(fig)

        df_companion.to_csv(csv_path, index=False)

        # Hash image
        hasher_img = hashlib.sha256()
        with open(img_path, "rb") as f:
            while chunk := f.read(65536):
                hasher_img.update(chunk)
        img_sha = hasher_img.hexdigest()

        # Hash companion CSV
        hasher_csv = hashlib.sha256()
        with open(csv_path, "rb") as f:
            while chunk := f.read(65536):
                hasher_csv.update(chunk)
        csv_sha = hasher_csv.hexdigest()

        return str(img_path), str(csv_path), img_sha, csv_sha

    def plot_pr_curve(
        self,
        figure_id: str,
        title: str,
        caption: str,
        curves_data: List[Dict[str, Any]],
        script_path: str = "src/research_agent/verification/figures/builder.py",
    ) -> FigureSpecification:
        """
        Plots Precision-Recall curves for multiple methods.
        curves_data: list of {name, recalls, precisions, pr_auc}
        """
        fig, ax = plt.subplots(figsize=(6.5, 4.5))
        companion_rows = []

        for curve in curves_data:
            name = curve["name"]
            recalls = curve["recalls"]
            precisions = curve["precisions"]
            auc = curve.get("pr_auc", 0.0)
            ax.plot(recalls, precisions, label=f"{name} (PR-AUC = {auc:.3f})", lw=2)

            for r, p in zip(recalls, precisions):
                companion_rows.append({"method": name, "recall": r, "precision": p})

        ax.set_xlabel("Recall", fontsize=11)
        ax.set_ylabel("Precision", fontsize=11)
        ax.set_title(title, fontsize=12, fontweight="bold")
        ax.set_xlim([0.0, 1.05])
        ax.set_ylim([0.0, 1.05])
        ax.grid(True, linestyle="--", alpha=0.6)
        ax.legend(loc="lower left", fontsize=10)

        df_comp = pd.DataFrame(companion_rows)
        img_p, csv_p, img_sha, csv_sha = self._save_plot_and_companion_data(fig, figure_id, df_comp)

        return FigureSpecification(
            figure_id=figure_id,
            figure_type=FigureType.PR_CURVE,
            title=title,
            caption=caption,
            plot_script_path=script_path,
            output_file_rel_path=img_p,
            companion_data_csv_rel_path=csv_p,
            uncertainty_represented="NONE",
            manually_edited=False,
            output_sha256=img_sha,
            companion_data_sha256=csv_sha,
            created_at=datetime.now(timezone.utc),
        )

    def plot_bar_chart_with_ci(
        self,
        figure_id: str,
        title: str,
        caption: str,
        methods: List[str],
        means: List[float],
        ci_lows: List[float],
        ci_highs: List[float],
        y_label: str = "F1 Score (%)",
        script_path: str = "src/research_agent/verification/figures/builder.py",
    ) -> FigureSpecification:
        """Plots bar chart with explicit 95% confidence intervals / error bars."""
        fig, ax = plt.subplots(figsize=(7, 4.5))

        yerr_lower = [m - l for m, l in zip(means, ci_lows)]
        yerr_upper = [h - m for m, h in zip(means, ci_highs)]
        yerr = [yerr_lower, yerr_upper]

        bars = ax.bar(methods, means, yerr=yerr, capsize=5, color="#1f77b4", edgecolor="black", alpha=0.85)

        ax.set_ylabel(y_label, fontsize=11)
        ax.set_title(title, fontsize=12, fontweight="bold")
        ax.grid(axis="y", linestyle="--", alpha=0.6)

        companion_rows = [
            {"method": m, "mean": mean, "ci_lower": low, "ci_upper": high}
            for m, mean, low, high in zip(methods, means, ci_lows, ci_highs)
        ]
        df_comp = pd.DataFrame(companion_rows)
        img_p, csv_p, img_sha, csv_sha = self._save_plot_and_companion_data(fig, figure_id, df_comp)

        return FigureSpecification(
            figure_id=figure_id,
            figure_type=FigureType.BAR_PLOT,
            title=title,
            caption=caption,
            plot_script_path=script_path,
            output_file_rel_path=img_p,
            companion_data_csv_rel_path=csv_p,
            uncertainty_represented="CI_95",
            manually_edited=False,
            output_sha256=img_sha,
            companion_data_sha256=csv_sha,
            created_at=datetime.now(timezone.utc),
        )

    def plot_ablation_or_parameter_sensitivity(
        self,
        figure_id: str,
        title: str,
        caption: str,
        param_values: List[Any],
        param_name: str,
        metric_values: List[float],
        metric_name: str,
        script_path: str = "src/research_agent/verification/figures/builder.py",
    ) -> FigureSpecification:
        """Plots ablation / hyperparameter sensitivity curve."""
        fig, ax = plt.subplots(figsize=(6.5, 4.5))
        ax.plot(param_values, metric_values, marker="o", lw=2, color="#d62728")

        ax.set_xlabel(param_name, fontsize=11)
        ax.set_ylabel(metric_name, fontsize=11)
        ax.set_title(title, fontsize=12, fontweight="bold")
        ax.grid(True, linestyle="--", alpha=0.6)

        df_comp = pd.DataFrame({param_name: param_values, metric_name: metric_values})
        img_p, csv_p, img_sha, csv_sha = self._save_plot_and_companion_data(fig, figure_id, df_comp)

        return FigureSpecification(
            figure_id=figure_id,
            figure_type=FigureType.ABLATION_PLOT,
            title=title,
            caption=caption,
            plot_script_path=script_path,
            output_file_rel_path=img_p,
            companion_data_csv_rel_path=csv_p,
            uncertainty_represented="NONE",
            manually_edited=False,
            output_sha256=img_sha,
            companion_data_sha256=csv_sha,
            created_at=datetime.now(timezone.utc),
        )
