import math

STOCKS=[
    {"sym":"HDFCBANK","name":"HDFC Bank","ikey":"NSE_EQ|INE040A01034","sec":"Banking"},
    {"sym":"RELIANCE","name":"Reliance Industries","ikey":"NSE_EQ|INE002A01018","sec":"Energy"},
    {"sym":"TCS","name":"Tata Consultancy","ikey":"NSE_EQ|INE467B01029","sec":"IT"},
    # ... Add remaining 27 Nifty 50 stocks
]

def build_setup(stock, macro=None, headlines=None):
    # Placeholder: Replace with real LTP/VWAP/RSI/ATR calculation from Upstox
    ltp_prev=1000
    vwap=1000
    rsi=50
    atr=10
    entry=ltp_prev+5
    target=entry+2*atr
    sl=ltp_prev-atr*0.3
    rr=abs(target-entry)/abs(sl-entry)
    confidence=80

    # Adjust confidence based on macro
    if macro:
        if macro.get("SPX_change",-0.5)<-1: confidence-=10
        if macro.get("VIX",20)>25: confidence-=10
    return {
        "sym":stock["sym"], "signal":"BUY","ltp_prev":ltp_prev,"vwap":vwap,"rsi":rsi,
        "atr":atr,"entry":entry,"target":target,"sl":sl,"rr":rr,"confidence":confidence
    }