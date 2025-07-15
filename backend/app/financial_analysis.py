import json
import math
from typing import Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class FinancialMetrics:
    subscriber_count: int
    total_views: int
    views_last_30d: int
    video_count: int
    estimated_revenue_usd: float

@dataclass
class SensitivityAnalysis:
    base_revenue: float
    optimistic_revenue: float
    pessimistic_revenue: float
    revenue_volatility: float
    growth_rate: float
    risk_score: float

@dataclass
class LoanRecommendation:
    recommended_advance: float
    max_loan_amount: float
    risk_adjusted_amount: float
    repayment_period_months: int
    interest_rate_percent: float
    monthly_payment: float
    risk_level: str
    confidence_score: float

class FinancialAnalyzer:
    def __init__(self):
        # Risk factors and weights
        self.risk_factors = {
            'subscriber_growth': 0.25,
            'view_consistency': 0.20,
            'content_frequency': 0.15,
            'audience_engagement': 0.20,
            'revenue_stability': 0.20
        }
        
        # Sensitivity parameters
        self.rpm_scenarios = {
            'base': 5.0,
            'optimistic': 7.5,
            'pessimistic': 2.5
        }
        
        # Loan parameters
        self.loan_terms = {
            'max_advance_multiplier': 12,  # 12 months of revenue
            'risk_adjustment_factor': 0.7,
            'base_interest_rate': 0.08,  # 8% annual
            'risk_premium': {
                'low': 0.02,
                'medium': 0.05,
                'high': 0.10
            }
        }

    def calculate_sensitivity_analysis(self, metrics: FinancialMetrics) -> SensitivityAnalysis:
        """Calculate revenue sensitivity under different scenarios"""
        
        # Base revenue calculation
        base_revenue = metrics.estimated_revenue_usd
        
        # Optimistic scenario (higher RPM, growth)
        optimistic_revenue = base_revenue * (self.rpm_scenarios['optimistic'] / self.rpm_scenarios['base']) * 1.2
        
        # Pessimistic scenario (lower RPM, decline)
        pessimistic_revenue = base_revenue * (self.rpm_scenarios['pessimistic'] / self.rpm_scenarios['base']) * 0.8
        
        # Calculate volatility
        revenue_volatility = (optimistic_revenue - pessimistic_revenue) / base_revenue
        
        # Estimate growth rate (simplified)
        growth_rate = min(0.15, max(-0.05, (optimistic_revenue - base_revenue) / base_revenue))
        
        # Calculate risk score (0-1, higher = more risky)
        risk_score = self._calculate_risk_score(metrics)
        
        return SensitivityAnalysis(
            base_revenue=base_revenue,
            optimistic_revenue=optimistic_revenue,
            pessimistic_revenue=pessimistic_revenue,
            revenue_volatility=revenue_volatility,
            growth_rate=growth_rate,
            risk_score=risk_score
        )

    def _calculate_risk_score(self, metrics: FinancialMetrics) -> float:
        """Calculate comprehensive risk score based on multiple factors"""
        
        risk_score = 0.0
        
        # Subscriber growth risk (simplified proxy)
        if metrics.subscriber_count > 10000000:  # 10M+ subscribers
            risk_score += 0.1
        elif metrics.subscriber_count > 1000000:  # 1M+ subscribers
            risk_score += 0.2
        else:
            risk_score += 0.4
        
        # View consistency risk
        avg_views_per_video = metrics.total_views / max(metrics.video_count, 1)
        if avg_views_per_video > 1000000:  # 1M+ avg views
            risk_score += 0.1
        elif avg_views_per_video > 100000:  # 100K+ avg views
            risk_score += 0.2
        else:
            risk_score += 0.4
        
        # Content frequency risk
        if metrics.video_count > 100:  # 100+ videos
            risk_score += 0.1
        elif metrics.video_count > 50:  # 50+ videos
            risk_score += 0.2
        else:
            risk_score += 0.3
        
        # Revenue stability risk
        monthly_revenue = metrics.estimated_revenue_usd
        if monthly_revenue > 100000:  # $100K+ monthly
            risk_score += 0.1
        elif monthly_revenue > 10000:  # $10K+ monthly
            risk_score += 0.2
        else:
            risk_score += 0.4
        
        return min(1.0, risk_score)

    def generate_loan_recommendation(self, metrics: FinancialMetrics, sensitivity: SensitivityAnalysis) -> LoanRecommendation:
        """Generate comprehensive loan recommendation with risk adjustment"""
        
        # Base loan amount (12 months of revenue)
        base_loan_amount = metrics.estimated_revenue_usd * self.loan_terms['max_advance_multiplier']
        
        # Risk-adjusted amount
        risk_adjusted_amount = base_loan_amount * (1 - sensitivity.risk_score * self.loan_terms['risk_adjustment_factor'])
        
        # Determine risk level and interest rate
        if sensitivity.risk_score < 0.3:
            risk_level = 'low'
            interest_rate = self.loan_terms['base_interest_rate'] + self.loan_terms['risk_premium']['low']
        elif sensitivity.risk_score < 0.6:
            risk_level = 'medium'
            interest_rate = self.loan_terms['base_interest_rate'] + self.loan_terms['risk_premium']['medium']
        else:
            risk_level = 'high'
            interest_rate = self.loan_terms['base_interest_rate'] + self.loan_terms['risk_premium']['high']
        
        # Calculate repayment terms
        repayment_period = 24 if risk_level == 'low' else 18 if risk_level == 'medium' else 12
        monthly_interest_rate = interest_rate / 12
        monthly_payment = (risk_adjusted_amount * monthly_interest_rate * (1 + monthly_interest_rate) ** repayment_period) / ((1 + monthly_interest_rate) ** repayment_period - 1)
        
        # Confidence score based on data quality and consistency
        confidence_score = self._calculate_confidence_score(metrics, sensitivity)
        
        return LoanRecommendation(
            recommended_advance=risk_adjusted_amount,
            max_loan_amount=base_loan_amount,
            risk_adjusted_amount=risk_adjusted_amount,
            repayment_period_months=repayment_period,
            interest_rate_percent=interest_rate * 100,
            monthly_payment=monthly_payment,
            risk_level=risk_level,
            confidence_score=confidence_score
        )

    def _calculate_confidence_score(self, metrics: FinancialMetrics, sensitivity: SensitivityAnalysis) -> float:
        """Calculate confidence score based on data quality and consistency"""
        
        confidence = 0.8  # Base confidence
        
        # Adjust based on subscriber count (more data = higher confidence)
        if metrics.subscriber_count > 1000000:
            confidence += 0.1
        elif metrics.subscriber_count < 100000:
            confidence -= 0.1
        
        # Adjust based on revenue volatility
        if sensitivity.revenue_volatility < 0.3:
            confidence += 0.05
        elif sensitivity.revenue_volatility > 0.7:
            confidence -= 0.05
        
        # Adjust based on video count (more content = higher confidence)
        if metrics.video_count > 50:
            confidence += 0.05
        
        return min(1.0, max(0.5, confidence))

    def generate_financial_report(self, metrics: FinancialMetrics) -> Dict:
        """Generate comprehensive financial analysis report"""
        
        # Create metrics object
        financial_metrics = FinancialMetrics(
            subscriber_count=metrics['subscriber_count'],
            total_views=metrics['total_views'],
            views_last_30d=metrics['views_last_30d'],
            video_count=metrics['video_count'],
            estimated_revenue_usd=metrics['estimated_revenue_usd']
        )
        
        # Perform sensitivity analysis
        sensitivity = self.calculate_sensitivity_analysis(financial_metrics)
        
        # Generate loan recommendation
        loan_rec = self.generate_loan_recommendation(financial_metrics, sensitivity)
        
        # Create comprehensive report
        report = {
            "financial_metrics": {
                "subscriber_count": financial_metrics.subscriber_count,
                "total_views": financial_metrics.total_views,
                "views_last_30d": financial_metrics.views_last_30d,
                "video_count": financial_metrics.video_count,
                "estimated_revenue_usd": financial_metrics.estimated_revenue_usd
            },
            "sensitivity_analysis": {
                "base_revenue": sensitivity.base_revenue,
                "optimistic_revenue": sensitivity.optimistic_revenue,
                "pessimistic_revenue": sensitivity.pessimistic_revenue,
                "revenue_volatility": sensitivity.revenue_volatility,
                "growth_rate": sensitivity.growth_rate,
                "risk_score": sensitivity.risk_score
            },
            "loan_recommendation": {
                "recommended_advance": loan_rec.recommended_advance,
                "max_loan_amount": loan_rec.max_loan_amount,
                "risk_adjusted_amount": loan_rec.risk_adjusted_amount,
                "repayment_period_months": loan_rec.repayment_period_months,
                "interest_rate_percent": loan_rec.interest_rate_percent,
                "monthly_payment": loan_rec.monthly_payment,
                "risk_level": loan_rec.risk_level,
                "confidence_score": loan_rec.confidence_score
            },
            "scenarios": {
                "optimistic": {
                    "revenue": sensitivity.optimistic_revenue,
                    "loan_amount": sensitivity.optimistic_revenue * self.loan_terms['max_advance_multiplier'] * 0.8
                },
                "base": {
                    "revenue": sensitivity.base_revenue,
                    "loan_amount": loan_rec.recommended_advance
                },
                "pessimistic": {
                    "revenue": sensitivity.pessimistic_revenue,
                    "loan_amount": sensitivity.pessimistic_revenue * self.loan_terms['max_advance_multiplier'] * 0.6
                }
            }
        }
        
        return report 