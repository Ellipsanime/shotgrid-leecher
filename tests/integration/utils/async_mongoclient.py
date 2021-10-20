from mongomock.collection import Collection
from mongomock.mongo_client import MongoClient
from pymongo.results import InsertManyResult, UpdateResult


class AsyncMongoClient:
    mongo_client: MongoClient
    database: str
    collection: str

    def __init__(self, mongo_client: MongoClient = MongoClient()):
        self.mongo_client = mongo_client

    def _collection(self) -> Collection:
        return self.mongo_client.get_database(self.database).get_collection(
            self.collection
        )

    def get_database(self, database: str) -> "AsyncMongoClient":
        self.database = database
        return self

    def get_collection(self, collection: str) -> "AsyncMongoClient":
        self.collection = collection
        return self

    async def insert_many(
        self,
        documents,
        ordered=True,
        bypass_document_validation=False,
        session=None,
    ) -> InsertManyResult:
        return self._collection().insert_many(
            documents, ordered, bypass_document_validation, session
        )

    async def update_one(
        self,
        filter,
        update,
        upsert=False,
        bypass_document_validation=False,
        hint=None,
        session=None,
        collation=None,
    ) -> UpdateResult:
        return self._collection().update_one(
            filter,
            update,
            upsert,
            bypass_document_validation,
            hint,
            session,
            collation,
        )
