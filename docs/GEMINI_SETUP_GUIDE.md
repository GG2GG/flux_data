# 🚀 Gemini API Integration Guide

## Complete Setup Guide for Google Gemini with Your Retail Placement System

---

## 🎯 What This Guide Covers

1. How to get your free Gemini API key
2. How to configure your system to use Gemini
3. How to test the integration
4. How to use the interactive planogram with AI chat

---

## 📝 Step 1: Get Your Gemini API Key (Free!)

### Option A: Using Google AI Studio (Recommended)

1. Visit **[Google AI Studio](https://makersuite.google.com/app/apikey)**
2. Sign in with your Google account
3. Click **"Get API Key"** or **"Create API Key"**
4. Select **"Create API key in new project"** (or use existing project)
5. Copy the API key (starts with `AIza...`)

**Free Tier includes:**
- 60 requests per minute
- 1,500 requests per day
- Perfect for development and testing!

### Option B: Using Google Cloud Console (Production)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the **"Generative Language API"**
4. Go to **APIs & Services > Credentials**
5. Click **"Create Credentials" > "API Key"**
6. Copy your API key

---

## ⚙️ Step 2: Configure Your System

### Method 1: Environment Variable (Recommended)

```bash
# Add this to your shell profile (~/.zshrc or ~/.bashrc)
export GEMINI_API_KEY="your-api-key-here"

# Reload your shell
source ~/.zshrc  # or ~/.bashrc
```

### Method 2: Create .env File

```bash
# In your project directory
cd /Users/gautham.ganesh/Documents/GG_Scripts/flux_data

# Create .env file
cat > .env << 'EOF'
GEMINI_API_KEY=your-api-key-here
EOF
```

### Method 3: Inline (For Testing)

```bash
# Run the API server with inline environment variable
GEMINI_API_KEY="your-api-key-here" python3 -m uvicorn api.main:app --port 8000
```

---

## 🔧 Step 3: Restart Your API Server

If your server is already running, restart it to load the new configuration:

```bash
# Stop the current server
pkill -f uvicorn

# Start with Gemini enabled
python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8000
```

You should see in the logs:
```
INFO:     Using Gemini API with model: gemini-1.5-pro
INFO:     [ExplainerAgent] LLM available, using AI-powered explanations
```

---

## ✅ Step 4: Test the Integration

### Test 1: Check API Health

```bash
curl http://localhost:8000/api/health
```

Expected output should show `llm_enabled: true`

### Test 2: Analyze a Product

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Premium Energy Drink",
    "category": "Beverages",
    "price": 2.99,
    "budget": 5000,
    "target_sales": 1000,
    "target_customers": "Young adults",
    "expected_roi": 1.5
  }'
```

You should get natural language explanations powered by Gemini!

### Test 3: Ask Follow-up Questions

```bash
# First, save the session_id from the analyze response
SESSION_ID="<session-id-from-response>"

curl -X POST http://localhost:8000/api/defend \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"question\": \"Why is this location better than alternatives?\"
  }"
```

---

## 🎨 Step 5: Use the Interactive Planogram

### Open the Interactive UI

```bash
open demo/interactive_planogram.html
```

### Features You Can Now Use:

1. **Analyze Products**
   - Fill in product details
   - Click "Analyze Placement"
   - See AI-powered recommendations

2. **Interactive Planogram**
   - Colors update automatically (gold for top, green for recommended)
   - Click any location to select it
   - See ROI badges on each shelf

3. **AI Chat for Locations** 🔥 **NEW!**
   - Click any shelf location
   - Chat section appears on the right
   - Ask questions like:
     - "Why is this location good for my product?"
     - "How can I optimize placement here?"
     - "What do competitors do in this location?"
     - "What customer behaviors should I consider?"

---

## 💬 Example Chat Conversations

### Example 1: Understanding a Location

**You:** "Why is End Cap Row 1 good for my energy drink?"

**AI:** "End Cap Row 1 is excellent for your Premium Energy Drink for several reasons:

1. **Premium Visibility**: End caps receive 2.0x more attention than standard shelf locations. Studies show customers are 70% more likely to notice products here.

2. **Impulse Purchase Zone**: This location is positioned where customers make quick decisions, perfect for grab-and-go products like energy drinks.

3. **Category Match**: Being in the beverage section means customers are already in the mindset to purchase drinks, increasing conversion likelihood by 45%.

4. **High Traffic**: This end cap sees 250+ daily visitors, giving you maximum exposure within your $5,000 budget.

Your predicted ROI of 1.85x here outperforms the average by 28%."

### Example 2: Optimization Strategies

**You:** "How can I optimize my placement in Checkout Lane Row 2?"

**AI:** "Here are 5 strategies to maximize ROI in Checkout Lane Row 2:

1. **Cross-Merchandising**: Place complementary snacks nearby (chips, gum) to increase basket size

2. **Eye-Catching Packaging**: Use bright colors and bold text—customers spend only 2-3 seconds at checkout

3. **Quantity Pricing**: Offer "2 for $5" or "Buy 3 Save 20%" to increase units per transaction

4. **Seasonal Rotation**: Checkout lanes perform 40% better with seasonal promotions

5. **Digital POS**: Consider a small screen showing product benefits or energy boost messaging

These tactics could improve your baseline ROI by 15-25%."

### Example 3: Competitor Intelligence

**You:** "What are competitors doing in Eye Level Row 3?"

**AI:** "Competitive analysis for Eye Level Row 3:

**Current Competitors:**
- Red Bull: $2.49, ROI 1.73
- Monster Energy: $2.79, ROI 1.74
- 5-hour Energy: $3.99, ROI 1.35

**Their Strategies:**
1. **Shelf Position**: They dominate the center 3 feet (most valuable real estate)
2. **Facings**: Red Bull has 8 facings vs your potential 4
3. **Promotions**: Monster runs weekly BOGO offers
4. **Cross-promo**: Often bundled with protein bars

**Your Competitive Edge:**
- Your price ($2.99) is positioned between budget (Red Bull) and premium (5-hour)
- Target younger demographic (18-35) vs their broader appeal
- Emphasize health-conscious positioning to differentiate

**Recommendation**: Negotiate for 6 facings minimum and run a launch promotion to gain initial shelf space."

---

## 🛠️ Advanced Configuration

### Change Gemini Model

```bash
# Use faster model (gemini-1.5-flash)
export LLM_MODEL="gemini-1.5-flash"

# Use most powerful model (default)
export LLM_MODEL="gemini-1.5-pro"

# Restart server
pkill -f uvicorn && python3 -m uvicorn api.main:app --port 8000
```

### Adjust Temperature (Creativity)

```bash
# More creative/varied responses
export LLM_TEMPERATURE=0.9

# More focused/deterministic responses
export LLM_TEMPERATURE=0.3

# Default: 0.7
```

### Adjust Max Tokens (Response Length)

```bash
# Longer, more detailed responses
export LLM_MAX_TOKENS=2000

# Shorter, more concise responses
export LLM_MAX_TOKENS=1000

# Default: 1500
```

---

## 🔍 Troubleshooting

### Issue 1: "No API key found"

**Solution:**
```bash
# Check if key is set
echo $GEMINI_API_KEY

# If empty, set it
export GEMINI_API_KEY="your-key-here"

# Or create .env file (see Step 2)
```

### Issue 2: "google-generativeai not installed"

**Solution:**
```bash
python3 -m pip install google-generativeai
```

### Issue 3: "API key invalid"

**Solution:**
- Verify your key at https://makersuite.google.com/app/apikey
- Make sure it starts with `AIza`
- Check for extra spaces or quotes when copying

### Issue 4: "Rate limit exceeded"

**Solution:**
- Free tier: 60 requests/minute, 1,500/day
- Wait a minute and try again
- Or upgrade to paid tier in Google Cloud Console

### Issue 5: Chat not working

**Solution:**
1. Check that you analyzed a product first (need session_id)
2. Make sure you selected a location by clicking on the planogram
3. Check browser console for errors (F12)
4. Verify API server is running on port 8000

---

## 📊 Gemini vs Other LLMs

| Feature | Gemini 1.5 Pro | GPT-4o | Claude 3.5 |
|---------|----------------|---------|-------------|
| **Free Tier** | ✅ 1,500/day | ❌ Paid only | ❌ Paid only |
| **Cost (Paid)** | $0.35/1M tokens | $5/1M tokens | $3/1M tokens |
| **Context Window** | 1M tokens | 128K tokens | 200K tokens |
| **Multimodal** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Speed** | Fast | Very Fast | Fast |
| **Quality** | Excellent | Excellent | Excellent |
| **Integration** | Native SDK | OpenAI SDK | OpenRouter |

**Recommendation:** Start with Gemini (free tier), then decide if you need to upgrade or switch based on usage.

---

## 🎓 Best Practices

### 1. Rate Limiting
```python
# Your system automatically handles rate limits
# But be mindful of the 60 req/min limit in free tier
```

### 2. Error Handling
- System falls back to template-based explanations if Gemini fails
- No user-facing errors, seamless experience

### 3. Cost Optimization
- Use `gemini-1.5-flash` for faster, cheaper responses
- Use `gemini-1.5-pro` for highest quality
- Monitor usage at https://makersuite.google.com/

### 4. Prompt Engineering
- The system is pre-configured with optimized prompts
- But you can customize in `agents/explainer_agent.py` if needed

---

## 🚀 Next Steps

Now that Gemini is integrated:

1. ✅ **Test the interactive planogram** - Open [demo/interactive_planogram.html](demo/interactive_planogram.html)
2. ✅ **Chat with AI about locations** - Click any shelf and ask questions
3. ✅ **Analyze different products** - Try beverages, snacks, dairy products
4. 📚 **Build knowledge graph** - Extract insights from retail research papers
5. 🎯 **Integrate knowledge graph** - Enhanced AI responses with research-backed knowledge

---

## 📞 Quick Reference

```bash
# Set API key
export GEMINI_API_KEY="your-key-here"

# Start server
python3 -m uvicorn api.main:app --port 8000

# Open interactive UI
open demo/interactive_planogram.html

# Test API
curl http://localhost:8000/api/health

# View logs
# Check terminal where uvicorn is running
```

---

## 🎉 You're All Set!

Your retail placement system now has:
- ✅ Gemini AI integration for natural language
- ✅ Interactive planogram with real-time colors
- ✅ Location-specific AI chat
- ✅ Research-backed ROI analysis
- ✅ Follow-up Q&A capability

**Next**: Add a research paper to build a knowledge graph for even more intelligent recommendations! 📚

---

**Need help?** Check the troubleshooting section or open an issue on GitHub.
