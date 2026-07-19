#!/bin/bash
set -e

echo "[INFO] ??????..."
cd /app
python3 -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('[INFO] ??????')
"

echo "[INFO] ??????..."
python3 -c "
from app import app, db, Disease
with app.app_context():
    if not Disease.query.first():
        from init_data import insert_disease_data
        insert_disease_data()
        print('[INFO] ???????')
    else:
        print('[INFO] ??????????')
"

echo "[INFO] ?? Flask ??..."
python3 app.py
