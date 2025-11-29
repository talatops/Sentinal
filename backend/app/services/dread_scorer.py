"""Automated DREAD scoring service."""

from typing import Dict, Any, Optional
from app.services.threat_patterns import match_threat_patterns, get_suggested_dread_from_patterns, detect_component_type


class DREADScorer:
    """Service for automated DREAD score suggestions."""

    def suggest_dread_scores(
        self, asset: str, flow: str, trust_boundary: Optional[str] = None, user_scores: Optional[Dict[str, int]] = None
    ) -> Dict[str, Any]:
        """
        Suggest DREAD scores based on threat patterns and context.

        Args:
            asset: Asset description
            flow: Data flow description
            trust_boundary: Trust boundary description
            user_scores: Optional user-provided scores to override suggestions

        Returns:
            Dictionary with suggested scores, confidence, and explanations
        """
        # Match threat patterns
        matched_patterns = match_threat_patterns(asset, flow, trust_boundary)

        # Get suggested scores from patterns
        suggested_scores = get_suggested_dread_from_patterns(matched_patterns)

        # Detect component types for context
        component_types = detect_component_type(asset, flow)

        # Adjust scores based on asset criticality and context
        adjusted_scores = self._adjust_scores_by_context(suggested_scores, asset, flow, component_types)

        # Calculate confidence for each score
        confidence_scores = self._calculate_confidence(matched_patterns, adjusted_scores, component_types)

        # Apply user overrides if provided
        if user_scores:
            for key in adjusted_scores:
                if key in user_scores:
                    adjusted_scores[key] = user_scores[key]
                    confidence_scores[key] = 1.0  # User input has 100% confidence

        # Generate explanations for each score
        explanations = self._generate_explanations(adjusted_scores, matched_patterns, component_types)

        return {
            "suggested_scores": adjusted_scores,
            "confidence": confidence_scores,
            "explanations": explanations,
            "matched_patterns": [name for name, _, _ in matched_patterns],
            "component_types": component_types,
        }

    def _adjust_scores_by_context(
        self, base_scores: Dict[str, int], asset: str, flow: str, component_types: list
    ) -> Dict[str, int]:
        """Adjust scores based on asset criticality and context."""
        adjusted = base_scores.copy()
        text = f"{asset} {flow}".lower()

        # Check for critical infrastructure indicators
        critical_keywords = [
            "payment",
            "financial",
            "bank",
            "credit card",
            "pii",
            "personal data",
            "health",
            "medical",
            "patient",
            "authentication",
            "authorization",
            "admin",
            "root",
            "critical",
            "production",
            "live",
        ]

        is_critical = any(keyword in text for keyword in critical_keywords)

        if is_critical:
            # Increase damage and affected_users for critical assets
            adjusted["damage"] = min(adjusted["damage"] + 1, 10)
            adjusted["affected_users"] = min(adjusted["affected_users"] + 1, 10)

        # Check for external exposure
        external_keywords = ["public", "internet", "external", "api", "web", "http"]
        is_external = any(keyword in text for keyword in external_keywords)

        if is_external:
            # Increase discoverability and exploitability
            adjusted["discoverability"] = min(adjusted["discoverability"] + 1, 10)
            adjusted["exploitability"] = min(adjusted["exploitability"] + 1, 10)

        # Check for authentication/authorization components
        if "authentication" in component_types or "authorization" in component_types:
            # These are high-value targets
            adjusted["damage"] = min(adjusted["damage"] + 1, 10)
            adjusted["affected_users"] = min(adjusted["affected_users"] + 1, 10)

        # Check for database components
        if "database" in component_types:
            # Databases often contain sensitive data
            adjusted["damage"] = min(adjusted["damage"] + 1, 10)
            adjusted["information_disclosure"] = min(adjusted.get("information_disclosure", adjusted["damage"]) + 1, 10)

        return adjusted

    def _calculate_confidence(
        self, matched_patterns: list, scores: Dict[str, int], component_types: list
    ) -> Dict[str, float]:
        """Calculate confidence level for each DREAD score."""
        confidence = {}

        # Base confidence from pattern matches
        if matched_patterns:
            # Average confidence of matched patterns
            avg_pattern_confidence = sum(conf for _, conf, _ in matched_patterns) / len(matched_patterns)
        else:
            avg_pattern_confidence = 0.4  # Lower confidence without pattern matches

        # Component type detection adds confidence
        component_confidence_boost = 0.1 if component_types else 0.0

        base_confidence = min(avg_pattern_confidence + component_confidence_boost, 1.0)

        # Individual score confidence (can vary)
        for key in scores:
            # Higher confidence for scores that align with matched patterns
            if matched_patterns:
                # Check if this score dimension is commonly high in matched patterns
                pattern_scores = [
                    data["suggested_dread"][key]
                    for _, _, data in matched_patterns
                    if "suggested_dread" in data and key in data["suggested_dread"]
                ]
                if pattern_scores:
                    avg_pattern_score = sum(pattern_scores) / len(pattern_scores)
                    score_diff = abs(scores[key] - avg_pattern_score)
                    # Lower difference = higher confidence
                    score_confidence = max(0.0, 1.0 - (score_diff / 10.0))
                    confidence[key] = (base_confidence + score_confidence) / 2.0
                else:
                    confidence[key] = base_confidence
            else:
                confidence[key] = base_confidence

        return confidence

    def _generate_explanations(
        self, scores: Dict[str, int], matched_patterns: list, component_types: list
    ) -> Dict[str, str]:
        """Generate human-readable explanations for each score."""
        explanations = {}

        # Damage explanation
        if scores["damage"] >= 8:
            damage_msg = (
                "High damage potential - could result in significant data loss, "
                "system compromise, or business impact."
            )
            explanations["damage"] = damage_msg
        elif scores["damage"] >= 5:
            explanations["damage"] = "Moderate damage potential - could affect functionality or expose sensitive data."
        else:
            explanations["damage"] = "Low damage potential - limited impact on system or data."

        # Reproducibility explanation
        if scores["reproducibility"] >= 8:
            explanations["reproducibility"] = "Highly reproducible - attack can be reliably triggered."
        elif scores["reproducibility"] >= 5:
            explanations["reproducibility"] = "Moderately reproducible - attack may require specific conditions."
        else:
            explanations["reproducibility"] = "Low reproducibility - attack is difficult to reproduce consistently."

        # Exploitability explanation
        if scores["exploitability"] >= 8:
            explanations["exploitability"] = "Easy to exploit - requires minimal technical skills or tools."
        elif scores["exploitability"] >= 5:
            explanations["exploitability"] = "Moderate exploitability - requires some technical knowledge."
        else:
            explanations["exploitability"] = "Difficult to exploit - requires advanced skills or specific conditions."

        # Affected users explanation
        if scores["affected_users"] >= 8:
            explanations["affected_users"] = "High user impact - affects majority of users or critical user groups."
        elif scores["affected_users"] >= 5:
            explanations["affected_users"] = "Moderate user impact - affects a significant portion of users."
        else:
            explanations["affected_users"] = "Low user impact - affects limited number of users."

        # Discoverability explanation
        if scores["discoverability"] >= 8:
            disc_msg = "Highly discoverable - vulnerability is obvious or well-documented."
            explanations["discoverability"] = disc_msg
        elif scores["discoverability"] >= 5:
            explanations["discoverability"] = "Moderately discoverable - requires some investigation to find."
        else:
            explanations["discoverability"] = (
                "Low discoverability - vulnerability is difficult to find or " "requires deep analysis."
            )

        # Add pattern-based context if available
        if matched_patterns:
            pattern_names = [name for name, _, _ in matched_patterns]
            explanations["pattern_context"] = f'Based on detected threat patterns: {", ".join(pattern_names)}.'

        if component_types:
            explanations["component_context"] = f'Detected component types: {", ".join(component_types)}.'

        return explanations
