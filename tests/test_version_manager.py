"""版本管理器单元测试。"""

import pytest
from packaging.version import InvalidVersion, Version

from bump_version.version_manager import VersionManager


class TestVersionParsing:
    """测试版本号解析。"""

    def test_parse_simple_version(self):
        """测试解析简单版本号。"""
        manager = VersionManager()
        result = manager.parse_version("1.2.3")

        assert result is not None
        assert result.major == 1
        assert result.minor == 2
        assert result.patch == 3
        assert result.prerelease_type is None
        assert result.prerelease_num is None

    def test_parse_alpha_version_compact(self):
        """测试解析紧凑格式的 alpha 版本。"""
        manager = VersionManager()
        result = manager.parse_version("1.0.0a0")

        assert result is not None
        assert result.major == 1
        assert result.minor == 0
        assert result.patch == 0
        assert result.prerelease_type == "a"
        assert result.prerelease_num == 0

    def test_parse_beta_version_dotted(self):
        """测试解析点分格式的 beta 版本。"""
        manager = VersionManager()
        result = manager.parse_version("2.1.0.beta1")

        assert result is not None
        assert result.major == 2
        assert result.minor == 1
        assert result.patch == 0
        assert result.prerelease_type == "b"
        assert result.prerelease_num == 1

    def test_parse_rc_version(self):
        """测试解析 RC 版本。"""
        manager = VersionManager()
        result = manager.parse_version("3.0.0rc2")

        assert result is not None
        assert result.major == 3
        assert result.minor == 0
        assert result.patch == 0
        assert result.prerelease_type == "rc"
        assert result.prerelease_num == 2

    def test_parse_dev_version(self):
        """测试解析开发版本。"""
        manager = VersionManager()
        result = manager.parse_version("1.0.0.dev0")

        assert result is not None
        assert result.prerelease_type == "dev"
        assert result.prerelease_num == 0

    def test_parse_dev_version_compact(self):
        """测试解析紧凑格式的开发版本。"""
        manager = VersionManager()
        result = manager.parse_version("1.0.0dev3")

        assert result is not None
        assert result.prerelease_type == "dev"
        assert result.prerelease_num == 3

    def test_parse_post_version(self):
        """测试解析 post 版本。"""
        manager = VersionManager()
        result = manager.parse_version("1.0.0.post1")

        assert result is not None
        assert result.prerelease_type == "post"
        assert result.prerelease_num == 1

    def test_parse_post_version_compact(self):
        """测试解析紧凑格式的 post 版本。"""
        manager = VersionManager()
        result = manager.parse_version("2.3.4post5")

        assert result is not None
        assert result.major == 2
        assert result.minor == 3
        assert result.patch == 4
        assert result.prerelease_type == "post"
        assert result.prerelease_num == 5

    def test_parse_version_with_v_prefix(self):
        """测试解析带 v 前缀的版本号。"""
        manager = VersionManager()
        result = manager.parse_version("v1.2.3")

        assert result is not None
        assert result.major == 1
        assert result.minor == 2
        assert result.patch == 3

    def test_parse_invalid_version(self):
        """测试解析无效版本号。"""
        manager = VersionManager()

        assert manager.parse_version("invalid") is None
        assert manager.parse_version("not-a-version") is None
        assert manager.parse_version("") is None


class TestVersionBumping:
    """测试版本号升级。"""

    def test_bump_patch_version(self):
        """测试 patch 版本升级。"""
        manager = VersionManager()
        result = manager.get_next_version("1.2.3", "patch", False, None)
        assert result == "1.2.4"

    def test_bump_minor_version(self):
        """测试 minor 版本升级。"""
        manager = VersionManager()
        result = manager.get_next_version("1.2.3", "minor", False, None)
        assert result == "1.3.0"

    def test_bump_major_version(self):
        """测试 major 版本升级。"""
        manager = VersionManager()
        result = manager.get_next_version("1.2.3", "major", False, None)
        assert result == "2.0.0"

    def test_create_alpha_from_production(self):
        """测试从正式版本创建 alpha 版本。"""
        manager = VersionManager()
        result = manager.get_next_version("1.0.0", "patch", True, "a")
        assert result == "1.0.1a0"

    def test_increment_alpha_version(self):
        """测试递增 alpha 版本号。"""
        manager = VersionManager()
        result = manager.get_next_version("1.0.0a0", "patch", True, "a")
        assert result == "1.0.0a1"

    def test_upgrade_alpha_to_beta(self):
        """测试从 alpha 升级到 beta。"""
        manager = VersionManager()
        result = manager.get_next_version("1.0.0a3", "patch", True, "b")
        assert result == "1.0.0b0"

    def test_upgrade_beta_to_rc(self):
        """测试从 beta 升级到 rc。"""
        manager = VersionManager()
        result = manager.get_next_version("1.0.0b2", "patch", True, "rc")
        assert result == "1.0.0rc0"

    def test_convert_rc_to_production(self):
        """测试从 rc 转为正式版本。"""
        manager = VersionManager()
        result = manager.get_next_version("1.0.0rc1", "patch", False, None)
        assert result == "1.0.0"

    def test_downgrade_prerelease_type(self):
        """测试降级预发布类型（如从 beta 到 alpha）。"""
        manager = VersionManager()
        # 虽然是降级，但仍然允许
        result = manager.get_next_version("1.0.0b1", "patch", True, "a")
        assert result == "1.0.0a0"

    def test_major_version_with_prerelease(self):
        """测试主版本号升级并创建预发布版本。"""
        manager = VersionManager()
        result = manager.get_next_version("1.5.3", "major", True, "a")
        assert result == "2.0.0a0"

    def test_dev_version_increment(self):
        """测试递增 dev 版本号。"""
        manager = VersionManager()
        result = manager.get_next_version("1.0.0.dev0", "patch", True, "dev")
        assert result == "1.0.0.dev1"

    def test_upgrade_dev_to_alpha(self):
        """测试从 dev 升级到 alpha。"""
        manager = VersionManager()
        result = manager.get_next_version("1.0.0.dev3", "patch", True, "a")
        assert result == "1.0.0a0"

    def test_create_post_from_production(self):
        """测试从正式版本创建 post 版本。"""
        manager = VersionManager()
        result = manager.get_next_version("1.0.0", "patch", True, "post")
        assert result == "1.0.0.post0"

    def test_increment_post_version(self):
        """测试递增 post 版本号。"""
        manager = VersionManager()
        result = manager.get_next_version("1.0.0.post0", "patch", True, "post")
        assert result == "1.0.0.post1"

    def test_cannot_upgrade_prerelease_to_post(self):
        """测试不能从预发布版本直接升级到 post。"""
        manager = VersionManager()
        with pytest.raises(ValueError, match="不能从预发布版本直接升级到 post 版本"):
            manager.get_next_version("1.0.0a0", "patch", True, "post")

    def test_cannot_downgrade_from_post(self):
        """测试不能从 post 版本降级到预发布版本。"""
        manager = VersionManager()
        with pytest.raises(ValueError, match="不能从 post 版本回到"):
            manager.get_next_version("1.0.0.post1", "patch", True, "a")


class TestEdgeCases:
    """测试边界情况。"""

    def test_version_with_zeros(self):
        """测试包含零的版本号。"""
        manager = VersionManager()
        result = manager.get_next_version("0.0.1", "patch", False, None)
        assert result == "0.0.2"

        result = manager.get_next_version("0.1.0", "minor", False, None)
        assert result == "0.2.0"

    def test_large_version_numbers(self):
        """测试大版本号。"""
        manager = VersionManager()
        result = manager.get_next_version("99.99.99", "patch", False, None)
        assert result == "99.99.100"

        result = manager.get_next_version("99.99.99", "minor", False, None)
        assert result == "99.100.0"

    def test_invalid_version_raises_error(self):
        """测试无效版本号抛出错误。"""
        manager = VersionManager()

        with pytest.raises(ValueError, match="无效的版本号格式"):
            manager.get_next_version("invalid", "patch", False, None)


class TestPEP440Compliance:
    """测试生成的版本号是否符合 PEP 440 规范。"""

    def test_all_generated_versions_are_pep440_compliant(self):
        """测试所有生成的版本号都符合 PEP 440 规范。"""
        manager = VersionManager()

        test_cases = [
            # (当前版本, 发布类型, 是否预发布, 预发布类型)
            ("1.0.0", "patch", False, None),
            ("1.0.0", "minor", False, None),
            ("1.0.0", "major", False, None),
            ("1.0.0", "patch", True, "a"),
            ("1.0.0", "patch", True, "b"),
            ("1.0.0", "patch", True, "rc"),
            ("1.0.0", "patch", True, "dev"),
            ("1.0.0", "patch", True, "post"),
            ("1.0.0a0", "patch", True, "a"),
            ("1.0.0a0", "patch", True, "b"),
            ("1.0.0b0", "patch", True, "rc"),
            ("1.0.0rc0", "patch", False, None),
            ("1.0.0.dev0", "patch", True, "dev"),
            ("1.0.0.dev0", "patch", True, "a"),
            ("2.5.3", "major", True, "a"),
            ("0.1.0", "minor", True, "b"),
            ("1.0.0.post0", "patch", True, "post"),
        ]

        for current, release_type, is_prerelease, prerelease_type in test_cases:
            # 跳过不允许的转换
            if current.startswith("1.0.0a0") and prerelease_type == "post":
                continue
            if "post" in current and prerelease_type in ["a", "b", "rc", "dev"]:
                continue

            new_version = manager.get_next_version(current, release_type, is_prerelease, prerelease_type)

            # 使用 packaging 库验证版本号
            try:
                Version(new_version)
                # 如果没有抛出异常，说明版本号有效
                assert True, f"版本号 {new_version} 符合 PEP 440 规范"
            except InvalidVersion:
                pytest.fail(f"生成的版本号 {new_version} 不符合 PEP 440 规范（从 {current} 升级）")

    def test_parsed_versions_are_pep440_compliant(self):
        """测试解析的版本号格式符合 PEP 440。"""
        manager = VersionManager()

        valid_versions = [
            "1.0.0",
            "1.0.0a0",
            "1.0.0b1",
            "1.0.0rc2",
            "1.0.0.dev3",
            "1.0.0dev3",
            "1.0.0.post4",
            "1.0.0post4",
            "2.1.0.beta1",
            "3.0.0.alpha0",
            "0.0.1",
            "99.99.99",
        ]

        for version in valid_versions:
            parsed = manager.parse_version(version)
            if parsed:
                # 重构版本号
                reconstructed = f"{parsed.major}.{parsed.minor}.{parsed.patch}"
                if parsed.prerelease_type:
                    if parsed.prerelease_type in ["dev", "post"]:
                        reconstructed += f".{parsed.prerelease_type}{parsed.prerelease_num}"
                    else:
                        reconstructed += f"{parsed.prerelease_type}{parsed.prerelease_num}"

                # 验证重构的版本号符合 PEP 440
                try:
                    Version(reconstructed)
                except InvalidVersion:
                    pytest.fail(f"重构的版本号 {reconstructed} 不符合 PEP 440 规范")
