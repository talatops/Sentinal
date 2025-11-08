"""Threat pattern library for advanced STRIDE/DREAD analysis."""

import re
from typing import Dict, List, Tuple, Any


# Threat patterns with regex patterns, STRIDE categories, and suggested DREAD scores
THREAT_PATTERNS = {
    "sql_injection": {
        "patterns": [
            r"sql.*query.*concatenat",
            r"database.*string.*format",
            r"query.*without.*parameter",
            r"raw.*sql.*query",
            r"direct.*sql.*execution",
            r"unsanitized.*sql",
            r"sql.*injection",
            r"execute.*query.*directly",
        ],
        "stride": ["Tampering", "Information Disclosure", "Elevation of Privilege"],
        "suggested_dread": {
            "damage": 9,
            "reproducibility": 8,
            "exploitability": 9,
            "affected_users": 10,
            "discoverability": 7,
        },
        "confidence": 0.9,
        "component_types": ["database", "api", "backend"],
    },
    "xss": {
        "patterns": [
            r"user.*input.*html",
            r"javascript.*inject",
            r"output.*without.*sanitiz",
            r"cross.*site.*scripting",
            r"xss",
            r"render.*user.*content",
            r"innerhtml.*user",
            r"eval.*user.*input",
        ],
        "stride": ["Tampering", "Information Disclosure"],
        "suggested_dread": {
            "damage": 6,
            "reproducibility": 7,
            "exploitability": 6,
            "affected_users": 7,
            "discoverability": 5,
        },
        "confidence": 0.85,
        "component_types": ["frontend", "web", "api"],
    },
    "authentication_bypass": {
        "patterns": [
            r"auth.*bypass",
            r"login.*without.*password",
            r"weak.*authentication",
            r"no.*authentication",
            r"bypass.*auth",
            r"skip.*authentication",
            r"default.*credential",
            r"hardcoded.*password",
        ],
        "stride": ["Spoofing", "Elevation of Privilege"],
        "suggested_dread": {
            "damage": 10,
            "reproducibility": 8,
            "exploitability": 9,
            "affected_users": 10,
            "discoverability": 6,
        },
        "confidence": 0.9,
        "component_types": ["authentication", "api", "backend"],
    },
    "idor": {
        "patterns": [
            r"insecure.*direct.*object.*reference",
            r"idor",
            r"access.*without.*authorization",
            r"direct.*object.*access",
            r"bypass.*authorization",
            r"user.*id.*in.*url",
            r"predictable.*resource.*id",
        ],
        "stride": ["Elevation of Privilege", "Information Disclosure"],
        "suggested_dread": {
            "damage": 8,
            "reproducibility": 9,
            "exploitability": 8,
            "affected_users": 8,
            "discoverability": 7,
        },
        "confidence": 0.85,
        "component_types": ["api", "backend", "authorization"],
    },
    "csrf": {
        "patterns": [
            r"cross.*site.*request.*forgery",
            r"csrf",
            r"no.*csrf.*token",
            r"state.*changing.*request",
            r"form.*without.*token",
            r"post.*request.*no.*validation",
        ],
        "stride": ["Tampering", "Repudiation"],
        "suggested_dread": {
            "damage": 7,
            "reproducibility": 8,
            "exploitability": 7,
            "affected_users": 7,
            "discoverability": 6,
        },
        "confidence": 0.8,
        "component_types": ["web", "frontend", "api"],
    },
    "session_management": {
        "patterns": [
            r"session.*fixation",
            r"weak.*session.*token",
            r"session.*not.*expire",
            r"predictable.*session.*id",
            r"session.*hijack",
            r"insecure.*session.*storage",
        ],
        "stride": ["Spoofing", "Tampering"],
        "suggested_dread": {
            "damage": 8,
            "reproducibility": 7,
            "exploitability": 7,
            "affected_users": 8,
            "discoverability": 6,
        },
        "confidence": 0.85,
        "component_types": ["authentication", "session", "web"],
    },
    "path_traversal": {
        "patterns": [
            r"path.*traversal",
            r"directory.*traversal",
            r"file.*path.*manipulation",
            r"\.\.\/.*file",
            r"unsanitized.*file.*path",
            r"read.*file.*arbitrary",
        ],
        "stride": ["Information Disclosure", "Tampering"],
        "suggested_dread": {
            "damage": 7,
            "reproducibility": 8,
            "exploitability": 7,
            "affected_users": 6,
            "discoverability": 5,
        },
        "confidence": 0.85,
        "component_types": ["file_system", "api", "backend"],
    },
    "command_injection": {
        "patterns": [
            r"command.*injection",
            r"os.*command.*execute",
            r"shell.*command.*user.*input",
            r"system.*call.*unsafe",
            r"exec.*user.*input",
            r"subprocess.*user.*data",
        ],
        "stride": ["Tampering", "Elevation of Privilege", "Denial of Service"],
        "suggested_dread": {
            "damage": 9,
            "reproducibility": 8,
            "exploitability": 7,
            "affected_users": 8,
            "discoverability": 6,
        },
        "confidence": 0.9,
        "component_types": ["backend", "system", "api"],
    },
    "xxe": {
        "patterns": [
            r"xml.*external.*entity",
            r"xxe",
            r"xml.*parse.*unsafe",
            r"external.*entity.*injection",
            r"xml.*bomb",
        ],
        "stride": ["Information Disclosure", "Denial of Service"],
        "suggested_dread": {
            "damage": 7,
            "reproducibility": 7,
            "exploitability": 6,
            "affected_users": 6,
            "discoverability": 5,
        },
        "confidence": 0.8,
        "component_types": ["xml_parser", "api", "backend"],
    },
    "insecure_deserialization": {
        "patterns": [
            r"insecure.*deserializ",
            r"untrusted.*deserializ",
            r"pickle.*unsafe",
            r"yaml.*load.*unsafe",
            r"json.*deserializ.*unsafe",
        ],
        "stride": ["Tampering", "Elevation of Privilege", "Denial of Service"],
        "suggested_dread": {
            "damage": 8,
            "reproducibility": 7,
            "exploitability": 6,
            "affected_users": 7,
            "discoverability": 4,
        },
        "confidence": 0.8,
        "component_types": ["api", "backend", "data_processing"],
    },
    "ssrf": {
        "patterns": [
            r"server.*side.*request.*forgery",
            r"ssrf",
            r"fetch.*url.*user.*input",
            r"request.*arbitrary.*url",
            r"proxy.*user.*url",
        ],
        "stride": ["Tampering", "Information Disclosure", "Denial of Service"],
        "suggested_dread": {
            "damage": 7,
            "reproducibility": 8,
            "exploitability": 7,
            "affected_users": 6,
            "discoverability": 6,
        },
        "confidence": 0.85,
        "component_types": ["api", "backend", "network"],
    },
    "broken_access_control": {
        "patterns": [
            r"broken.*access.*control",
            r"missing.*authorization",
            r"no.*permission.*check",
            r"bypass.*access.*control",
            r"weak.*authorization",
        ],
        "stride": ["Elevation of Privilege", "Information Disclosure"],
        "suggested_dread": {
            "damage": 9,
            "reproducibility": 8,
            "exploitability": 8,
            "affected_users": 9,
            "discoverability": 7,
        },
        "confidence": 0.9,
        "component_types": ["authorization", "api", "backend"],
    },
    "sensitive_data_exposure": {
        "patterns": [
            r"sensitive.*data.*exposure",
            r"password.*plaintext",
            r"credit.*card.*unencrypted",
            r"pii.*unencrypted",
            r"secret.*in.*log",
            r"api.*key.*exposed",
        ],
        "stride": ["Information Disclosure"],
        "suggested_dread": {
            "damage": 9,
            "reproducibility": 10,
            "exploitability": 8,
            "affected_users": 10,
            "discoverability": 8,
        },
        "confidence": 0.9,
        "component_types": ["data_store", "api", "logging"],
    },
    "dos": {
        "patterns": [
            r"denial.*of.*service",
            r"dos",
            r"resource.*exhaustion",
            r"rate.*limit.*missing",
            r"unlimited.*requests",
            r"expensive.*operation.*no.*limit",
        ],
        "stride": ["Denial of Service"],
        "suggested_dread": {
            "damage": 6,
            "reproducibility": 9,
            "exploitability": 8,
            "affected_users": 9,
            "discoverability": 7,
        },
        "confidence": 0.85,
        "component_types": ["api", "backend", "network"],
    },
}


def detect_component_type(asset: str, flow: str) -> List[str]:
    """
    Detect component types from asset and flow descriptions.

    Args:
        asset: Asset name/description
        flow: Data flow description

    Returns:
        List of detected component types
    """
    text = f"{asset} {flow}".lower()
    component_types = []

    # Component type detection patterns
    if any(keyword in text for keyword in ["database", "db", "postgres", "mysql", "mongodb", "sql"]):
        component_types.append("database")

    if any(keyword in text for keyword in ["api", "endpoint", "rest", "graphql", "service"]):
        component_types.append("api")

    if any(keyword in text for keyword in ["auth", "login", "credential", "token", "session"]):
        component_types.append("authentication")

    if any(keyword in text for keyword in ["authorize", "permission", "role", "access control"]):
        component_types.append("authorization")

    if any(keyword in text for keyword in ["frontend", "ui", "web", "browser", "client"]):
        component_types.append("frontend")

    if any(keyword in text for keyword in ["backend", "server", "application"]):
        component_types.append("backend")

    if any(keyword in text for keyword in ["file", "storage", "s3", "blob"]):
        component_types.append("file_system")

    if any(keyword in text for keyword in ["network", "http", "https", "tcp", "udp"]):
        component_types.append("network")

    if any(keyword in text for keyword in ["log", "audit", "monitoring"]):
        component_types.append("logging")

    return component_types if component_types else ["generic"]


def match_threat_patterns(asset: str, flow: str, trust_boundary: str = None) -> List[Tuple[str, float, Dict[str, Any]]]:
    """
    Match threat patterns against asset and flow descriptions.

    Args:
        asset: Asset description
        flow: Data flow description
        trust_boundary: Trust boundary description

    Returns:
        List of tuples: (pattern_name, confidence, pattern_data)
    """
    text = f"{asset} {flow} {trust_boundary or ''}".lower()
    matches = []

    for pattern_name, pattern_data in THREAT_PATTERNS.items():
        confidence = 0.0
        matched_patterns = []

        # Check each regex pattern
        for pattern in pattern_data["patterns"]:
            if re.search(pattern, text, re.IGNORECASE):
                matched_patterns.append(pattern)
                confidence = max(confidence, pattern_data["confidence"])

        # Boost confidence if component types match
        component_types = detect_component_type(asset, flow)
        if any(ct in pattern_data.get("component_types", []) for ct in component_types):
            confidence = min(confidence + 0.1, 1.0)

        if matched_patterns:
            matches.append((pattern_name, confidence, pattern_data))

    # Sort by confidence (highest first)
    matches.sort(key=lambda x: x[1], reverse=True)
    return matches


def get_stride_from_patterns(matched_patterns: List[Tuple[str, float, Dict[str, Any]]]) -> List[str]:
    """
    Extract STRIDE categories from matched threat patterns.

    Args:
        matched_patterns: List of matched patterns

    Returns:
        List of unique STRIDE categories
    """
    stride_categories = set()
    for _, _, pattern_data in matched_patterns:
        stride_categories.update(pattern_data["stride"])
    return list(stride_categories)


def get_suggested_dread_from_patterns(matched_patterns: List[Tuple[str, float, Dict[str, Any]]]) -> Dict[str, int]:
    """
    Get suggested DREAD scores from matched patterns (weighted average).

    Args:
        matched_patterns: List of matched patterns with confidence

    Returns:
        Dictionary with suggested DREAD scores
    """
    if not matched_patterns:
        return {"damage": 5, "reproducibility": 5, "exploitability": 5, "affected_users": 5, "discoverability": 5}

    # Weighted average based on confidence
    total_weight = sum(conf for _, conf, _ in matched_patterns)
    if total_weight == 0:
        total_weight = 1

    suggested = {"damage": 0, "reproducibility": 0, "exploitability": 0, "affected_users": 0, "discoverability": 0}

    for _, confidence, pattern_data in matched_patterns:
        weight = confidence / total_weight
        dread = pattern_data["suggested_dread"]
        for key in suggested:
            suggested[key] += dread[key] * weight

    # Round to integers
    return {key: int(round(value)) for key, value in suggested.items()}
