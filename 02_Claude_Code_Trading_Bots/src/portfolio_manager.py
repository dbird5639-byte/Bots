"""
Portfolio Manager Module

This module manages the trading portfolio including positions,
capital allocation, and performance tracking.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json


class PortfolioManager:
    """
    Manages the trading portfolio and capital allocation.
    """
    
    def __init__(self, initial_capital: float = 10000.0):
        """
        Initialize the portfolio manager.
        
        Args:
            initial_capital: Starting capital amount
        """
        self.logger = logging.getLogger(__name__)
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.positions = {}
        self.portfolio_history = []
        self.performance_metrics = {}
    
    def add_position(self, 
                    symbol: str,
                    quantity: float,
                    entry_price: float,
                    position_type: str = 'long') -> Dict[str, Any]:
        """
        Add a new position to the portfolio.
        
        Args:
            symbol: Trading symbol
            quantity: Position quantity
            entry_price: Entry price
            position_type: Position type (long/short)
            
        Returns:
            Position information
        """
        try:
            position_id = f"{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            position = {
                'id': position_id,
                'symbol': symbol,
                'quantity': quantity,
                'entry_price': entry_price,
                'position_type': position_type,
                'entry_time': datetime.now().isoformat(),
                'current_price': entry_price,
                'unrealized_pnl': 0.0,
                'realized_pnl': 0.0,
                'status': 'open'
            }
            
            self.positions[position_id] = position
            self._update_portfolio_value()
            self._record_portfolio_snapshot()
            
            self.logger.info(f"Added position {position_id}: {symbol} {quantity} @ {entry_price}")
            return position
            
        except Exception as e:
            self.logger.error(f"Error adding position: {e}")
            raise
    
    def update_position(self, 
                       position_id: str,
                       current_price: float,
                       quantity_change: float = 0) -> Dict[str, Any]:
        """
        Update position with current market data.
        
        Args:
            position_id: Position identifier
            current_price: Current market price
            quantity_change: Change in quantity (for partial closes)
            
        Returns:
            Updated position information
        """
        try:
            if position_id not in self.positions:
                raise ValueError(f"Position {position_id} not found")
            
            position = self.positions[position_id]
            old_quantity = position['quantity']
            
            # Update quantity if there's a change
            if quantity_change != 0:
                position['quantity'] += quantity_change
                
                # Close position if quantity becomes 0
                if position['quantity'] <= 0:
                    position['status'] = 'closed'
                    position['close_time'] = datetime.now().isoformat()
                    position['realized_pnl'] = self._calculate_realized_pnl(
                        position, current_price, abs(quantity_change)
                    )
                    position['quantity'] = 0
            
            # Update current price and unrealized PnL
            position['current_price'] = current_price
            position['unrealized_pnl'] = self._calculate_unrealized_pnl(position)
            
            # Update portfolio value
            self._update_portfolio_value()
            self._record_portfolio_snapshot()
            
            self.logger.info(f"Updated position {position_id}: PnL = {position['unrealized_pnl']:.2f}")
            return position
            
        except Exception as e:
            self.logger.error(f"Error updating position: {e}")
            raise
    
    def close_position(self, position_id: str, exit_price: float) -> Dict[str, Any]:
        """
        Close a position completely.
        
        Args:
            position_id: Position identifier
            exit_price: Exit price
            
        Returns:
            Closed position information
        """
        try:
            if position_id not in self.positions:
                raise ValueError(f"Position {position_id} not found")
            
            position = self.positions[position_id]
            
            # Calculate realized PnL
            realized_pnl = self._calculate_realized_pnl(
                position, exit_price, position['quantity']
            )
            
            # Update position
            position['status'] = 'closed'
            position['close_time'] = datetime.now().isoformat()
            position['exit_price'] = exit_price
            position['realized_pnl'] = realized_pnl
            position['unrealized_pnl'] = 0.0
            position['quantity'] = 0
            
            # Update portfolio
            self._update_portfolio_value()
            self._record_portfolio_snapshot()
            
            self.logger.info(f"Closed position {position_id}: PnL = {realized_pnl:.2f}")
            return position
            
        except Exception as e:
            self.logger.error(f"Error closing position: {e}")
            raise
    
    def _calculate_unrealized_pnl(self, position: Dict[str, Any]) -> float:
        """Calculate unrealized profit/loss for a position."""
        if position['position_type'] == 'long':
            return (position['current_price'] - position['entry_price']) * position['quantity']
        else:  # short
            return (position['entry_price'] - position['current_price']) * position['quantity']
    
    def _calculate_realized_pnl(self, 
                               position: Dict[str, Any],
                               exit_price: float,
                               quantity: float) -> float:
        """Calculate realized profit/loss for a position."""
        if position['position_type'] == 'long':
            return (exit_price - position['entry_price']) * quantity
        else:  # short
            return (position['entry_price'] - exit_price) * quantity
    
    def _update_portfolio_value(self):
        """Update current portfolio value."""
        total_value = self.current_capital
        
        for position in self.positions.values():
            if position['status'] == 'open':
                total_value += position['unrealized_pnl']
            else:
                total_value += position['realized_pnl']
        
        self.current_capital = total_value
    
    def _record_portfolio_snapshot(self):
        """Record a snapshot of the current portfolio state."""
        snapshot = {
            'timestamp': datetime.now().isoformat(),
            'total_capital': self.current_capital,
            'total_positions': len([p for p in self.positions.values() if p['status'] == 'open']),
            'unrealized_pnl': sum(p['unrealized_pnl'] for p in self.positions.values() if p['status'] == 'open'),
            'realized_pnl': sum(p['realized_pnl'] for p in self.positions.values()),
            'positions': {pid: pos.copy() for pid, pos in self.positions.items()}
        }
        
        self.portfolio_history.append(snapshot)
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get current portfolio summary."""
        open_positions = [p for p in self.positions.values() if p['status'] == 'open']
        closed_positions = [p for p in self.positions.values() if p['status'] == 'closed']
        
        return {
            'initial_capital': self.initial_capital,
            'current_capital': self.current_capital,
            'total_return': ((self.current_capital - self.initial_capital) / self.initial_capital) * 100,
            'open_positions': len(open_positions),
            'closed_positions': len(closed_positions),
            'total_unrealized_pnl': sum(p['unrealized_pnl'] for p in open_positions),
            'total_realized_pnl': sum(p['realized_pnl'] for p in closed_positions),
            'portfolio_value': self.current_capital
        }
    
    def get_position(self, position_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific position by ID."""
        return self.positions.get(position_id)
    
    def get_open_positions(self) -> List[Dict[str, Any]]:
        """Get all open positions."""
        return [p for p in self.positions.values() if p['status'] == 'open']
    
    def get_portfolio_history(self) -> List[Dict[str, Any]]:
        """Get portfolio history snapshots."""
        return self.portfolio_history.copy()
