all: master control_node worker_node

master:
	docker build -f Dockerfile.master . -t master

control_node:
	docker build -f Dockerfile.control_node . -t control_node

worker_node:
	docker build -f Dockerfile.worker_node . -t worker_node
