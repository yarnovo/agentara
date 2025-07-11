"""集成测试 - 参考 JS 版本的测试用例。"""

import subprocess
import sys
from pathlib import Path

import pytest
import tomlkit
from tomlkit import items

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from bump_version.cli import run_version_bump
from tests.conftest import get_git_tags, get_last_commit_message, get_version_from_pyproject


def update_pyproject_version(config_path: Path, new_version: str) -> None:
    """更新 pyproject.toml 中的版本号。"""
    with open(config_path) as f:
        doc = tomlkit.load(f)

    project = doc.get("project")
    if isinstance(project, dict | items.Table):
        project["version"] = new_version

    with open(config_path, "w") as f:
        f.write(tomlkit.dumps(doc))


class TestVersionBumping:
    """版本升级测试。"""

    def test_bump_patch_version_for_production(self, project_with_pyproject, mock_user_input, monkeypatch):
        """测试正式版本的 patch 升级。"""
        project_path = project_with_pyproject["path"]

        # 模拟用户输入
        mock_user_input(
            {
                "选择发布类型": "正式版本 (Production)",
                "选择版本号递增类型": "Patch (修订号): 1.0.0 → 1.0.1",
                "确认执行": True,
            }
        )

        # 设置环境变量，跳过推送
        monkeypatch.setenv("BUMP_VERSION_SKIP_PUSH", "true")

        # 切换到项目目录
        monkeypatch.chdir(project_path)

        # 执行主函数
        try:
            run_version_bump()
        except SystemExit:
            pass

        # 验证版本号更新
        new_version = get_version_from_pyproject(project_path)
        assert new_version == "1.0.1"

        # 验证标签创建
        tags = get_git_tags(project_path)
        assert "v1.0.1" in tags

        # 验证提交信息
        commit_msg = get_last_commit_message(project_path)
        assert commit_msg == "chore: release 1.0.1"

    def test_bump_minor_version_for_production(self, project_with_pyproject, mock_user_input, monkeypatch):
        """测试正式版本的 minor 升级。"""
        project_path = project_with_pyproject["path"]

        mock_user_input(
            {
                "选择发布类型": "正式版本 (Production)",
                "选择版本号递增类型": "Minor (次版本号): 1.0.0 → 1.1.0",
                "确认执行": True,
            }
        )

        monkeypatch.setenv("BUMP_VERSION_SKIP_PUSH", "true")
        monkeypatch.chdir(project_path)

        try:
            run_version_bump()
        except SystemExit:
            pass

        new_version = get_version_from_pyproject(project_path)
        assert new_version == "1.1.0"

        tags = get_git_tags(project_path)
        assert "v1.1.0" in tags

    def test_bump_major_version_for_production(self, project_with_pyproject, mock_user_input, monkeypatch):
        """测试正式版本的 major 升级。"""
        project_path = project_with_pyproject["path"]

        mock_user_input(
            {
                "选择发布类型": "正式版本 (Production)",
                "选择版本号递增类型": "Major (主版本号): 1.0.0 → 2.0.0",
                "确认执行": True,
            }
        )

        monkeypatch.setenv("BUMP_VERSION_SKIP_PUSH", "true")
        monkeypatch.chdir(project_path)

        try:
            run_version_bump()
        except SystemExit:
            pass

        new_version = get_version_from_pyproject(project_path)
        assert new_version == "2.0.0"

        tags = get_git_tags(project_path)
        assert "v2.0.0" in tags


class TestPrereleaseVersions:
    """预发布版本测试。"""

    def test_create_alpha_version_from_production(self, project_with_pyproject, mock_user_input, monkeypatch):
        """测试从正式版本创建 alpha 版本。"""
        project_path = project_with_pyproject["path"]

        mock_user_input(
            {"选择发布类型": "Alpha 版本", "选择版本号递增类型": "Patch (修订号): 1.0.0 → 1.0.1a0", "确认执行": True}
        )

        monkeypatch.setenv("BUMP_VERSION_SKIP_PUSH", "true")
        monkeypatch.chdir(project_path)

        try:
            run_version_bump()
        except SystemExit:
            pass

        new_version = get_version_from_pyproject(project_path)
        assert new_version == "1.0.1a0"

        tags = get_git_tags(project_path)
        assert "v1.0.1a0" in tags

    def test_increment_alpha_version(self, project_with_pyproject, mock_user_input, monkeypatch):
        """测试递增 alpha 版本号。"""
        project_path = project_with_pyproject["path"]

        # 先设置为 alpha 版本
        config_path = project_path / "pyproject.toml"
        update_pyproject_version(config_path, "1.0.0a0")

        # 提交更改
        subprocess.run(["git", "add", "."], cwd=project_path, check=True)
        subprocess.run(["git", "commit", "-m", "Update to alpha"], cwd=project_path, check=True)

        mock_user_input({"选择发布类型": "Alpha 版本", "确认执行": True})

        monkeypatch.setenv("BUMP_VERSION_SKIP_PUSH", "true")
        monkeypatch.chdir(project_path)

        try:
            run_version_bump()
        except SystemExit:
            pass

        new_version = get_version_from_pyproject(project_path)
        assert new_version == "1.0.0a1"

    def test_upgrade_from_alpha_to_beta(self, project_with_pyproject, mock_user_input, monkeypatch):
        """测试从 alpha 升级到 beta。"""
        project_path = project_with_pyproject["path"]

        # 设置为 alpha 版本
        config_path = project_path / "pyproject.toml"
        update_pyproject_version(config_path, "1.0.0a3")

        subprocess.run(["git", "add", "."], cwd=project_path, check=True)
        subprocess.run(["git", "commit", "-m", "Update to alpha.3"], cwd=project_path, check=True)

        mock_user_input({"选择发布类型": "Beta 版本", "确认执行": True})

        monkeypatch.setenv("BUMP_VERSION_SKIP_PUSH", "true")
        monkeypatch.chdir(project_path)

        try:
            run_version_bump()
        except SystemExit:
            pass

        new_version = get_version_from_pyproject(project_path)
        assert new_version == "1.0.0b0"

    def test_upgrade_from_beta_to_rc(self, project_with_pyproject, mock_user_input, monkeypatch):
        """测试从 beta 升级到 rc。"""
        project_path = project_with_pyproject["path"]

        # 设置为 beta 版本
        config_path = project_path / "pyproject.toml"
        update_pyproject_version(config_path, "1.0.0b2")

        subprocess.run(["git", "add", "."], cwd=project_path, check=True)
        subprocess.run(["git", "commit", "-m", "Update to beta.2"], cwd=project_path, check=True)

        mock_user_input({"选择发布类型": "RC 版本", "确认执行": True})

        monkeypatch.setenv("BUMP_VERSION_SKIP_PUSH", "true")
        monkeypatch.chdir(project_path)

        try:
            run_version_bump()
        except SystemExit:
            pass

        new_version = get_version_from_pyproject(project_path)
        assert new_version == "1.0.0rc0"

    def test_convert_rc_to_production(self, project_with_pyproject, mock_user_input, monkeypatch):
        """测试从 rc 转为正式版本。"""
        project_path = project_with_pyproject["path"]

        # 设置为 rc 版本
        config_path = project_path / "pyproject.toml"
        update_pyproject_version(config_path, "1.0.0rc1")

        subprocess.run(["git", "add", "."], cwd=project_path, check=True)
        subprocess.run(["git", "commit", "-m", "Update to rc.1"], cwd=project_path, check=True)

        mock_user_input({"选择发布类型": "正式版本 (Production)", "确认执行": True})

        monkeypatch.setenv("BUMP_VERSION_SKIP_PUSH", "true")
        monkeypatch.chdir(project_path)

        try:
            run_version_bump()
        except SystemExit:
            pass

        new_version = get_version_from_pyproject(project_path)
        assert new_version == "1.0.0"


class TestDevAndPostVersions:
    """测试 Dev 和 Post 版本功能。"""

    def test_create_dev_version_from_production(self, project_with_pyproject, mock_user_input, monkeypatch):
        """测试从正式版本创建 dev 版本。"""
        project_path = project_with_pyproject["path"]

        mock_user_input(
            {"选择发布类型": "Dev 版本", "选择版本号递增类型": "Patch (修订号): 1.0.0 → 1.0.1dev0", "确认执行": True}
        )

        monkeypatch.setenv("BUMP_VERSION_SKIP_PUSH", "true")
        monkeypatch.chdir(project_path)

        try:
            run_version_bump()
        except SystemExit:
            pass

        new_version = get_version_from_pyproject(project_path)
        assert new_version == "1.0.1.dev0"

    def test_increment_dev_version(self, project_with_pyproject, mock_user_input, monkeypatch):
        """测试递增 dev 版本。"""
        project_path = project_with_pyproject["path"]

        # 先设置为 dev 版本
        update_pyproject_version(project_path / "pyproject.toml", "1.0.0.dev0")

        # 提交更改
        subprocess.run(["git", "add", "."], cwd=project_path, check=True)
        subprocess.run(["git", "commit", "-m", "Update to dev version"], cwd=project_path, check=True)

        mock_user_input({"选择发布类型": "Dev 版本", "确认执行": True})

        monkeypatch.setenv("BUMP_VERSION_SKIP_PUSH", "true")
        monkeypatch.chdir(project_path)

        try:
            run_version_bump()
        except SystemExit:
            pass

        new_version = get_version_from_pyproject(project_path)
        assert new_version == "1.0.0.dev1"

    def test_create_post_version_from_production(self, project_with_pyproject, mock_user_input, monkeypatch):
        """测试从正式版本创建 post 版本。"""
        project_path = project_with_pyproject["path"]

        mock_user_input({"选择发布类型": "Post 版本", "确认执行": True})

        monkeypatch.setenv("BUMP_VERSION_SKIP_PUSH", "true")
        monkeypatch.chdir(project_path)

        try:
            run_version_bump()
        except SystemExit:
            pass

        new_version = get_version_from_pyproject(project_path)
        assert new_version == "1.0.0.post0"

    def test_increment_post_version(self, project_with_pyproject, mock_user_input, monkeypatch):
        """测试递增 post 版本。"""
        project_path = project_with_pyproject["path"]

        # 先设置为 post 版本
        update_pyproject_version(project_path / "pyproject.toml", "1.0.0.post0")

        # 提交更改
        subprocess.run(["git", "add", "."], cwd=project_path, check=True)
        subprocess.run(["git", "commit", "-m", "Update to post version"], cwd=project_path, check=True)

        mock_user_input({"选择发布类型": "Post 版本", "确认执行": True})

        monkeypatch.setenv("BUMP_VERSION_SKIP_PUSH", "true")
        monkeypatch.chdir(project_path)

        try:
            run_version_bump()
        except SystemExit:
            pass

        new_version = get_version_from_pyproject(project_path)
        assert new_version == "1.0.0.post1"


class TestErrorHandling:
    """错误处理测试。"""

    def test_abort_on_dirty_working_tree(self, project_with_pyproject, monkeypatch):
        """测试工作区有未提交更改时中止。"""
        project_path = project_with_pyproject["path"]

        # 创建未提交的更改
        readme_path = project_path / "README.md"
        readme_path.write_text("# Test Project\n")

        monkeypatch.setenv("BUMP_VERSION_SKIP_PUSH", "true")
        monkeypatch.chdir(project_path)

        # 应该因为工作区不干净而退出
        with pytest.raises(SystemExit) as exc_info:
            run_version_bump()

        assert exc_info.value.code == 0  # 用户取消

        # 版本号应该没有改变
        version = get_version_from_pyproject(project_path)
        assert version == "1.0.0"

    def test_user_cancel_on_confirmation(self, project_with_pyproject, mock_user_input, monkeypatch):
        """测试用户在确认步骤取消。"""
        project_path = project_with_pyproject["path"]

        mock_user_input(
            {
                "选择发布类型": "正式版本 (Production)",
                "选择版本号递增类型": "Patch (修订号): 1.0.0 → 1.0.1",
                "确认执行": False,  # 用户取消
            }
        )

        monkeypatch.setenv("BUMP_VERSION_SKIP_PUSH", "true")
        monkeypatch.chdir(project_path)

        with pytest.raises(SystemExit) as exc_info:
            run_version_bump()

        assert exc_info.value.code == 0

        # 版本号应该没有改变
        version = get_version_from_pyproject(project_path)
        assert version == "1.0.0"

        # 不应该创建标签
        tags = get_git_tags(project_path)
        assert len(tags) == 0
