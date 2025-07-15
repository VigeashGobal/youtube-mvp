import os, json
from dotenv import load_dotenv
from openai import OpenAI
from .youtube_public import resolve_channel_id, fetch_public_metrics
from .financial_analysis import FinancialAnalyzer

load_dotenv(".env")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
DEFAULT_RPM = 5.0  # USD revenue per 1k views (tuneable)

def estimate_revenue(views: int, rpm: float = DEFAULT_RPM) -> float:
    return (views / 1000.0) * rpm

def get_channel_report(query: str, days: int = 30):
    cid      = resolve_channel_id(query)
    metrics  = fetch_public_metrics(cid, days)
    est_rev  = estimate_revenue(metrics[f"views_last_{days}d"])
    
    # Update metrics with estimated revenue
    metrics['estimated_revenue_usd'] = est_rev
    
    # Perform comprehensive financial analysis
    analyzer = FinancialAnalyzer()
    financial_report = analyzer.generate_financial_report(metrics)
    
    # Enhanced AI prompt with financial analysis
    prompt = f"""
You are a senior creator-economy analyst and financial advisor.

Channel metrics: {json.dumps(metrics, indent=2)}

Financial Analysis:
- Base Revenue: ${financial_report['sensitivity_analysis']['base_revenue']:,.0f}
- Optimistic Revenue: ${financial_report['sensitivity_analysis']['optimistic_revenue']:,.0f}
- Pessimistic Revenue: ${financial_report['sensitivity_analysis']['pessimistic_revenue']:,.0f}
- Risk Score: {financial_report['sensitivity_analysis']['risk_score']:.2f}
- Revenue Volatility: {financial_report['sensitivity_analysis']['revenue_volatility']:.2f}

Loan Recommendation:
- Recommended Advance: ${financial_report['loan_recommendation']['recommended_advance']:,.0f}
- Risk Level: {financial_report['loan_recommendation']['risk_level'].title()}
- Interest Rate: {financial_report['loan_recommendation']['interest_rate_percent']:.1f}%
- Repayment Period: {financial_report['loan_recommendation']['repayment_period_months']} months
- Monthly Payment: ${financial_report['loan_recommendation']['monthly_payment']:,.0f}

Write JSON with:
summary (≤150 words including financial insights),
opportunities (array of 3 short bullets including financial strategies),
risk_factors (array of 2-3 key risk considerations),
financial_recommendations (array of 2-3 specific financial actions).
"""
    
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    
    return {
        "channel_id": cid,
        "metrics": metrics,
        "estimated_revenue_usd": est_rev,
        "financial_analysis": financial_report,
        "ai": res.choices[0].message.content,
    } 