# 🔑 FREE API KEYS GUIDE FOR RAJAN BOT

## ⚡ RECOMMENDED FREE APIs (Pick Any One)

### 1. 🔥 **Groq (FASTEST & FREE)** - HIGHLY RECOMMENDED
- **Speed**: Ultra-fast responses
- **Free Tier**: Very generous
- **Setup**:
  1. Go to: https://console.groq.com/keys
  2. Sign up with email
  3. Create API key
  4. Add to `.env` file:
     ```env
     GROQ_API_KEY=your_groq_api_key_here
     ```

### 2. 🤗 **Hugging Face (COMPLETELY FREE)**
- **Speed**: Good
- **Free Tier**: Unlimited
- **Setup**:
  1. Go to: https://huggingface.co/settings/tokens
  2. Sign up with email
  3. Create token
  4. Add to `.env` file:
     ```env
     HUGGINGFACE_API_KEY=your_hf_token_here
     ```

### 3. 🚀 **Together AI (FAST & FREE)**
- **Speed**: Very fast
- **Free Tier**: Good allowance
- **Setup**:
  1. Go to: https://api.together.xyz/settings/api-keys
  2. Sign up
  3. Create API key
  4. Add to `.env` file:
     ```env
     TOGETHER_API_KEY=your_together_key_here
     ```

### 4. 🧠 **OpenAI (PREMIUM)**
- **Speed**: Excellent
- **Cost**: Paid (but very affordable)
- **Setup**:
  1. Go to: https://platform.openai.com/api-keys
  2. Add payment method ($5 minimum)
  3. Create API key
  4. Add to `.env` file:
     ```env
     OPENAI_API_KEY=your_openai_key_here
     ```

## 📝 QUICK SETUP STEPS

### Step 1: Choose Your API
Pick any one API from above (Groq is recommended for free users)

### Step 2: Create `.env` file
Create/edit `.env` file in the `backend` folder:

```env
# Choose ONE of these APIs:

# Option 1: Groq (Recommended for free)
GROQ_API_KEY=your_groq_key_here

# Option 2: Hugging Face (Completely free)
HUGGINGFACE_API_KEY=your_hf_token_here

# Option 3: Together AI (Fast and free)
TOGETHER_API_KEY=your_together_key_here

# Option 4: OpenAI (Premium)
OPENAI_API_KEY=your_openai_key_here

# Database (keep as is for now)
DATABASE_TYPE=sqlite
```

### Step 3: Update API Service
I'll update the code to support these APIs automatically!

### Step 4: Restart Servers
Run the startup script:
```bash
# Windows
start_rajan_bot.bat

# Or PowerShell
start_rajan_bot.ps1
```

## 🎯 WHICH API TO CHOOSE?

### 🏆 **For Best Experience**: 
**Groq** - Fastest free API with excellent responses

### 💰 **For Zero Cost**: 
**Hugging Face** - Completely free, good quality

### ⚡ **For Speed**: 
**Together AI** - Very fast with good free tier

### 🧠 **For Best Quality**: 
**OpenAI** - Premium quality (costs ~$0.002 per message)

## 🔧 CURRENT STATUS
- ✅ Backend Server: Working
- ✅ Chat System: Working  
- ✅ Rajan Bot Personality: Active
- ⚠️ Need API Key: For full LLM responses
- ✅ Fallback System: Working offline

## 🚀 NEXT STEPS
1. Get ANY one API key from above
2. Add it to `.env` file
3. Restart servers
4. Enjoy full Rajan Bot experience!

**Rajan Bot will work even without API keys using intelligent fallbacks!**