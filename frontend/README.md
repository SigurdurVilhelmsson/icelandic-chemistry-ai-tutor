# Efnafræði Aðstoðarkennari - Frontend

React + TypeScript chat interface for the Icelandic Chemistry AI Tutor.

## Features

- 🇮🇸 Full Icelandic language support
- 💬 Real-time chat interface
- 📚 Source citation display
- 💾 Local conversation history
- 📤 CSV export functionality
- 📱 Responsive design (mobile to desktop)
- ♿ Accessible UI with ARIA labels
- 🎨 Tailwind CSS styling

## Tech Stack

- **React 18** - UI library
- **TypeScript 5** - Type safety
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first styling
- **Lucide React** - Icon library
- **date-fns** - Date formatting

## Getting Started

### Prerequisites

- Node.js 18+ and npm

### Installation

```bash
# Install dependencies
npm install

# Copy environment variables
cp .env.example .env

# Update .env with your API endpoint
# VITE_API_ENDPOINT=http://localhost:8000
```

### Development

```bash
# Start development server
npm run dev

# Open http://localhost:5173
```

### Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/       # React components
│   │   ├── ChatInterface.tsx
│   │   ├── Message.tsx
│   │   ├── ChatInput.tsx
│   │   ├── CitationCard.tsx
│   │   ├── ConversationSidebar.tsx
│   │   ├── Toast.tsx
│   │   └── Modal.tsx
│   ├── contexts/         # React context providers
│   │   └── ChatContext.tsx
│   ├── utils/            # Utility functions
│   │   ├── storage.ts    # localStorage management
│   │   ├── export.ts     # CSV export
│   │   └── api.ts        # API client
│   ├── types/            # TypeScript types
│   │   └── index.ts
│   ├── App.tsx           # Main app component
│   ├── main.tsx          # Entry point
│   └── index.css         # Global styles
├── public/               # Static assets
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

## Key Features

### Chat Interface

- Real-time messaging with the AI assistant
- Auto-scroll to latest messages
- Loading indicators
- Error handling with retry logic

### Citations

- Collapsible source information
- Chapter and section references
- Full text preview on demand

### Conversation Management

- Persistent storage in localStorage
- Load previous conversations
- Delete conversations
- Export to CSV

### Responsive Design

- Mobile-first approach
- Breakpoints: 640px (sm), 768px (md), 1024px (lg)
- Collapsible sidebar on mobile
- Touch-friendly UI elements

## API Integration

The frontend communicates with the backend API at the endpoint specified in `.env`:

```typescript
POST /api/chat
{
  "question": "Hvað er atóm?",
  "session_id": "session_123..."
}

Response:
{
  "answer": "Atóm er...",
  "citations": [...],
  "timestamp": "2026-01-15T10:30:00Z"
}
```

## Accessibility

- ARIA labels on all interactive elements
- Keyboard navigation support
- Semantic HTML
- High contrast ratios
- Focus indicators

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## License

MIT
