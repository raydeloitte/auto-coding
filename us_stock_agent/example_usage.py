#!/usr/bin/env python3
"""
Example usage of the Stock Analysis Multi-Agent System

This script demonstrates how to use the orchestrator and various agents
to perform comprehensive stock analysis.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from orchestrator.main_agent import StockAnalysisOrchestrator
from shared.data_models import Portfolio
from utils.logger import setup_logging
from utils.config import LoggingConfig


async def basic_stock_analysis():
    """Example of basic stock analysis for a single symbol."""
    print("🚀 Starting Basic Stock Analysis Example")
    print("=" * 50)
    
    # Initialize orchestrator with configuration
    config_path = Path(__file__).parent / "config" / "agent_config.yaml"
    
    try:
        orchestrator = StockAnalysisOrchestrator(str(config_path))
    except FileNotFoundError:
        print("⚠️  Configuration file not found, using default configuration")
        orchestrator = StockAnalysisOrchestrator()
    
    try:
        # Start the orchestrator
        print("🔧 Starting orchestrator and agents...")
        await orchestrator.start()
        
        print("✅ All agents started successfully!")
        
        # Perform analysis for Apple stock
        symbol = "AAPL"
        print(f"\n📊 Analyzing {symbol}...")
        
        # Basic analysis
        results = await orchestrator.analyze_stock(
            symbol=symbol,
            analysis_types=["technical", "fundamental", "risk", "sentiment"],
            depth="standard"
        )
        
        print(f"\n📈 Analysis Results for {symbol}:")
        print("-" * 30)
        
        for agent_name, result in results.items():
            print(f"\n{agent_name.upper()}:")
            print(f"  Confidence: {result.confidence:.2f}")
            print(f"  Signals: {len(result.signals)}")
            if result.signals:
                for signal in result.signals[:3]:  # Show first 3 signals
                    print(f"    • {signal.signal_type.value.upper()}: {signal.reason} (confidence: {signal.confidence:.2f})")
        
        print(f"\n✅ Analysis completed for {symbol}")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
    finally:
        # Clean shutdown
        print("\n🛑 Shutting down orchestrator...")
        await orchestrator.stop()
        print("✅ Shutdown completed")


async def comprehensive_analysis():
    """Example of comprehensive analysis with multiple symbols."""
    print("\n🚀 Starting Comprehensive Multi-Stock Analysis")
    print("=" * 50)
    
    orchestrator = StockAnalysisOrchestrator()
    
    try:
        await orchestrator.start()
        
        # Analyze multiple tech stocks
        symbols = ["AAPL", "GOOGL", "MSFT", "TSLA"]
        
        print(f"📊 Performing comprehensive analysis for: {', '.join(symbols)}")
        
        # Sequential analysis for each symbol
        all_results = {}
        for symbol in symbols:
            print(f"\n🔍 Analyzing {symbol}...")
            
            results = await orchestrator.analyze_stock(
                symbol=symbol,
                analysis_types=["technical", "fundamental", "risk", "sentiment"],
                depth="comprehensive"
            )
            
            all_results[symbol] = results
            
            # Show quick summary
            if results:
                signal_count = sum(len(result.signals) for result in results.values())
                avg_confidence = sum(result.confidence for result in results.values()) / len(results)
                print(f"  ✅ {symbol}: {signal_count} signals, avg confidence: {avg_confidence:.2f}")
        
        # Generate summary
        print(f"\n📋 ANALYSIS SUMMARY")
        print("-" * 30)
        
        for symbol, results in all_results.items():
            print(f"\n{symbol}:")
            
            # Collect all signals
            all_signals = []
            for result in results.values():
                all_signals.extend(result.signals)
            
            if all_signals:
                # Count signal types
                buy_signals = len([s for s in all_signals if s.signal_type.value in ['buy', 'strong_buy']])
                sell_signals = len([s for s in all_signals if s.signal_type.value in ['sell', 'strong_sell']])
                hold_signals = len([s for s in all_signals if s.signal_type.value == 'hold'])
                
                print(f"  📈 Buy signals: {buy_signals}")
                print(f"  📉 Sell signals: {sell_signals}")
                print(f"  🔄 Hold signals: {hold_signals}")
                
                # Overall sentiment
                total_strength = sum(s.strength for s in all_signals)
                if total_strength > 0.2:
                    sentiment = "🟢 BULLISH"
                elif total_strength < -0.2:
                    sentiment = "🔴 BEARISH"
                else:
                    sentiment = "🟡 NEUTRAL"
                    
                print(f"  Overall: {sentiment}")
        
    except Exception as e:
        print(f"❌ Error during comprehensive analysis: {e}")
    finally:
        await orchestrator.stop()


async def portfolio_analysis():
    """Example of portfolio-level analysis."""
    print("\n🚀 Starting Portfolio Analysis Example")
    print("=" * 50)
    
    orchestrator = StockAnalysisOrchestrator()
    
    try:
        await orchestrator.start()
        
        # Create a sample portfolio
        portfolio = Portfolio(
            holdings={
                "AAPL": 100,    # 100 shares of Apple
                "GOOGL": 50,    # 50 shares of Google
                "MSFT": 75,     # 75 shares of Microsoft
                "TSLA": 25      # 25 shares of Tesla
            },
            cash=10000.0  # $10,000 cash
        )
        
        print(f"💼 Analyzing portfolio with {len(portfolio.holdings)} holdings:")
        for symbol, shares in portfolio.holdings.items():
            print(f"  • {symbol}: {shares} shares")
        print(f"  • Cash: ${portfolio.cash:,.2f}")
        
        # Perform portfolio analysis
        results = await orchestrator.analyze_portfolio(
            portfolio=portfolio,
            analysis_types=["technical", "fundamental", "risk"],
            depth="standard"
        )
        
        print(f"\n📊 Portfolio Analysis Results:")
        print("-" * 40)
        
        for symbol, symbol_results in results.items():
            print(f"\n{symbol}:")
            
            # Calculate position value (mock current prices)
            import random
            current_price = random.uniform(80, 300)  # Mock price
            shares = portfolio.holdings[symbol]
            position_value = current_price * shares
            
            print(f"  Position Value: ${position_value:,.2f}")
            print(f"  Analysis Agents: {len(symbol_results)}")
            
            # Show risk assessment if available
            for agent_name, result in symbol_results.items():
                if 'risk' in agent_name.lower():
                    risk_data = result.data
                    if risk_data:
                        print(f"  Risk Level: {risk_data.get('risk_level', 'Unknown')}")
                        volatility = risk_data.get('volatility')
                        if volatility:
                            print(f"  Volatility: {volatility:.1%}")
        
        print(f"\n✅ Portfolio analysis completed")
        
    except Exception as e:
        print(f"❌ Error during portfolio analysis: {e}")
    finally:
        await orchestrator.stop()


async def system_monitoring():
    """Example of system health monitoring."""
    print("\n🚀 System Health Monitoring Example")
    print("=" * 50)
    
    orchestrator = StockAnalysisOrchestrator()
    
    try:
        await orchestrator.start()
        
        # Get system status
        print("🔍 Checking system health...")
        status = await orchestrator.get_system_status()
        
        print(f"\n🖥️  SYSTEM STATUS:")
        print("-" * 20)
        print(f"Orchestrator Running: {'✅' if status['orchestrator']['running'] else '❌'}")
        print(f"Active Agents: {status['orchestrator']['agents_count']}")
        
        # Message bus status
        msg_bus = status['message_bus']
        print(f"\n📬 MESSAGE BUS:")
        print(f"  Registered Agents: {len(msg_bus['registered_agents'])}")
        print(f"  Queue Size: {msg_bus['queue_size']}")
        print(f"  Messages Sent: {msg_bus['message_stats']['total_sent']}")
        print(f"  Messages Delivered: {msg_bus['message_stats']['total_delivered']}")
        
        # Agent health
        print(f"\n🤖 AGENT HEALTH:")
        for agent_name, health in status['agents'].items():
            status_icon = "✅" if health.get('status') == 'healthy' else "❌"
            print(f"  {agent_name}: {status_icon}")
            
            if 'message_queue_size' in health:
                queue_size = health['message_queue_size']
                if queue_size > 0:
                    print(f"    Queue: {queue_size} messages")
        
        print(f"\n✅ System monitoring completed")
        
    except Exception as e:
        print(f"❌ Error during monitoring: {e}")
    finally:
        await orchestrator.stop()


async def main():
    """Main function to run examples."""
    # Setup logging
    logging_config = LoggingConfig(level="INFO")
    setup_logging(logging_config)
    
    print("🎯 Stock Analysis Multi-Agent System Examples")
    print("=" * 60)
    
    try:
        # Run examples
        await basic_stock_analysis()
        await comprehensive_analysis() 
        await portfolio_analysis()
        await system_monitoring()
        
        print(f"\n🎉 All examples completed successfully!")
        
    except KeyboardInterrupt:
        print(f"\n⏹️  Examples interrupted by user")
    except Exception as e:
        print(f"\n❌ Example execution failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run the examples
    asyncio.run(main())