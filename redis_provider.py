import time

import redis as redis

from config import Config
from models.cell import Cell


class RedisProvider:
    get_seconds = 0

    client = redis.StrictRedis(host=Config.redis_host, port=Config.redis_port, db=Config.redis_db)
    key = Config.file_path + ":"

    @staticmethod
    def set(cell_id, value):
        RedisProvider.client.set(RedisProvider.key + cell_id, RedisProvider.to_redis_cells(value))
        return

    @staticmethod
    def get(cell_id):
        t0 = time.time()
        ids = RedisProvider.client.get(RedisProvider.key + cell_id)
        if ids is None:
            return None
        cells = RedisProvider.from_redis_cells(ids)
        RedisProvider.get_seconds = RedisProvider.get_seconds + time.time() - t0

        return cells

    @staticmethod
    def to_redis_cells(cells):
        ids = {k: v.id for k, v in cells.items()}
        return ';'.join(ids)

    @staticmethod
    def from_redis_cells(ids):
        ids = ids.decode("utf-8")
        cell_ids = ids.split(";")
        cells = {}
        if len(ids) < 3:
            return cells

        for cell_id in cell_ids:
            cell_id_split = cell_id.split(",")
            cell = Cell.get(int(cell_id_split[0]), int(cell_id_split[1]))
            cells[cell.id] = cell

        return cells
