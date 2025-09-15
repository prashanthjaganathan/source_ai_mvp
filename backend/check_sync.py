#!/usr/bin/env python3
"""
Sanity checks for backend-database sync.
Run this after applying the migration to verify everything is in sync.
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/source_ai_mvp")

def run_sanity_checks():
    """Run sanity checks to verify database-backend sync"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            print("🔍 Running sanity checks...")
            
            # Check 1: users.uid exists and is populated
            cur.execute("SELECT COUNT(*) AS missing_user_uid FROM users WHERE uid IS NULL;")
            missing_user_uid = cur.fetchone()['missing_user_uid']
            print(f"✅ Missing user UIDs: {missing_user_uid} (should be 0)")
            
            # Check 2: photos.uid exists and is populated
            cur.execute("SELECT COUNT(*) AS missing_photo_uid FROM photos WHERE uid IS NULL;")
            missing_photo_uid = cur.fetchone()['missing_photo_uid']
            print(f"✅ Missing photo UIDs: {missing_photo_uid} (should be 0)")
            
            # Check 3: photos.original_key exists and is populated
            cur.execute("SELECT COUNT(*) AS missing_original_key FROM photos WHERE original_key IS NULL;")
            missing_original_key = cur.fetchone()['missing_original_key']
            print(f"✅ Missing original_key: {missing_original_key} (should be 0)")
            
            # Check 4: Verify users table structure
            cur.execute("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'users' 
                ORDER BY ordinal_position;
            """)
            user_columns = cur.fetchall()
            print(f"\n📋 Users table columns ({len(user_columns)}):")
            for col in user_columns:
                print(f"  - {col['column_name']}: {col['data_type']} ({'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'})")
            
            # Check 5: Verify photos table structure
            cur.execute("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'photos' 
                ORDER BY ordinal_position;
            """)
            photo_columns = cur.fetchall()
            print(f"\n📋 Photos table columns ({len(photo_columns)}):")
            for col in photo_columns:
                print(f"  - {col['column_name']}: {col['data_type']} ({'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'})")
            
            # Check 6: Sample data
            cur.execute("SELECT COUNT(*) as user_count FROM users;")
            user_count = cur.fetchone()['user_count']
            print(f"\n📊 Sample data:")
            print(f"  - Total users: {user_count}")
            
            cur.execute("SELECT COUNT(*) as photo_count FROM photos;")
            photo_count = cur.fetchone()['photo_count']
            print(f"  - Total photos: {photo_count}")
            
            if user_count > 0:
                cur.execute("SELECT id, uid, name, email, incentives_earned FROM users LIMIT 3;")
                sample_users = cur.fetchall()
                print(f"  - Sample users:")
                for user in sample_users:
                    print(f"    * ID: {user['id']}, UID: {user['uid']}, Name: {user['name']}, Email: {user['email']}, Earned: {user['incentives_earned']}")
            
            if photo_count > 0:
                cur.execute("SELECT id, uid, filename, original_key, user_id FROM photos LIMIT 3;")
                sample_photos = cur.fetchall()
                print(f"  - Sample photos:")
                for photo in sample_photos:
                    print(f"    * ID: {photo['id']}, UID: {photo['uid']}, Filename: {photo['filename']}, Key: {photo['original_key']}, User: {photo['user_id']}")
            
            print(f"\n🎉 Sanity checks completed!")
            
            # Summary
            all_good = (missing_user_uid == 0 and missing_photo_uid == 0 and missing_original_key == 0)
            if all_good:
                print("✅ All checks passed! Backend and database are in sync.")
            else:
                print("❌ Some checks failed. Please review the issues above.")
                return False
                
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error running sanity checks: {e}")
        return False

if __name__ == "__main__":
    success = run_sanity_checks()
    sys.exit(0 if success else 1)
