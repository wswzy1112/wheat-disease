Here is the complete security audit and deployment checklist for 小麦病虫害识别系统.

= BEFORE YOUR CURRENT WORK (ORIGINAL STATUS) =

SECURITY ISSUES FOUND (14 total):

CRITICAL (3):
  1. Passwords stored in plaintext - anyone with DB access sees all passwords
  2. No authentication system - user_id passed in URL, anyone can forge requests
  3. Database credentials hardcoded in source code

HIGH (6):
  4. Flask debug mode enabled - leaks stack traces in production
  5. No file upload validation - accepts any file type and size
  6. CORS allows all origins (wildcard *)
  7. No secret key configured
  8. frontend main.ts creates + mounts app TWICE (runtime bug)
  9. All API URLs hardcoded to localhost:5000

MEDIUM (5):
  10. No rate limiting on login/register endpoints
  11. No error handling - user_id and page params not sanitized
  12. No security response headers (CSP, X-Frame-Options, etc.)
  13. index.html title is "Vite App" - no SEO
  14. No .gitignore / .env.example / requirements.txt

= FIXES APPLIED =

BACKEND (app.py):
  ✓ Password hashing via werkzeug.security (generate_password_hash)
  ✓ JWT token authentication (returned on login/register, required for all secured endpoints)
  ✓ Database credentials moved to environment variables (.env / os.environ)
  ✓ debug=False by default, only enabled when FLASK_ENV=development
  ✓ File validation: extension whitelist + content-type check + PIL verify
  ✓ MAX_CONTENT_LENGTH = 10MB
  ✓ CORS locked to ALLOWED_ORIGINS from env var
  ✓ Rate limiting (flask-limiter): 5/min register, 10/min login, 30/hr upload
  ✓ Input sanitization: username regex validation, pagination clamped
  ✓ Security headers: X-Content-Type-Options, X-Frame-Options, X-XSS-Protection, HSTS, CSP
  ✓ Proper error handlers for 400/401/404/413/429/500
  ✓ UUID-based filenames (unpredictable, no path traversal)

FRONTEND:
  ✓ main.ts: single createApp (fixed double-mount bug)
  ✓ API_BASE_URL from environment variable (VITE_API_URL), with /api fallback
  ✓ JWT token stored and sent via Authorization header
  ✓ 401 error handling on records fetch (auto-logout on token expiry)
  ✓ index.html: proper zh-CN lang, SEO meta description, theme-color
  ✓ api.js: centralized token management (getToken/setToken/clearToken)

DEVOPS:
  ✓ .env.example with all configuration options documented
  ✓ requirements.txt with all Python dependencies
  ✓ .gitignore (Python, Node, env, IDE, uploads, model files)

= REMAINING -> WHAT TO DO ON YOUR SERVER =

BEFORE DEPLOYING:
  1. cp .env.example .env  (edit with your real values)
  2. Set SECRET_KEY to a long random string
  3. Set DATABASE_URL to your production MySQL connection
  4. Set ALLOWED_ORIGINS to your actual domain(s)
  5. Set FLASK_ENV=production

BUILD & START:
  6. cd wheat-frontend && npm run build (generates dist/)
  7. The backend serves the built frontend automatically
  8. python app.py  (or use gunicorn: gunicorn app:app -w 4 -b 0.0.0.0:5000)

RECOMMENDED (not implemented, future work):
  - HTTPS via nginx reverse proxy (LetsEncrypt)
  - Database migration script for old plaintext passwords
  - Session-based auth (HttpOnly cookies) instead of localStorage tokens
  - File upload virus scanning
  - Containerization (Dockerfile + docker-compose)
