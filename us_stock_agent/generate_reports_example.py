#!/usr/bin/env python3
"""
Example to demonstrate actual report generation with file output
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from orchestrator.main_agent import StockAnalysisOrchestrator
from shared.data_models import Portfolio
from utils.logger import setup_logging, LoggingConfig


async def generate_reports_example():
    """Generate actual report files for AAPL analysis."""
    print("📊 Stock Analysis with Report Generation")
    print("=" * 50)
    
    orchestrator = StockAnalysisOrchestrator()
    
    try:
        await orchestrator.start()
        print("✅ All agents started!")
        
        # Analyze AAPL with all agents including report generation
        symbol = "AAPL"
        print(f"\n🔍 Analyzing {symbol} and generating reports...")
        
        results = await orchestrator.analyze_stock(
            symbol=symbol,
            analysis_types=["technical", "fundamental", "risk", "sentiment", "visualization", "report"],
            depth="comprehensive"
        )
        
        print(f"\n📈 Analysis Results for {symbol}:")
        print("-" * 40)
        
        for agent_name, result in results.items():
            print(f"\n{agent_name.upper()}:")
            print(f"  Confidence: {result.confidence:.2f}")
            print(f"  Signals: {len(result.signals)}")
            
            # Show report file paths if generated
            if 'file_path' in result.data:
                print(f"  📄 Report saved: {result.data['file_path']}")
            
            # Show chart files if generated
            if 'charts' in result.data:
                charts = result.data['charts']
                if isinstance(charts, dict):
                    for chart_type, chart_info in charts.items():
                        if isinstance(chart_info, dict) and 'file_path' in chart_info:
                            print(f"  📊 {chart_type} chart: {chart_info['file_path']}")
            
            # Show any other generated files
            for key, value in result.data.items():
                if isinstance(value, dict) and 'file_path' in value:
                    print(f"  📁 {key}: {value['file_path']}")
        
        # List all generated files
        print(f"\n📂 Generated Files:")
        print("-" * 20)
        
        reports_dir = Path("reports")
        if reports_dir.exists():
            all_files = list(reports_dir.rglob("*"))
            report_files = [f for f in all_files if f.is_file()]
            
            if report_files:
                for file_path in sorted(report_files):
                    print(f"  📄 {file_path}")
            else:
                print("  (No files generated yet)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await orchestrator.stop()


async def main():
    """Run the report generation example."""
    # Setup logging
    logging_config = LoggingConfig(level="INFO")
    setup_logging(logging_config)
    
    await generate_reports_example()


if __name__ == "__main__":
    asyncio.run(main())