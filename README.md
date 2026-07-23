# 🐾 PetPal

> Connecting loving families with pets who need a home.

PetPal is a full-stack web application built with Django that makes pet adoption simple, transparent, and humane. Shelter administrators can list and manage pets, while adopters can browse, fall in love, and submit adoption requests — all from a clean, modern interface.

---

## ✨ What PetPal Does

Adopting a pet should feel joyful, not bureaucratic. PetPal removes the friction:

- **Adopters** create an account, browse available pets, and submit a request with a personal message in under a minute.
- **Shelter Admins** get a dedicated dashboard to manage their entire pet catalogue, review incoming requests, and approve or reject them with one click.
- When a request is approved, the pet's status automatically updates to **Adopted** and disappears from the browse page — no manual cleanup needed.
- If a user account is deleted, their pending requests are cleaned up and any affected pets are automatically reset to **Available**.

---

## 🖼️ Application Overview

| Role | What they see |
|---|---|
| **Guest** | Landing page, About, Contact |
| **Adopter** | Dashboard, Browse Pets, Pet Details, My Requests |
| **Shelter Admin** | Dashboard with stats, Manage Pets (add/edit/delete), Manage Requests (approve/reject), Manage Users |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 6 · Python 3.14 |
| Frontend | Django Templates · HTMX · Alpine.js |
| Styling | Tailwind CSS v4 · DaisyUI |
| Auth | Django Allauth (email-based) |
| Database | SQLite (local) · PostgreSQL (production) |
| Asset bundling | Vite |
| Task queue | Celery + Redis (production) |
| Package manager | uv (Python) · npm (JS) |

---

## 📁 Project Structure

```
petpal/
├── apps/
│   ├── adoptions/      # Adoption requests — models, views, signals, URLs
│   ├── pets/           # Pet catalogue — models, views, admin, URLs
│   ├── users/          # Custom user model, profile, avatar upload
│   ├── utils/          # Shared BaseModel (created_at / updated_at)
│   └── web/            # Home, About, Contact, dashboard, context processors
├── assets/
│   ├── javascript/     # Site JS built by Vite
│   └── styles/         # Tailwind CSS entry points
├── config/
│   ├── settings/
│   │   ├── base.py     # Shared settings
│   │   ├── dev.py      # Local development
│   │   └── prod.py     # Production (Docker + Postgres + Redis)
│   ├── urls.py
│   └── celery.py
├── templates/
│   ├── account/        # Login, signup, password reset, profile
│   ├── adoptions/      # Request form, my requests, admin request list
│   ├── pets/           # Pet list, detail, form, delete confirm
│   └── web/            # Base layout, landing page, dashboard, nav, footer
├── static/             # Built static files (committed manifest)
├── media/              # User-uploaded pet images and avatars
├── manage.py
├── Makefile            # All common commands in one place
└── docker-compose.yml  # Production stack
```

---

## 🚀 Getting Started (Local Development)

### Prerequisites

You need these installed before anything else:

- **[uv](https://docs.astral.sh/uv/getting-started/installation/)** — fast Python package manager
- **[Node.js 20+](https://nodejs.org/)** — for the Vite frontend build
- **`make`** — to run project commands (Windows users: use Git Bash, WSL, or run the commands inside the Makefile manually)

---

### 1. Clone the repo

```bash
git clone <your-repo-url>
cd django
```

---

### 2. Bootstrap everything

```bash
make init
```

This single command will:
- Copy `.env.example` → `.env`
- Install all Python dependencies via `uv sync`
- Install all npm packages
- Create the SQLite database
- Apply all migrations

---

### 3. Start the development servers

Local development needs **two terminals running at the same time**. Django serves the app; Vite serves hot-reloaded CSS and JS.

**Terminal 1 — Django (http://localhost:8000):**
```bash
make start
```

**Terminal 2 — Vite (http://localhost:5173):**
```bash
make npm-dev
```

Open **http://localhost:8000** in your browser. Without the Vite server running, pages will load but look unstyled.

---

### 4. Log in

In `DEBUG` mode a superuser is automatically created on first run:

| Field | Value |
|---|---|
| Email | `admin@example.com` |
| Password | `admin` |

> Change these immediately if you ever expose the app to the internet.

---

## 👥 User Roles

PetPal has two user roles, managed via Django Groups.

### Shelter Admin

Has full control over the platform. A Shelter Admin can:
- Add, edit, and delete pets
- View all adoption requests from all users
- Approve requests (automatically marks the pet as Adopted)
- Reject requests
- Access the Django admin panel at `/admin/`

**How to create a Shelter Admin:**
1. Sign up for an account via the normal registration page, or create one via the Django admin.
2. In the Django admin (`/admin/`) go to **Users**, find the account, and add them to the **Shelter** group.

### Adopter

The default role for any registered user. An Adopter can:
- Browse all available pets
- Filter by species and gender
- View pet details
- Submit one adoption request per pet
- Track their own requests
- Cancel pending requests

No special setup required — anyone who registers is an Adopter by default.

---

## 🐕 How the Adoption Flow Works

```
Adopter signs up
      ↓
Browse available pets
      ↓
Click "View Details" on a pet
      ↓
Click "Request Adoption"
      ↓
Submit optional message → Request created (status: Pending)
      ↓
Shelter Admin reviews in Manage Requests
      ↓
      ├── Approve → Request: Approved, Pet: Adopted, other requests: Rejected
      └── Reject  → Request: Rejected, pet remains Available
```

**Important rules enforced by the system:**
- A user cannot submit two requests for the same pet.
- Once a pet is Adopted it no longer appears on Browse Pets.
- If an adopter's account is deleted, their requests are deleted and the pet's status is automatically reset to Available.
- Cancelling a request also resets the pet's status to Available if no other active requests remain.

---

## 🗃️ Data Models

### Pet

| Field | Type | Notes |
|---|---|---|
| `name` | CharField | |
| `breed` | CharField | |
| `species` | CharField | Dog, Cat, Bird, Rabbit, Other |
| `age` | PositiveIntegerField | In years |
| `gender` | CharField | Male / Female |
| `description` | TextField | Optional |
| `adoption_status` | CharField | Available / Pending / Adopted |
| `image` | ImageField | Optional, stored in `media/pet-images/` |
| `created_at` | DateTimeField | Auto |
| `updated_at` | DateTimeField | Auto |

### AdoptionRequest

| Field | Type | Notes |
|---|---|---|
| `user` | FK → CustomUser | CASCADE delete |
| `pet` | FK → Pet | CASCADE delete |
| `status` | CharField | Pending / Approved / Rejected / Cancelled |
| `message` | TextField | Optional note from adopter |
| `created_at` | DateTimeField | Auto |
| `updated_at` | DateTimeField | Auto |

Unique constraint: one request per `(user, pet)` pair.

### CustomUser

Extends Django's `AbstractUser` with:
- `avatar` — profile picture (stored in `media/profile-pictures/`)
- `get_display_name()` — returns full name, falls back to email
- `avatar_url` — returns upload URL or Gravatar fallback
- `is_shelter()` — returns True if user is in the Shelter group
- `is_adopter()` — returns True if user is in the Adopter group

---

## ⌨️ Common Commands

All commands live in `Makefile`. Run `make` with no arguments to see the full list.

### Daily development

```bash
make start                          # Start Django dev server
make npm-dev                        # Start Vite dev server (separate terminal)
make shell                          # Open Django shell
make dbshell                        # Open SQLite shell
```

### Database

```bash
make migrations                     # Generate new migrations
make migrate                        # Apply pending migrations
make manage ARGS='createsuperuser'  # Create a superuser manually
```

### Testing

```bash
make test                                        # Run all tests
make test ARGS='apps.pets'                       # Run a specific app's tests
make test ARGS='apps.web.tests.test_basic_views' # Run a specific test file
```

### Code quality

```bash
make ruff-format    # Auto-format Python code
make ruff-lint      # Lint and auto-fix
make ruff           # Run both
```

### Dependencies

```bash
make uv add 'package-name'    # Add a Python package
make requirements              # Re-sync Python deps from lockfile
make npm-install package-name  # Add an npm package
```

---

## ⚙️ Environment Variables

Copy `.env.example` to `.env` and adjust as needed. Key variables:

```bash
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Email (console backend by default — prints to terminal)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Email verification: "none" | "optional" | "mandatory"
ACCOUNT_EMAIL_VERIFICATION=none

# Production only
DATABASE_URL=postgres://user:pass@host:5432/dbname
REDIS_URL=redis://localhost:6379/0
```

---

## 🐳 Production Deployment

### Setup

```bash
cp .env.prod.example .env.prod
# Edit .env.prod with real values: SECRET_KEY, DATABASE_URL, REDIS_URL, ALLOWED_HOSTS
```

### Build and run

```bash
make prod-build      # Build the Docker image
make prod-start      # Start all containers in foreground
make prod-start-bg   # Start in background
make prod-stop       # Stop all containers
make prod-ssh        # Shell into the running web container
```

### Production stack (Docker Compose)

```
nginx (or direct Gunicorn)
      ↓
gunicorn (Django WSGI)
      ↓
postgres (database)
redis (cache + Celery broker)
celery worker (background tasks)
```

---

## 🧪 Running Tests

```bash
make test
```

The test suite covers:
- Landing page, login, signup, robots.txt
- Profile editing and email change flow
- Password change
- API schema generation
- No pending migrations check

All 18 tests should pass on a clean checkout.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Run `make ruff` and `make test` — both must pass
5. Commit with a clear message
6. Open a pull request

Please don't commit `.env` files, `db.sqlite3`, or anything in `media/`.

---

## 📄 License

This project is built on top of the [Django Starter Template](https://github.com/ChrisDevCode-Technologies/django-starter).
See `LICENSE` for details.

---

## 🙏 Acknowledgements

- **[Django](https://www.djangoproject.com/)** — the web framework that makes this possible
- **[Django Allauth](https://docs.allauth.org/)** — battle-tested authentication
- **[DaisyUI](https://daisyui.com/)** — beautiful component library on top of Tailwind
- **[HTMX](https://htmx.org/)** — server-driven interactivity without the JavaScript overhead
- **[Alpine.js](https://alpinejs.dev/)** — lightweight client-side reactivity
- **[Vite](https://vitejs.dev/)** — blazing fast frontend tooling
- **[uv](https://docs.astral.sh/uv/)** — Python packaging done right
- Original starter template by [SaaS Pegasus](https://www.saaspegasus.com/)

---

*Built with care for the animals waiting for their forever home. 🐾*
