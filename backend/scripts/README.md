# Scripts

- `commands.py`: runner command di `src/commands/`.
  `uv run python -m scripts.commands run <nama> [argumen]`
  - `seed_database`: isi Waste_Category, Waste_Subcategory, Facility, Facility_Category
  - `extract_road_graph`: unduh graf OSM (OSMnx) ke Road_Node dan Road_Edge
  - `evaluate_navigation`: bandingkan A* dan Dijkstra
- `alembic/`: migrasi skema basis data (`uv run alembic upgrade head`).
- `start.sh`: menjalankan server produksi (granian).
