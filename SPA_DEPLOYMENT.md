# SPA (Single Page Application) Deployment Guide

This guide explains how to properly deploy the Waves Quant Engine React app with SPA routing support.

## 🚀 Quick Start

### Development
```powershell
# Start development server with SPA routing
.\dev-server.ps1
```

### Production Build
```powershell
# Build for production with SPA configuration
.\deploy.ps1
```

## 📁 Files Created/Modified

### Frontend Configuration
- `vite.config.ts` - Updated with SPA fallback for development
- `public/_redirects` - Netlify/Vercel redirects for production
- `public/.htaccess` - Apache server configuration
- `nginx.conf` - Nginx server configuration template

### Backend Integration
- `waves_quant_agi/backend-main/spa_handler.py` - Python SPA handler for FastAPI
- `waves_quant_agi/backend-main/app.py` - Updated to include SPA handler

### Deployment Scripts
- `deploy.ps1` - Production build and deployment preparation
- `dev-server.ps1` - Development server with SPA routing

## 🔧 How SPA Routing Works

### The Problem
When you visit `http://localhost:5173/about` directly:
1. Browser requests `/about` from server
2. Server looks for a file called `about` 
3. Server returns 404 (file not found)
4. React Router never gets a chance to handle the route

### The Solution
Configure the server to serve `index.html` for all unknown routes, letting React Router handle client-side routing.

## 🌐 Deployment Options

### 1. Development (Vite Dev Server)
- ✅ **Already configured** in `vite.config.ts`
- SPA fallback enabled with `historyApiFallback: true`
- Direct URL access works out of the box

### 2. Netlify/Vercel
- ✅ **Already configured** with `public/_redirects`
- Upload the `dist` folder to your hosting platform
- Routes like `/about`, `/contact`, `/terms` will work directly

### 3. Apache Server
- ✅ **Already configured** with `public/.htaccess`
- Upload contents of `dist` folder to your web server
- Ensure Apache has `mod_rewrite` enabled

### 4. Nginx Server
- ✅ **Template provided** in `nginx.conf`
- Copy the configuration to your server
- Update `server_name` and `root` paths
- Restart Nginx

### 5. Python Backend (FastAPI)
- ✅ **Already configured** with SPA handler
- Backend will serve React app automatically
- Build frontend and place in `dist` folder relative to backend

## 🧪 Testing SPA Routing

### Development Testing
1. Start dev server: `.\dev-server.ps1`
2. Try these direct URLs:
   - `http://localhost:5173/about`
   - `http://localhost:5173/contact`
   - `http://localhost:5173/terms`
   - `http://localhost:5173/investor-dashboard` (should redirect to auth)

### Production Testing
1. Build the app: `.\deploy.ps1`
2. Deploy to your chosen platform
3. Test direct URL access on your domain

## 🔍 Troubleshooting

### Development Issues
- **Routes still not working**: Check that `vite.config.ts` has `historyApiFallback: true`
- **Port conflicts**: Change port in `vite.config.ts` if 5173 is busy

### Production Issues
- **Netlify/Vercel**: Ensure `_redirects` file is in the root of your deployment
- **Apache**: Check that `mod_rewrite` is enabled: `a2enmod rewrite`
- **Nginx**: Verify configuration syntax: `nginx -t`
- **Python Backend**: Ensure `dist` folder exists relative to backend

### Common Error Messages
- **404 on direct access**: SPA fallback not configured
- **500 server error**: Check server configuration syntax
- **Blank page**: JavaScript errors or missing build files

## 📋 File Structure After Deployment

```
dist/
├── index.html          # Main HTML file
├── static/             # Built JavaScript/CSS
├── _redirects          # Netlify/Vercel (copied from public/)
├── .htaccess          # Apache (copied from public/)
└── nginx.conf         # Nginx template (copied from root)
```

## 🚀 Advanced Configuration

### Custom Base Path
If deploying to a subdirectory (e.g., `https://example.com/app/`):

1. Update `vite.config.ts`:
```typescript
export default defineConfig({
  base: '/app/',
  // ... rest of config
})
```

2. Update `public/_redirects`:
```
/app/*    /app/index.html   200
```

### Environment Variables
Ensure your `.env` file has:
```env
VITE_SUPABASE_URL=your-supabase-url
VITE_SUPABASE_ANON_KEY=your-supabase-anon-key
```

## ✅ Verification Checklist

- [ ] Development server handles direct URL access
- [ ] Production build completes successfully
- [ ] Deployment files are copied to `dist/`
- [ ] Server configuration is applied
- [ ] Direct URL access works in production
- [ ] Authentication redirects work correctly
- [ ] Static assets load properly

## 🆘 Need Help?

If you're still experiencing routing issues:

1. **Check browser console** for JavaScript errors
2. **Check server logs** for configuration errors
3. **Verify file paths** in your deployment
4. **Test with a simple route** like `/about` first

The SPA configuration should now work for both development and production environments! 