"""预跑按专区缩小检查范围（可选）。

prepush_ci.py 在“改动仅属于若干专区”时设置环境变量 PREPUSH_GAMES=pokepath,risk-of-rain-2，
布局、图片、图注检查据此只检查这些专区；未设置（GitHub CI、手动全量、--full）时检查全部。
专区名即仓库顶层目录名。
"""
import os


def scoped_games():
    """返回本次限定的专区名集合；未限定返回 None。"""
    value = os.environ.get('PREPUSH_GAMES', '').strip()
    games = {g.strip() for g in value.split(',') if g.strip()}
    return games or None


def route_in_scope(route, games):
    """路由或相对路径（如 /pokepath/x/ 或 pokepath/x/index.html）的第一段是否属于限定专区。"""
    if games is None:
        return True
    return route.strip('/').split('/', 1)[0] in games
