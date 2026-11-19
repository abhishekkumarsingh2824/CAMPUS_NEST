"""
CampusNest MongoDB Database Utility
Provides a reusable connection to MongoDB via PyMongo.
All application data is stored in the 'campusnest' database.
"""
import os
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv

load_dotenv()

_client = None
_db = None


def get_client():
    """Return the singleton MongoClient instance."""
    global _client
    if _client is None:
        uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/')
        _client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    return _client


class MongoCursorWrapper:
    """Wrapper around PyMongo cursor that injects string 'id' into documents."""
    def __init__(self, cursor):
        self._cursor = cursor

    def __iter__(self):
        for doc in self._cursor:
            if isinstance(doc, dict) and '_id' in doc and 'id' not in doc:
                doc['id'] = str(doc['_id'])
            yield doc

    def sort(self, *args, **kwargs):
        self._cursor = self._cursor.sort(*args, **kwargs)
        return self

    def limit(self, *args, **kwargs):
        self._cursor = self._cursor.limit(*args, **kwargs)
        return self

    def skip(self, *args, **kwargs):
        self._cursor = self._cursor.skip(*args, **kwargs)
        return self

    def __getitem__(self, index):
        res = self._cursor[index]
        if isinstance(res, list):
            for d in res:
                if isinstance(d, dict) and '_id' in d and 'id' not in d:
                    d['id'] = str(d['_id'])
            return res
        elif isinstance(res, dict) and '_id' in res and 'id' not in res:
            res['id'] = str(res['_id'])
        return res

    def __getattr__(self, name):
        return getattr(self._cursor, name)


class MongoCollectionWrapper:
    """Wrapper around PyMongo collection to automatically normalize document IDs."""
    def __init__(self, collection):
        self._col = collection

    def find_one(self, *args, **kwargs):
        doc = self._col.find_one(*args, **kwargs)
        if isinstance(doc, dict) and '_id' in doc and 'id' not in doc:
            doc['id'] = str(doc['_id'])
        return doc

    def find(self, *args, **kwargs):
        cursor = self._col.find(*args, **kwargs)
        return MongoCursorWrapper(cursor)

    def __getattr__(self, name):
        return getattr(self._col, name)


class MongoDatabaseWrapper:
    """Wrapper around PyMongo database to return wrapped collections."""
    def __init__(self, db):
        self._db = db

    def __getitem__(self, name):
        return MongoCollectionWrapper(self._db[name])

    def __getattr__(self, name):
        from pymongo.collection import Collection
        attr = getattr(self._db, name)
        if isinstance(attr, Collection):
            return MongoCollectionWrapper(attr)
        return attr


def format_doc(doc):
    """Ensure a document dictionary has string 'id'."""
    if isinstance(doc, dict) and '_id' in doc and 'id' not in doc:
        doc['id'] = str(doc['_id'])
    return doc


def format_docs(docs):
    """Ensure a list/iterable of documents have string 'id'."""
    return [format_doc(d) for d in (docs or [])]


def get_db():
    """Return the campusnest database handle wrapped for template safety."""
    global _db
    if _db is None:
        db_name = os.environ.get('MONGODB_DB_NAME', 'campusnest')
        raw_db = get_client()[db_name]
        _ensure_indexes(raw_db)
        _db = MongoDatabaseWrapper(raw_db)
    return _db


def _ensure_indexes(db):
    """Create indexes for frequently queried fields."""
    # users collection
    db.users.create_index([('email', ASCENDING)], unique=True)

    # properties collection
    db.properties.create_index([('city', ASCENDING)])
    db.properties.create_index([('approval_status', ASCENDING)])
    db.properties.create_index([('owner_id', ASCENDING)])
    db.properties.create_index([('monthly_rent', ASCENDING)])
    db.properties.create_index([('room_type', ASCENDING)])
    db.properties.create_index([('created_at', DESCENDING)])

    # favorites: prevent duplicate favourites for same student+property
    db.favorites.create_index(
        [('student_id', ASCENDING), ('property_id', ASCENDING)],
        unique=True
    )

    # inquiries
    db.inquiries.create_index([('student_id', ASCENDING)])
    db.inquiries.create_index([('owner_id', ASCENDING)])
    db.inquiries.create_index([('property_id', ASCENDING)])

    # reviews
    db.reviews.create_index([('property_id', ASCENDING)])
    db.reviews.create_index(
        [('student_id', ASCENDING), ('property_id', ASCENDING)],
        unique=True
    )


def test_connection():
    """Test MongoDB connection. Returns (success: bool, message: str)."""
    try:
        client = get_client()
        client.admin.command('ping')
        return True, "MongoDB connected successfully."
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        return False, f"MongoDB connection failed: {e}"
    except Exception as e:
        return False, f"Unexpected error: {e}"
