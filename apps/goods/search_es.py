from elasticsearch import AsyncElasticsearch

from mall.conf import settings
from apps.goods.models import SKU, GoodsCategory, SPU

client = AsyncElasticsearch(hosts=settings.ELASTICSEARCH_ADDRESS)
index = "mall"


async def to_es():
    """数据库数据插入Es"""
    results = await SKU.filter(is_delete=False, is_launched=True).order_by("-id").all()
    for result in results:
        await client.index(index, body={
            **result.__dict__,
            "category": await GoodsCategory.filter(pk=result.category_id).values("id", "name")[0],
            "spu": await SPU.filter(pk=result.spu_id).values()[0]
        })


async def query_es(query: str = "手机"):
    """查询"""
    body = {
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["name", "caption", "category", "spu"]
            }
        }
    }
    response = await client.search(index=index, body=body)
    total = response["hits"]["total"]["value"]

    return total, [hit["_source"] for hit in response["hits"]["hits"]]