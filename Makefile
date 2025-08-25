.PHONY: seeds load app api up schema down reset

seeds:
	python db/seeds.py

load:
	python etl/load_excel.py

api:
	uvicorn api.main:app --reload

app:
	streamlit run app/Dashboard.py

up:
	docker compose up -d db
	@echo "Esperando a Postgres..."
	sleep 3
	$(MAKE) schema
	$(MAKE) seeds
	$(MAKE) load
	@echo "Listo. Ejecuta: make app"

schema:
	@echo "Aplicando db/schema.sql en Postgres (Docker)..."
	cat db/schema.sql | docker compose exec -T db psql -U app -d marketing -v ON_ERROR_STOP=1

down:
	docker compose down

reset:
	docker compose down -v
	$(MAKE) up
