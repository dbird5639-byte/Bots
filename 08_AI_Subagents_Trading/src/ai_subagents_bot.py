"""
AI Subagents Trading Bot - Main Class

This is the main trading bot class for AI Subagents Trading,
implementing a multi-agent system where specialized AI agents
handle different aspects of trading.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import signal
import sys
from decimal import Decimal

from .config_manager import ConfigManager
from .logger import Logger
from .agent_orchestrator import AgentOrchestrator
from .market_analysis_agent import MarketAnalysisAgent
from .strategy_agent import StrategyAgent
from .risk_management_agent import RiskManagementAgent
from .execution_agent import ExecutionAgent
from .portfolio_agent import PortfolioAgent
from .research_agent import ResearchAgent


class AISubagentsTradingBot:
    """
    Main AI Subagents Trading Bot class
    
    This class orchestrates a multi-agent AI system where specialized agents handle:
    - Market Analysis Agent: Market data analysis and insights
    - Strategy Agent: Trading strategy generation and optimization
    - Risk Management Agent: Risk assessment and mitigation
    - Execution Agent: Trade execution and order management
    - Portfolio Agent: Portfolio optimization and rebalancing
    - Research Agent: Market research and trend analysis
    """
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize the AI Subagents Trading Bot"""
        self.config_path = config_path
        self.config = ConfigManager(config_path)
        self.logger = Logger(self.config)
        self.log = logging.getLogger(__name__)
        
        # Agent orchestrator
        self.agent_orchestrator: Optional[AgentOrchestrator] = None
        
        # Individual AI agents
        self.market_analysis_agent: Optional[MarketAnalysisAgent] = None
        self.strategy_agent: Optional[StrategyAgent] = None
        self.risk_management_agent: Optional[RiskManagementAgent] = None
        self.execution_agent: Optional[ExecutionAgent] = None
        self.portfolio_agent: Optional[PortfolioAgent] = None
        self.research_agent: Optional[ResearchAgent] = None
        
        # Bot state
        self.is_running = False
        self.is_initialized = False
        self.start_time = None
        
        # Performance tracking
        self.performance_metrics = {}
        self.trade_history = []
        self.agent_performance = {}
        
        # Setup signal handlers
        self._setup_signal_handlers()
        
        self.log.info("AI Subagents Trading Bot initialized")
    
    async def initialize(self) -> bool:
        """Initialize all bot components and agents"""
        try:
            self.log.info("Initializing AI Subagents Trading Bot...")
            
            # Initialize agent orchestrator
            self.agent_orchestrator = AgentOrchestrator(self.config, self.logger)
            await self.agent_orchestrator.initialize()
            
            # Initialize individual agents
            self.market_analysis_agent = MarketAnalysisAgent(self.config, self.logger)
            self.strategy_agent = StrategyAgent(self.config, self.logger)
            self.risk_management_agent = RiskManagementAgent(self.config, self.logger)
            self.execution_agent = ExecutionAgent(self.config, self.logger)
            self.portfolio_agent = PortfolioAgent(self.config, self.logger)
            self.research_agent = ResearchAgent(self.config, self.logger)
            
            # Initialize each agent
            await self.market_analysis_agent.initialize()
            await self.strategy_agent.initialize()
            await self.risk_management_agent.initialize()
            await self.execution_agent.initialize()
            await self.portfolio_agent.initialize()
            await self.research_agent.initialize()
            
            # Register agents with orchestrator
            await self.agent_orchestrator.register_agent('market_analysis', self.market_analysis_agent)
            await self.agent_orchestrator.register_agent('strategy', self.strategy_agent)
            await self.agent_orchestrator.register_agent('risk_management', self.risk_management_agent)
            await self.agent_orchestrator.register_agent('execution', self.execution_agent)
            await self.agent_orchestrator.register_agent('portfolio', self.portfolio_agent)
            await self.agent_orchestrator.register_agent('research', self.research_agent)
            
            self.is_initialized = True
            self.log.info("AI Subagents Trading Bot initialization completed successfully")
            return True
            
        except Exception as e:
            self.log.error(f"Failed to initialize AI Subagents Trading Bot: {e}")
            return False
    
    async def start(self) -> bool:
        """Start the trading bot"""
        if not self.is_initialized:
            self.log.error("Bot not initialized. Call initialize() first.")
            return False
        
        try:
            self.log.info("Starting AI Subagents Trading Bot...")
            self.is_running = True
            self.start_time = datetime.now()
            
            # Start main trading loop
            await self._trading_loop()
            
            return True
            
        except Exception as e:
            self.log.error(f"Failed to start trading bot: {e}")
            return False
    
    async def stop(self):
        """Stop the trading bot gracefully"""
        try:
            self.log.info("Stopping AI Subagents Trading Bot...")
            self.is_running = False
            
            # Stop all agents
            if self.market_analysis_agent:
                await self.market_analysis_agent.shutdown()
            if self.strategy_agent:
                await self.strategy_agent.shutdown()
            if self.risk_management_agent:
                await self.risk_management_agent.shutdown()
            if self.execution_agent:
                await self.execution_agent.shutdown()
            if self.portfolio_agent:
                await self.portfolio_agent.shutdown()
            if self.research_agent:
                await self.research_agent.shutdown()
            if self.agent_orchestrator:
                await self.agent_orchestrator.shutdown()
            
            self.log.info("AI Subagents Trading Bot stopped successfully")
            
        except Exception as e:
            self.log.error(f"Error during bot shutdown: {e}")
    
    async def _trading_loop(self):
        """Main trading loop for AI Subagents system"""
        try:
            while self.is_running:
                # Phase 1: Market Analysis
                await self._execute_market_analysis_phase()
                
                # Phase 2: Research and Strategy
                await self._execute_research_strategy_phase()
                
                # Phase 3: Risk Assessment
                await self._execute_risk_assessment_phase()
                
                # Phase 4: Portfolio Optimization
                await self._execute_portfolio_optimization_phase()
                
                # Phase 5: Trade Execution
                await self._execute_trade_execution_phase()
                
                # Phase 6: Performance Monitoring
                await self._execute_performance_monitoring_phase()
                
                # Update performance metrics
                await self._update_performance_metrics()
                
                # Wait for next iteration
                await asyncio.sleep(self.config.get('trading.update_interval', 60))
                
        except Exception as e:
            self.log.error(f"Error in trading loop: {e}")
            await self.stop()
    
    async def _execute_market_analysis_phase(self):
        """Execute market analysis phase using AI agents"""
        try:
            self.log.info("Executing Market Analysis Phase...")
            
            # Get market data
            market_data = await self.agent_orchestrator.get_market_data()
            
            # Market analysis agent analyzes the data
            market_analysis = await self.market_analysis_agent.analyze_markets(market_data)
            
            # Store analysis results
            await self.agent_orchestrator.store_analysis_results('market_analysis', market_analysis)
            
            self.log.info("Market Analysis Phase completed")
            
        except Exception as e:
            self.log.error(f"Error in market analysis phase: {e}")
    
    async def _execute_research_strategy_phase(self):
        """Execute research and strategy phase using AI agents"""
        try:
            self.log.info("Executing Research and Strategy Phase...")
            
            # Research agent conducts market research
            research_results = await self.research_agent.conduct_research()
            
            # Strategy agent generates trading strategies
            strategies = await self.strategy_agent.generate_strategies(research_results)
            
            # Store results
            await self.agent_orchestrator.store_analysis_results('research', research_results)
            await self.agent_orchestrator.store_analysis_results('strategies', strategies)
            
            self.log.info("Research and Strategy Phase completed")
            
        except Exception as e:
            self.log.error(f"Error in research and strategy phase: {e}")
    
    async def _execute_risk_assessment_phase(self):
        """Execute risk assessment phase using AI agents"""
        try:
            self.log.info("Executing Risk Assessment Phase...")
            
            # Get current portfolio state
            portfolio_state = await self.portfolio_agent.get_portfolio_state()
            
            # Risk management agent assesses risk
            risk_assessment = await self.risk_management_agent.assess_portfolio_risk(portfolio_state)
            
            # Store risk assessment
            await self.agent_orchestrator.store_analysis_results('risk_assessment', risk_assessment)
            
            self.log.info("Risk Assessment Phase completed")
            
        except Exception as e:
            self.log.error(f"Error in risk assessment phase: {e}")
    
    async def _execute_portfolio_optimization_phase(self):
        """Execute portfolio optimization phase using AI agents"""
        try:
            self.log.info("Executing Portfolio Optimization Phase...")
            
            # Get all analysis results
            analysis_results = await self.agent_orchestrator.get_all_analysis_results()
            
            # Portfolio agent optimizes portfolio
            optimization_recommendations = await self.portfolio_agent.optimize_portfolio(analysis_results)
            
            # Store optimization recommendations
            await self.agent_orchestrator.store_analysis_results('optimization', optimization_recommendations)
            
            self.log.info("Portfolio Optimization Phase completed")
            
        except Exception as e:
            self.log.error(f"Error in portfolio optimization phase: {e}")
    
    async def _execute_trade_execution_phase(self):
        """Execute trade execution phase using AI agents"""
        try:
            self.log.info("Executing Trade Execution Phase...")
            
            # Get optimization recommendations
            optimization = await self.agent_orchestrator.get_analysis_results('optimization')
            
            if optimization and optimization.get('recommendations'):
                # Execution agent executes trades
                execution_results = await self.execution_agent.execute_recommendations(
                    optimization['recommendations']
                )
                
                # Store execution results
                await self.agent_orchestrator.store_analysis_results('execution', execution_results)
                
                # Log trades
                for result in execution_results:
                    if result['success']:
                        self.trade_history.append({
                            'timestamp': datetime.now(),
                            'type': 'ai_agent_execution',
                            'result': result,
                            'status': 'executed'
                        })
                
                self.log.info(f"Trade Execution Phase completed: {len(execution_results)} trades executed")
            else:
                self.log.info("Trade Execution Phase: No trades to execute")
            
        except Exception as e:
            self.log.error(f"Error in trade execution phase: {e}")
    
    async def _execute_performance_monitoring_phase(self):
        """Execute performance monitoring phase using AI agents"""
        try:
            self.log.info("Executing Performance Monitoring Phase...")
            
            # Monitor agent performance
            agent_performance = await self.agent_orchestrator.get_agent_performance()
            
            # Update agent performance metrics
            self.agent_performance.update(agent_performance)
            
            # Log performance
            self.log.info(f"Agent Performance: {agent_performance}")
            
            self.log.info("Performance Monitoring Phase completed")
            
        except Exception as e:
            self.log.error(f"Error in performance monitoring phase: {e}")
    
    async def _update_performance_metrics(self):
        """Update performance metrics"""
        try:
            # Get current portfolio performance
            portfolio_performance = await self.portfolio_agent.get_performance_metrics()
            
            # Update metrics
            self.performance_metrics.update(portfolio_performance)
            self.performance_metrics['uptime'] = (
                datetime.now() - self.start_time
            ).total_seconds() if self.start_time else 0
            self.performance_metrics['total_trades'] = len(self.trade_history)
            self.performance_metrics['agent_performance'] = self.agent_performance
            
            # Log performance
            self.log.info(f"Performance metrics updated: {self.performance_metrics}")
            
        except Exception as e:
            self.log.error(f"Error updating performance metrics: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current bot status"""
        return {
            'is_running': self.is_running,
            'is_initialized': self.is_initialized,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'uptime': self.performance_metrics.get('uptime', 0),
            'total_trades': len(self.trade_history),
            'agent_count': len(self.agent_performance),
            'performance_metrics': self.performance_metrics
        }
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            self.log.info(f"Received signal {signum}, shutting down gracefully...")
            asyncio.create_task(self.stop())
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.stop()


# Main execution function
async def main():
    """Main function to run the AI Subagents Trading Bot"""
    config_path = "config/config.yaml"
    
    async with AISubagentsTradingBot(config_path) as bot:
        await bot.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Error running bot: {e}")
