# This file is auto-generated from config.json. Do not edit manually.
from pydantic import BaseModel, Field

class Invoice(BaseModel):
    invoice_number: str = Field(description="The unique identifier/number of the invoice")
    date: str = Field(description="The date when the invoice was issued")
    client_name: str = Field(description="The name of the client or customer")
    total_amount: float = Field(description="The total amount to be paid")
    vat_amount: float = Field(description="The VAT (Value Added Tax) amount")
    currency: str = Field(description="The currency code (e.g., EUR, USD, GBP)")
