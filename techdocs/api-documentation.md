# Project Sentinel - API Documentation

## Base URL
```
http://localhost/api
```

## Authentication

Most endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <access_token>
```

## Endpoints

### Authentication

#### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "string",
  "email": "string",
  "password": "string",
  "role": "Admin" | "Developer"
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "string",
  "password": "string"
}

Response:
{
  "access_token": "string",
  "refresh_token": "string",
  "user": { ... }
}
```

#### GitHub OAuth Initiation
```http
GET /api/auth/github

Response:
{
  "auth_url": "string"
}
```

#### GitHub OAuth Callback
```http
GET /api/auth/github/callback?code=<code>
```

#### Refresh Token
```http
POST /api/auth/refresh
Authorization: Bearer <refresh_token>

Response:
{
  "access_token": "string"
}
```

#### Get User Profile
```http
GET /api/auth/profile
Authorization: Bearer <access_token>
```

### Threat Modeling

#### Analyze Threat
```http
POST /api/threats/analyze
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "asset": "string",
  "flow": "string",
  "trust_boundary": "string",
  "damage": 0-10,
  "reproducibility": 0-10,
  "exploitability": 0-10,
  "affected_users": 0-10,
  "discoverability": 0-10
}

Response:
{
  "threat": { ... },
  "analysis": {
    "stride_categories": ["string"],
    "dread_score": number,
    "risk_level": "High" | "Medium" | "Low",
    "mitigation": "string"
  }
}
```

#### List Threats
```http
GET /api/threats
Authorization: Bearer <access_token>
```

#### Get Threat Details
```http
GET /api/threats/{id}
Authorization: Bearer <access_token>
```

#### Update Threat
```http
PUT /api/threats/{id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "mitigation": "string",
  "risk_level": "High" | "Medium" | "Low"
}
```

#### Delete Threat
```http
DELETE /api/threats/{id}
Authorization: Bearer <access_token>
```

### Requirements Management

#### List Requirements
```http
GET /api/requirements
Authorization: Bearer <access_token>
```

#### Create Requirement
```http
POST /api/requirements
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "string",
  "description": "string",
  "security_controls": [
    {
      "name": "string",
      "description": "string",
      "owasp_asvs_level": "Level 1" | "Level 2" | "Level 3"
    }
  ],
  "status": "Draft" | "Review" | "Approved" | "Implemented",
  "owasp_asvs_level": "Level 1" | "Level 2" | "Level 3"
}
```

#### Get Requirement Details
```http
GET /api/requirements/{id}
Authorization: Bearer <access_token>
```

#### Update Requirement
```http
PUT /api/requirements/{id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "string",
  "description": "string",
  "status": "string",
  "owasp_asvs_level": "string"
}
```

#### Delete Requirement
```http
DELETE /api/requirements/{id}
Authorization: Bearer <access_token>
```

#### Get Security Controls
```http
GET /api/requirements/{id}/controls
Authorization: Bearer <access_token>
```

#### Add Security Control
```http
POST /api/requirements/{id}/controls
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "string",
  "description": "string",
  "owasp_asvs_level": "string"
}
```

#### Export Requirements
```http
GET /api/requirements/export?format=json|csv
Authorization: Bearer <access_token>
```

#### Compliance Dashboard (Admin Only)
```http
GET /api/requirements/compliance
Authorization: Bearer <access_token>
```

### CI/CD Dashboard

#### List CI/CD Runs
```http
GET /api/cicd/runs?limit=50
Authorization: Bearer <access_token>
```

#### Get Run Details
```http
GET /api/cicd/runs/{id}
Authorization: Bearer <access_token>
```

#### Trigger CI/CD Run
```http
POST /api/cicd/trigger
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "commit_hash": "string",
  "branch": "string"
}
```

#### Get Dashboard Statistics
```http
GET /api/cicd/dashboard
Authorization: Bearer <access_token>

Response:
{
  "total_runs": number,
  "successful_runs": number,
  "failed_runs": number,
  "blocked_runs": number,
  "success_rate": number,
  "recent_runs": [...],
  "vulnerability_trend": [...]
}
```

## Error Responses

All errors follow this format:
```json
{
  "error": "Error message",
  "errors": {
    "field": "Field-specific error"
  }
}
```

### Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error

## Rate Limiting

- Registration: 5 requests per minute
- Login: 10 requests per minute
- Other endpoints: Configurable per endpoint

