"""STRIDE/DREAD threat analysis engine."""
from typing import List, Dict, Any
from app.services.threat_patterns import (
    match_threat_patterns,
    detect_component_type,
    get_stride_from_patterns
)


class STRIDEEngine:
    """Engine for STRIDE threat modeling."""

    # STRIDE mapping rules
    STRIDE_MAP = {
        'Data Flow Crossing Boundary': ['Tampering', 'Information Disclosure'],
        'Authentication Component': ['Spoofing', 'Elevation of Privilege'],
        'Authorization Component': ['Elevation of Privilege'],
        'Data Store': ['Tampering', 'Information Disclosure', 'Denial of Service'],
        'External Entity': ['Spoofing', 'Repudiation'],
        'Process Component': ['Tampering', 'Denial of Service'],
        'Network Communication': ['Tampering', 'Information Disclosure', 'Denial of Service']
    }

    def analyze_threat(self, asset: str, flow: str, trust_boundary: str = None) -> List[str]:
        """
        Analyze threat and return STRIDE categories.

        Args:
            asset: The asset being protected
            flow: Description of data flow
            trust_boundary: Trust boundary description

        Returns:
            List of STRIDE categories
        """
        categories = set()

        # Analyze based on keywords in flow
        flow_lower = flow.lower()

        # Check for authentication
        if any(keyword in flow_lower for keyword in ['auth', 'login', 'credential', 'password', 'token']):
            categories.add('Spoofing')
            categories.add('Elevation of Privilege')

        # Check for data crossing boundaries
        if trust_boundary or 'boundary' in flow_lower or 'cross' in flow_lower:
            categories.add('Tampering')
            categories.add('Information Disclosure')

        # Check for data storage
        if any(keyword in flow_lower for keyword in ['store', 'database', 'file', 'save']):
            categories.add('Tampering')
            categories.add('Information Disclosure')
            categories.add('Denial of Service')

        # Check for external entities
        if any(keyword in flow_lower for keyword in ['external', 'third-party', 'api', 'service']):
            categories.add('Spoofing')
            categories.add('Repudiation')

        # Check for network communication
        if any(keyword in flow_lower for keyword in ['network', 'http', 'https', 'tcp', 'udp', 'send', 'receive']):
            categories.add('Tampering')
            categories.add('Information Disclosure')
            categories.add('Denial of Service')

        # Check for logging/audit
        if any(keyword in flow_lower for keyword in ['log', 'audit', 'record']):
            categories.add('Repudiation')

        # If no categories found, apply default based on component type
        if not categories:
            if trust_boundary:
                categories.update(self.STRIDE_MAP.get('Data Flow Crossing Boundary', []))
            else:
                categories.update(['Tampering', 'Information Disclosure'])

        return list(categories)

    def analyze_threat_advanced(self, asset: str, flow: str, trust_boundary: str = None) -> Dict[str, Any]:
        """
        Advanced threat analysis using pattern matching and component detection.

        Args:
            asset: The asset being protected
            flow: Description of data flow
            trust_boundary: Trust boundary description

        Returns:
            Dictionary with STRIDE categories, confidence scores, matched patterns, and component types
        """
        # Detect component types
        component_types = detect_component_type(asset, flow)

        # Match threat patterns
        matched_patterns = match_threat_patterns(asset, flow, trust_boundary)

        # Get STRIDE categories from patterns
        stride_categories = get_stride_from_patterns(matched_patterns)

        # If no patterns matched, fall back to basic analysis
        if not stride_categories:
            stride_categories = self.analyze_threat(asset, flow, trust_boundary)
            matched_patterns = []

        # Calculate confidence scores for each STRIDE category
        stride_confidence = {}
        for category in stride_categories:
            # Confidence based on pattern matches
            if matched_patterns:
                # Average confidence of patterns that include this STRIDE category
                relevant_patterns = [
                    conf for _, conf, data in matched_patterns
                    if category in data['stride']
                ]
                if relevant_patterns:
                    stride_confidence[category] = sum(relevant_patterns) / len(relevant_patterns)
                else:
                    stride_confidence[category] = 0.5  # Default confidence
            else:
                stride_confidence[category] = 0.5  # Basic analysis confidence

        # Get the primary matched pattern (highest confidence)
        primary_pattern = matched_patterns[0][0] if matched_patterns else None
        pattern_confidence = matched_patterns[0][1] if matched_patterns else 0.0

        return {
            'stride_categories': stride_categories,
            'stride_confidence': stride_confidence,
            'component_types': component_types,
            'matched_patterns': [name for name, _, _ in matched_patterns],
            'primary_pattern': primary_pattern,
            'pattern_confidence': pattern_confidence
        }

    def calculate_dread_score(
        self,
        damage: int,
        reproducibility: int,
        exploitability: int,
        affected_users: int,
        discoverability: int
    ) -> Dict[str, Any]:
        """
        Calculate DREAD score.

        Args:
            damage: Damage potential (0-10)
            reproducibility: Reproducibility (0-10)
            exploitability: Exploitability (0-10)
            affected_users: Affected users (0-10)
            discoverability: Discoverability (0-10)

        Returns:
            Dictionary with DREAD scores and risk level
        """
        total_score = (damage + reproducibility + exploitability + affected_users + discoverability) / 5.0

        if total_score > 7:
            risk_level = 'High'
        elif total_score > 4:
            risk_level = 'Medium'
        else:
            risk_level = 'Low'

        return {
            'damage': damage,
            'reproducibility': reproducibility,
            'exploitability': exploitability,
            'affected_users': affected_users,
            'discoverability': discoverability,
            'total_score': round(total_score, 2),
            'risk_level': risk_level
        }

    def get_mitigation_recommendations(self, stride_categories: List[str], risk_level: str) -> str:
        """
        Get mitigation recommendations based on STRIDE categories and risk level.

        Args:
            stride_categories: List of STRIDE categories
            risk_level: Risk level (High, Medium, Low)

        Returns:
            Mitigation recommendations string
        """
        # Use enhanced mitigation engine if available
        try:
            from app.services.enhanced_mitigations import EnhancedMitigationEngine
            engine = EnhancedMitigationEngine()
            mitigations_data = engine.get_mitigations(
                stride_categories,
                risk_level
            )
            # Format as string for backward compatibility
            mitigation_lines = [m['text'] for m in mitigations_data['mitigations']]
            return '\n'.join(mitigation_lines) if mitigation_lines else 'No specific mitigations identified.'
        except ImportError:
            # Fallback to basic mitigations
            pass

        mitigations = []

        if 'Spoofing' in stride_categories:
            mitigations.append('Implement strong authentication mechanisms (MFA, certificate-based auth)')

        if 'Tampering' in stride_categories:
            mitigations.append('Use cryptographic signatures and integrity checks')
            mitigations.append('Implement input validation and sanitization')

        if 'Repudiation' in stride_categories:
            mitigations.append('Implement comprehensive audit logging')
            mitigations.append('Use digital signatures for critical transactions')

        if 'Information Disclosure' in stride_categories:
            mitigations.append('Encrypt sensitive data at rest and in transit')
            mitigations.append('Implement proper access controls and least privilege')

        if 'Denial of Service' in stride_categories:
            mitigations.append('Implement rate limiting and resource quotas')
            mitigations.append('Use load balancing and redundancy')

        if 'Elevation of Privilege' in stride_categories:
            mitigations.append('Implement principle of least privilege')
            mitigations.append('Use role-based access control (RBAC)')
            mitigations.append('Regular security audits and privilege reviews')

        # Add risk-level specific recommendations
        if risk_level == 'High':
            mitigations.append('URGENT: Address immediately. Consider security review and penetration testing.')
        elif risk_level == 'Medium':
            mitigations.append('Address within next sprint. Schedule security review.')
        else:
            mitigations.append('Monitor and address in regular security maintenance.')

        return '\n'.join(mitigations) if mitigations else 'No specific mitigations identified.'
