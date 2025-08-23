from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime


class NewsSerializer(BaseModel):
    title: str
    url: str
    source: str
    date: str
    category: str
    description: Optional[str] = None
    sentiment: Optional[Dict[str, float]] = None
    scraped_at: datetime = datetime.now()