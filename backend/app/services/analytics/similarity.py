"""
Similarity service — finds municipalities similar to a given one using
Euclidean distance on min-max-normalised indicator vectors.

Base indicators used (any missing values are simply omitted from the vector):
  POP_TOTAL, EMP_RATE, BUDGET_PER_CAPITA, EDU_BAGRUT_RATE

The socioeconomic_cluster from the Municipality model is also included when
available (it is already a 1-10 ordinal scale so it participates naturally).
"""

import math
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.data_point import DataPoint
from app.models.municipality import Municipality
from app.models.indicator import Indicator

BASE_INDICATORS = ["POP_TOTAL", "EMP_RATE", "BUDGET_PER_CAPITA", "EDU_BAGRUT_RATE"]


def _fetch_indicator_map(db: Session) -> dict[str, int]:
    """Return {indicator_code: indicator_id} for the base indicators that exist in DB."""
    rows = db.query(Indicator.code, Indicator.id).filter(Indicator.code.in_(BASE_INDICATORS)).all()
    return {row.code: row.id for row in rows}


def _fetch_vectors(
    db: Session,
    indicator_map: dict[str, int],
    year: int,
) -> dict[int, dict[str, Optional[float]]]:
    """
    Return {municipality_id: {indicator_code: value}} for all municipalities
    for the given year.  Missing data-points are represented as None.
    """
    if not indicator_map:
        return {}

    indicator_ids = list(indicator_map.values())
    code_by_id = {v: k for k, v in indicator_map.items()}

    data_points = (
        db.query(DataPoint)
        .filter(
            and_(
                DataPoint.indicator_id.in_(indicator_ids),
                DataPoint.year == year,
            )
        )
        .all()
    )

    # Build {muni_id: {code: value}}
    vectors: dict[int, dict[str, Optional[float]]] = {}
    for dp in data_points:
        if dp.value is None:
            continue
        muni_id = dp.municipality_id
        code = code_by_id.get(dp.indicator_id)
        if code is None:
            continue
        if muni_id not in vectors:
            vectors[muni_id] = {}
        vectors[muni_id][code] = dp.value

    return vectors


def _fetch_municipalities(db: Session) -> dict[int, Municipality]:
    """Return {id: Municipality} for all municipalities."""
    rows = db.query(Municipality).all()
    return {m.id: m for m in rows}


def _min_max_normalise(
    vectors: dict[int, dict[str, float]],
    dimensions: list[str],
) -> dict[int, list[float]]:
    """
    For each dimension, compute min/max across all municipalities that have
    that dimension, then normalise to [0, 1].

    Municipality vectors that are completely empty after normalisation are
    excluded from the returned dict.
    """
    # Compute per-dimension min/max
    dim_min: dict[str, float] = {}
    dim_max: dict[str, float] = {}
    for dim in dimensions:
        values = [v[dim] for v in vectors.values() if dim in v]
        if not values:
            continue
        dim_min[dim] = min(values)
        dim_max[dim] = max(values)

    available_dims = [d for d in dimensions if d in dim_min]

    normalised: dict[int, list[float]] = {}
    for muni_id, vec in vectors.items():
        coords: list[float] = []
        for dim in available_dims:
            if dim not in vec:
                # Skip municipalities that are missing any available dimension
                # (we mark them as incomplete — handled below)
                coords = []
                break
            lo = dim_min[dim]
            hi = dim_max[dim]
            if hi == lo:
                coords.append(0.0)
            else:
                coords.append((vec[dim] - lo) / (hi - lo))
        if coords:
            normalised[muni_id] = coords

    return normalised


def find_similar(
    db: Session,
    municipality_id: int,
    year: int,
    n: int = 5,
) -> list[dict]:
    """
    Returns a list of the n most similar municipalities (excluding the target),
    sorted by similarity_score descending (1 = identical, 0 = maximally different).

    Each item:
    {
        "id": int,
        "name": str,
        "similarity_score": float,   # 0–1 via 1/(1+distance)
        "district": str | None,
        "municipality_type": str | None,
        "socioeconomic_cluster": int | None,
    }
    """
    # --- Step 1: build raw vectors for all municipalities ---
    indicator_map = _fetch_indicator_map(db)
    raw_vectors = _fetch_vectors(db, indicator_map, year)

    # --- Step 2: attach socioeconomic_cluster (treat as extra numeric dimension) ---
    all_munis = _fetch_municipalities(db)

    # Add cluster as an extra dimension where available
    CLUSTER_DIM = "_cluster"
    for muni_id, muni in all_munis.items():
        if muni.socioeconomic_cluster is not None:
            if muni_id not in raw_vectors:
                raw_vectors[muni_id] = {}
            raw_vectors[muni_id][CLUSTER_DIM] = float(muni.socioeconomic_cluster)

    all_dimensions = BASE_INDICATORS + [CLUSTER_DIM]

    # --- Step 3: min-max normalise across ALL municipalities ---
    normalised = _min_max_normalise(raw_vectors, all_dimensions)

    if municipality_id not in normalised:
        # Target municipality has no data for the given year — return empty list
        return []

    target_vec = normalised[municipality_id]
    n_dims = len(target_vec)

    # --- Step 4: compute Euclidean distance from target ---
    results: list[dict] = []
    for muni_id, vec in normalised.items():
        if muni_id == municipality_id:
            continue
        if len(vec) != n_dims:
            continue  # incompatible dimensionality (shouldn't happen after normalise)

        dist = math.sqrt(sum((a - b) ** 2 for a, b in zip(target_vec, vec)))
        similarity_score = 1.0 / (1.0 + dist)

        muni = all_munis.get(muni_id)
        results.append(
            {
                "id": muni_id,
                "name": muni.name if muni else str(muni_id),
                "similarity_score": round(similarity_score, 4),
                "district": muni.district if muni else None,
                "municipality_type": muni.municipality_type if muni else None,
                "socioeconomic_cluster": muni.socioeconomic_cluster if muni else None,
            }
        )

    # --- Step 5: return top-N sorted by similarity descending ---
    results.sort(key=lambda x: x["similarity_score"], reverse=True)
    return results[:n]
