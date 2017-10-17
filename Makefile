.PHONY: image package

default: package

image:
	docker build -t shippable/req-exec:master .

package: image
	docker run -v $(shell pwd):/home/shippable/reqExec shippable/req-exec:master ./package.sh
