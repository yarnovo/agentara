.PHONY: help sync test format lint typecheck check all build publish clean pre-commit pre-commit-run

# 默认目标：显示帮助信息
help:
	@echo "agentara 开发常用命令："
	@echo ""
	@echo "开发环境设置："
	@echo "  make sync                 - 同步依赖（使用 uv sync）"
	@echo ""
	@echo "代码质量："
	@echo "  make test          - 运行测试"
	@echo "  make format        - 格式化代码（ruff format + ruff fix）"
	@echo "  make lint          - 代码检查（ruff）"
	@echo "  make typecheck     - 类型检查（pyright）"
	@echo "  make check         - 运行所有检查（lint + typecheck + test）"
	@echo ""
	@echo "Pre-commit hooks："
	@echo "  make pre-commit     - 安装 pre-commit hooks"
	@echo "  make pre-commit-run - 运行 pre-commit 检查（不提交）"
	@echo ""
	@echo "构建和发布："
	@echo "  make build         - 构建包"
	@echo "  make publish       - 发布到 PyPI"
	@echo ""
	@echo "清理："
	@echo "  make clean         - 清理构建文件和缓存"

# 同步依赖（包括开发依赖）
sync:
	uv sync

# 运行测试
test:
	uv run pytest

# 代码格式化
format:
	uv run ruff format agentara/ tests/
	uv run ruff check --fix agentara/ tests/

# 代码检查
lint:
	uv run ruff check agentara/

# 类型检查
typecheck:
	uv run pyright agentara/

# 运行所有检查
check: lint typecheck test

# 构建包
build:
	uv build

# 发布到 PyPI
publish:
	uv publish

# 安装 pre-commit hooks
pre-commit:
	uv run pre-commit install
	uv run pre-commit install --hook-type pre-push
	@echo "Pre-commit hooks installed successfully!"

# 运行 pre-commit 检查（不提交）
pre-commit-run:
	uv run pre-commit run --all-files

# 清理构建文件和缓存
clean:
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete