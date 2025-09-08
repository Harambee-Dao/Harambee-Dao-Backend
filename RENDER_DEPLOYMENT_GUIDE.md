# 🚀 Harambee DAO Backend - Render Deployment Guide

This comprehensive guide will walk you through deploying the Harambee DAO backend to Render, a modern cloud platform that makes deployment simple and scalable.

## 📋 **Prerequisites**

### 1. **Accounts Required**
- ✅ **GitHub Account** (you already have this)
- ✅ **Render Account** - Sign up at [render.com](https://render.com)
- ✅ **Twilio Account** - Sign up at [twilio.com](https://twilio.com) for SMS functionality
- ✅ **Groq Account** (Optional) - For AI features at [groq.com](https://groq.com)

### 2. **Repository Setup**
- ✅ **Backend Repository**: https://github.com/Harambee-Dao/Harambee-Dao-Backend
- ✅ **All deployment files** are already included in the repository

---

## 🔧 **Step 1: Prepare Environment Variables**

Before deploying, gather the following credentials:

### **Required Environment Variables**

#### **Twilio SMS Configuration**
1. **Log into Twilio Console**: https://console.twilio.com
2. **Get Account SID**: Found on your dashboard
3. **Get Auth Token**: Found on your dashboard (click "Show" to reveal)
4. **Get Phone Number**: Purchase a phone number in Twilio Console

#### **Security Configuration**
- **SECRET_KEY**: Render will auto-generate this
- **ACCESS_TOKEN_EXPIRE_MINUTES**: Set to `30` (default)

#### **AI Configuration (Optional)**
- **GROQ_API_KEY**: Get from Groq console if using AI features
- **GROQ_API_URL**: `https://api.groq.com/openai/v1/chat/completions`

#### **Rate Limiting**
- **RATE_LIMIT_PER_MINUTE**: `60` (default)
- **OTP_RATE_LIMIT_PER_HOUR**: `5` (default)

---

## 🚀 **Step 2: Deploy to Render**

### **Method 1: Using Render Dashboard (Recommended)**

#### **2.1 Create New Web Service**

1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Click "New +"** → **"Web Service"**
3. **Connect GitHub Repository**:
   - Click "Connect account" if not already connected
   - Search for `Harambee-Dao-Backend`
   - Click "Connect"

#### **2.2 Configure Service Settings**

**Basic Settings:**
```
Name: harambee-dao-backend
Environment: Python 3
Region: Choose closest to your users (e.g., Oregon, Frankfurt)
Branch: main
Root Directory: . (leave empty)
```

**Build & Deploy Settings:**
```
Build Command: pip install -e .
Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**Plan Selection:**
```
Plan: Starter ($7/month) - Recommended for production
     or
     Free Plan - For testing (sleeps after 15 min inactivity)
```

#### **2.3 Configure Environment Variables**

In the **Environment Variables** section, add:

```bash
# Application Settings
APP_ENV=production
LOG_LEVEL=INFO
PORT=10000

# Twilio SMS Settings (REQUIRED)
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890

# Security Settings
SECRET_KEY=auto-generated-by-render
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI Settings (Optional)
GROQ_API_KEY=your_groq_api_key_here
GROQ_API_URL=https://api.groq.com/openai/v1/chat/completions

# Blockchain Settings (Default values)
IPFS_API_URL=https://ipfs.infura.io:5001
ORACLE_SIGNER=0x0000000000000000000000000000000000000000
CELESTIA_ENDPOINT=https://rpc.celestia.pops.one

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
OTP_RATE_LIMIT_PER_HOUR=5
```

#### **2.4 Advanced Settings**

```bash
Health Check Path: /health
Auto-Deploy: Yes (recommended)
```

#### **2.5 Deploy**

1. **Click "Create Web Service"**
2. **Wait for deployment** (usually 2-5 minutes)
3. **Monitor build logs** for any issues

### **Method 2: Using render.yaml (Infrastructure as Code)**

The repository includes a `render.yaml` file for automated deployment:

1. **Fork the repository** to your GitHub account
2. **Go to Render Dashboard** → **"New +"** → **"Blueprint"**
3. **Connect the repository**
4. **Render will automatically** read the `render.yaml` configuration
5. **Set environment variables** in the Render dashboard

---

## 🔍 **Step 3: Verify Deployment**

### **3.1 Check Service Status**

1. **Go to your service** in Render dashboard
2. **Check "Events" tab** for deployment status
3. **Verify "Logs" tab** shows no errors

### **3.2 Test API Endpoints**

Once deployed, test your API:

```bash
# Replace YOUR_RENDER_URL with your actual Render URL
export API_URL="https://harambee-dao-backend.onrender.com"

# Test health endpoint
curl $API_URL/health

# Test API ping
curl $API_URL/api/ping

# Test all services
curl $API_URL/api/testall
```

**Expected Response for Health Check:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-XX...",
  "version": "1.0.0"
}
```

### **3.3 Test SMS Functionality**

```bash
# Test OTP request (replace with real phone number)
curl -X POST $API_URL/api/users/phone/request-otp \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+1234567890"}'
```

---

## 🔧 **Step 4: Configure Twilio Webhook**

### **4.1 Set Webhook URL in Twilio**

1. **Go to Twilio Console** → **Phone Numbers** → **Manage** → **Active Numbers**
2. **Click your phone number**
3. **In "Messaging" section**, set:
   ```
   Webhook URL: https://YOUR_RENDER_URL.onrender.com/api/users/webhooks/sms
   HTTP Method: POST
   ```
4. **Save configuration**

### **4.2 Test SMS Webhook**

1. **Send SMS to your Twilio number**: `YES001`
2. **Check Render logs** for webhook processing
3. **Verify vote is recorded** in the system

---

## 📊 **Step 5: Monitor and Maintain**

### **5.1 Monitoring**

**Render Dashboard Monitoring:**
- **Metrics**: CPU, Memory, Response time
- **Logs**: Real-time application logs
- **Events**: Deployment and service events
- **Health Checks**: Automatic health monitoring

**Set up Alerts:**
1. **Go to service settings**
2. **Enable "Failure Notifications"**
3. **Add email/Slack notifications**

### **5.2 Scaling**

**Vertical Scaling:**
- **Starter Plan**: 0.5 CPU, 512 MB RAM
- **Standard Plan**: 1 CPU, 2 GB RAM
- **Pro Plan**: 2 CPU, 4 GB RAM

**Horizontal Scaling:**
- Available on Standard+ plans
- Auto-scaling based on traffic

### **5.3 Custom Domain (Optional)**

1. **Go to service settings** → **Custom Domains**
2. **Add your domain** (e.g., `api.harambeedao.com`)
3. **Configure DNS** as instructed by Render
4. **SSL certificate** is automatically provided

---

## 🔒 **Step 6: Security Best Practices**

### **6.1 Environment Variables Security**

- ✅ **Never commit** `.env` files to Git
- ✅ **Use Render's environment variables** for secrets
- ✅ **Rotate API keys** regularly
- ✅ **Use strong SECRET_KEY** (auto-generated by Render)

### **6.2 API Security**

- ✅ **Rate limiting** is enabled by default
- ✅ **Input validation** via Pydantic
- ✅ **HTTPS** is enforced by Render
- ✅ **Health checks** monitor service status

### **6.3 Twilio Security**

- ✅ **Webhook validation** (implement signature verification)
- ✅ **Phone number validation** (E.164 format)
- ✅ **Rate limiting** on OTP requests

---

## 🐛 **Troubleshooting**

### **Common Issues**

#### **Build Failures**
```bash
# Check build logs in Render dashboard
# Common fixes:
1. Verify requirements.txt includes all dependencies
2. Check Python version compatibility
3. Ensure pyproject.toml is valid
```

#### **Environment Variable Issues**
```bash
# Symptoms: 500 errors, missing configuration
# Fixes:
1. Verify all required env vars are set
2. Check for typos in variable names
3. Ensure Twilio credentials are correct
```

#### **SMS Not Working**
```bash
# Check:
1. Twilio webhook URL is correct
2. Phone number is verified in Twilio
3. Webhook endpoint returns 200 status
4. Check Render logs for webhook processing
```

#### **Health Check Failures**
```bash
# Check:
1. /health endpoint is accessible
2. Service is running on correct port
3. No startup errors in logs
```

### **Getting Help**

- **Render Support**: https://render.com/docs
- **Twilio Support**: https://support.twilio.com
- **GitHub Issues**: https://github.com/Harambee-Dao/Harambee-Dao-Backend/issues

---

## 🎉 **Success! Your Backend is Live**

Once deployed successfully, you'll have:

- ✅ **Production API** running on Render
- ✅ **SMS functionality** via Twilio
- ✅ **Automatic deployments** from GitHub
- ✅ **Health monitoring** and logging
- ✅ **HTTPS security** and SSL certificates
- ✅ **Scalable infrastructure** ready for growth

**Your API will be available at:**
`https://harambee-dao-backend.onrender.com`

**Next Steps:**
1. **Connect your frontend** to the deployed API
2. **Set up monitoring** and alerts
3. **Configure custom domain** (optional)
4. **Start onboarding** community groups
5. **Monitor usage** and scale as needed

---

## 📞 **Support**

For deployment issues:
- **Documentation**: This guide and README.md
- **GitHub Issues**: Report bugs and get help
- **Render Docs**: https://render.com/docs
- **Community**: GitHub Discussions

**Happy Deploying! 🚀**
