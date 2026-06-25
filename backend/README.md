# AI Content Generation Studio — Backend

FastAPI backend for generating blog articles, product descriptions, marketing
campaigns, social media posts, email templates, ad copy, and SEO content using
OpenAI or Gemini.

## Project Structure
```
backend/
├── app/                  # reserved (app-level config/wiring if you grow this)
├── routes/
│   ├── auth.py            # POST /register, POST /login
│   └── content.py         # POST /generate-content, GET /history, GET/DELETE /history/{id}
├── models/
│   ├── user.py            # Users table
│   └── content.py         # Generated_Content table
├── schemas/
│   ├── user.py            # Pydantic request/response models
│   └── content.py
├── services/
│   └── ai_service.py       # Prompt building + OpenAI/Gemini integration
├── database/
│   └── db.py               # Engine, session, Base
├── middleware/
│   └── auth.py              # Password hashing, JWT, get_current_user
├── tests/
│   └── test_api.py
├── main.py                 # FastAPI app entrypoint
├── requirements.txt
└── .env.example
```

## Setup
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env`:
- Set `DATABASE_URL` (PostgreSQL/MySQL connection string, or use SQLite for quick local testing).
- Set `AI_PROVIDER` to `openai` or `gemini`, and fill in the matching API key.
- Set a strong `SECRET_KEY`.

Run the server:
```bash
uvicorn main:app --reload
```
Docs at `http://localhost:8000/docs`.

## Running Tests
```bash
pytest tests/ -v
```
The AI call is mocked in tests, so no API key is required to run the suite.

## API Endpoints

| Method | Path                    | Description                          | Auth   |
|--------|--------------------------|---------------------------------------|--------|
| POST   | /register                | Create a new account                  | Public |
| POST   | /login                   | OAuth2 password login → JWT           | Public |
| POST   | /generate-content        | Generate AI content, save to history  | Bearer |
| GET    | /history                 | List my generated content (paginated) | Bearer |
| GET    | /history/{id}            | Get one history item                  | Bearer |
| DELETE | /history/{id}            | Delete a history item                 | Bearer |
| GET    | /health                  | Liveness check                        | Public |

### Example: generate content
```bash
curl -X POST http://localhost:8000/generate-content \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "content_type": "product_description",
    "product_name": "Wireless Earbuds",
    "tone": "professional"
  }'
```

### Supported content_type values
`blog_article`, `product_description`, `marketing_campaign`, `social_media_post`,
`email_template`, `ad_copy`, `seo_content`

## How content generation works
1. `routes/content.py` receives the request and calls `services/ai_service.py`.
2. `ai_service.build_prompt()` assembles a prompt like:
   ```
   Generate a product description
   for Wireless Earbuds
   with a professional tone.
   ```
3. The prompt is sent to OpenAI (`gpt-4o-mini` by default) or Gemini
   (`gemini-1.5-flash` by default), controlled by `AI_PROVIDER` in `.env`.
4. Both the prompt and the generated result are saved to `Generated_Content`,
   linked to the requesting user, so it shows up in `/history`.

## Notes
- Passwords are hashed with bcrypt before storage — never stored in plain text.
- JWT access tokens are required on all `/generate-content` and `/history` routes.
- `Base.metadata.create_all()` runs on startup for convenience; for schema
  migrations in production, add Alembic on top of `database/db.py`'s `Base`.
