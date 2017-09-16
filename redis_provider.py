import redis as redis

from config import Config
from models.cell import Cell


class RedisProvider:
    client = redis.StrictRedis(host=Config.redis_host, port=Config.redis_port, db=Config.redis_db)
    key = Config.file_path + ":"

    @staticmethod
    def set(cell_id, value):
        RedisProvider.client.set(RedisProvider.key + cell_id, RedisProvider.to_redis_cells(value))
        return

    @staticmethod
    def get(cell_id):
        ids = RedisProvider.client.get(RedisProvider.key + cell_id)
        if ids is None:
            return None

        return RedisProvider.from_redis_cells(ids)

    @staticmethod
    def to_redis_cells(cells):
        ids = list(map(lambda c: c.id, cells))
        return ';'.join(ids)

    @staticmethod
    def from_redis_cells(ids):
        ids = ids.decode("utf-8")
        cell_ids = ids.split(";")
        cells = []
        if len(ids) < 3:
            return cells

        for cell_id in cell_ids:
            cell_id_split = cell_id.split(",")
            cell = Cell.get(int(cell_id_split[0]), int(cell_id_split[1]))
            cells.append(cell)

        return cells