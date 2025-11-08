"""Enhanced mitigation recommendations with contextual and prioritized suggestions."""
from typing import List, Dict, Any
from app.services.threat_patterns import THREAT_PATTERNS


class EnhancedMitigationEngine:
    """Enhanced mitigation engine with contextual recommendations."""

    def get_mitigations(
        self,
        stride_categories: List[str],
        risk_level: str,
        threat_pattern: str = None,
        asset_type: str = None,
        component_types: List[str] = None
    ) -> Dict[str, Any]:
        """
        Get enhanced mitigation recommendations.

        Returns:
            Dictionary with prioritized mitigations and metadata
        """
        mitigations = []

        # Pattern-specific mitigations
        if threat_pattern and threat_pattern in THREAT_PATTERNS:
            # Add pattern-specific mitigations first (highest priority)
            mitigations.extend(self._get_pattern_mitigations(threat_pattern, risk_level))

        # STRIDE category mitigations
        for category in stride_categories:
            mitigations.extend(self._get_stride_mitigations(category, risk_level, asset_type, component_types))

        # Asset/component-specific mitigations
        if component_types:
            mitigations.extend(self._get_component_mitigations(component_types, risk_level))

        # Risk-level specific actions
        mitigations.extend(self._get_risk_level_mitigations(risk_level))

        # Prioritize and deduplicate
        prioritized = self._prioritize_mitigations(mitigations, risk_level)

        return {
            'mitigations': prioritized,
            'total_count': len(prioritized),
            'high_priority_count': len([m for m in prioritized if m['priority'] == 'high']),
            'medium_priority_count': len([m for m in prioritized if m['priority'] == 'medium']),
            'low_priority_count': len([m for m in prioritized if m['priority'] == 'low'])
        }

    def _get_pattern_mitigations(self, pattern: str, risk_level: str) -> List[Dict[str, Any]]:
        """Get mitigations specific to threat pattern."""
        pattern_mitigations = {
            'sql_injection': [
                {
                    'text': 'URGENT: Use parameterized queries or prepared statements for all database operations',
                    'priority': 'high',
                    'difficulty': 'easy',
                    'effectiveness': 9
                },
                {
                    'text': 'Implement input validation using whitelist approach',
                    'priority': 'high',
                    'difficulty': 'medium',
                    'effectiveness': 8
                },
                {
                    'text': 'Apply principle of least privilege to database user accounts',
                    'priority': 'medium',
                    'difficulty': 'medium',
                    'effectiveness': 7
                }
            ],
            'xss': [
                {
                    'text': 'Implement output encoding (HTML entity encoding) for all user-generated content',
                    'priority': 'high',
                    'difficulty': 'easy',
                    'effectiveness': 9
                },
                {
                    'text': 'Use Content Security Policy (CSP) headers',
                    'priority': 'high',
                    'difficulty': 'medium',
                    'effectiveness': 8
                },
                {
                    'text': 'Validate and sanitize all user input before rendering',
                    'priority': 'medium',
                    'difficulty': 'medium',
                    'effectiveness': 7
                }
            ],
            'authentication_bypass': [
                {
                    'text': 'CRITICAL: Implement strong authentication mechanisms immediately',
                    'priority': 'high',
                    'difficulty': 'hard',
                    'effectiveness': 10
                },
                {
                    'text': 'Enable multi-factor authentication (MFA) for all users',
                    'priority': 'high',
                    'difficulty': 'medium',
                    'effectiveness': 9
                },
                {
                    'text': 'Use secure password storage (bcrypt, Argon2)',
                    'priority': 'high',
                    'difficulty': 'easy',
                    'effectiveness': 8
                }
            ]
        }

        return pattern_mitigations.get(pattern, [])

    def _get_stride_mitigations(
        self,
        category: str,
        risk_level: str,
        asset_type: str = None,
        component_types: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Get mitigations for STRIDE category."""
        mitigations = []

        base_mitigations = {
            'Spoofing': [
                {
                    'text': 'Implement strong authentication mechanisms (MFA, certificate-based auth)',
                    'priority': 'high',
                    'difficulty': 'medium',
                    'effectiveness': 9
                },
                {
                    'text': 'Use digital signatures for critical communications',
                    'priority': 'medium',
                    'difficulty': 'medium',
                    'effectiveness': 7
                }
            ],
            'Tampering': [
                {
                    'text': 'Use cryptographic signatures and integrity checks',
                    'priority': 'high',
                    'difficulty': 'medium',
                    'effectiveness': 8
                },
                {
                    'text': 'Implement input validation and sanitization',
                    'priority': 'high',
                    'difficulty': 'easy',
                    'effectiveness': 8
                },
                {
                    'text': 'Use HTTPS/TLS for all network communications',
                    'priority': 'medium',
                    'difficulty': 'easy',
                    'effectiveness': 7
                }
            ],
            'Repudiation': [
                {
                    'text': 'Implement comprehensive audit logging',
                    'priority': 'high',
                    'difficulty': 'easy',
                    'effectiveness': 8
                },
                {
                    'text': 'Use digital signatures for critical transactions',
                    'priority': 'medium',
                    'difficulty': 'medium',
                    'effectiveness': 7
                },
                {
                    'text': 'Implement non-repudiation mechanisms',
                    'priority': 'medium',
                    'difficulty': 'hard',
                    'effectiveness': 8
                }
            ],
            'Information Disclosure': [
                {
                    'text': 'Encrypt sensitive data at rest and in transit',
                    'priority': 'high',
                    'difficulty': 'medium',
                    'effectiveness': 9
                },
                {
                    'text': 'Implement proper access controls and least privilege',
                    'priority': 'high',
                    'difficulty': 'medium',
                    'effectiveness': 8
                },
                {
                    'text': 'Use data masking for sensitive information in logs',
                    'priority': 'medium',
                    'difficulty': 'easy',
                    'effectiveness': 6
                }
            ],
            'Denial of Service': [
                {
                    'text': 'Implement rate limiting and resource quotas',
                    'priority': 'high',
                    'difficulty': 'easy',
                    'effectiveness': 8
                },
                {
                    'text': 'Use load balancing and redundancy',
                    'priority': 'medium',
                    'difficulty': 'hard',
                    'effectiveness': 7
                },
                {
                    'text': 'Implement DDoS protection',
                    'priority': 'medium',
                    'difficulty': 'medium',
                    'effectiveness': 8
                }
            ],
            'Elevation of Privilege': [
                {
                    'text': 'Implement principle of least privilege',
                    'priority': 'high',
                    'difficulty': 'medium',
                    'effectiveness': 9
                },
                {
                    'text': 'Use role-based access control (RBAC)',
                    'priority': 'high',
                    'difficulty': 'medium',
                    'effectiveness': 8
                },
                {
                    'text': 'Regular security audits and privilege reviews',
                    'priority': 'medium',
                    'difficulty': 'medium',
                    'effectiveness': 7
                }
            ]
        }

        mitigations.extend(base_mitigations.get(category, []))

        # Adjust priority based on risk level
        if risk_level == 'High':
            for m in mitigations:
                if m['priority'] == 'medium':
                    m['priority'] = 'high'

        return mitigations

    def _get_component_mitigations(self, component_types: List[str], risk_level: str) -> List[Dict[str, Any]]:
        """Get mitigations specific to component types."""
        mitigations = []

        if 'database' in component_types:
            mitigations.append({
                'text': 'Enable database encryption at rest',
                'priority': 'high' if risk_level == 'High' else 'medium',
                'difficulty': 'medium',
                'effectiveness': 8
            })
            mitigations.append({
                'text': 'Implement database access controls and audit logging',
                'priority': 'high',
                'difficulty': 'medium',
                'effectiveness': 8
            })

        if 'api' in component_types:
            mitigations.append({
                'text': 'Implement API rate limiting and throttling',
                'priority': 'high' if risk_level == 'High' else 'medium',
                'difficulty': 'easy',
                'effectiveness': 7
            })
            mitigations.append({
                'text': 'Use API authentication and authorization (OAuth2, API keys)',
                'priority': 'high',
                'difficulty': 'medium',
                'effectiveness': 9
            })

        if 'authentication' in component_types:
            mitigations.append({
                'text': 'Implement account lockout after failed login attempts',
                'priority': 'medium',
                'difficulty': 'easy',
                'effectiveness': 7
            })
            mitigations.append({
                'text': 'Use secure session management with proper expiration',
                'priority': 'high',
                'difficulty': 'medium',
                'effectiveness': 8
            })

        return mitigations

    def _get_risk_level_mitigations(self, risk_level: str) -> List[Dict[str, Any]]:
        """Get risk-level specific mitigation actions."""
        mitigations = []

        if risk_level == 'High':
            mitigations.append({
                'text': 'URGENT: Address immediately. Schedule security review and penetration testing.',
                'priority': 'high',
                'difficulty': 'hard',
                'effectiveness': 10
            })
            mitigations.append({
                'text': 'Implement temporary mitigation measures while permanent fix is developed',
                'priority': 'high',
                'difficulty': 'medium',
                'effectiveness': 6
            })
        elif risk_level == 'Medium':
            mitigations.append({
                'text': 'Address within next sprint. Schedule security review.',
                'priority': 'medium',
                'difficulty': 'medium',
                'effectiveness': 7
            })
        else:
            mitigations.append({
                'text': 'Monitor and address in regular security maintenance.',
                'priority': 'low',
                'difficulty': 'easy',
                'effectiveness': 5
            })

        return mitigations

    def _prioritize_mitigations(self, mitigations: List[Dict[str, Any]], risk_level: str) -> List[Dict[str, Any]]:
        """Prioritize and deduplicate mitigations."""
        # Remove duplicates based on text
        seen = set()
        unique = []
        for m in mitigations:
            text_key = m['text'].lower().strip()
            if text_key not in seen:
                seen.add(text_key)
                unique.append(m)

        # Sort by priority (high > medium > low), then by effectiveness
        priority_order = {'high': 3, 'medium': 2, 'low': 1}
        unique.sort(
            key=lambda x: (
                priority_order.get(x.get('priority', 'low'), 1),
                x.get('effectiveness', 0)
            ),
            reverse=True
        )

        return unique
