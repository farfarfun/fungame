"""
手机屏幕截图的代码
"""
import os
from io import BytesIO

from farlog import getLogger
from funshell import run_shell
from PIL import Image, UnidentifiedImageError

from .auto_adb import AutoADB

logger = getLogger("fungame")

adb = AutoADB()
# SCREENSHOT_WAY 是截图方法，经过 check_screenshot 后，会自动递减，不需手动修改
SCREENSHOT_WAY = 3


def pull_screenshot():
    """
    获取屏幕截图，目前有 0 1 2 3 四种方法，未来添加新的平台监测方法时，
    可根据效率及适用性由高到低排序
    """
    global SCREENSHOT_WAY
    if 1 <= SCREENSHOT_WAY <= 3:
        binary_screenshot = run_shell(f"{adb.adb_path} shell screencap -p", printf=False).encode("utf-8")
        if SCREENSHOT_WAY == 2:
            binary_screenshot = binary_screenshot.replace(b'\r\n', b'\n')
        elif SCREENSHOT_WAY == 1:
            binary_screenshot = binary_screenshot.replace(b'\r\r\n', b'\n')
        return Image.open(BytesIO(binary_screenshot))
    elif SCREENSHOT_WAY == 0:
        run_shell(f"{adb.adb_path} shell screencap -p /sdcard/autojump.png")
        run_shell(f"{adb.adb_path} pull /sdcard/autojump.png .")
        return Image.open('./autojump.png')


def check_screenshot():
    """
    检查获取截图的方式，依次尝试各截图方式，全部失败则抛出异常
    """
    global SCREENSHOT_WAY
    if os.path.isfile('autojump.png'):
        try:
            os.remove('autojump.png')
        except OSError as e:
            logger.warning(f"删除临时截图文件失败: {e}")

    if SCREENSHOT_WAY < 0:
        raise RuntimeError("暂不支持当前设备：所有截图方式均已尝试失败")

    try:
        im = pull_screenshot()
        im.load()
        im.close()
        logger.info(f"采用方式 {SCREENSHOT_WAY} 获取截图")
    except (OSError, UnidentifiedImageError) as e:
        logger.warning(f"截图方式 {SCREENSHOT_WAY} 失败，尝试下一种方式: {e}")
        SCREENSHOT_WAY -= 1
        check_screenshot()


# check_screenshot()
# pull_screenshot()
