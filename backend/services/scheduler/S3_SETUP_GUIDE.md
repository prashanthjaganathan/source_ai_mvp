# 🚀 S3 Storage Setup Guide

## Overview
The scheduler service has been successfully updated to support S3 storage for photos. This guide will help you configure and use S3 storage.

## ✅ What's Been Implemented

1. **S3Service Class**: Complete S3 integration with upload, download, and management
2. **PhotoCaptureService**: Updated to use S3 instead of local storage
3. **Configuration**: Flexible S3 configuration with environment variables
4. **Fallback Support**: Automatic fallback to local storage if S3 fails
5. **Photo Management**: List, delete, and metadata operations for S3 photos

## 🔧 Configuration Options

### Environment Variables

```bash
# Enable/disable S3 storage
USE_S3_STORAGE=true

# S3 Bucket Configuration
S3_BUCKET_NAME=source-ai-photos
AWS_REGION=us-east-1

# AWS Credentials (optional - can use IAM roles)
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here

# Optional: CloudFront or Custom Domain
CLOUDFRONT_DOMAIN=your-cloudfront-domain.cloudfront.net
S3_CUSTOM_DOMAIN=photos.yourdomain.com
```

## 🚀 Setup Instructions

### Option 1: AWS Credentials (Recommended for Development)

1. **Get AWS Credentials**:
   - Go to AWS Console → IAM → Users → Create User
   - Attach policy: `AmazonS3FullAccess`
   - Create access key

2. **Set Environment Variables**:
   ```bash
   export AWS_ACCESS_KEY_ID=AKIA...
   export AWS_SECRET_ACCESS_KEY=...
   export S3_BUCKET_NAME=your-bucket-name
   export AWS_REGION=us-east-1
   export USE_S3_STORAGE=true
   ```

3. **Test Configuration**:
   ```bash
   python test_s3_config.py
   ```

### Option 2: AWS CLI (Alternative)

1. **Install AWS CLI**:
   ```bash
   pip install awscli
   ```

2. **Configure**:
   ```bash
   aws configure
   # Enter your credentials when prompted
   ```

3. **Test**:
   ```bash
   aws s3 ls
   ```

### Option 3: IAM Roles (Production)

If running on EC2, use IAM roles instead of credentials:
- Create IAM role with S3 permissions
- Attach role to EC2 instance
- No credentials needed in environment

## 📦 S3 Bucket Setup

### Automatic Bucket Creation
The service will automatically create the bucket if it doesn't exist with:
- Public read access for photos
- Proper CORS configuration
- Organized folder structure: `photos/{user_id}/{filename}`

### Manual Bucket Setup (Optional)
```bash
# Create bucket
aws s3 mb s3://your-bucket-name --region us-east-1

# Set public read policy for photos
aws s3api put-bucket-policy --bucket your-bucket-name --policy '{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::your-bucket-name/photos/*"
    }
  ]
}'
```

## 🧪 Testing S3 Integration

### 1. Test Configuration
```bash
python test_s3_config.py
```

### 2. Test Photo Capture with S3
```bash
# Set S3 environment
export USE_S3_STORAGE=true
export S3_BUCKET_NAME=your-bucket-name
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret

# Restart service
kill $(lsof -ti:8003)
export DATABASE_URL="postgresql://user:password@localhost:5432/source_ai_mvp"
export ENVIRONMENT="development"
nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8003 > scheduler.log 2>&1 &

# Test photo capture
curl -X POST "http://localhost:8003/capture/capture" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test-user-123"}'

# Check photos
curl http://localhost:8003/capture/photos/test-user-123
```

## 📁 Photo Storage Structure

### S3 Structure
```
your-bucket/
└── photos/
    ├── user-1/
    │   ├── 20250914_190107_session_1.jpg
    │   └── 20250914_190652_session_2.jpg
    └── user-2/
        └── 20250914_191407_session_3.jpg
```

### Photo URLs
- **Direct S3**: `https://your-bucket.s3.us-east-1.amazonaws.com/photos/user-1/photo.jpg`
- **CloudFront**: `https://your-cloudfront-domain.cloudfront.net/photos/user-1/photo.jpg`
- **Custom Domain**: `https://photos.yourdomain.com/photos/user-1/photo.jpg`

## 🔄 Fallback Behavior

The service includes intelligent fallback:
1. **Primary**: Try S3 upload
2. **Fallback**: If S3 fails, use local storage
3. **Error Handling**: Graceful degradation with proper logging

## 📊 API Changes

### New Response Fields
```json
{
  "photos": [
    {
      "filename": "photo.jpg",
      "s3_key": "photos/user-1/photo.jpg",
      "photo_url": "https://bucket.s3.region.amazonaws.com/photos/user-1/photo.jpg",
      "size_bytes": 1234567,
      "storage_type": "s3",
      "bucket": "your-bucket"
    }
  ],
  "storage_type": "s3"
}
```

## 🚨 Troubleshooting

### Common Issues

1. **"Unable to locate credentials"**
   - Set AWS credentials or configure AWS CLI
   - Check IAM permissions

2. **"Bucket does not exist"**
   - Service will auto-create bucket
   - Or create manually with proper permissions

3. **"Access Denied"**
   - Check IAM policy includes S3 permissions
   - Verify bucket policy allows public read

4. **"Connection timeout"**
   - Check network connectivity
   - Verify AWS region is correct

### Debug Commands
```bash
# Check AWS credentials
aws sts get-caller-identity

# List S3 buckets
aws s3 ls

# Test bucket access
aws s3 ls s3://your-bucket-name

# Check service logs
tail -f scheduler.log
```

## 🎯 Benefits of S3 Storage

1. **Scalability**: Unlimited storage capacity
2. **Accessibility**: Photos accessible from anywhere
3. **Reliability**: 99.999999999% durability
4. **Performance**: Global CDN with CloudFront
5. **Cost-effective**: Pay only for what you use
6. **Security**: Fine-grained access controls

## 🔐 Security Best Practices

1. **Use IAM Roles** instead of access keys when possible
2. **Limit S3 permissions** to only what's needed
3. **Enable S3 access logging** for audit trails
4. **Use CloudFront** for better performance and security
5. **Set up lifecycle policies** to manage old photos

## 📈 Next Steps

1. **Set up AWS credentials** using one of the methods above
2. **Test the configuration** with the test script
3. **Enable S3 storage** by setting `USE_S3_STORAGE=true`
4. **Monitor the logs** to ensure everything works correctly
5. **Consider CloudFront** for better performance

The S3 integration is now ready to use! 🚀

