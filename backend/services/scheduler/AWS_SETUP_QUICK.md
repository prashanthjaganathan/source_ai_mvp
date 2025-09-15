# 🚀 Quick AWS Setup for S3 Integration

## Current Status
✅ S3 integration code is complete  
✅ Environment variables are configured  
❌ AWS credentials need to be set  

## 🔧 Quick Setup Steps

### 1. Get AWS Credentials
- Go to [AWS Console](https://console.aws.amazon.com)
- Navigate to IAM → Users → Create User
- Attach policy: `AmazonS3FullAccess`
- Create access key and download credentials

### 2. Update Your .env File
Edit `/Users/yashas/Desktop/Source AI/source_ai_mvp/.env` and replace:

```bash
# Replace these lines in your .env file:
AWS_ACCESS_KEY_ID=your_actual_access_key_here
AWS_SECRET_ACCESS_KEY=your_actual_secret_key_here
```

### 3. Test the Integration
```bash
cd /Users/yashas/Desktop/Source\ AI/source_ai_mvp/backend/services/scheduler

# Load environment and test
source ../../../.env
python test_s3_integration.py
```

### 4. Enable S3 Storage
```bash
# Set S3 as the storage method
export USE_S3_STORAGE=true

# Restart the scheduler service
kill $(lsof -ti:8003)
export DATABASE_URL="postgresql://user:password@localhost:5432/source_ai_mvp"
export ENVIRONMENT="development"
nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8003 > scheduler.log 2>&1 &
```

### 5. Test Photo Capture
```bash
# Test photo capture with S3
curl -X POST "http://localhost:8003/capture/capture" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test-user-123"}'

# Check if photos are stored in S3
curl http://localhost:8003/capture/photos/test-user-123
```

## 🎯 Expected Results

When working correctly, you should see:
- Photos stored in S3 bucket: `s3://source-ai-photos/photos/user_id/photo.jpg`
- Photo URLs like: `https://source-ai-photos.s3.us-east-1.amazonaws.com/photos/user_id/photo.jpg`
- Response includes `"storage_type": "s3"`

## 🚨 Troubleshooting

### "Unable to locate credentials"
- Check your AWS credentials are set correctly
- Verify the .env file is loaded

### "Access Denied"
- Check IAM permissions include S3 access
- Verify bucket exists or has create permissions

### "Bucket does not exist"
- Service will auto-create bucket
- Or create manually: `aws s3 mb s3://source-ai-photos`

## 📞 Need Help?

1. Check the full setup guide: `S3_SETUP_GUIDE.md`
2. Run the test script: `python test_s3_integration.py`
3. Check service logs: `tail -f scheduler.log`

The S3 integration is ready - just add your AWS credentials! 🚀

