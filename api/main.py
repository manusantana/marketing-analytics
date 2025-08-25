from fastapi import FastAPI
from routers import kpis, products, customers

app = FastAPI(title="Marketing Analytics API")
app.include_router(kpis.router, prefix="/kpis", tags=["kpis"])
app.include_router(products.router, prefix="/products", tags=["products"])
app.include_router(customers.router, prefix="/customers", tags=["customers"])
