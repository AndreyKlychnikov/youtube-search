from app.services.search.base import SearchService
from app.services.search.elastic.subtitles import ElasticSearchService


class SingletonMeta(type):  # TODO: remove duplications
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class Container(metaclass=SingletonMeta):
    search_service: SearchService = ElasticSearchService()


def get_container():
    return Container()
