# 测试指南

本文档详细说明如何在本地测试 bumpster 工具，包括类似 npm link 的本地开发测试流程、全局安装和卸载方法。

## 目录

- [本地开发测试](#本地开发测试)
- [全局安装与卸载](#全局安装与卸载)
- [单元测试](#单元测试)
- [集成测试](#集成测试)
- [测试覆盖率](#测试覆盖率)
- [调试技巧](#调试技巧)

## 本地开发测试

### 1. 使用 uv tool install -e（类似 npm link）

这是推荐的本地开发测试方式，相当于 npm 生态中的 `npm link`：

```bash
# 在项目根目录执行
uv tool install -e .

# 现在可以在任何地方使用 bump 命令
bump --help
bump-py --help
```

**优点**：
- 实时反映代码修改（editable 安装）
- 全局可用，方便测试
- 无需重复安装

### 2. 使用 uv run（直接运行）

不安装到全局，直接在项目目录运行：

```bash
# 在项目根目录
uv run bump --help
uv run python -m bump_version.cli --help
```

### 3. 使用 Makefile 快捷命令

项目提供了便捷的 Makefile 命令：

```bash
# 全局安装开发版本
make dev-install-global

# 卸载开发版本
make dev-uninstall-global
```

## 全局安装与卸载

### 全局安装

#### 1. 从 PyPI 安装（发布后）

```bash
# 使用 uv
uv tool install bumpster

# 使用 pip
pip install --user bumpster
```

#### 2. 从本地源码安装

```bash
# 开发模式（推荐）
uv tool install -e .

# 或构建后安装
uv tool install dist/bumpster-*.whl
```

#### 3. 从 Git 仓库安装

```bash
# 直接从 GitHub 安装
uv tool install git+https://github.com/yarnovo/bumpster-py.git

# 安装特定分支或标签
uv tool install git+https://github.com/yarnovo/bumpster-py.git@main
uv tool install git+https://github.com/yarnovo/bumpster-py.git@v0.1.1
```

### 全局卸载

```bash
# 使用 uv
uv tool uninstall bumpster

# 如果使用 pip 安装
pip uninstall bumpster
```

### 查看已安装的工具

```bash
# 列出所有通过 uv tool 安装的工具
uv tool list

# 查看特定工具信息
uv tool show bumpster
```

## 单元测试

### 运行所有测试

```bash
# 使用 make
make test

# 或直接使用 pytest
uv run pytest

# 运行特定测试文件
uv run pytest tests/test_cli.py

# 运行特定测试函数
uv run pytest tests/test_cli.py::test_validate_command
```

### 运行特定类型的测试

```bash
# 只运行单元测试
uv run pytest -m unit

# 只运行集成测试
uv run pytest -m integration

# 跳过慢速测试
uv run pytest -m "not slow"
```

### 测试输出选项

```bash
# 详细输出
uv run pytest -v

# 显示打印输出
uv run pytest -s

# 失败时进入调试
uv run pytest --pdb

# 只运行上次失败的测试
uv run pytest --lf
```

## 集成测试

### 测试版本升级流程

```bash
# 1. 创建测试项目
mkdir test-project
cd test-project

# 2. 初始化 pyproject.toml
cat > pyproject.toml << EOF
[project]
name = "test-project"
version = "0.1.0"
EOF

# 3. 初始化 Git
git init
git add .
git commit -m "Initial commit"

# 4. 测试版本升级
bump

# 5. 验证结果
cat pyproject.toml  # 检查版本号
git log --oneline  # 检查提交
git tag            # 检查标签
```

### 测试版本验证功能

```bash
# 测试有效版本
bump validate 1.0.0
bump validate 1.0.0a1
bump validate 1.0.0.dev0

# 测试无效版本
bump validate invalid
bump validate 1.0
```

## 测试覆盖率

### 生成覆盖率报告

```bash
# 运行测试并生成覆盖率
make test

# 或使用详细命令
uv run pytest --cov=bump_version --cov-report=html --cov-report=term

# 查看 HTML 报告
open htmlcov/index.html  # macOS
# 或
xdg-open htmlcov/index.html  # Linux
```

### 覆盖率目标

- 单元测试覆盖率目标：>= 80%
- 关键路径覆盖率目标：100%
- 集成测试：覆盖主要用户流程

## 调试技巧

### 1. 使用调试模式

```bash
# 设置环境变量启用调试
export DEBUG=1
bump

# 或直接在命令中设置
DEBUG=1 bump
```

### 2. 使用 Python 调试器

```python
# 在代码中添加断点
import pdb; pdb.set_trace()

# 或使用更现代的 breakpoint()
breakpoint()
```

### 3. 查看详细日志

```bash
# 使用 -v 或 --verbose 选项
bump -v
bump-py --verbose
```

### 4. 测试特定场景

```bash
# 测试干跑模式（不实际执行）
bump --dry-run

# 干跑模式的特点：
# - 显示所有操作步骤
# - 显示将要执行的 Git 命令
# - 不修改任何文件
# - 不创建提交或标签
# - 完全无副作用
```

## 常见测试场景

### 1. 测试预发布版本

```bash
# 创建 alpha 版本
echo "选择 pre-release -> alpha"

# 创建 beta 版本
echo "选择 pre-release -> beta"

# 创建 rc 版本
echo "选择 pre-release -> rc"
```

### 2. 测试 Git 集成

```bash
# 测试不在 Git 仓库中
cd /tmp
mkdir no-git && cd no-git
echo '[project]\nname="test"\nversion="1.0.0"' > pyproject.toml
bump  # 应该报错

# 测试工作区不干净
cd /path/to/project
echo "test" > test.txt
bump  # 应该提示工作区不干净
```

### 3. 测试配置文件支持

```bash
# 测试 setup.py（如果支持）
# 测试 pyproject.toml
# 测试没有配置文件的情况
```

## 持续集成测试

### GitHub Actions 本地测试

使用 [act](https://github.com/nektos/act) 在本地运行 GitHub Actions：

```bash
# 安装 act
brew install act  # macOS
# 或查看 https://github.com/nektos/act 其他安装方式

# 运行工作流
act push
act pull_request
```

## 性能测试

### 测试大型项目

```bash
# 测试在大型 monorepo 中的性能
time bump validate 1.0.0

# 测试版本历史很长的项目
# （有很多标签的 Git 仓库）
```

## 测试检查清单

在发布前，确保完成以下测试：

- [ ] 所有单元测试通过
- [ ] 所有集成测试通过
- [ ] 测试覆盖率达标
- [ ] 在干净的环境中测试全局安装
- [ ] 测试所有命令行选项
- [ ] 测试错误处理（无效输入、权限问题等）
- [ ] 在不同 Python 版本中测试（3.12+）
- [ ] 测试跨平台兼容性（Windows/macOS/Linux）

## 故障排查

### 常见问题

1. **命令找不到**
   ```bash
   # 检查是否正确安装
   uv tool list | grep bumpster
   
   # 检查 PATH
   echo $PATH | grep -o "[^:]*/.local/bin"
   ```

2. **权限问题**
   ```bash
   # 确保有执行权限
   ls -la $(which bump)
   ```

3. **依赖冲突**
   ```bash
   # 重新创建虚拟环境
   rm -rf .venv
   uv sync
   ```

## 相关文档

- [开发指南](DEVELOPMENT.md) - 开发环境设置
- [部署指南](DEPLOYMENT.md) - 发布流程
- [项目说明](README.md) - 使用说明