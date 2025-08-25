import random, csv, datetime as dt, uuid
from pathlib import Path

random.seed(42)

base = Path(__file__).resolve().parents[1] / 'data' / 'seeds'
base.mkdir(parents=True, exist_ok=True)

products = [
    {"id":"P-100","name":"Exprimidora Pro","category":"Máquinas","cost":900,"price":1500},
    {"id":"P-200","name":"Cortadora Piñas","category":"Máquinas","cost":700,"price":1200},
    {"id":"P-300","name":"Kit Recambios","category":"Accesorios","cost":20,"price":60},
]
customers = [
    {"id":"C-ES-01","name":"Hotel Sol","country":"ES","segment":"HORECA"},
    {"id":"C-IT-02","name":"Super Milano","country":"IT","segment":"Retail"},
    {"id":"C-FR-03","name":"Fresh Bar","country":"FR","segment":"HORECA"},
]

# Orders
start = (dt.date.today().replace(day=1) - dt.timedelta(days=180))
orders = []
for d in (start + dt.timedelta(days=i) for i in range(180)):
    for _ in range(random.randint(0,3)):
        p = random.choice(products)
        c = random.choice(customers)
        qty = random.randint(1,5)
        price = p["price"]
        net = qty * price
        cogs = qty * p["cost"]
        orders.append({
            "id": str(uuid.uuid4())[:8],
            "customer_id": c["id"],
            "date": d.isoformat(),
            "product_id": p["id"],
            "qty": qty,
            "net_revenue": round(net,2),
            "cogs": round(cogs,2),
        })

# Campaigns & GA sessions
sources = [("google","cpc"),("meta","social"),("email","email"),("direct","none")]
ga_rows, camp_rows = [], []
for d in (start + dt.timedelta(days=i) for i in range(180)):
    for s, m in sources:
        sessions = random.randint(20,400)
        users = int(sessions*0.9)
        bounces = int(sessions*random.uniform(0.2,0.6))
        tx = random.randint(0, max(1, sessions//100))
        rev = round(tx * random.uniform(50, 400), 2)
        ga_rows.append({
            "date": d.isoformat(), "source": s, "medium": m, "country": random.choice(["ES","IT","FR"]),
            "sessions": sessions, "transactions": tx, "revenue": rev, "users": users, "bounces": bounces
        })
        if s in ("google","meta"):
            cost = round(sessions * random.uniform(0.1,0.6),2)
            clicks = int(sessions*random.uniform(0.2,0.7))
            impressions = clicks*random.randint(10,50)
            purchases = tx
            camp_rows.append({
                "id": str(uuid.uuid4())[:8], "source": s, "medium": m, "campaign_name": f"{s}-{m}",
                "date": d.isoformat(), "cost": cost, "clicks": clicks, "impressions": impressions,
                "sessions": sessions, "purchases": purchases, "revenue": rev
            })

def write_csv(name, rows):
    fp = base / name
    if not rows:
        return
    header = list(rows[0].keys())
    with open(fp, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=header)
        w.writeheader(); w.writerows(rows)
    print(f"Wrote {name}: {len(rows)} rows")

write_csv("products.csv", products)
write_csv("customers.csv", customers)
write_csv("orders.csv", orders)
write_csv("ga_sessions.csv", ga_rows)
write_csv("campaigns.csv", camp_rows)

print(f"Seeds escritos en {base}")
