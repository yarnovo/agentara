"""Pytest 配置和共享 fixtures。"""

import shutil
import subprocess
import tempfile
from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest
import tomlkit
from tomlkit import items


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """创建临时目录用于测试。"""
    temp_path = tempfile.mkdtemp(prefix="bump-version-test-")
    yield Path(temp_path)
    shutil.rmtree(temp_path)


@pytest.fixture
def git_repo(temp_dir: Path) -> Generator[Path, None, None]:
    """创建一个初始化的 Git 仓库。"""
    # 初始化 Git 仓库
    subprocess.run(["git", "init"], cwd=temp_dir, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=temp_dir, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=temp_dir, check=True)

    # 创建 main 分支
    subprocess.run(["git", "checkout", "-b", "main"], cwd=temp_dir, check=True)

    yield temp_dir


@pytest.fixture
def project_with_pyproject(git_repo: Path) -> Generator[dict[str, Any], None, None]:
    """创建一个带有 pyproject.toml 的项目。"""
    pyproject_data = {
        "project": {"name": "test-package", "version": "1.0.0", "description": "Test package for bump-version"}
    }

    pyproject_path = git_repo / "pyproject.toml"
    with open(pyproject_path, "w") as f:
        f.write(tomlkit.dumps(pyproject_data))

    # 创建初始提交
    subprocess.run(["git", "add", "."], cwd=git_repo, check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=git_repo, check=True)

    yield {"path": git_repo, "config_file": pyproject_path, "config_type": "pyproject.toml"}


@pytest.fixture
def project_with_setup_py(git_repo: Path) -> Generator[dict[str, Any], None, None]:
    """创建一个带有 setup.py 的项目。"""
    setup_py_content = """from setuptools import setup

setup(
    name="test-package",
    version="1.0.0",
    description="Test package for bump-version",
    author="Test Author",
)
"""

    setup_py_path = git_repo / "setup.py"
    with open(setup_py_path, "w") as f:
        f.write(setup_py_content)

    # 创建初始提交
    subprocess.run(["git", "add", "."], cwd=git_repo, check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=git_repo, check=True)

    yield {"path": git_repo, "config_file": setup_py_path, "config_type": "setup.py"}


@pytest.fixture
def mock_user_input(monkeypatch):
    """模拟用户输入的 fixture。"""

    def _mock_input(answers: dict[str, Any]):
        """设置模拟的用户输入答案。"""

        # 直接 mock inquirer 的底层组件
        class MockRender:
            def __init__(self, question, *args, **kwargs):
                self.question = question

            def render(self):
                message = self.question.message
                for key, value in answers.items():
                    if key in message:
                        return value
                # 返回默认值
                if hasattr(self.question, "choices") and self.question.choices:
                    return self.question.choices[0]
                if hasattr(self.question, "default"):
                    return self.question.default
                return True

        # Mock list_input
        def mock_list_input(message, choices=None, **kwargs):
            for key, value in answers.items():
                if key in message:
                    return value
            return choices[0] if choices else None

        # Mock confirm
        def mock_confirm(message, default=True, **kwargs):
            for key, value in answers.items():
                if key in message:
                    return value
            return default

        monkeypatch.setattr("bump_version.cli.list_input", mock_list_input)
        monkeypatch.setattr("bump_version.cli.confirm", mock_confirm)

    return _mock_input


def get_version_from_pyproject(path: Path) -> str:
    """从 pyproject.toml 获取版本号。"""
    with open(path / "pyproject.toml") as f:
        doc = tomlkit.load(f)

    project = doc.get("project")
    if isinstance(project, dict | items.Table) and "version" in project:
        return str(project["version"])

    tool = doc.get("tool")
    if isinstance(tool, dict | items.Table):
        poetry = tool.get("poetry")
        if isinstance(poetry, dict | items.Table) and "version" in poetry:
            return str(poetry["version"])

    raise ValueError("No version found in pyproject.toml")


def get_version_from_setup_py(path: Path) -> str:
    """从 setup.py 获取版本号。"""
    with open(path / "setup.py") as f:
        content = f.read()
    import re

    match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
    if match:
        return match.group(1)
    raise ValueError("No version found in setup.py")


def get_git_tags(path: Path) -> list[str]:
    """获取 Git 标签列表。"""
    result = subprocess.run(["git", "tag"], cwd=path, capture_output=True, text=True, check=True)
    return [tag.strip() for tag in result.stdout.strip().split("\n") if tag.strip()]


def get_last_commit_message(path: Path) -> str:
    """获取最后一次提交的信息。"""
    result = subprocess.run(["git", "log", "-1", "--pretty=%s"], cwd=path, capture_output=True, text=True, check=True)
    return result.stdout.strip()
