from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings

client = AsyncIOMotorClient(settings.MONGODB_URL)
db = client[settings.DATABASE_NAME]

vulnerabilities = db.get_collection("vulnerabilities")
groups = db.get_collection("groups")
subgroups = db.get_collection("subgroups")

async def create_indexes():
    await vulnerabilities.create_index("cve", unique=True, sparse=True)
    await vulnerabilities.create_index("group")
    await vulnerabilities.create_index("subgroup")
    await vulnerabilities.create_index("cvss_v4")