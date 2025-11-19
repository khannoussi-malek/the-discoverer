# The Discoverer Frontend

A modern React TypeScript frontend for The Discoverer API, built with Vite, shadcn/ui, and React Query.

## Features

- 🎨 Modern UI with shadcn/ui components
- 📊 Interactive charts with Recharts
- 🔍 Natural language query execution
- 💾 Database management
- 📈 Analytics and insights
- 📅 Scheduled queries
- 🎯 Query templates
- 📱 Responsive design

## Getting Started

### Prerequisites

- Node.js 18+ and npm

### Installation

1. Install dependencies:
```bash
npm install
```

2. Configure environment variables:
```bash
cp .env.example .env
```

Edit `.env` and set:
- `VITE_API_BASE_URL` - Your API base URL (default: http://localhost:8000)
- `VITE_API_KEY` - Optional API key for authentication
- `VITE_APP_NAME` - Application name
- `VITE_ENABLE_ANALYTICS` - Enable analytics (true/false)

3. Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:5173`

## Project Structure

```
frontend/
├── src/
│   ├── api/              # API client and services
│   ├── components/       # React components
│   │   ├── ui/          # shadcn/ui components
│   │   ├── layout/      # Layout components
│   │   ├── dashboard/   # Dashboard page
│   │   ├── databases/   # Database management
│   │   ├── query/       # Query execution
│   │   ├── visualization/ # Chart components
│   │   └── shared/      # Shared components
│   ├── config/          # Configuration
│   ├── hooks/           # Custom React hooks
│   ├── lib/             # Utilities
│   ├── types/           # TypeScript types
│   └── App.tsx          # Main app component
├── .env                 # Environment variables
└── package.json
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Technologies

- **React 19** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **shadcn/ui** - UI components
- **Tailwind CSS** - Styling
- **React Query** - Data fetching
- **React Router** - Routing
- **Recharts** - Charts
- **Axios** - HTTP client
- **Zod** - Schema validation

## API Integration

The frontend communicates with the FastAPI backend through REST APIs. All API services are located in `src/api/services/`.

## Environment Variables

All sensitive configuration should be stored in `.env` file:

- `VITE_API_BASE_URL` - Backend API URL
- `VITE_API_KEY` - API key for authentication
- `VITE_APP_NAME` - Application name
- `VITE_ENABLE_ANALYTICS` - Analytics toggle

## Building for Production

```bash
npm run build
```

The production build will be in the `dist/` directory.

## License

MIT
