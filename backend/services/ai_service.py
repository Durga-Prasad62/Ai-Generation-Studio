"""
services/ai_service.py
Builds prompts for each content type and sends them to the configured AI
provider (OpenAI GPT or Google Gemini), returning the generated text.

Set AI_PROVIDER=openai or AI_PROVIDER=gemini in the environment to choose.
"""
import os

from dotenv import load_dotenv

load_dotenv()

AI_PROVIDER = os.getenv("AI_PROVIDER", "openai").lower()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")


CONTENT_TYPE_GUIDANCE = {
    "blog_article": "Write an engaging, well-structured blog article with a hook opening, "
                     "clear sections, and a concluding takeaway.",
    "product_description": "Write a concise, benefit-driven product description optimized "
                            "for conversion. 2-4 sentences.",
    "marketing_campaign": "Write persuasive marketing campaign copy with a strong value "
                           "proposition and a call to action.",
    "social_media_post": "Write a short, punchy social media post suited to a fast scroll speed.",
    "email_template": "Write a friendly, professional email with a subject line, greeting, "
                       "body, and sign-off.",
    "ad_copy": "Write tight, high-converting ad copy with an irresistible call to action.",
    "seo_content": "Write SEO-optimized content that naturally incorporates relevant keywords "
                    "while remaining readable and valuable to the reader.",
}


def build_prompt(content_type: str, product_name: str, tone: str, extra_details: str | None) -> str:
    """
    Builds the natural-language prompt sent to the AI model.
    Mirrors the structure: Generate a {content_type} for {product_name} with {tone} tone.
    """
    guidance = CONTENT_TYPE_GUIDANCE.get(content_type, "Write high-quality business content.")
    details = f"\nAdditional details: {extra_details}" if extra_details else ""

    prompt = f"""
Generate a {content_type.replace('_', ' ')}
for {product_name}
with a {tone} tone.

Guidance: {guidance}{details}

Return only the generated content text, with no extra commentary, labels, or markdown fences.
""".strip()
    return prompt


def _call_openai(prompt: str) -> str:
    from openai import OpenAI

    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not configured")

    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "You are an expert business content copywriter."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=800,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()


def _call_gemini(prompt: str) -> str:
    import google.generativeai as genai

    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not configured")

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(GEMINI_MODEL)
    response = model.generate_content(prompt)
    return response.text.strip()


def generate_ai_content(content_type: str, product_name: str, tone: str, extra_details: str | None = None) -> tuple[str, str]:
    """
    Returns a tuple of (prompt_used, generated_text).
    Raises RuntimeError if the AI provider call fails.
    """
    prompt = build_prompt(content_type, product_name, tone, extra_details)

    try:
        if AI_PROVIDER == "gemini":
            generated_text = _call_gemini(prompt)
        else:
            generated_text = _call_openai(prompt)
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"AI generation failed: {exc}") from exc

    return prompt, generated_text
