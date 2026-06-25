"""
schemas/content.py
Request/response models for content generation and history.
"""
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ContentType(str, Enum):
    BLOG_ARTICLE = "blog_article"
    PRODUCT_DESCRIPTION = "product_description"
    MARKETING_CAMPAIGN = "marketing_campaign"
    SOCIAL_MEDIA_POST = "social_media_post"
    EMAIL_TEMPLATE = "email_template"
    AD_COPY = "ad_copy"
    SEO_CONTENT = "seo_content"


class ContentGenerateRequest(BaseModel):
    content_type: ContentType
    product_name: str = Field(min_length=2, max_length=200, description="Product, topic, or subject")
    tone: str = Field(default="professional", max_length=50)
    extra_details: Optional[str] = Field(default=None, max_length=1000)

    class Config:
        json_schema_extra = {
            "example": {
                "content_type": "product_description",
                "product_name": "Wireless Earbuds",
                "tone": "professional",
                "extra_details": "Highlight battery life and comfort",
            }
        }


class ContentOut(BaseModel):
    id: int
    user_id: int
    content_type: ContentType
    prompt: str
    generated_content: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class HistoryListResponse(BaseModel):
    total: int
    items: list[ContentOut]
