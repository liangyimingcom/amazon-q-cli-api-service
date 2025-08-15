# Amazon Q CLI API服务开发工具

.PHONY: help install test lint format clean run dev list-sessions clean-sessions clean-old-sessions export-sessions test-isolation demo health

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

# 会话管理命令
list-sessions:  ## 列出所有会话目录
	python scripts/manage_sessions.py list

clean-sessions:  ## 清理空的会话目录
	python scripts/manage_sessions.py cleanup-empty

clean-old-sessions:  ## 清理过期的会话目录（24小时）
	python scripts/manage_sessions.py cleanup-old --hours 24

export-sessions:  ## 导出会话信息到JSON文件
	python scripts/manage_sessions.py export sessions_info.json
	@echo "会话信息已导出到 sessions_info.json"

# 测试和演示命令
test-isolation:  ## 测试会话隔离功能
	python scripts/test_session_isolation.py

demo:  ## 运行会话隔离演示
	python examples/session_isolation_demo.py

# 健康检查
health:  ## 检查服务健康状态
	curl -f http://localhost:8080/health || exit 1