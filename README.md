# Marketing Analytics – MVP

Plataforma mínima para ingestar datos (CSV/Excel), calcular KPIs (ABC, RFM, márgenes) y mostrarlos en un dashboard web.

## Requisitos
- Python 3.11+
- pip
- (Opcional) Docker Desktop si usas Postgres con docker-compose

## Instalación
```bash
pip install -r requirements.txt
```

## Uso rápido con SQLite
```bash
python db/seeds.py           # genera datos falsos
python etl/load_excel.py     # carga CSV a DB
streamlit run app/Dashboard.py
```

## Uso con Postgres (Docker)
```bash
docker compose up -d db
cp .env.example .env
# edita .env para usar Postgres:
# DB_URL=postgresql+psycopg://app:app@localhost:5432/marketing
make up     # levanta DB, aplica schema y carga datos
make app    # abre el dashboard
```

### Páginas del dashboard
- **Dashboard** (KPIs básicos)
- **⚙️ Ingesta** (subir Excel/CSV a tablas destino)
- **🔌 Conectores** (guardar credenciales GA4, Meta, Shopify)

### Variables de entorno
Copia `.env.example` a `.env` y ajusta `DB_URL`.
