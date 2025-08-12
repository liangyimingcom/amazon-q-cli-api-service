# Amazon Q CLI API服务开发工具

.PHONY: help install test lint format clean run dev

help:  ## 显示帮助信息
	@echo "Amazon Q CLI API服务开发工具"
	@echo ""
	@echo "可用命令:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

install:  ## 安装依赖包
	pip install -r requirements.txt

test:  ## 运行所有测试
	pytest

test-unit:  ## 运行单元测试
	pytest tests/unit/ -m unit

test-integration:  ## 运行集成测试
	pytest tests/integration/ -m integration

test-coverage:  ## 运行测试并生成覆盖率报告
	pytest --cov=qcli_api_service --cov-report=html --cov-report=term

lint:  ## 代码检查
	flake8 qcli_api_service/ tests/
	mypy qcli_api_service/

format:  ## 代码格式化
	black qcli_api_service/ tests/ app.py

clean:  ## 清理临时文件
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf *.log

run:  ## 运行服务（生产模式）
	python app.py

dev:  ## 运行服务（开发模式）
	DEBUG=true python app.py

check:  ## 运行所有检查（测试、代码检查、格式化）
	make format
	make lint
	make test