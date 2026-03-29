# Production Deployment & Security Checklist

## 🚀 Pre-Deployment Checklist

### Code Quality
- [ ] No hardcoded API URLs (using `import.meta.env.VITE_API_BASE_URL`)
- [ ] No sensitive data in code (API keys, passwords)
- [ ] No console.log() statements in production code
- [ ] No TODO comments without issues
- [ ] Unused imports removed
- [ ] No `any` types in TypeScript (if using TS)
- [ ] Error boundaries implemented
- [ ] Loading states on all async operations
- [ ] No memory leaks (useEffect cleanup functions)

### Performance
- [ ] Images optimized and lazy-loaded
- [ ] Code splitting for large components
- [ ] No infinite loops or recursive renders
- [ ] Memoization used for expensive computations
- [ ] No unnecessary re-renders
- [ ] CSS is minified in production build
- [ ] Bundle size < 500KB (JS + CSS)

### Security
- [ ] HTTPS enforced in production
- [ ] No API key exposure in client-side code
- [ ] CORS configured correctly on backend
- [ ] Input validation on all forms
- [ ] XSS protection (React escapes by default)
- [ ] CSRF tokens included in requests (if needed)
- [ ] Sensitive operations require re-authentication
- [ ] Password fields masked
- [ ] Session tokens stored securely (httpOnly cookies preferred)

### Mobile Responsiveness
- [ ] Tested on iPhone 12, 13, 14
- [ ] Tested on Android phones (various sizes)
- [ ] Tested on tablets (iPad, Samsung Tab)
- [ ] Touch targets are 48px minimum
- [ ] Mobile menu works correctly
- [ ] No horizontal scrolling
- [ ] Viewport meta tag set correctly

### Accessibility (a11y)
- [ ] Color contrast meets WCAG AA (4.5:1 minimum)
- [ ] Alt text on all images
- [ ] Form labels properly associated
- [ ] Keyboard navigation works
- [ ] ARIA labels where needed
- [ ] Focus indicators visible

### Testing
- [ ] Unit tests passing (if implemented)
- [ ] E2E tests passing (if implemented)
- [ ] Manual testing checklist completed
- [ ] Cross-browser testing (Chrome, Firefox, Safari)
- [ ] Network throttling tested (slow 3G)

### Documentation
- [ ] README.md updated with setup instructions
- [ ] Environment variables documented
- [ ] API endpoints documented
- [ ] Deployment instructions provided
- [ ] Troubleshooting guide included

---

## 📋 Environment Configuration

### Development (.env)
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_SOCKET_URL=http://localhost:8000
VITE_ENVIRONMENT=development
VITE_APP_NAME=Pharma AI
VITE_AUTH_TIMEOUT=3600
VITE_ENABLE_ANALYTICS=false
VITE_LOG_LEVEL=debug
```

### Staging (.env.staging)
```env
VITE_API_BASE_URL=https://api-staging.pharmaai.com
VITE_SOCKET_URL=https://api-staging.pharmaai.com
VITE_ENVIRONMENT=staging
VITE_APP_NAME=Pharma AI (Staging)
VITE_AUTH_TIMEOUT=3600
VITE_ENABLE_ANALYTICS=true
VITE_LOG_LEVEL=warn
```

### Production (.env.production)
```env
VITE_API_BASE_URL=https://api.pharmaai.com
VITE_SOCKET_URL=https://api.pharmaai.com
VITE_ENVIRONMENT=production
VITE_APP_NAME=Pharma AI
VITE_AUTH_TIMEOUT=1800
VITE_ENABLE_ANALYTICS=true
VITE_LOG_LEVEL=error
VITE_SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
```

---

## 🌐 Deployment Platforms

### Option 1: Vercel (Easiest for Vite)

**Setup:**
1. Push code to GitHub
2. Connect GitHub to Vercel
3. Add environment variables in Vercel dashboard
4. Set build command: `npm run build`
5. Set output directory: `dist`

**Deploy:**
```bash
npm run build
npx vercel deploy
# Or push to main branch - auto-deploys
```

**Pros:**
- ✅ Zero-config deployment
- ✅ Automatic HTTPS
- ✅ Global CDN
- ✅ Preview deployments
- ✅ Free tier available

**Cost:** Free (up to 100GB bandwidth/month)

---

### Option 2: Netlify

**Setup:**
1. Connect GitHub to Netlify
2. Configure build settings:
   - Build command: `npm run build`
   - Publish directory: `dist`
3. Add environment variables
4. Deploy

**Deploy:**
```bash
npm run build
npm install netlify-cli
npx netlify deploy --prod --dir=dist
```

**Pros:**
- ✅ Easy GitHub integration
- ✅ Built-in SSL
- ✅ Free tier generous
- ✅ Environment variables UI

**Cost:** Free (up to 100GB bandwidth/month)

---

### Option 3: Docker + Cloud Run/App Engine

**Dockerfile:**
```dockerfile
# Build stage
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
ARG VITE_API_URL=https://api.pharmaai.com
ARG VITE_SOCKET_URL=https://api.pharmaai.com
ENV VITE_API_BASE_URL=${VITE_API_URL}
ENV VITE_SOCKET_URL=${VITE_SOCKET_URL}
RUN npm run build

# Production stage
FROM node:18-alpine
WORKDIR /app
RUN npm install -g http-server
COPY --from=builder /app/dist ./dist
EXPOSE 3000
CMD ["http-server", "dist", "-p", "3000"]
```

**Deploy to Google Cloud Run:**
```bash
# Build Docker image
docker build \
  --build-arg VITE_API_URL=https://api.pharmaai.com \
  --build-arg VITE_SOCKET_URL=https://api.pharmaai.com \
  -t pharmaai-frontend .

# Tag for Google Cloud
docker tag pharmaai-frontend gcr.io/PROJECT-ID/pharmaai-frontend

# Push to Google Container Registry
docker push gcr.io/PROJECT-ID/pharmaai-frontend

# Deploy to Cloud Run
gcloud run deploy pharmaai-frontend \
  --image gcr.io/PROJECT-ID/pharmaai-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

**Pros:**
- ✅ Full control over environment
- ✅ Easy to integrate with backend
- ✅ Can optimize build process
- ✅ Works anywhere

**Cost:** ~$2-5/month (Google Cloud Free Tier)

---

### Option 4: AWS (S3 + CloudFront)

**Setup:**
```bash
# 1. Build the application
npm run build

# 2. Create S3 bucket
aws s3 mb s3://pharmaai-frontend

# 3. Upload build files
aws s3 sync dist/ s3://pharmaai-frontend --delete

# 4. Create CloudFront distribution (point to S3)
# Done through AWS console
```

**Pros:**
- ✅ Highly scalable
- ✅ Global CDN (CloudFront)
- ✅ Enterprise-grade security
- ✅ Integration with AWS services

**Cost:** $0.50-2/month (S3 + CloudFront)

---

## 🔧 Production Build Optimization

### Step 1: Build and Analyze
```bash
npm run build

# Check file sizes
npm install -D vite-plugin-visualizer
```

### Step 2: Update vite.config.js
```javascript
export default {
  build: {
    // Optimize chunks
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom'],
          'ui-vendor': ['lucide-react'],
          'map-vendor': ['leaflet'],
          'http-vendor': ['axios'],
        }
      }
    },
    // Compress assets
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
      },
    },
    // Chunk size warnings
    chunkSizeWarningLimit: 500,
  },
  // Use compression
  plugins: [
    // ... your plugins
  ]
}
```

### Step 3: Enable Compression
```bash
npm install -D vite-plugin-compression
```

In vite.config.js:
```javascript
import compression from 'vite-plugin-compression'

export default {
  plugins: [
    compression({
      algorithm: 'gzip',
      ext: '.gz',
    })
  ]
}
```

---

## 🔐 Security Headers

Add to your backend (nginx, Express, etc.):

```
# Content Security Policy
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self' https://api.pharmaai.com;

# X-Frame-Options
X-Frame-Options: DENY

# X-Content-Type-Options
X-Content-Type-Options: nosniff

# X-XSS-Protection
X-XSS-Protection: 1; mode=block

# Referrer-Policy
Referrer-Policy: strict-origin-when-cross-origin

# Permissions-Policy
Permissions-Policy: camera=(), microphone=(), geolocation=(self)

# HSTS (after proving HTTPS works)
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

---

## 📊 Monitoring & Analytics

### Option 1: Google Analytics
```javascript
// Install GA4
npm install web-vitals

// In main.jsx
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

function sendToAnalytics(metric) {
  // Send to your analytics endpoint
  console.log(metric);
}

getCLS(sendToAnalytics);
getFID(sendToAnalytics);
getFCP(sendToAnalytics);
getLCP(sendToAnalytics);
getTTFB(sendToAnalytics);
```

### Option 2: Sentry (Error Tracking)
```bash
npm install @sentry/react

# In main.jsx
import * as Sentry from "@sentry/react";

Sentry.init({
  dsn: import.meta.env.VITE_SENTRY_DSN,
  environment: import.meta.env.VITE_ENVIRONMENT,
  tracesSampleRate: 0.1,
});
```

### Option 3: Datadog
```bash
npm install @datadog/browser-rum

# In main.jsx
import { datadogRum } from '@datadog/browser-rum';

datadogRum.init({
  applicationId: 'YOUR_APP_ID',
  clientToken: 'YOUR_CLIENT_TOKEN',
  site: 'datadoghq.com',
  service: 'pharmaai-frontend',
  env: import.meta.env.VITE_ENVIRONMENT,
  sessionSampleRate: 100,
  sessionReplaySampleRate: 20,
  trackUserInteractions: true,
});

datadogRum.startSessionReplayRecording();
```

---

## 🚀 CI/CD Pipeline (GitHub Actions)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Run linter
      run: npm run lint
    
    - name: Build production
      run: npm run build
      env:
        VITE_API_URL: ${{ secrets.PROD_API_URL }}
        VITE_ENVIRONMENT: production
    
    - name: Deploy to Vercel
      uses: amondnet/vercel-action@v25
      with:
        vercel-token: ${{ secrets.VERCEL_TOKEN }}
        vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
        vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
        working-directory: ./frontend
```

---

## 📱 Mobile App Optimization

### Viewport Meta Tag (ensure in index.html)
```html
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=5">
```

### App Manifest (PWA Support)
```json
{
  "name": "Pharma AI",
  "short_name": "PharmaAI",
  "description": "Smart healthcare pharmacy assistant",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#0ea5a4",
  "icons": [
    {
      "src": "/icon-192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "any"
    },
    {
      "src": "/icon-512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "any"
    }
  ]
}
```

---

## 🐛 Debugging Production Issues

### Enable Source Maps (carefully)
```javascript
// Only in staging
if (import.meta.env.VITE_ENVIRONMENT === 'staging') {
  // Source maps available for debugging
}
```

### Network Inspection
```javascript
if (import.meta.env.DEV) {
  // Only log in development
  console.log('API Response:', data);
}
```

### Performance Logging
```javascript
const measurePerformance = (name, fn) => {
  const start = performance.now();
  const result = fn();
  const end = performance.now();
  console.log(`${name} took ${end - start}ms`);
  return result;
};
```

---

## ✅ Final Deployment Checklist

- [ ] All environment variables configured on hosting platform
- [ ] API URL points to production backend
- [ ] HTTPS enabled and enforced
- [ ] Security headers configured
- [ ] Monitoring/logging setup (Sentry, Analytics)
- [ ] Database migrations run on backend
- [ ] CDN cache headers configured
- [ ] Compression enabled (gzip/brotli)
- [ ] Rate limiting configured on backend
- [ ] Backup strategy in place
- [ ] Rollback plan documented
- [ ] Status page setup (statuspage.io)
- [ ] Uptime monitoring configured (UptimeRobot)
- [ ] Log aggregation setup (ELK, Datadog)
- [ ] Performance baseline established

---

## 📞 Post-Deployment Support

### Monitoring
1. **Error Tracking**: Sentry dashboard for exceptions
2. **Performance**: Core Web Vitals in Google Analytics
3. **Logs**: CloudWatch/ELK for request logs
4. **Uptime**: UptimeRobot for availability

### Incident Response
1. **Alert Threshold**: Error rate > 5% → Page on-call
2. **Degradation**: Manual rollback to previous version
3. **Data Issues**: Contact backend team
4. **Outages**: Post incident review within 24hrs

---

## 📈 Scaling Checklist

As your app grows:
- [ ] Implement code splitting for views
- [ ] Setup image CDN (Cloudinary, Imgix)
- [ ] Redis cache for API responses
- [ ] GraphQL instead of REST (optional)
- [ ] Service Worker for offline support
- [ ] Database query optimization
- [ ] API rate limiting with user quotas
- [ ] Load testing before peak usage

---

**Last Updated:** 2024  
**Status:** Production Ready  
**Support:** See troubleshooting section or contact devops@pharmaai.com
