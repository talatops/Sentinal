# Project Sentinel - Frontend

## Overview
React + Vite frontend application for Project Sentinel DevSecOps framework with advanced threat modeling visualization and cybersecurity-themed UI.

## Technology Stack
- React 19
- Vite 7
- React Router v6
- Zustand (state management)
- Tailwind CSS
- Axios
- Zod (validation)
- Recharts (charts)
- ReactFlow (diagrams)
- Framer Motion (animations)

## Setup

### Prerequisites
- Node.js 20+
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Set environment variables:
```bash
VITE_API_URL=http://localhost/api
```

3. Run development server:
```bash
npm run dev
```

4. Build for production:
```bash
npm run build
```

## Project Structure

```
src/
├── components/      # Reusable UI components
│   ├── ThreatDiagram.jsx      # Interactive data flow visualization
│   ├── ThreatMatrix.jsx       # STRIDE vs Asset heatmap
│   ├── DREADScorer.jsx        # Interactive DREAD scoring component
│   └── ...
├── pages/          # Page components
│   ├── Dashboard.jsx          # Main dashboard
│   ├── ThreatModeling.jsx     # Threat analysis page
│   ├── Requirements.jsx       # Requirements management
│   └── APITokens.jsx          # API token management (Admin)
├── services/       # API services
│   ├── api.js                 # Axios instance with interceptors
│   ├── threatService.js       # Threat modeling API
│   ├── requirementService.js  # Requirements API
│   └── apiTokenService.js     # API token management
├── store/          # Zustand stores
│   └── authStore.js           # Authentication state
├── utils/          # Utility functions
└── hooks/          # Custom React hooks
```

## Features

### Authentication
- JWT-based authentication with GitHub OAuth
- Token refresh mechanism
- Protected routes
- Role-based UI (Admin/Developer)

### Threat Modeling (Advanced)
- **Advanced STRIDE Analysis**: Pattern recognition with confidence scores
- **Automated DREAD Scoring**: AI-powered suggestions with interactive sliders
- **Threat Visualization**: 
  - Interactive data flow diagrams (ReactFlow)
  - STRIDE vs Asset heatmap matrix
  - Threat-vulnerability correlation matrix
- **Threat Templates**: Pre-built templates for common scenarios
- **Threat Similarity**: Find and compare similar threats
- **Vulnerability Linking**: Link threats to actual scan findings
- **Analytics Dashboard**: Threat statistics and trends

### Requirements Management
- Create, read, update, delete requirements
- Link security controls to requirements
- Compliance dashboard (Admin only)
- Export functionality

### CI/CD Dashboard
- Real-time scan results
- SonarQube (SAST) integration
- OWASP ZAP (DAST) integration
- Trivy container scanning
- Scan history and trends

### API Token Management (Admin Only)
- Create API tokens for webhooks
- List and manage tokens
- Revoke tokens
- Scope-based permissions

## UI/UX Features

### Cybersecurity Theme
- Dark mode with cyber blue/green accents
- Storytelling interface with guided onboarding
- Animated transitions (Framer Motion)
- Responsive design
- Accessibility features

### Components

#### ThreatDiagram
Interactive data flow visualization using ReactFlow:
- Component nodes with icons
- Data flow edges
- Trust boundary visualization
- Color-coded by risk level
- Clickable nodes for details

#### ThreatMatrix
STRIDE vs Asset heatmap:
- Visual threat distribution
- Color-coded risk levels
- Filterable and sortable
- Summary statistics

#### DREADScorer
Interactive DREAD scoring component:
- Sliders for each DREAD dimension
- Confidence indicators
- Score explanations
- Manual override support

## Development

### Running Development Server
```bash
npm run dev
```

### Building for Production
```bash
npm run build
```

### Linting
```bash
npm run lint
```

### Formatting
```bash
npm run format
```

## State Management

Using Zustand for global state:
- `authStore`: Authentication state, user profile, tokens
- Persistent storage with localStorage
- Automatic token refresh

## API Integration

### Axios Configuration
- Base URL: `VITE_API_URL`
- Request interceptor: Adds JWT token
- Response interceptor: Handles token refresh
- Error handling: Redirects to login on 401

### Services
- `threatService`: Threat modeling API calls
- `requirementService`: Requirements API calls
- `apiTokenService`: API token management
- `cicdService`: CI/CD dashboard API calls

## Routing

Protected routes require authentication:
- `/` - Dashboard
- `/threats` - Threat Modeling
- `/requirements` - Requirements Management
- `/api-tokens` - API Tokens (Admin only)

Public routes:
- `/login` - Login page
- `/register` - Registration page
- `/callback` - GitHub OAuth callback

## Styling

### Tailwind CSS Configuration
- Custom color palette (cyber-blue, cyber-green, cyber-dark)
- Dark mode by default
- Responsive breakpoints
- Custom animations

### Component Styling
- Card components with glassmorphism effect
- Button variants (primary, secondary, danger)
- Form inputs with validation states
- Modal dialogs
- Toast notifications

## Docker

Build and run with Docker:
```bash
docker build -t sentinal-frontend .
docker run -p 80:80 sentinal-frontend
```

Or use docker-compose from project root:
```bash
docker compose --env-file .docker.env up -d frontend
```

## Environment Variables

- `VITE_API_URL`: Backend API URL (default: `http://localhost/api`)

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## Performance

- Code splitting with Vite
- Lazy loading for routes
- Optimized bundle size
- Image optimization

## Accessibility

- ARIA labels
- Keyboard navigation
- Screen reader support
- Focus management
- Color contrast compliance
