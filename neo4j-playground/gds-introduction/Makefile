DATADIR:=./data


install:
	uv sync

# Run Neo4j in a Docker container with apoc and gds plugins
docker-neo4j-run:
	docker run \
		-v $(PWD)/$(DATADIR):/data \
		-v $(PWD)/neo4j.conf:/etc/neo4j/neo4j.conf \
		-d -p 7474:7474 -p 7687:7687 \
		-e NEO4J_AUTH=neo4j/test \
		-e NEO4JLABS_PLUGINS='["apoc","gds"]' \
		--name neo4j-gds-intro \
		neo4j:latest

docker-neo4j-stop:
	docker stop neo4j-gds-intro

docker-neo4j-start:
	docker start neo4j-gds-intro

docker-neo4j-remove:
	docker rm neo4j-gds-intro