.PHONY: clean python build-docker publish-docker python

default:

python:
	scripts/build_and_publish_python.sh

build-docker:
	scripts/build_docker.sh

publish-docker:
	scripts/publish_docker.sh

clean:
	rm -rf build/ dist/
