"""
Main Pipeline for Red Flag Analysis
Orchestrates reading, analysis, and reporting
"""

import sys
import logging
from pathlib import Path
from typing import Optional
import argparse

from excel_reader import ExcelReader
from red_flag_analyzer import RedFlagAnalyzer
from report_generator import ReportGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)


class RedFlagPipeline:
    """
    Main pipeline for red flag analysis
    """
    
    def __init__(self):
        self.reader = ExcelReader()
        self.analyzer = RedFlagAnalyzer()
        self.report_gen = ReportGenerator()
        self.df = None
        self.results = None
        
    def run(self, excel_file_path: str, 
            sheet_name: Optional[str] = None,
            output_formats: list = ['excel', 'pdf']) -> dict:
        """
        Run complete pipeline
        
        Args:
            excel_file_path: Path to Excel file
            sheet_name: Optional sheet name
            output_formats: List of output formats ('excel', 'html', 'json', 'pdf')
            
        Returns:
            Dictionary with results and output file paths
        """
        logger.info("="*80)
        logger.info("Starting Red Flag Analysis Pipeline")
        logger.info("="*80)
        
        try:
            # Step 1: Read Excel file
            logger.info("Step 1: Reading Excel file...")
            self.df = self.reader.read_excel(excel_file_path, sheet_name)
            
            # Validate data quality
            quality_report = self.reader.validate_data_quality()
            logger.info(f"Data quality score: {quality_report.get('quality_score', 0)}/100")
            
            if quality_report.get('total_issues', 0) > 0:
                logger.warning(f"Found {quality_report['total_issues']} data quality issues")
                for issue in quality_report.get('issues', []):
                    logger.warning(f"  - {issue}")
            
            # Step 2: Analyze for red flags
            logger.info("Step 2: Analyzing for red flags...")
            self.results = self.analyzer.analyze_all_flags(self.df)
            
            # Step 3: Batch analysis for cross-record flags
            logger.info("Step 3: Running batch analysis for cross-record flags...")
            batch_flags = self.analyzer.analyze_batch_flags(self.df)
            
            # Merge batch flags into results
            if batch_flags:
                logger.info(f"Found {len(batch_flags)} cross-record flags")
                # Add batch flags to appropriate records
                for batch_flag in batch_flags:
                    affected_records = batch_flag.get('affected_records', [])
                    for affected in affected_records:
                        record_idx = affected['record_index'] - 2  # Convert back to 0-indexed
                        
                        # Find or create red flag entry
                        existing_entry = None
                        for entry in self.results['red_flagged']:
                            if entry['record_index'] == affected['record_index']:
                                existing_entry = entry
                                break
                        
                        if existing_entry:
                            existing_entry['flags'].append(batch_flag)
                        else:
                            # Check if it was in green flags
                            for i, green_entry in enumerate(self.results['green_flagged']):
                                if green_entry['record_index'] == affected['record_index']:
                                    # Move to red flags
                                    new_red_entry = green_entry.copy()
                                    new_red_entry['flags'] = [batch_flag]
                                    self.results['red_flagged'].append(new_red_entry)
                                    self.results['green_flagged'].pop(i)
                                    break
            
            # Recalculate summary
            self.results['flag_summary'] = self.analyzer._calculate_summary(
                self.results['red_flagged']
            )
            
            # Step 4: Generate reports
            logger.info("Step 4: Generating reports...")
            output_files = {}
            
            for fmt in output_formats:
                logger.info(f"  Generating {fmt.upper()} report...")
                output_file = self.report_gen.generate_report(self.results, fmt)
                output_files[fmt] = output_file
                logger.info(f"  ✓ {fmt.upper()} report saved: {output_file}")
            
            # Step 5: Summary
            logger.info("="*80)
            logger.info("Analysis Complete!")
            logger.info("="*80)
            logger.info(f"Total records analyzed: {self.results['total_records']}")
            logger.info(f"Red flagged entries: {len(self.results['red_flagged'])}")
            logger.info(f"Green flagged entries: {len(self.results['green_flagged'])}")
            logger.info("="*80)
            
            return {
                'success': True,
                'results': self.results,
                'output_files': output_files,
                'data_quality': quality_report
            }
            
        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_summary(self) -> dict:
        """Get summary of analysis results"""
        if not self.results:
            return {"error": "No analysis has been run yet"}
        
        return {
            'total_records': self.results['total_records'],
            'red_flagged': len(self.results['red_flagged']),
            'green_flagged': len(self.results['green_flagged']),
            'flag_summary': self.results['flag_summary']
        }


def main():
    """Main entry point for CLI"""
    parser = argparse.ArgumentParser(
        description='PWD Works Red Flag Analysis Pipeline'
    )
    parser.add_argument(
        'excel_file',
        type=str,
        help='Path to Excel file to analyze'
    )
    parser.add_argument(
        '--sheet',
        type=str,
        default=None,
        help='Sheet name (default: first sheet)'
    )
    parser.add_argument(
        '--formats',
        type=str,
        nargs='+',
        default=['excel', 'pdf'],
        choices=['excel', 'html', 'json', 'pdf'],
        help='Output formats (default: excel pdf)'
    )
    
    args = parser.parse_args()
    
    # Validate file exists
    if not Path(args.excel_file).exists():
        logger.error(f"File not found: {args.excel_file}")
        sys.exit(1)
    
    # Run pipeline
    pipeline = RedFlagPipeline()
    result = pipeline.run(
        args.excel_file,
        sheet_name=args.sheet,
        output_formats=args.formats
    )
    
    if result['success']:
        logger.info("\nGenerated reports:")
        for fmt, filepath in result['output_files'].items():
            logger.info(f"  {fmt.upper()}: {filepath}")
        sys.exit(0)
    else:
        logger.error(f"\nPipeline failed: {result.get('error', 'Unknown error')}")
        sys.exit(1)


if __name__ == '__main__':
    main()
