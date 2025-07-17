
# Waves Quant Engine Frontend Guide

## Overview
The frontend is built with React, TypeScript, and Tailwind CSS, providing a responsive and intuitive interface for both investors and platform owners.

## Architecture

### Technology Stack
- **React 18** - Modern UI framework
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **Shadcn/UI** - Component library
- **React Router** - Client-side routing
- **Supabase** - Backend integration
- **React Query** - Server state management
- **Zustand/Redux** - Client state management

### Project Structure
```
src/
├── components/          # Reusable UI components
│   ├── ui/             # Base UI components (buttons, cards, etc.)
│   ├── common/         # Common components (ErrorBoundary, etc.)
│   ├── investor/       # Investor-specific components
│   └── trading/        # Trading-related components
├── pages/              # Page components
├── hooks/              # Custom React hooks
├── services/           # API service layers
├── contexts/           # React contexts
├── integrations/       # Third-party integrations
└── lib/                # Utility functions
```

## Key Features

### Responsive Design
- Mobile-first approach
- Breakpoint-based layouts
- Touch-friendly interactions
- Optimized for all screen sizes

### Authentication System
- Supabase Auth integration
- Role-based access control (Owner/Investor)
- Automatic redirects based on user role
- Session management

### Real-time Updates
- Live trading data
- Real-time portfolio updates
- WebSocket connections for market data
- Push notifications

### Performance Optimizations
- Lazy loading for routes and components
- Image optimization
- Bundle splitting
- Memoization for expensive calculations

## Component Architecture

### Base Components
Located in `src/components/ui/`, these are styled with Tailwind CSS and follow the Shadcn/UI design system:
- Buttons, Cards, Forms
- Data display components
- Navigation components
- Feedback components (toasts, alerts)

### Feature Components
Organized by domain:
- **Investor Components**: Dashboard, portfolio, payments
- **Trading Components**: Charts, signals, trade history
- **Common Components**: Error boundaries, loading states

### Page Components
Each page is a complete view with:
- Layout management
- Data fetching
- Error handling
- Loading states

## State Management

### Client State (Redux/Zustand)
- UI state (modals, forms, preferences)
- Temporary data
- User interactions

### Server State (React Query)
- API data caching
- Optimistic updates
- Background refetching
- Error retry logic

## Routing Structure

```
/                    # Landing page
/auth               # Authentication
/investor-dashboard # Investor dashboard
/owner-dashboard    # Owner dashboard
/about              # About page
/contact            # Contact page
/terms              # Terms of service
```

### Protected Routes
- Automatic authentication checks
- Role-based access control
- Redirect to appropriate dashboard

## API Integration

- All portfolio, transaction, trade history, and analytics features now use backend API endpoints (see API_REFERENCE.md).
- Direct Supabase queries are deprecated for these features.
- The frontend sends the Supabase JWT access token in the Authorization header for all API calls.
- The useAuth hook now includes automatic session refresh logic to keep the JWT valid.

### Trade History Example

To fetch trade history:
```js
const trades = await apiService.getTrades();
```

### Service Layer
All API calls are abstracted through service functions:
```typescript
// services/api.ts
export const apiService = {
  async getBalance(userId: string) {
    // Implementation
  }
};
```

### Error Handling
- Global error boundaries
- Automatic error reporting
- User-friendly error messages
- Fallback UI components

## Styling Guidelines

### Tailwind CSS Classes
- Use utility classes for styling
- Follow consistent spacing scale
- Use design tokens for colors
- Responsive design with breakpoint prefixes

### Dark Mode Support
- CSS custom properties for theming
- Toggle component for theme switching
- Consistent color schemes

### Component Styling
```typescript
// Example component with Tailwind
const Button = ({ children, variant = "primary" }) => (
  <button 
    className={cn(
      "px-4 py-2 rounded-lg font-medium transition-colors",
      variant === "primary" && "bg-blue-600 text-white hover:bg-blue-700",
      variant === "secondary" && "bg-gray-200 text-gray-900 hover:bg-gray-300"
    )}
  >
    {children}
  </button>
);
```

## Performance Best Practices

### Code Splitting
```typescript
// Lazy loading for better performance
const DashboardOverview = lazy(() => import("@/components/investor/DashboardOverview"));
```

### Memoization
```typescript
// Prevent unnecessary re-renders
const ExpensiveComponent = memo(({ data }) => {
  const processedData = useMemo(() => processData(data), [data]);
  return <div>{processedData}</div>;
});
```

### Bundle Optimization
- Tree shaking for unused code
- Dynamic imports for large libraries
- Image optimization and lazy loading

## Testing Strategy

### Unit Tests
- Component rendering tests
- Hook functionality tests
- Utility function tests

### Integration Tests
- User flow testing
- API integration testing
- Authentication flow testing

### E2E Tests
- Critical user journeys
- Cross-browser compatibility
- Mobile responsiveness

## Development Workflow

### Getting Started
```bash
npm install
npm run dev
```

### Environment Setup
```env
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_anon_key
```

### Code Quality
- ESLint for code linting
- Prettier for code formatting
- TypeScript for type checking
- Husky for pre-commit hooks

## Deployment

### Build Process
```bash
npm run build
npm run preview
```

### Production Optimizations
- Minification and compression
- Static asset optimization
- Service worker for caching
- CDN integration

## Security Considerations

### Authentication
- Secure token storage
- Automatic session refresh
- Role-based route protection

### Data Protection
- Input sanitization
- XSS prevention
- CSRF protection
- Secure API communication

## Browser Support
- Modern browsers (Chrome, Firefox, Safari, Edge)
- Mobile browsers (iOS Safari, Chrome Mobile)
- Progressive enhancement for older browsers

## Accessibility
- WCAG 2.1 compliance
- Keyboard navigation support
- Screen reader compatibility
- High contrast mode support

## Support & Maintenance
For frontend issues and feature requests, contact: adus7661@gmail.com
