"""
Risk Manager Module

This module handles risk management for trading strategies
including position sizing, stop losses, and portfolio protection.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import math


class RiskManager:
    """
    Manages risk across all trading strategies and positions.
    """
    
    def __init__(self, max_portfolio_risk: float = 0.02, max_position_risk: float = 0.01):
        """
        Initialize the risk manager.
        
        Args:
            max_portfolio_risk: Maximum portfolio risk per trade (default: 2%)
            max_position_risk: Maximum position risk per trade (default: 1%)
        """
        self.logger = logging.getLogger(__name__)
        self.max_portfolio_risk = max_portfolio_risk
        self.max_position_risk = max_position_risk
        self.risk_alerts = []
        self.risk_metrics = {}
    
    def calculate_position_size(self, 
                               capital: float,
                               entry_price: float,
                               stop_loss: float,
                               risk_per_trade: float = None) -> Dict[str, Any]:
        """
        Calculate optimal position size based on risk parameters.
        
        Args:
            capital: Available capital
            entry_price: Entry price for the trade
            stop_loss: Stop loss price
            risk_per_trade: Risk per trade (overrides default)
            
        Returns:
            Position sizing information
        """
        try:
            if risk_per_trade is None:
                risk_per_trade = self.max_position_risk
            
            # Calculate risk per share
            risk_per_share = abs(entry_price - stop_loss)
            
            if risk_per_share == 0:
                return {
                    'position_size': 0,
                    'risk_amount': 0,
                    'shares': 0,
                    'error': 'Invalid stop loss price'
                }
            
            # Calculate risk amount
            risk_amount = capital * risk_per_trade
            
            # Calculate position size
            shares = risk_amount / risk_per_share
            position_value = shares * entry_price
            
            # Ensure position doesn't exceed capital
            if position_value > capital:
                shares = capital / entry_price
                position_value = capital
                risk_amount = shares * risk_per_share
            
            return {
                'position_size': position_value,
                'risk_amount': risk_amount,
                'shares': shares,
                'risk_percentage': (risk_amount / capital) * 100
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating position size: {e}")
            return {
                'position_size': 0,
                'risk_amount': 0,
                'shares': 0,
                'error': str(e)
            }
    
    def validate_trade_risk(self, 
                           trade_params: Dict[str, Any],
                           portfolio_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate if a trade meets risk management criteria.
        
        Args:
            trade_params: Trade parameters
            portfolio_state: Current portfolio state
            
        Returns:
            Risk validation results
        """
        try:
            # Calculate trade risk
            position_size = trade_params.get('position_size', 0)
            capital = portfolio_state.get('total_capital', 0)
            
            if capital == 0:
                return {
                    'is_valid': False,
                    'reason': 'No capital available',
                    'risk_score': 0
                }
            
            # Calculate risk metrics
            position_risk = position_size / capital
            portfolio_risk = self._calculate_portfolio_risk(portfolio_state)
            total_risk = portfolio_risk + position_risk
            
            # Risk validation
            is_valid = (
                position_risk <= self.max_position_risk and
                total_risk <= self.max_portfolio_risk
            )
            
            risk_score = self._calculate_risk_score(position_risk, portfolio_risk)
            
            return {
                'is_valid': is_valid,
                'position_risk': position_risk,
                'portfolio_risk': portfolio_risk,
                'total_risk': total_risk,
                'risk_score': risk_score,
                'reason': 'Trade approved' if is_valid else 'Risk limits exceeded'
            }
            
        except Exception as e:
            self.logger.error(f"Error validating trade risk: {e}")
            return {
                'is_valid': False,
                'reason': f'Validation error: {str(e)}',
                'risk_score': 0
            }
    
    def _calculate_portfolio_risk(self, portfolio_state: Dict[str, Any]) -> float:
        """Calculate current portfolio risk."""
        positions = portfolio_state.get('positions', [])
        total_risk = 0.0
        
        for position in positions:
            position_value = position.get('current_value', 0)
            total_capital = portfolio_state.get('total_capital', 1)
            if total_capital > 0:
                total_risk += position_value / total_capital
        
        return total_risk
    
    def _calculate_risk_score(self, position_risk: float, portfolio_risk: float) -> float:
        """Calculate overall risk score (0-100, lower is better)."""
        # Normalize risks to 0-100 scale
        position_score = min(position_risk * 1000, 100)  # Scale up small percentages
        portfolio_score = min(portfolio_risk * 1000, 100)
        
        # Weighted average (position risk weighted more heavily)
        risk_score = (position_score * 0.7) + (portfolio_score * 0.3)
        
        return min(risk_score, 100)
    
    def generate_risk_alert(self, 
                           alert_type: str,
                           message: str,
                           severity: str = 'medium') -> Dict[str, Any]:
        """
        Generate a risk alert.
        
        Args:
            alert_type: Type of risk alert
            message: Alert message
            severity: Alert severity (low, medium, high, critical)
            
        Returns:
            Risk alert information
        """
        alert = {
            'id': f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'type': alert_type,
            'message': message,
            'severity': severity,
            'timestamp': datetime.now().isoformat(),
            'acknowledged': False
        }
        
        self.risk_alerts.append(alert)
        self.logger.warning(f"Risk alert generated: {message}")
        
        return alert
    
    def get_risk_alerts(self, severity: str = None) -> List[Dict[str, Any]]:
        """Get risk alerts, optionally filtered by severity."""
        if severity:
            return [alert for alert in self.risk_alerts 
                   if alert['severity'] == severity]
        return self.risk_alerts
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Mark a risk alert as acknowledged."""
        for alert in self.risk_alerts:
            if alert['id'] == alert_id:
                alert['acknowledged'] = True
                return True
        return False
    
    def get_risk_metrics(self) -> Dict[str, Any]:
        """Get current risk metrics."""
        return {
            'max_portfolio_risk': self.max_portfolio_risk,
            'max_position_risk': self.max_position_risk,
            'active_alerts': len([a for a in self.risk_alerts if not a['acknowledged']]),
            'total_alerts': len(self.risk_alerts),
            'last_alert': self.risk_alerts[-1] if self.risk_alerts else None
        }
