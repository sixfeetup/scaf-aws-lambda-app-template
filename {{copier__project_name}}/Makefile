.PHONY: build deploy local clean test setup{% if copier__dynamo_db %} dynamo-up dynamo-down create-table{% endif %}

# Configuration
STACK_NAME ?= {{ copier__project_name }}
REGION ?= us-east-1
TEMPLATE_FILE ?= template.yaml
BUILD_DIR ?= .aws-sam/build
{% if copier__dynamo_db %}DYNAMO_ENDPOINT ?= http://localhost:8000{% endif %}

# Default target
all: build

build:
	sam build {% if copier__package_type != "image" %}--use-container{% endif %}

deploy:
	sam deploy --guided

deploy-sandbox:
	sam deploy --stack-name $(STACK_NAME)-sandbox \
        	--capabilities CAPABILITY_IAM \
        	--parameter-overrides StageName=sandbox

local:
	sam local start-api {% if copier__dynamo_db %}--env-vars env_example.json --docker-network lambda-local{% endif %}

invoke:
	sam local invoke HelloWorldFunction --event events/event.json{% if copier__dynamo_db %} --env-vars env_example.json --docker-network lambda-local{% endif %}

{% if copier__dynamo_db %}
dynamo-up:
	@if [ -f .dynamodb-container-id ] && [ -n "$$(docker ps -q -f id=$$(cat .dynamodb-container-id 2>/dev/null))" ]; then \
		echo "DynamoDB local container is already running with ID: $$(cat .dynamodb-container-id)"; \
	else \
		echo "Starting DynamoDB local container..."; \
		rm -f .dynamodb-container-id 2>/dev/null || true; \
		docker run -d --rm -p 8000:8000 --name dynamodb-local amazon/dynamodb-local -jar DynamoDBLocal.jar -sharedDb > .dynamodb-container-id; \
		echo "DynamoDB local container started with ID: $$(cat .dynamodb-container-id)"; \
	fi

dynamo-down:
	@if [ -f .dynamodb-container-id ]; then \
		if [ -n "$$(docker ps -q -f id=$$(cat .dynamodb-container-id 2>/dev/null))" ]; then \
			echo "Stopping DynamoDB local container with ID: $$(cat .dynamodb-container-id)"; \
			docker stop $$(cat .dynamodb-container-id); \
		else \
			echo "No running container found with saved ID"; \
		fi; \
		rm -f .dynamodb-container-id; \
	else \
		echo "No container ID file found"; \
	fi

create-table:
	@# Store the AWS command output in a variable
	$(eval AWS_OUTPUT := $(shell aws dynamodb create-table \
		--table-name $(TABLE_NAME) \
		--attribute-definitions AttributeName=id,AttributeType=S \
		--key-schema AttributeName=id,KeyType=HASH \
		--provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
		--endpoint-url $(DYNAMO_ENDPOINT) \
		--no-cli-pager))

	@# Check if jq exists and use it if available
	@if command -v jq > /dev/null 2>&1; then \
		echo '$(AWS_OUTPUT)' | jq; \
	else \
		echo '$(AWS_OUTPUT)'; \
		echo "\033[33mNote: Install jq for colorized JSON output\033[0m"; \
	fi

setup: dynamo-up create-table{% else %}
setup:
	pip install -r requirements.txt{% endif %}

delete:
	sam delete --stack-name $(STACK_NAME)
