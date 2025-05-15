.PHONY: build deploy local clean test setup{% if copier__dynamo_db %} dynamo-up dynamo-down create-table{% endif %}

# Configuration
STACK_NAME ?= {{ copier__stack_name }}
REGION ?= {{copier__aws_region}}
TEMPLATE_FILE ?= template.yaml
BUILD_DIR ?= .aws-sam/build
{% if copier__dynamo_db %}
DYNAMO_ENDPOINT ?= http://localhost:8000
TABLE_NAME ?= RequestsTable-{{copier__stack_name}}
{% endif %}

# Default target
all: build

build:
	sam build {% if copier__package_type != "image" %}--use-container{% endif %} > /dev/null 2>&1

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
	sam local start-api {% if copier__dynamo_db %}--env-vars env_example.json --docker-network lambda-local{% endif %}

invoke:
	sam local invoke HelloWorldFunction --event events/event.json{% if copier__dynamo_db %} --env-vars env_example.json --docker-network lambda-local{% endif %}

{% if copier__dynamo_db %}
dynamo-up:
	@if [ -z "$$(docker network ls --filter name=^lambda-local$$ -q)" ]; then \
		echo "Creating Docker network 'lambda-local'..."; \
		docker network create lambda-local; \
	else \
		echo "Docker network 'lambda-local' already exists."; \
	fi; \
	if [ -f .dynamodb-container-id ] && [ -n "$$(docker ps -q -f id=$$(cat .dynamodb-container-id 2>/dev/null))" ]; then \
		echo "DynamoDB local container is already running with ID: $$(cat .dynamodb-container-id)"; \
	else \
		echo "Starting DynamoDB local container..."; \
		rm -f .dynamodb-container-id 2>/dev/null || true; \
		docker run -d --rm --network lambda-local -p 8000:8000 --name {{copier__stack_name}}-dynamodb-local amazon/dynamodb-local:latest -jar DynamoDBLocal.jar -sharedDb > .dynamodb-container-id; \
		echo "DynamoDB local container started with ID: $$(cat .dynamodb-container-id)"; \
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
	pip install -r requirements.txt{% endif %}

test:
	AWS_SAM_STACK_NAME=$(STACK_NAME) PYTHONPATH=. uv run --with pytest,boto3,requests,pytest-mock pytest -v --disable-warnings --tb=short tests

delete-sandbox:
	sam delete --stack-name $(STACK_NAME)-sandbox

delete:
	sam delete --stack-name $(STACK_NAME)
