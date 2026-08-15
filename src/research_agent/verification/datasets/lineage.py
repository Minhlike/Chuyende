"""
Dataset Lineage & Provenance Graph (Prompt 6 Section 27)
"""

from typing import Dict, List, Optional
from research_agent.schemas.verification import PreprocessingTransformation


class DatasetLineageTracker:
    """
    Constructs and queries the lineage graph from raw datasets to feature inputs.
    Ensures every derived dataset has an explicit, reproducible transformation.
    """

    def __init__(self):
        self._transformations: Dict[str, PreprocessingTransformation] = {}

    def record_transformation(self, trf: PreprocessingTransformation):
        self._transformations[trf.transformation_id] = trf

    def get_ancestors(self, dataset_version_id: str) -> List[str]:
        """Traces all parent dataset versions leading to dataset_version_id."""
        ancestors = []
        current = dataset_version_id
        while True:
            parent = None
            for trf in self._transformations.values():
                if trf.output_dataset_version_id == current:
                    parent = trf.input_dataset_version_id
                    break
            if parent and parent != current:
                ancestors.append(parent)
                current = parent
            else:
                break
        return ancestors

    def get_lineage_trail(self, dataset_version_id: str) -> List[PreprocessingTransformation]:
        """Returns the ordered list of transformations applied to produce dataset_version_id."""
        trail = []
        current = dataset_version_id
        while True:
            step = None
            for trf in self._transformations.values():
                if trf.output_dataset_version_id == current:
                    step = trf
                    break
            if step:
                trail.append(step)
                current = step.input_dataset_version_id
            else:
                break
        return list(reversed(trail))
