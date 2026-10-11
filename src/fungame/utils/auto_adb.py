"""通过 ADB 操作已连接设备的受控工具。"""

import os
import platform
import re
import shlex

from farlog import getLogger
from funshell import run_shell

logger = getLogger("fungame")

_ALLOWED_ADB_COMMANDS = frozenset(
    {"connect", "devices", "disconnect", "shell", "version"}
)
_HOST_LABEL_PATTERN = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?")


def _validate_text(value: str, name: str) -> str:
    """验证命令参数文本。"""
    if not isinstance(value, str) or not value or "\x00" in value:
        raise ValueError(f"{name} 必须是非空且不含 NUL 字符的字符串")
    return value


def _validate_coordinate(value: int, name: str) -> int:
    """验证 ADB 坐标为整数。"""
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} 必须是整数")
    return value


def _validate_port(port: int | str) -> int:
    """验证 TCP 端口范围。"""
    try:
        value = int(port)
    except (TypeError, ValueError) as err:
        raise ValueError("port 必须是 1 到 65535 的整数") from err
    if not 1 <= value <= 65535:
        raise ValueError("port 必须是 1 到 65535 的整数")
    return value


def _validate_host(host: str) -> str:
    """验证 IPv4 地址或主机名的字符格式。"""
    host = _validate_text(host, "ip")
    if len(host) > 253 or any(
        not _HOST_LABEL_PATTERN.fullmatch(label) for label in host.split(".")
    ):
        raise ValueError("ip 必须是 IPv4 地址或有效主机名")
    return host


def _run_adb(adb_path: str, *arguments: str) -> str:
    """安全地组合 ADB 参数后执行命令。"""
    return run_shell(shlex.join([adb_path, *arguments]), printf=False)


def check_phone() -> str:
    """查看当前由 ADB 识别到的设备。

    :return: ``adb devices`` 的标准输出。
    """
    stdout = _run_adb("adb", "devices")
    logger.info(stdout)
    return stdout


def copy_file_to_local(
    from_path: str = "/sdcard/screenshots.png", to_path: str = "screenshots.png"
) -> str:
    """将设备文件复制到本地。

    :param from_path: 设备端文件路径。
    :param to_path: 本地目标文件路径。
    :return: ADB 命令的标准输出。
    :raises ValueError: 当路径为空或包含 NUL 字符时抛出。
    """
    from_path = _validate_text(from_path, "from_path")
    to_path = _validate_text(to_path, "to_path")
    stdout = _run_adb("adb", "pull", from_path, to_path)
    logger.info("copy file from {} to {}", from_path, to_path)
    return stdout


def screenshot_to_phone(file_path: str = "/sdcard/screenshots.png") -> str:
    """在设备上截图并保存到指定路径。

    :param file_path: 设备端截图保存路径。
    :return: ADB 命令的标准输出。
    :raises ValueError: 当路径为空或包含 NUL 字符时抛出。
    """
    file_path = _validate_text(file_path, "file_path")
    stdout = _run_adb("adb", "shell", "/system/bin/screencap", "-p", file_path)
    logger.info("screenshots and save to phone {}", file_path)
    return stdout


def screenshot_to_local(file_path: str = "screenshots.png") -> str:
    """在设备上截图后复制到本地。

    :param file_path: 本地截图保存路径。
    :return: 复制命令的标准输出。
    """
    file_path = _validate_text(file_path, "file_path")
    screenshot_to_phone()
    return copy_file_to_local(to_path=file_path)


def swipe(x1: int, y1: int, x2: int, y2: int) -> str:
    """模拟从一个坐标滑动到另一个坐标。

    :param x1: 起点横坐标。
    :param y1: 起点纵坐标。
    :param x2: 终点横坐标。
    :param y2: 终点纵坐标。
    :return: ADB 命令的标准输出。
    :raises TypeError: 当任一坐标不是整数时抛出。
    """
    coordinates = [
        _validate_coordinate(value, name)
        for name, value in zip(("x1", "y1", "x2", "y2"), (x1, y1, x2, y2))
    ]
    stdout = _run_adb(
        "adb", "shell", "input", "swipe", *(str(value) for value in coordinates)
    )
    logger.info("swipe position {} {} {} {}", *coordinates)
    return stdout


def click(axis_x: int, axis_y: int) -> str:
    """模拟点击设备坐标。

    :param axis_x: 点击位置横坐标。
    :param axis_y: 点击位置纵坐标。
    :return: ADB 命令的标准输出。
    :raises TypeError: 当任一坐标不是整数时抛出。
    """
    axis_x = _validate_coordinate(axis_x, "axis_x")
    axis_y = _validate_coordinate(axis_y, "axis_y")
    stdout = _run_adb("adb", "shell", "input", "tap", str(axis_x), str(axis_y))
    logger.info("click position {} {}", axis_x, axis_y)
    return stdout


def connect_ip(ip: str, port: int | str = 5555) -> str:
    """通过 TCP/IP 连接设备。

    :param ip: 设备的 IP 地址或主机名。
    :param port: ADB TCP 端口，范围为 1 到 65535。
    :return: ADB 命令的标准输出。
    :raises ValueError: 当地址无效或端口不在有效范围内时抛出。
    """
    ip = _validate_host(ip)
    port = _validate_port(port)
    stdout = _run_adb("adb", "connect", f"{ip}:{port}")
    logger.info("connected to {}:{}", ip, port)
    return stdout


def disconnect_ip(ip: str, port: int | str = 5555) -> str:
    """断开通过 TCP/IP 连接的设备。

    :param ip: 设备的 IP 地址或主机名。
    :param port: ADB TCP 端口，范围为 1 到 65535。
    :return: ADB 命令的标准输出。
    :raises ValueError: 当地址无效或端口不在有效范围内时抛出。
    """
    ip = _validate_host(ip)
    port = _validate_port(port)
    stdout = _run_adb("adb", "disconnect", f"{ip}:{port}")
    logger.info("disconnected to {}:{}", ip, port)
    return stdout


class AutoADB:
    """封装本机 ADB 可执行文件及常用设备查询操作。"""

    def __init__(self) -> None:
        """定位 ADB 并确认其可执行。

        :return: 无。
        :raises RuntimeError: 当系统中没有可用的 ADB 时抛出。
        """
        adb_path = "adb"
        if platform.system() == "Windows":
            candidate = os.path.join("Tools", "adb", "adb.exe")
            if os.path.exists(candidate):
                adb_path = candidate
        self.adb_path = adb_path
        result = _run_adb(self.adb_path, "version")
        if not result or result.startswith("run shell error"):
            logger.error(
                "请安装 ADB 及驱动并配置环境变量，参考 "
                "https://github.com/wangshub/wechat_jump_game/wiki"
            )
            raise RuntimeError("未找到可用的 adb 可执行文件")

    def get_screen(self) -> str:
        """获取当前设备屏幕尺寸。

        :return: ADB 命令的标准输出。
        """
        return _run_adb(self.adb_path, "shell", "wm", "size")

    def run(self, command: str, *arguments: str) -> str:
        """执行受限的 ADB 子命令。

        :param command: 顶层 ADB 子命令，仅支持 ``connect``、``devices``、
            ``disconnect``、``shell`` 和 ``version``。
        :param arguments: 子命令的独立参数，不能传入拼接好的原始命令文本。
        :return: ADB 命令的标准输出。
        :raises ValueError: 当子命令不受支持或参数为空时抛出。
        """
        command = _validate_text(command, "command")
        if command not in _ALLOWED_ADB_COMMANDS:
            raise ValueError(f"不支持的 ADB 子命令: {command}")
        validated_arguments = (
            _validate_text(argument, "argument") for argument in arguments
        )
        return _run_adb(self.adb_path, command, *validated_arguments)

    def test_device(self) -> str:
        """检查是否有设备已连接。

        :return: 已连接设备列表。
        :raises RuntimeError: 当未找到设备时抛出。
        """
        logger.info("检查设备是否连接...")
        output = _run_adb(self.adb_path, "devices")
        if output == "List of devices attached":
            logger.warning("未找到设备")
            raise RuntimeError("未找到已连接的 adb 设备")
        logger.info("设备已连接: {}", output)
        return output

    def test_density(self) -> str:
        """获取当前设备屏幕密度。

        :return: ADB 命令的标准输出。
        """
        return _run_adb(self.adb_path, "shell", "wm", "density")

    def test_device_detail(self) -> str:
        """获取当前设备型号标识。

        :return: ADB 命令的标准输出。
        """
        return _run_adb(self.adb_path, "shell", "getprop", "ro.product.device")

    def test_device_os(self) -> str:
        """获取当前设备 Android 版本。

        :return: ADB 命令的标准输出。
        """
        return _run_adb(self.adb_path, "shell", "getprop", "ro.build.version.release")
