"""Threat similarity detection service."""

from typing import List, Dict, Any
from app.models.threat import Threat
from app.services.threat_patterns import match_threat_patterns


class ThreatSimilarityService:
    """Service for finding similar threats."""

    def find_similar_threats(self, threat_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Find threats similar to the given threat.

        Args:
            threat_id: ID of the threat to find similarities for
            limit: Maximum number of similar threats to return

        Returns:
            List of similar threats with similarity scores
        """
        target_threat = Threat.query.get(threat_id)
        if not target_threat:
            return []

        all_threats = Threat.query.filter(Threat.id != threat_id).all()
        similarities = []

        target_patterns = match_threat_patterns(target_threat.asset, target_threat.flow, target_threat.trust_boundary)
        target_pattern_names = {name for name, _, _ in target_patterns}
        target_stride = set(target_threat.stride_categories or [])

        for threat in all_threats:
            similarity_score = self._calculate_similarity(target_threat, threat, target_pattern_names, target_stride)

            if similarity_score > 0:
                similarities.append(
                    {
                        "threat": threat.to_dict(),
                        "similarity_score": round(similarity_score, 2),
                        "similarity_percentage": round(similarity_score * 100, 1),
                    }
                )

        # Sort by similarity score (highest first)
        similarities.sort(key=lambda x: x["similarity_score"], reverse=True)

        return similarities[:limit]

    def _calculate_similarity(
        self, target: Threat, candidate: Threat, target_patterns: set, target_stride: set
    ) -> float:
        """Calculate similarity score between two threats (0-1)."""
        score = 0.0
        factors = 0

        # Factor 1: Asset similarity (exact match = 1.0, partial = 0.5)
        if target.asset.lower() == candidate.asset.lower():
            score += 1.0
        elif target.asset.lower() in candidate.asset.lower() or candidate.asset.lower() in target.asset.lower():
            score += 0.5
        factors += 1

        # Factor 2: STRIDE category overlap
        candidate_stride = set(candidate.stride_categories or [])
        stride_intersection = target_stride.intersection(candidate_stride)
        stride_union = target_stride.union(candidate_stride)
        if stride_union:
            stride_similarity = len(stride_intersection) / len(stride_union)
            score += stride_similarity
        factors += 1

        # Factor 3: Pattern matching similarity
        candidate_patterns = match_threat_patterns(candidate.asset, candidate.flow, candidate.trust_boundary)
        candidate_pattern_names = {name for name, _, _ in candidate_patterns}
        pattern_intersection = target_patterns.intersection(candidate_pattern_names)
        pattern_union = target_patterns.union(candidate_pattern_names)
        if pattern_union:
            pattern_similarity = len(pattern_intersection) / len(pattern_union)
            score += pattern_similarity
        factors += 1

        # Factor 4: Risk level similarity
        risk_levels = {"Low": 1, "Medium": 2, "High": 3}
        target_risk = risk_levels.get(target.risk_level, 2)
        candidate_risk = risk_levels.get(candidate.risk_level, 2)
        risk_diff = abs(target_risk - candidate_risk)
        risk_similarity = 1.0 - (risk_diff / 2.0)  # Max diff is 2 (Low to High)
        score += max(0, risk_similarity)
        factors += 1

        # Factor 5: DREAD score similarity
        target_dread = target.dread_score or {}
        candidate_dread = candidate.dread_score or {}
        dread_keys = ["damage", "reproducibility", "exploitability", "affected_users", "discoverability"]
        dread_similarities = []
        for key in dread_keys:
            target_val = target_dread.get(key, 5)
            candidate_val = candidate_dread.get(key, 5)
            diff = abs(target_val - candidate_val)
            similarity = 1.0 - (diff / 10.0)  # Max diff is 10
            dread_similarities.append(max(0, similarity))

        if dread_similarities:
            avg_dread_similarity = sum(dread_similarities) / len(dread_similarities)
            score += avg_dread_similarity
        factors += 1

        # Average all factors
        return score / factors if factors > 0 else 0.0
