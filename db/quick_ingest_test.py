import os, uuid, hashlib, datetime, mimetypes, sys
import boto3
import psycopg2
from psycopg2.extras import RealDictCursor

BUCKET = os.environ["AWS_S3_BUCKET"]
REGION = os.getenv("AWS_REGION", "us-east-2")  # keep consistent with your bucket
DATABASE_URL = os.environ["DATABASE_URL"]
USER_ID = int(os.getenv("TEST_USER_ID", "1"))

def sha256_bytes(b: bytes) -> bytes:
    h = hashlib.sha256(); h.update(b); return h.digest()

def put_original(key: str, body: bytes, content_type: str):
    s3 = boto3.client("s3", region_name=REGION, endpoint_url=os.getenv("S3_ENDPOINT_URL"))
    resp = s3.put_object(Bucket=BUCKET, Key=key, Body=body, ContentType=content_type)
    return resp.get("VersionId")  # None if versioning is off

def insert_photo_row(conn, **row):
    cols = ", ".join(row.keys())
    vals = ", ".join(["%s"] * len(row))
    sql = f"INSERT INTO photos ({cols}) VALUES ({vals}) RETURNING id, uid, original_key, version_id"
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql, list(row.values()))
        return cur.fetchone()

def fetch_photo(conn, pid: int):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "SELECT id, user_id, original_key, version_id, sha256, created_at FROM photos WHERE id=%s",
            (pid,))
        return cur.fetchone()

if __name__ == "__main__":
    test_path = os.getenv("TEST_IMAGE", "test.jpg")
    if not os.path.exists(test_path):
        sys.exit(f"TEST_IMAGE not found: {test_path}")

    with open(test_path, "rb") as f:
        data = f.read()

    ctype = mimetypes.guess_type(test_path)[0] or "image/jpeg"
    capture_id = str(uuid.uuid4())
    key = f"faces-raw/original/{USER_ID}/{capture_id}.jpg"

    vId = put_original(key, data, ctype)
    digest = sha256_bytes(data)

    conn = psycopg2.connect(DATABASE_URL)
    try:
        row = dict(
            uid=str(uuid.uuid4()),
            title=None,
            description=None,
            filename=os.path.basename(test_path),
            original_key=key,
            normalized_key=None,
            version_id=vId,
            file_size=len(data),
            mime_type=ctype,
            width=None, height=None,
            captured_at=datetime.datetime.now(datetime.timezone.utc),
            sha256=psycopg2.Binary(digest),
            face_valid=False,
            face_match=None,
            consent_version=None,
            monetizable=False,
            user_id=USER_ID
        )
        with conn:  # commits automatically
            inserted = insert_photo_row(conn, **row)
        fetched = fetch_photo(conn, inserted["id"])
        print("Inserted:", inserted)
        print("Fetched :", fetched)
        if vId is None:
            print("Note: Bucket versioning appears disabled for this bucket.")
    finally:
        conn.close()