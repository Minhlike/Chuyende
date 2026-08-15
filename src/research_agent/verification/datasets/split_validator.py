"""
Anti-Leakage Split Validator (Prompt 6 Section 25, RC-14)
"""

from typing import Any, Dict, List, Optional, Set, Tuple
import pandas as pd


class AntiLeakageSplitValidator:
    """
    Audits experiment dataset splits for data leakage, temporal overlap,
    entity holdout contamination, and feature normalization leakage.
    """

    def audit_temporal_order(
        self,
        train_df: pd.DataFrame,
        val_df: Optional[pd.DataFrame],
        test_df: pd.DataFrame,
        timestamp_col: str,
    ) -> Tuple[bool, List[str]]:
        """
        Validates strict temporal progression:
        max(Train_ts) <= min(Val_ts) and max(Val_ts) <= min(Test_ts).
        """
        issues = []
        train_ts = pd.to_datetime(train_df[timestamp_col], errors="coerce")
        test_ts = pd.to_datetime(test_df[timestamp_col], errors="coerce")

        train_max = train_ts.max()
        test_min = test_ts.min()

        if train_max > test_min:
            issues.append(
                f"TEMPORAL_LEAKAGE: Train max timestamp ({train_max}) is after Test min timestamp ({test_min})."
            )

        if val_df is not None and not val_df.empty:
            val_ts = pd.to_datetime(val_df[timestamp_col], errors="coerce")
            val_min = val_ts.min()
            val_max = val_ts.max()
            if train_max > val_min:
                issues.append(f"TEMPORAL_LEAKAGE: Train max timestamp ({train_max}) is after Validation min ({val_min}).")
            if val_max > test_min:
                issues.append(f"TEMPORAL_LEAKAGE: Validation max timestamp ({val_max}) is after Test min ({test_min}).")

        return len(issues) == 0, issues

    def audit_entity_holdout(
        self,
        train_df: pd.DataFrame,
        test_df: pd.DataFrame,
        entity_col: str,
    ) -> Tuple[bool, List[str]]:
        """
        Audits if train and test share identical entities (hosts, users, IP addresses).
        Enforces strict entity-level holdout for out-of-distribution evaluation.
        """
        issues = []
        train_entities = set(train_df[entity_col].dropna().unique())
        test_entities = set(test_df[entity_col].dropna().unique())
        overlap = train_entities.intersection(test_entities)

        if overlap:
            issues.append(
                f"ENTITY_LEAKAGE: {len(overlap)} entities present in both Train and Test splits: {list(overlap)[:5]}..."
            )

        return len(issues) == 0, issues

    def audit_row_hash_overlap(
        self,
        train_df: pd.DataFrame,
        test_df: pd.DataFrame,
        feature_cols: Optional[List[str]] = None,
    ) -> Tuple[bool, List[str]]:
        """Checks for duplicate raw events appearing in both train and test partitions."""
        issues = []
        cols = feature_cols if feature_cols else list(train_df.columns)
        common_cols = [c for c in cols if c in train_df.columns and c in test_df.columns]

        train_sub = train_df[common_cols].astype(str)
        test_sub = test_df[common_cols].astype(str)

        train_hashes: Set[int] = set(pd.util.hash_pandas_object(train_sub, index=False))
        test_hashes: Set[int] = set(pd.util.hash_pandas_object(test_sub, index=False))

        overlap = train_hashes.intersection(test_hashes)
        if overlap:
            issues.append(
                f"EXACT_ROW_LEAKAGE: {len(overlap)} exact identical event rows appear in both Train and Test splits."
            )

        return len(issues) == 0, issues

    def audit_preprocessing_split_fit(
        self,
        fitted_on: str,
        transformation_name: str,
    ) -> Tuple[bool, Optional[str]]:
        """Flags if a parser, normalizer, or vocabulary was fitted on the entire dataset."""
        if fitted_on.upper() not in ["TRAIN", "TRAIN_ONLY", "TRAIN_SPLIT"]:
            return False, f"PREPROCESSING_LEAKAGE: '{transformation_name}' was fitted on '{fitted_on}' instead of 'TRAIN_ONLY'."
        return True, None
