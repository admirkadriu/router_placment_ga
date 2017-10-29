import time

import redis as redis

from config import Config
from models.cell import Cell


class RedisProvider:
    get_seconds = 0
    calc_seconds = 0

    client = redis.StrictRedis(host=Config.redis_host, port=Config.redis_port, db=Config.redis_db)
    key = Config.file_name + ":"

    @staticmethod
    def set_cell(cell_id, value):
        RedisProvider.client.set(RedisProvider.key + cell_id, RedisProvider.to_redis_cells(value))
        return

    @staticmethod
    def set(id, value):
        RedisProvider.client.set(RedisProvider.key + id, value)
        return

    @staticmethod
    def get(id):
        value = RedisProvider.client.get(RedisProvider.key + id)
        value = value.decode("utf-8")
        return value

    @staticmethod
    def get_cell(cell_id):
        #t0 = time.time()
        ids = RedisProvider.client.get(RedisProvider.key + cell_id)
        #RedisProvider.get_seconds = RedisProvider.get_seconds + time.time() - t0
        if ids is None:
            return None
        #t0 = time.time()
        cells = RedisProvider.from_redis_cells(ids)
        #RedisProvider.calc_seconds = RedisProvider.calc_seconds + time.time() - t0

        return cells

    @staticmethod
    def to_redis_cells(cell_ids):
        return ';'.join(cell_ids)

    @staticmethod
    def from_redis_cells(ids):
        ids = ids.decode("utf-8")
        cell_ids = ids.split(";")
        cells = []
        if len(ids) < 3:
            return cells

        for cell_id in cell_ids:
            cells.append(cell_id)

        return cells
