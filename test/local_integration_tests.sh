#
sudo docker build --build-arg BASE_DIR=/app/ --file db.Dockerfile --tag loris-db .
sudo docker build --file mri.Dockerfile --tag loris-mri .
sudo docker compose --file docker-compose.yml run mri pytest python/tests/integration
