import datetime
from signals import STOCKS, build_setup
from macro import get_macro_context, fetch_news_sentiment

session_date=""
session_alerts=set()

def is_dangerous_day(stock_prev_close, macro, news_headlines):
    danger=False
    score_adj=0
    if macro.get("fed_today") or macro.get("rbi_today") or macro.get("budget_today"):
        danger=True; score_adj-=30
    gap_pct = (stock_prev_close['open']-stock_prev_close['prev_close'])/stock_prev_close['prev_close']*100
    if abs(gap_pct)>=3:
        danger=True; score_adj-=20
    if macro["VIX"]>25 or macro["SPX_change"]<-1 or abs(macro.get("USDINR_change",0))>1:
        danger=True; score_adj-=15
    neg_count = sum(1 for h in news_headlines if h['sentiment']=='negative')
    if neg_count>3:
        danger=True; score_adj-=10
    return danger, score_adj

def run_scan_all():
    macro=get_macro_context()
    headlines=fetch_news_sentiment()
    results=[]
    for s in STOCKS:
        sig=build_setup(s, macro=macro, headlines=headlines)
        danger, score_adj=is_dangerous_day({'open':sig['entry'],'prev_close':sig['ltp_prev']}, macro, headlines)
        sig['danger']=danger
        sig['score_adj']=score_adj
        sig['confidence']=max(0,min(100,sig['confidence']+score_adj))
        if sig['danger'] and sig['confidence']<55: sig['signal']='WATCH'
        results.append(sig)
    return {"data":results}

def get_alert_status():
    return {"date":datetime.date.today().isoformat(), "alerts_sent":list(session_alerts)}