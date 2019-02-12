docker-compose build
rm -rf local_deployment
mkdir local_deployment
cd local_deployment
echo "Saving docker images"
docker save -o miqa_web_server.tar miqa_web_server
docker save -o miqa_provision.tar miqa_provision
docker save -o mongo.tar mongo
cp ../docker-compose.yml docker-compose.yml
sed -i -z 's/web_server:.*ports/web_server:\n    image: miqa_web_server\n    ports/' docker-compose.yml
sed -i -z 's/provision:.*Dockerfile/provision:\n    image: miqa_provision/' docker-compose.yml
cp ../.env.template .env
cp ../prepare_local_deployment.sh prepare_local_deployment.sh
echo "Complete"
