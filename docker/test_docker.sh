#docker run -ti --rm \
#-v /Users/boydb1/Desktop/TEST_DOCKER/OUTPUTS:/OUTPUTS \
#-v /Users/boydb1/Desktop/TEST_DOCKER/INPUTS:/INPUTS \
#-v /Users/boydb1/git/dax/dax/docker/docker_dax_settings.ini:/root/.dax_settings.ini:ro \
#-v /Users/boydb1/.daxnetrc:/root/.daxnetrc:ro \
#-v /Users/boydb1/.dax_templates:/root/.dax_templates:ro \
#-v /Users/boydb1/git/dax/dax/docker/project_settings.yaml:/root/settings.yaml:ro \
#-v /Users/boydb1/git/dax/dax/docker/dax-modules:/root/dax-modules:ro \
#bud42/dax build /root/settings.yaml --sess 6001a

docker run -ti --rm \
-v /Users/boydb1/Desktop/TEST_DOCKER/INPUTS:/root \
-v /Users/boydb1/Desktop/TEST_DOCKER/OUTPUTS:/OUTPUTS \
bud42/dax build /root/settings.yaml --sess 6001a
