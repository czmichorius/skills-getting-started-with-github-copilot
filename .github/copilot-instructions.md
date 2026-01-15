# Copilot Instructions for Mergington High School Activities API

## Project Overview

This is a **full-stack educational application** showcasing a school activity sign-up system with:
- **Backend**: FastAPI server providing REST API endpoints
- **Frontend**: Vanilla JavaScript single-page application
- **Data**: In-memory activity database with student email participants

The project demonstrates basic CRUD operations and API-frontend integration patterns suitable for learning GitHub Copilot workflows.

## Architecture

### Backend Structure (`src/app.py`)
- **Framework**: FastAPI (lightweight Python web framework)
- **Data Model**: Dictionary-based in-memory storage with no persistence
  - Activities indexed by name (string keys)
  - Each activity has: `description`, `schedule`, `max_participants`, `participants` (list of emails)
- **Key Endpoints**:
  - `GET /activities` → Returns all activities JSON object
  - `POST /activities/{activity_name}/signup?email=...` → Adds email to activity's participants list

### Frontend Structure (`src/static/`)
- **index.html**: Static page with form and activity card container
- **app.js**: Client-side logic using vanilla fetch API
  - `fetchActivities()`: Loads activities and populates UI
  - Form submission handler: POSTs to signup endpoint
  - Transient message notifications (auto-hide after 5s)
- **styles.css**: Styling for activity cards and form

## Key Patterns & Conventions

### Data Validation
- Activity name must exist in activities dictionary (404 error if not)
- Student email must not already be signed up (400 error if duplicate)
- Server validates on POST; client validates form inputs
- No persistent storage—all data lost on server restart

### Error Handling
- HTTPException with status codes and detail messages
- Frontend catches fetch errors and displays user-friendly messages
- JavaScript uses console.error for debugging

### JavaScript Patterns
- Event-driven: DOMContentLoaded initialization, form submit listeners
- Async/await with fetch API (no external HTTP libraries)
- Template literals for HTML generation
- URL encoding for activity names with special characters using `encodeURIComponent()`

### API Response Format
- GET /activities returns plain activity object
- POST /activities/{name}/signup returns `{"message": "..."}` or `{"detail": "error"}`

## Development Workflows

### Running the Application
```bash
# Install dependencies
pip install fastapi uvicorn

# Start server (port 8000)
python src/app.py

# Access at http://localhost:8000
```

### Testing
```bash
# Project uses pytest (configured in pytest.ini with pythonpath = .)
pytest
```

## Important Notes for AI Agents

1. **No Database**: All activity/student data is hardcoded in memory; changes don't persist
2. **Activity Name as ID**: Activities use string names, not numeric IDs—be careful with URL encoding in signup POST requests
3. **Email Format**: Students identified by email addresses (format: `*@mergington.edu`)
4. **Max Participants**: Each activity has a limit; signup should reject if full
5. **Stateless Reload**: Restarting server resets all signups to initial state
6. **CORS Not Configured**: Frontend served from same origin; no cross-origin requests needed
7. **Static File Mounting**: Ensure `src/static/` path is correct when modifying file serving

## Reference Files for Common Tasks

| Task | Key File(s) |
|------|------------|
| Add new API endpoint | `src/app.py` |
| Fix frontend form/UI | `src/static/app.js`, `index.html` |
| Styling updates | `src/static/styles.css` |
| View API contracts | `src/README.md` (endpoint table) |
