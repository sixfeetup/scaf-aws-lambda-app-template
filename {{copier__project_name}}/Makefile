.PHONY: build deploy local clean test setup{% if copier__dynamo_db %} dynamo-up dynamo-down wait-for-dynamodb create-table{% endif %}

# Configuration
STACK_NAME ?= {{ copier__stack_name }}
REGION ?= {{copier__aws_region}}
TEMPLATE_FILE ?= template.yaml
BUILD_DIR ?= .aws-sam/build
AWS_PROFILE ?= {{copier__aws_profile}}
{% if copier__dynamo_db %}
DYNAMO_ENDPOINT ?= http://localhost:8000
TABLE_NAME ?= RequestsTable-{{copier__stack_name}}
CONTAINER_NAME ?= {{copier__stack_name}}-dynamodb-local
NETWORK_NAME ?= {{copier__stack_name}}-network
{% endif %}

## Build & Deploy

build:  ## Build the AWS SAM project
	@sam build > /dev/null 2>build_error.log && echo "Build succeeded!" || (cat build_error.log && exit 1)
	@rm -f build_error.log

validate:  ## Validate the SAM template with linting
	sam validate --lint

deploy:  ## Deploy the stack using interactive guided mode
	sam deploy --guided --profile $(AWS_PROFILE) \
	{% if copier__package_type == "image" %}--resolve-image-repos{% endif %}

## Local Development

local:  ## Start the local API using SAM
	sam local start-api {% if copier__dynamo_db %}--env-vars env_example.json --docker-network $(NETWORK_NAME){% endif %}

invoke:  ## Invoke a Lambda function locally using an event payload
	sam local invoke HelloWorldFunction --event events/event.json{% if copier__dynamo_db %} --env-vars env_example.json --docker-network $(NETWORK_NAME){% endif %}

{% if copier__dynamo_db %}
## DynamoDB (Local) Setup

dynamo-up:  ## Start a local DynamoDB instance in a Docker container
	@if [ -z "$$(docker network ls --filter name=^$(NETWORK_NAME)$$ -q)" ]; then \
		echo "Creating Docker network '$(NETWORK_NAME)'..."; \
		docker network create $(NETWORK_NAME); \
	else \
		echo "Docker network '$(NETWORK_NAME)' already exists."; \
	fi; \
	if [ -n "$$(docker ps -q -f name=^/$(CONTAINER_NAME)$$)" ]; then \
		echo "DynamoDB local container '$(CONTAINER_NAME)' is already running."; \
	else \
		echo "Starting DynamoDB local container..."; \
		docker run -d --rm --network $(NETWORK_NAME) --name $(CONTAINER_NAME) amazon/dynamodb-local:latest -jar DynamoDBLocal.jar -sharedDb; \
		echo "DynamoDB local container '$(CONTAINER_NAME)' started."; \
	fi

wait-for-dynamodb:  ## Wait until DynamoDB Local is ready inside the container
	@echo "Waiting for DynamoDB Local to be ready (inside container)..."
	@attempts=0; \
	until docker exec $(CONTAINER_NAME) curl -s http://localhost:8000 >/dev/null 2>&1; do \
		if [ $$attempts -ge 10 ]; then \
			echo "DynamoDB Local did not become ready in time"; \
			exit 1; \
		fi; \
		echo "Waiting..."; \
		sleep 1; \
		attempts=$$((attempts + 1)); \
	done; \
	echo "DynamoDB Local is ready."

create-table:  ## Create the DynamoDB table in the local container
	@echo "Creating DynamoDB table '$(TABLE_NAME)' in container '$(CONTAINER_NAME)'..."
	@docker run --rm --network $(NETWORK_NAME) \
		-e AWS_ACCESS_KEY_ID=dummy \
		-e AWS_SECRET_ACCESS_KEY=dummy \
		amazon/aws-cli \
		dynamodb create-table \
		--table-name $(TABLE_NAME) \
		--attribute-definitions \
		AttributeName=ip_address,AttributeType=S \
		AttributeName=timestamp,AttributeType=S \
		--key-schema \
		AttributeName=ip_address,KeyType=HASH \
		AttributeName=timestamp,KeyType=RANGE \
		--billing-mode PAY_PER_REQUEST \
		--endpoint-url http://$(CONTAINER_NAME):8000 \
		--region $(REGION)

list-records:  ## List all records in the DynamoDB table
	@echo "Listing records from DynamoDB table '$(TABLE_NAME)'..."
	@docker run --rm --network $(NETWORK_NAME) \
		-e AWS_ACCESS_KEY_ID=dummy \
		-e AWS_SECRET_ACCESS_KEY=dummy \
		amazon/aws-cli \
		dynamodb scan \
		--table-name $(TABLE_NAME) \
		--endpoint-url http://$(CONTAINER_NAME):8000 \
		--region $(REGION)

count-records:  ## Count the number of records in the DynamoDB table
	@echo "Counting records in DynamoDB table '$(TABLE_NAME)'..."
	@docker run --rm --network $(NETWORK_NAME) \
		-e AWS_ACCESS_KEY_ID=dummy \
		-e AWS_SECRET_ACCESS_KEY=dummy \
		amazon/aws-cli \
		dynamodb scan \
		--table-name $(TABLE_NAME) \
		--select "COUNT" \
		--endpoint-url http://$(CONTAINER_NAME):8000 \
		--region $(REGION)

setup: dynamo-up wait-for-dynamodb create-table  ## Set up local DynamoDB environment{% else %}
setup: ## Install Python dependencies
	pip3 install -r src/requirements.txt{% endif %}

## Testing

test:  ## Run Python unit tests using uv and pytest
	AWS_SAM_STACK_NAME=$(STACK_NAME) PYTHONPATH=. uv run --with pytest,boto3,requests,pytest-mock pytest -v --disable-warnings --tb=short tests

## Cleanup

down:  ## Stop and remove local DynamoDB container and network
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

delete:  ## Delete the deployed SAM stack
	sam delete --stack-name $(STACK_NAME)

## Help

help: ## Show the list of all the commands and their help text
	@awk 'BEGIN 	{ FS = ":.*##"; target="";printf "\nUsage:\n  make \033[36m<target>\033[33m\n\nTargets:\033[0m\n" } \
		/^[a-zA-Z_-]+:.*?##/ { if(target=="")print ""; target=$$1; printf " \033[36m%-10s\033[0m %s\n\n", $$1, $$2 } \
		/^([a-zA-Z_-]+):/ {if(target=="")print "";match($$0, "(.*):"); target=substr($$0,RSTART,RLENGTH) } \
		/^\t## (.*)/ { match($$0, "[^\t#:\\\\]+"); txt=substr($$0,RSTART,RLENGTH);printf " \033[36m%-10s\033[0m", target; printf " %s\n", txt ; target=""} \
		/^## .*/ {match($$0, "## (.+)$$"); txt=substr($$0,4,RLENGTH);printf "\n\033[33m%s\033[0m\n", txt ; target=""} \
	' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help
