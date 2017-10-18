.PHONY: image package

default: package

image:
	docker build -t shippable/reqexec:master .

package: image
	docker run -v $(shell pwd):/home/shippable/reqExec shippable/reqexec:master ./package.sh
