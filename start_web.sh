#!/bin/sh

echo "Building Databases"

python3 create_db.py

echo "Starting Miya Bot"

python3 bot.py