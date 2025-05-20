.PHONY: build deploy local clean test setup{% if copier__dynamo_db %} dynamo-up dynamo-down wait-for-dynamodb create-table{% endif %}

# Configuration
STACK_NAME ?= {{ copier__stack_name }}
REGION ?= {{copier__aws_region}}
TEMPLATE_FILE ?= template.yaml
BUILD_DIR ?= .aws-sam/build
{% if copier__dynamo_db %}
DYNAMO_ENDPOINT ?= http://localhost:8000
TABLE_NAME ?= RequestsTable-{{copier__stack_name}}
CONTAINER_NAME ?= {{copier__stack_name}}-dynamodb-local
NETWORK_NAME ?= {{copier__stack_name}}-network
{% endif %}

# Default target
all: build

build:
	sam build > /dev/null 2>&1

validate:
	sam validate --lint

deploy:
	sam deploy --guided --profile {{copier__aws_profile}}

deploy-sandbox:
	sam deploy --stack-name $(STACK_NAME)-sandbox \
        	--capabilities CAPABILITY_IAM \
        	--parameter-overrides StageName=sandbox \
			{% if copier__package_type != "image" %}--resolve-image-repos{% endif %}

local:
	sam local start-api {% if copier__dynamo_db %}--env-vars env_example.json --docker-network $(NETWORK_NAME){% endif %}

invoke:
	sam local invoke HelloWorldFunction --event events/event.json{% if copier__dynamo_db %} --env-vars env_example.json --docker-network $(NETWORK_NAME){% endif %}

{% if copier__dynamo_db %}
dynamo-up:
	@if [ -z "$$(docker network ls --filter name=^$(NETWORK_NAME)$$ -q)" ]; then \
		echo "Creating Docker network '$(NETWORK_NAME)'..."; \
		docker network create $(NETWORK_NAME); \
	else \
		echo "Docker network '$(NETWORK_NAME)' already exists."; \
	fi; \
	if [ -n "$$(docker ps -q -f name=^/$(CONTAINER_NAME)$$)" ]; then \
		echo "DynamoDB local container '$(CONTAINER_NAME)' is already running."; \
	else \
		if docker ps --format "{% raw %}{{.Ports}}{% endraw %}" | grep ':8000->'; then \
			echo "Error: Port 8000 is already in use by another container. Cannot start DynamoDB local container."; \
			exit 1; \
		fi; \
		echo "Starting DynamoDB local container..."; \
		docker run -d --rm --network $(NETWORK_NAME) -p 8000:8000 --name $(CONTAINER_NAME) amazon/dynamodb-local:latest -jar DynamoDBLocal.jar -sharedDb; \
		echo "DynamoDB local container '$(CONTAINER_NAME)' started."; \
	fi

wait-for-dynamodb:
	@echo "Waiting for DynamoDB Local to be ready..."
	@attempts=0; \
	until curl -s http://localhost:8000 >/dev/null; do \
		if [ $$attempts -ge 10 ]; then \
			echo "DynamoDB Local did not become ready in time"; \
			exit 1; \
		fi; \
		echo "Waiting..."; \
		sleep 1; \
		attempts=$$((attempts + 1)); \
	done; \
	echo "DynamoDB Local is ready."

create-table:
	@# Store the AWS command output in a variable
	$(eval AWS_OUTPUT := $(shell aws dynamodb create-table \
		--table-name $(TABLE_NAME) \
		--attribute-definitions \
		AttributeName=ip_address,AttributeType=S \
		AttributeName=timestamp,AttributeType=S \
		--key-schema \
		AttributeName=ip_address,KeyType=HASH \
		AttributeName=timestamp,KeyType=RANGE \
		--billing-mode PAY_PER_REQUEST \
		--endpoint-url $(DYNAMO_ENDPOINT)))

	@# Check if jq exists and use it if available
	@if command -v jq > /dev/null 2>&1; then \
		echo '$(AWS_OUTPUT)' | jq; \
	else \
		echo '$(AWS_OUTPUT)'; \
		echo "\033[33mNote: Install jq for colorized JSON output\033[0m"; \
	fi

setup: dynamo-up wait-for-dynamodb create-table{% else %}
setup:
	pip install -r src/requirements.txt{% endif %}

test:
	AWS_SAM_STACK_NAME=$(STACK_NAME) PYTHONPATH=. uv run --with pytest,boto3,requests,pytest-mock pytest -v --disable-warnings --tb=short tests

down:
	@if [ -n "$$(docker ps -q -f name=^/$(CONTAINER_NAME)$$)" ]; then \
		echo "Stopping DynamoDB local container..."; \
		docker stop $(CONTAINER_NAME); \
		echo "DynamoDB local container '$(CONTAINER_NAME)' stopped."; \
	else \
		echo "DynamoDB local container '$(CONTAINER_NAME)' is not running."; \
	fi; \
	if [ -n "$$(docker network ls --filter name=^$(NETWORK_NAME)$$ -q)" ]; then \
		echo "Removing Docker network '$(NETWORK_NAME)'..."; \
		docker network rm $(NETWORK_NAME); \
		echo "Docker network '$(NETWORK_NAME)' removed."; \
	else \
		echo "Docker network '$(NETWORK_NAME)' does not exist."; \
	fi

delete-sandbox:
	sam delete --stack-name $(STACK_NAME)-sandbox

delete:
	sam delete --stack-name $(STACK_NAME)
