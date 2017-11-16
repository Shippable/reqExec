.PHONY: image_x86_64_Ubuntu package_x86_64_Ubuntu image_aarch64_Ubuntu package_aarch64_Ubuntu

default: package

image_x86_64_Ubuntu:
	sed -i "s/{{%DRYDOCK_ORG%}}/drydock/g" Dockerfile
	docker build -t shippable/reqexec:master .

package_x86_64_Ubuntu: image_x86_64_Ubuntu
	docker run -v $(shell pwd):/home/shippable/reqExec shippable/reqexec:master ./package/x86_64/Ubuntu/package.sh

image_aarch64_Ubuntu:
	sed -i "s/{{%DRYDOCK_ORG%}}/drydockaarch64/g" Dockerfile
	docker build -t shippable/reqexec:master .

package_aarch64_Ubuntu: image_aarch64_Ubuntu
	docker run -v $(shell pwd):/home/shippable/reqExec shippable/reqexec:master ./package/aarch64/Ubuntu/package.sh

lint:
	pylint *.py
