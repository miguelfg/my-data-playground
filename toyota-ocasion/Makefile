init:
	mkdir -p data/scraped
	mkdir -p data/transformed
	mkdir -p data/mapped
	poetry init -n
	poetry env use 3.12

clean:
	find . -name "*.pyc" -exec rm -f {} \;

install-jupyter-extensions:
	poetry run jupyter contrib nbextension install --user
	poetry run jupyter nbextensions_configurator enable --user

install-dev:
	poetry add --dev flake8 black isort pytest

lynt:
	poetry run flake8 ./

install:
	poetry install

jupyter:
	poetry run jupyter notebook

scrape-toyota:
	poetry run python cli.py scrape --debug 10

parse-toyota:
	poetry run python cli.py parse --debug 10

transform-toyota:
	poetry run python cli.py transform --debug 10

map-toyota:
	poetry run python cli.py map --debug 10

load-last:
	poetry run python cli.py load --debug 10

load-file:
	poetry run python cli.py load -i "$(FILE)"

update-last-seen:
	poetry run python cli.py update-last-seen

run-etl:
	poetry run python cli.py scrape --debug 10
	poetry run python cli.py parse --debug 10
	poetry run python cli.py transform --debug 10
	poetry run python cli.py map --debug 10
	poetry run python cli.py load

run-etl-no-scrape:
	poetry run python cli.py parse --debug 10
	poetry run python cli.py transform --debug 10
	poetry run python cli.py map --debug 10
	poetry run python cli.py load

db-init:
	# create database with schema
	poetry run sqlite3 streamlits/coches.db < loaders/create_schema_history.sql
	poetry run sqlite3 streamlits/coches.db < loaders/create_schema_last_seen_avail.sql

db-drop-coches:
	# drop coches table from sqlite3
	poetry run sqlite3 streamlits/coches.db "drop table offers_history;"

db-flush:
	# flush offers_history table from sqlite3
	poetry run sqlite3 streamlits/coches.db "delete from offers_history;"

db-schema-temp:
	poetry run sqlite3 data/temp.db .schema > data/temp_schema.sql

db-schema:
	poetry run sqlite3 streamlits/coches.db .schema

db-count-rows:
	poetry run sqlite3 streamlits/coches.db "select count(*) from offers_history;"
	poetry run sqlite3 streamlits/coches.db "select count(*) from offers_last_seen_available;"

db-head:
	poetry run sqlite3 streamlits/coches.db "select * from offers_history limit 3;"

db-quick-stats: db-head db-count-rows

run-streamlit:
	poetry run streamlit run streamlits/app.py

gcp-deploy:
	cd streamlits/ && gcloud app deploy
