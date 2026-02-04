"""
Test Script for Red Flag Analysis System
Demonstrates how to use the system and validates functionality
"""

import sys
import pandas as pd
from datetime import datetime, timedelta
import os

def create_sample_excel():
    """Create a sample Excel file for testing"""
    print("Creating sample Excel file...")
    
    # Sample data based on the provided structure
    data = {
        'Sr.': [1, 2, 3, 4, 5],
        'Budget Item No.': ['2104/019/00168', '2105/020/00169', '2106/021/00170', '2107/022/00171', '2108/023/00172'],
        'District': ['LATUR', 'LATUR', 'LATUR', 'LATUR', 'LATUR'],
        'Head of Accounts': ['30540078', '30540078', '30540078', '30540078', '30540078'],
        'Name of the work': [
            'Improvement to Two line road SH-56 Km 183/00 to 195/500',
            'Construction of Bridge on MDR-43 Km 10/00 to 15/00',
            'Road Widening SH-240 Km 19/500 to 28/500',
            'Improvement of Road MDR-44 Km 5/00 to 10/00',
            'Construction of New Road NH-752 Km 30/00 to 40/00'
        ],
        'Name Of The Work (In Marathi)': [
            'रा.मा.-56 कि.मी.183/00 ते 195/500 दोन पदरी रस्त्याची सुधारणा',
            'MDR-43 वर पुलाचे बांधकाम कि.मी. 10/00 ते 15/00',
            'रा.मा.-240 रस्ता रुंदीकरण कि.मी. 19/500 ते 28/500',
            'MDR-44 रस्ता सुधारणा कि.मी. 5/00 ते 10/00',
            'NH-752 नवीन रस्ता बांधकाम कि.मी. 30/00 ते 40/00'
        ],
        'Administrative Approval Cost (Lakh)': [1983.02, 850.50, 1200.00, 450.00, 2500.00],
        'Administrative Approval Date': [
            '25/7/2021', '15/8/2021', '10/9/2021', '5/10/2021', '20/11/2021'
        ],
        'Technical Sanction Cost (Lakh)': [1563.08, 820.00, 1150.00, 440.00, 2450.00],
        'Contract Agreement Cost (Lakh)': [2441665.84, 900.00, 1100.00, 8.50, 2400.00],
        'Conract % above / below': [6.57, 5.88, -8.33, -98.11, -4.00],
        'Expenditure Upto March (Lakhs)': [1883.10, 600.00, 800.00, 250.00, 1500.00],
        'Expenditure April to January (Lakhs)': [0, 150.00, 200.00, 100.00, 500.00],
        'Total Expenditure (Lakhs)': [1883.10, 750.00, 1000.00, 350.00, 2000.00],
        '% of Expenditure': [94.96, 88.24, 83.33, 77.78, 80.00],
        'Physical Progress': [94, 85, 80, 75, 78],
        'Date of Work_Order': [
            '4/4/2022', '1/5/2022', '15/6/2022', '1/7/2022', '10/8/2022'
        ],
        'Original Time Limit in Days': [365, 300, 400, 200, 500],
        'Work Category': ['WIDENING SURFACING', 'BRIDGE', 'WIDENING', 'IMPROVEMENT', 'NEW CONSTRUCTION'],
        'Road Category': ['SH-56', 'MDR-43', 'SH-240', 'MDR-44', 'NH-752'],
        'Chainage From': [183.0, 10.0, 19.5, 5.0, 30.0],
        'Chainage To': [195.5, 15.0, 28.5, 10.0, 40.0],
        'Taluka': ['AHMEDPUR', 'NILANGA', 'NILANGA', 'AHMEDPUR', 'DEONI'],
        'Constituency': ['AHMEDPUR', 'NILANGA', 'NILANGA', 'AHMEDPUR', 'DEONI'],
        'PW Division': ['AURANGABAD', 'LATUR', 'LATUR', 'AURANGABAD', 'LATUR'],
        'PW Circle': ['H', 'H', 'H', 'H', 'H'],
        'PW Region': ['-', '-', '-', '-', '-'],
        'User Department': ['PUBLIC WORKS DEPARTMENT'] * 5
    }
    
    df = pd.DataFrame(data)
    
    # Save to Excel
    output_file = '/home/claude/sample_pwd_works.xlsx'
    df.to_excel(output_file, index=False)
    
    print(f"✓ Sample Excel file created: {output_file}")
    return output_file


def test_pipeline():
    """Test the complete pipeline"""
    print("\n" + "="*80)
    print("Testing Red Flag Analysis Pipeline")
    print("="*80 + "\n")
    
    # Create sample file
    sample_file = create_sample_excel()
    
    # Import and run pipeline
    try:
        from pipeline import RedFlagPipeline
        
        print("\nInitializing pipeline...")
        pipeline = RedFlagPipeline()
        
        print("Running analysis...")
        result = pipeline.run(
            sample_file,
            output_formats=['excel', 'html', 'json']
        )
        
        if result['success']:
            print("\n" + "="*80)
            print("✓ ANALYSIS SUCCESSFUL")
            print("="*80)
            
            # Print summary
            summary = result['results']
            print(f"\nTotal Records: {summary['total_records']}")
            print(f"Red Flagged: {len(summary['red_flagged'])}")
            print(f"Green Flagged: {len(summary['green_flagged'])}")
            
            # Print red flags if any
            if summary['red_flagged']:
                print("\nRed Flagged Entries:")
                for entry in summary['red_flagged']:
                    print(f"  - Row {entry['record_index']}: {entry['budget_item_no']}")
                    for flag in entry['flags']:
                        print(f"    • {flag['flag_name']}: {flag['description']}")
            
            # Print output files
            print("\nGenerated Reports:")
            for fmt, filepath in result['output_files'].items():
                print(f"  - {fmt.upper()}: {filepath}")
            
            # Data quality
            quality = result['data_quality']
            print(f"\nData Quality Score: {quality.get('quality_score', 'N/A')}/100")
            
            return True
        else:
            print("\n" + "="*80)
            print("✗ ANALYSIS FAILED")
            print("="*80)
            print(f"Error: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"\n✗ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_excel_reader():
    """Test the Excel reader module"""
    print("\n" + "="*80)
    print("Testing Excel Reader")
    print("="*80 + "\n")
    
    try:
        from excel_reader import ExcelReader
        
        # Create sample file
        sample_file = create_sample_excel()
        
        # Test reader
        reader = ExcelReader()
        df = reader.read_excel(sample_file)
        
        print(f"✓ Successfully read {len(df)} rows and {len(df.columns)} columns")
        
        # Validate data
        quality = reader.validate_data_quality()
        print(f"✓ Data quality score: {quality['quality_score']}/100")
        
        if quality['issues']:
            print(f"⚠ Found {len(quality['issues'])} data quality issues")
        
        return True
        
    except Exception as e:
        print(f"✗ Excel reader test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_analyzer():
    """Test the analyzer module"""
    print("\n" + "="*80)
    print("Testing Red Flag Analyzer")
    print("="*80 + "\n")
    
    try:
        from excel_reader import ExcelReader
        from red_flag_analyzer import RedFlagAnalyzer
        
        # Create and read sample file
        sample_file = create_sample_excel()
        reader = ExcelReader()
        df = reader.read_excel(sample_file)
        
        # Test analyzer
        analyzer = RedFlagAnalyzer()
        results = analyzer.analyze_all_flags(df)
        
        print(f"✓ Analyzed {results['total_records']} records")
        print(f"✓ Found {len(results['red_flagged'])} red flags")
        print(f"✓ Found {len(results['green_flagged'])} green flags")
        
        # Test batch analysis
        batch_flags = analyzer.analyze_batch_flags(df)
        print(f"✓ Batch analysis found {len(batch_flags)} cross-record flags")
        
        return True
        
    except Exception as e:
        print(f"✗ Analyzer test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("PWD WORKS RED FLAG ANALYSIS SYSTEM - TEST SUITE")
    print("="*80)
    
    tests = [
        ("Excel Reader", test_excel_reader),
        ("Red Flag Analyzer", test_analyzer),
        ("Complete Pipeline", test_pipeline)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*80}")
        print(f"Running: {test_name}")
        print('='*80)
        results[test_name] = test_func()
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 All tests passed successfully!")
        print("\nYou can now:")
        print("1. Run the web interface: python3 app.py")
        print("2. Use CLI: python3 pipeline.py sample_pwd_works.xlsx")
        print("3. Import as library: from pipeline import RedFlagPipeline")
    else:
        print("\n⚠ Some tests failed. Please check the errors above.")
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
