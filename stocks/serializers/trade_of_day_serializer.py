import re
from datetime import datetime
from typing import List
from pydantic import BaseModel


class TradeOfTheDaySerializer(BaseModel):
    ticker: str
    price: float
    avg_forward_return_21d: float
    insights: List[str]
    date: datetime = datetime.now()

    @classmethod
    def from_raw_text(cls, raw_text: str):
        trades =  []

        # Dividimos por bloques de trades (cada bloque empieza con número + **TICKER)
        trade_blocks = re.split(r"\n\d+\.\s+\*\*", raw_text)
        for block in trade_blocks[1:]:  # el primero es el encabezado, lo ignoramos
            try:
                # --- Extraer ticker y precio ---
                ticker_price_match = re.match(r"([A-Z]+)\s+\(\$(.*?)\)\*\*", block)
                if ticker_price_match:
                    ticker = ticker_price_match.group(1)
                    try:
                        price = float(ticker_price_match.group(2))
                    except ValueError:
                        price = 0.0
                else:
                    ticker, price = "", 0.0

                # --- Extraer average forward 21-day return ---
                return_match = re.search(r"21-day return(?:\:| of)\s*([0-9.]+)%", block, re.IGNORECASE)
                if return_match:
                    avg_forward_return_21d = float(return_match.group(1))
                else:
                    avg_forward_return_21d = 0.0


                # --- Extraer insights ---
                insights = []
                for line in block.splitlines():
                    line = line.strip()
                    if line.startswith("-"):
                        insights.append(line.lstrip("- ").strip())
                if not insights:
                    insights = ["No insights available"]

                trades.append(
                    cls(
                        ticker=ticker,
                        price=price,
                        avg_forward_return_21d=avg_forward_return_21d,
                        insights=insights,
                        date=datetime.now(),
                    )
                )

            except Exception as e:
                # fallback para no romper si algo cambia en el formato
                trades.append(
                    cls(
                        ticker="",
                        price=0.0,
                        avg_forward_return_21d=0.0,
                        insights=[f"Parsing error: {e}"],
                        date=datetime.now(),
                    )
                )

        return trades
