import pandas as pd
from pathlib import Path
from .utils import get_engine

engine = get_engine()

files = {
    'products': 'data/seeds/products.csv',
    'customers': 'data/seeds/customers.csv',
    'orders': 'data/seeds/orders.csv',
    'ga_sessions': 'data/seeds/ga_sessions.csv',
    'campaigns': 'data/seeds/campaigns.csv',
}

for table, path in files.items():
    fp = Path(path)
    if not fp.exists():
        print(f"[WARN] {path} no existe. Omite {table}.")
        continue
    df = pd.read_csv(fp)
    df.to_sql(table, engine, if_exists='replace', index=False)
    print(f"Cargado {table}: {len(df)} filas")
print("Carga finalizada.")
