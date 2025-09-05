"""
Performance Tracker Module

This module tracks and analyzes trading performance metrics
including returns, drawdowns, and risk-adjusted measures.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import math


class PerformanceTracker:
    """
    Tracks and analyzes trading performance metrics.
    """
    
    def __init__(self):
        """Initialize the performance tracker."""
        self.logger = logging.getLogger(__name__)
        self.trades = []
        self.performance_history = []
        self.metrics = {}
    
    def add_trade(self, trade_data: Dict[str, Any]) -> str:
        """
        Add a new trade to the performance tracker.
        
        Args:
            trade_data: Trade information
            
        Returns:
            Trade ID
        """
        try:
            trade_id = f"trade_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            trade = {
                'id': trade_id,
                'symbol': trade_data.get('symbol', ''),
                'entry_time': trade_data.get('entry_time', datetime.now().isoformat()),
                'exit_time': trade_data.get('exit_time'),
                'entry_price': float(trade_data.get('entry_price', 0)),
                'exit_price': float(trade_data.get('exit_price', 0)),
                'quantity': float(trade_data.get('quantity', 0)),
                'position_type': trade_data.get('position_type', 'long'),
                'status': trade_data.get('status', 'open'),
                'pnl': 0.0,
                'pnl_percent': 0.0,
                'commission': float(trade_data.get('commission', 0)),
                'slippage': float(trade_data.get('slippage', 0))
            }
            
            # Calculate PnL if trade is closed
            if trade['status'] == 'closed' and trade['exit_price']:
                trade['pnl'] = self._calculate_trade_pnl(trade)
                trade['pnl_percent'] = self._calculate_trade_pnl_percent(trade)
            
            self.trades.append(trade)
            self._update_performance_metrics()
            
            self.logger.info(f"Added trade {trade_id}: {trade['symbol']} PnL: {trade['pnl']:.2f}")
            return trade_id
            
        except Exception as e:
            self.logger.error(f"Error adding trade: {e}")
            raise
    
    def update_trade(self, trade_id: str, update_data: Dict[str, Any]) -> bool:
        """
        Update an existing trade.
        
        Args:
            trade_id: Trade identifier
            update_data: Updated trade data
            
        Returns:
            True if update successful
        """
        try:
            trade = self._find_trade(trade_id)
            if not trade:
                return False
            
            # Update trade data
            for key, value in update_data.items():
                if key in trade:
                    trade[key] = value
            
            # Recalculate PnL if trade is closed
            if trade['status'] == 'closed' and trade['exit_price']:
                trade['pnl'] = self._calculate_trade_pnl(trade)
                trade['pnl_percent'] = self._calculate_trade_pnl_percent(trade)
            
            self._update_performance_metrics()
            
            self.logger.info(f"Updated trade {trade_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating trade {trade_id}: {e}")
            return False
    
    def _calculate_trade_pnl(self, trade: Dict[str, Any]) -> float:
        """Calculate trade profit/loss."""
        if trade['position_type'] == 'long':
            pnl = (trade['exit_price'] - trade['entry_price']) * trade['quantity']
        else:  # short
            pnl = (trade['entry_price'] - trade['exit_price']) * trade['quantity']
        
        # Subtract costs
        pnl -= trade['commission'] + trade['slippage']
        
        return pnl
    
    def _calculate_trade_pnl_percent(self, trade: Dict[str, Any]) -> float:
        """Calculate trade profit/loss percentage."""
        if trade['entry_price'] == 0:
            return 0.0
        
        entry_value = trade['entry_price'] * trade['quantity']
        if entry_value == 0:
            return 0.0
        
        return (trade['pnl'] / entry_value) * 100
    
    def _find_trade(self, trade_id: str) -> Optional[Dict[str, Any]]:
        """Find a trade by ID."""
        for trade in self.trades:
            if trade['id'] == trade_id:
                return trade
        return None
    
    def _update_performance_metrics(self):
        """Update performance metrics based on current trades."""
        if not self.trades:
            return
        
        closed_trades = [t for t in self.trades if t['status'] == 'closed']
        open_trades = [t for t in self.trades if t['status'] == 'open']
        
        # Calculate basic metrics
        total_trades = len(closed_trades)
        winning_trades = len([t for t in closed_trades if t['pnl'] > 0])
        losing_trades = len([t for t in closed_trades if t['pnl'] < 0])
        
        # Calculate returns
        total_pnl = sum(t['pnl'] for t in closed_trades)
        total_return = sum(t['pnl_percent'] for t in closed_trades)
        
        # Calculate win rate
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        # Calculate average PnL
        avg_win = sum(t['pnl'] for t in closed_trades if t['pnl'] > 0) / winning_trades if winning_trades > 0 else 0
        avg_loss = sum(t['pnl'] for t in closed_trades if t['pnl'] < 0) / losing_trades if losing_trades > 0 else 0
        
        # Calculate profit factor
        total_wins = sum(t['pnl'] for t in closed_trades if t['pnl'] > 0)
        total_losses = abs(sum(t['pnl'] for t in closed_trades if t['pnl'] < 0))
        profit_factor = total_wins / total_losses if total_losses > 0 else float('inf')
        
        # Calculate drawdown
        max_drawdown = self._calculate_max_drawdown()
        
        # Calculate Sharpe ratio (simplified)
        sharpe_ratio = self._calculate_sharpe_ratio()
        
        # Update metrics
        self.metrics = {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'total_return': total_return,
            'average_win': avg_win,
            'average_loss': avg_loss,
            'profit_factor': profit_factor,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'open_positions': len(open_trades),
            'last_updated': datetime.now().isoformat()
        }
        
        # Record performance snapshot
        self._record_performance_snapshot()
    
    def _calculate_max_drawdown(self) -> float:
        """Calculate maximum drawdown."""
        if not self.trades:
            return 0.0
        
        # Calculate cumulative PnL over time
        cumulative_pnl = []
        running_pnl = 0.0
        
        # Sort trades by time
        sorted_trades = sorted(self.trades, key=lambda x: x['entry_time'])
        
        for trade in sorted_trades:
            if trade['status'] == 'closed':
                running_pnl += trade['pnl']
                cumulative_pnl.append(running_pnl)
        
        if not cumulative_pnl:
            return 0.0
        
        # Calculate drawdown
        peak = cumulative_pnl[0]
        max_dd = 0.0
        
        for pnl in cumulative_pnl:
            if pnl > peak:
                peak = pnl
            drawdown = (peak - pnl) / peak if peak > 0 else 0
            max_dd = max(max_dd, drawdown)
        
        return max_dd * 100  # Convert to percentage
    
    def _calculate_sharpe_ratio(self) -> float:
        """Calculate Sharpe ratio (simplified)."""
        if not self.trades:
            return 0.0
        
        closed_trades = [t for t in self.trades if t['status'] == 'closed']
        if len(closed_trades) < 2:
            return 0.0
        
        # Calculate returns
        returns = [t['pnl_percent'] for t in closed_trades]
        
        # Calculate mean and standard deviation
        mean_return = sum(returns) / len(returns)
        variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
        std_dev = math.sqrt(variance)
        
        # Calculate Sharpe ratio (assuming risk-free rate of 0)
        if std_dev == 0:
            return 0.0
        
        return mean_return / std_dev
    
    def _record_performance_snapshot(self):
        """Record a performance snapshot."""
        snapshot = {
            'timestamp': datetime.now().isoformat(),
            'metrics': self.metrics.copy(),
            'total_trades': len(self.trades)
        }
        
        self.performance_history.append(snapshot)
        
        # Keep only recent history (last 1000 snapshots)
        if len(self.performance_history) > 1000:
            self.performance_history = self.performance_history[-1000:]
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get current performance summary."""
        return self.metrics.copy()
    
    def get_trade_history(self, symbol: str = None) -> List[Dict[str, Any]]:
        """Get trade history, optionally filtered by symbol."""
        if symbol:
            return [t for t in self.trades if t['symbol'] == symbol]
        return self.trades.copy()
    
    def get_performance_history(self) -> List[Dict[str, Any]]:
        """Get performance history snapshots."""
        return self.performance_history.copy()
    
    def get_monthly_performance(self, year: int = None) -> Dict[str, Any]:
        """Get monthly performance breakdown."""
        if year is None:
            year = datetime.now().year
        
        monthly_data = {}
        
        for trade in self.trades:
            if trade['status'] == 'closed':
                trade_date = datetime.fromisoformat(trade['entry_time'])
                if trade_date.year == year:
                    month = trade_date.strftime('%B')
                    if month not in monthly_data:
                        monthly_data[month] = {
                            'trades': 0,
                            'pnl': 0.0,
                            'wins': 0,
                            'losses': 0
                        }
                    
                    monthly_data[month]['trades'] += 1
                    monthly_data[month]['pnl'] += trade['pnl']
                    
                    if trade['pnl'] > 0:
                        monthly_data[month]['wins'] += 1
                    else:
                        monthly_data[month]['losses'] += 1
        
        return monthly_data
