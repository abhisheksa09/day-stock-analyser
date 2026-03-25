import yfinance as yf
import datetime

# ===== Calendar helpers =====
FED_DATES=["2026-03-22","2026-06-15"]
RBI_POLICY_DATES=["2026-04-01"]
BUDGET_DATES=["2026-02-01"]

def is_fed_meeting_today():
    return datetime.date.today().isoformat() in FED_DATES
def is_rbi_policy_today():
    return datetime.date.today().isoformat() in RBI_POLICY_DATES
def is_budget_today():
    return datetime.date.today().isoformat() in BUDGET_DATES

# ===== Macro context =====
def get_macro_context():
    data={}
    spx=yf.Ticker("^GSPC").history(period="2d")['Close']
    data["SPX_change"]=(spx[-1]-spx[-2])/spx[-2]*100
    vix=yf.Ticker("^VIX").history(period="2d")['Close']
    data["VIX"]=vix[-1]
    usd_inr=yf.Ticker("USDINR=X").history(period="2d")['Close']
    data["USDINR"]=usd_inr[-1]
    data["USDINR_change"]=(usd_inr[-1]-usd_inr[-2])/usd_inr[-2]*100
    crude=yf.Ticker("CL=F").history(period="2d")['Close']
    data["Crude_change"]=(crude[-1]-crude[-2])/crude[-2]*100
    gold=yf.Ticker("GC=F").history(period="2d")['Close']
    data["Gold_change"]=(gold[-1]-gold[-2])/gold[-2]*100
    data["fed_today"]=is_fed_meeting_today()
    data["rbi_today"]=is_rbi_policy_today()
    data["budget_today"]=is_budget_today()
    return data

# ===== News Sentiment (AI) =====
import requests, os
NEWS_API_KEY=os.environ.get("NEWS_API_KEY")
def get_sentiment_ai(text):
    # Placeholder: Replace with real AI model call
    text=text.lower()
    if any(w in text for w in ["loss","fall","drop","shock","war"]): return "negative"
    if any(w in text for w in ["rise","gain","bull","profit"]): return "positive"
    return "neutral"

def fetch_news_sentiment():
    url=f"https://newsapi.org/v2/top-headlines?country=in&category=business&apiKey={NEWS_API_KEY}"
    r=requests.get(url).json()
    headlines=[]
    for article in r.get("articles",[]):
        text=article["title"]
        sentiment=get_sentiment_ai(text)
        headlines.append({"text":text,"sentiment":sentiment})
    return headlines