"""
测试工具模块
"""
import pytest
from core import utils


class TestFormatBytes:
    """测试 format_bytes 函数"""

    def test_empty_data(self):
        """测试空数据"""
        assert utils.format_bytes(b"") == ""

    def test_normal_data(self):
        """测试正常数据"""
        result = utils.format_bytes(b"hello")
        assert result == "68656c6c6f"

    def test_truncate_long_data(self):
        """测试截断长数据"""
        data = b"x" * 300
        result = utils.format_bytes(data, max_len=100)
        assert result.endswith("...")
        assert len(result) < len(data.hex())

    def test_custom_max_len(self):
        """测试自定义最大长度"""
        data = b"hello world"
        result = utils.format_bytes(data, max_len=5)
        assert result.endswith("...")


class TestDetectEncoding:
    """测试 detect_encoding 函数"""

    def test_empty_data(self):
        """测试空数据"""
        assert utils.detect_encoding(b"") == 'ascii'

    def test_ascii_data(self):
        """测试 ASCII 数据"""
        assert utils.detect_encoding(b"hello") == 'ascii'

    def test_utf8_data(self):
        """测试 UTF-8 数据"""
        assert utils.detect_encoding("你好".encode('utf-8')) == 'utf-8'

    def test_binary_data(self):
        """测试二进制数据"""
        assert utils.detect_encoding(b"\xff\xfe\x00\x01") == 'binary'


class TestTryDecodeText:
    """测试 try_decode_text 函数"""

    def test_empty_data(self):
        """测试空数据"""
        text, success = utils.try_decode_text(b"")
        assert text == ""
        assert success is True

    def test_utf8_decode(self):
        """测试 UTF-8 解码"""
        text, success = utils.try_decode_text("你好".encode('utf-8'))
        assert text == "你好"
        assert success is True

    def test_ascii_decode(self):
        """测试 ASCII 解码"""
        text, success = utils.try_decode_text(b"hello")
        assert text == "hello"
        assert success is True

    def test_specified_encoding(self):
        """测试指定编码"""
        text, success = utils.try_decode_text(b"hello", encoding='ascii')
        assert text == "hello"
        assert success is True

    def test_invalid_encoding(self):
        """测试无效编码"""
        text, success = utils.try_decode_text(b"\xff\xfe", encoding='invalid')
        assert success is False

    def test_binary_data(self):
        """测试二进制数据"""
        text, success = utils.try_decode_text(b"\xff\xfe\x00\x01")
        assert success is False


class TestTryParseJson:
    """测试 try_parse_json 函数"""

    def test_empty_data(self):
        """测试空数据"""
        result, success = utils.try_parse_json(b"")
        assert success is False

    def test_valid_json_object(self):
        """测试有效 JSON 对象"""
        result, success = utils.try_parse_json(b'{"key": "value"}')
        assert success is True
        assert result == {"key": "value"}

    def test_valid_json_array(self):
        """测试有效 JSON 数组"""
        result, success = utils.try_parse_json(b'[1, 2, 3]')
        assert success is True
        assert result == [1, 2, 3]

    def test_invalid_json(self):
        """测试无效 JSON"""
        result, success = utils.try_parse_json(b'not json')
        assert success is False

    def test_non_utf8_data(self):
        """测试非 UTF-8 数据"""
        result, success = utils.try_parse_json(b"\xff\xfe")
        assert success is False


class TestTryParseMsgpack:
    """测试 try_parse_msgpack 函数"""

    def test_empty_data(self):
        """测试空数据"""
        result, success = utils.try_parse_msgpack(b"")
        assert success is False

    def test_valid_msgpack(self):
        """测试有效 MessagePack 数据"""
        if not utils.HAS_MSGPACK:
            pytest.skip("msgpack not installed")

        import msgpack
        packed = msgpack.packb({"key": "value"})
        result, success = utils.try_parse_msgpack(packed)
        assert success is True
        assert result == {"key": "value"}

    def test_invalid_msgpack(self):
        """测试无效 MessagePack 数据"""
        result, success = utils.try_parse_msgpack(b"not msgpack")
        assert success is False


class TestFormatSize:
    """测试 format_size 函数"""

    def test_zero_bytes(self):
        """测试 0 字节"""
        assert utils.format_size(0) == "0 B"

    def test_negative_bytes(self):
        """测试负数字节"""
        assert utils.format_size(-1) == "0 B"

    def test_bytes(self):
        """测试字节级别"""
        assert utils.format_size(100) == "100 B"
        assert utils.format_size(1023) == "1023 B"

    def test_kilobytes(self):
        """测试 KB 级别"""
        assert utils.format_size(1024) == "1.00 KB"
        assert utils.format_size(1536) == "1.50 KB"

    def test_megabytes(self):
        """测试 MB 级别"""
        assert utils.format_size(1024 * 1024) == "1.00 MB"

    def test_gigabytes(self):
        """测试 GB 级别"""
        assert utils.format_size(1024 * 1024 * 1024) == "1.00 GB"

    def test_terabytes(self):
        """测试 TB 级别"""
        result = utils.format_size(1024 * 1024 * 1024 * 1024)
        assert "TB" in result

    def test_custom_precision(self):
        """测试自定义精度"""
        result = utils.format_size(1536, precision=0)
        assert result == "2 KB"


class TestIsPrintable:
    """测试 is_printable 函数"""

    def test_empty_data(self):
        """测试空数据"""
        assert utils.is_printable(b"") is True

    def test_printable_text(self):
        """测试可打印文本"""
        assert utils.is_printable(b"hello world") is True

    def test_text_with_newline(self):
        """测试带换行的文本"""
        assert utils.is_printable(b"hello\nworld") is True

    def test_text_with_tab(self):
        """测试带制表符的文本"""
        assert utils.is_printable(b"hello\tworld") is True

    def test_binary_data(self):
        """测试二进制数据"""
        assert utils.is_printable(b"\x00\x01\x02\x03") is False

    def test_mixed_data(self):
        """测试混合数据"""
        # 主要是可打印字符
        assert utils.is_printable(b"hello\x01world") is True
        # 主要是二进制
        assert utils.is_printable(b"\x00\x01\x02\x03hello") is False

    def test_custom_threshold(self):
        """测试自定义阈值"""
        data = b"hello\x00\x00"  # 5 printable, 2 not
        assert utils.is_printable(data, threshold=0.7) is True
        assert utils.is_printable(data, threshold=0.9) is False


class TestTruncateBytes:
    """测试 truncate_bytes 函数"""

    def test_empty_data(self):
        """测试空数据"""
        result, truncated = utils.truncate_bytes(b"")
        assert result == b""
        assert truncated is False

    def test_short_data(self):
        """测试短数据"""
        result, truncated = utils.truncate_bytes(b"hello", max_len=10)
        assert result == b"hello"
        assert truncated is False

    def test_exact_length(self):
        """测试刚好达到长度"""
        result, truncated = utils.truncate_bytes(b"hello", max_len=5)
        assert result == b"hello"
        assert truncated is False

    def test_long_data(self):
        """测试长数据"""
        data = b"x" * 100
        result, truncated = utils.truncate_bytes(data, max_len=50)
        assert len(result) == 50
        assert truncated is True


class TestSafeRepr:
    """测试 safe_repr 函数"""

    def test_empty_data(self):
        """测试空数据"""
        assert utils.safe_repr(b"") == "(empty)"

    def test_printable_data(self):
        """测试可打印数据"""
        result = utils.safe_repr(b"hello")
        assert result == "hello"

    def test_binary_data(self):
        """测试二进制数据"""
        result = utils.safe_repr(b"\xff\xfe")
        assert result.startswith("<hex>")

    def test_truncated_data(self):
        """测试截断数据"""
        data = b"x" * 200
        result = utils.safe_repr(data, max_len=50)
        assert "..." in result


class TestCalculateHash:
    """测试 calculate_hash 函数"""

    def test_empty_data(self):
        """测试空数据"""
        assert utils.calculate_hash(b"") == ""

    def test_md5(self):
        """测试 MD5"""
        result = utils.calculate_hash(b"hello", algorithm='md5')
        assert result == "5d41402abc4b2a76b9719d911017c592"

    def test_sha1(self):
        """测试 SHA1"""
        result = utils.calculate_hash(b"hello", algorithm='sha1')
        assert result == "aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d"

    def test_sha256(self):
        """测试 SHA256"""
        result = utils.calculate_hash(b"hello", algorithm='sha256')
        expected = "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
        assert result == expected

    def test_unsupported_algorithm(self):
        """测试不支持的算法"""
        with pytest.raises(ValueError):
            utils.calculate_hash(b"hello", algorithm='invalid')
