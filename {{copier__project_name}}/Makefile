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
	docker-compose up -d dynamodb-local

dynamo-down:
	dokcer-compose down

create-table:
	aws dynamodb create-table \
    		--table-name RequestsTable \
        	--attribute-definitions \
            	AttributeName=ip_address,AttributeType=S \
            	AttributeName=timestamp,AttributeType=S \
            	--key-schema \
            	AttributeName=ip_address,KeyType=HASH \
            	AttributeName=timestamp,KeyType=RANGE \
        	--billing-mode PAY_PER_REQUEST \
        	--endpoint-url $(DYNAMO_ENDPOINT)

setup: dynamo-up create-table{% else %}
setup:
	pip install -r requirements.txt{% endif %}

delete:
	sam delete --stack-name $(STACK_NAME)
