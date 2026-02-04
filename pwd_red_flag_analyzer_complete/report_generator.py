"""
Report Generator for Red Flag Analysis
Generates comprehensive reports in multiple formats
"""

import pandas as pd
from datetime import datetime
from typing import Dict, List, Any
import json
import logging

logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    Generates comprehensive analysis reports
    """
    
    def __init__(self):
        self.report_data = None
        
    def generate_report(self, analysis_results: Dict[str, Any], 
                       output_format: str = 'excel') -> str:
        """
        Generate comprehensive report
        
        Args:
            analysis_results: Results from RedFlagAnalyzer
            output_format: 'excel', 'html', or 'json'
            
        Returns:
            Path to generated report file
        """
        self.report_data = analysis_results
        
        if output_format == 'excel':
            return self._generate_excel_report()
        elif output_format == 'html':
            return self._generate_html_report()
        elif output_format == 'json':
            return self._generate_json_report()
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
    
    def _generate_excel_report(self) -> str:
        """Generate Excel report with multiple sheets"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f'/home/claude/Red_Flag_Analysis_Report_{timestamp}.xlsx'
        
        logger.info(f"Generating Excel report: {output_file}")
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Sheet 1: Summary
            summary_df = self._create_summary_dataframe()
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Sheet 2: Red Flagged Entries
            if self.report_data['red_flagged']:
                red_flag_df = self._create_red_flag_dataframe()
                red_flag_df.to_excel(writer, sheet_name='Red Flagged Entries', index=False)
            
            # Sheet 3: Green Flagged Entries
            if self.report_data['green_flagged']:
                green_flag_df = self._create_green_flag_dataframe()
                green_flag_df.to_excel(writer, sheet_name='Green Flagged Entries', index=False)
            
            # Sheet 4: Flag Type Summary
            flag_summary_df = self._create_flag_summary_dataframe()
            if not flag_summary_df.empty:
                flag_summary_df.to_excel(writer, sheet_name='Flag Type Summary', index=False)
            
            # Sheet 5: Detailed Findings
            if self.report_data['red_flagged']:
                detailed_df = self._create_detailed_findings_dataframe()
                detailed_df.to_excel(writer, sheet_name='Detailed Findings', index=False)
        
        logger.info(f"Excel report generated successfully")
        return output_file
    
    def _create_summary_dataframe(self) -> pd.DataFrame:
        """Create summary statistics dataframe"""
        summary = self.report_data.get('flag_summary', {})
        
        data = {
            'Metric': [
                'Total Records Analyzed',
                'Red Flagged Entries',
                'Green Flagged Entries',
                'High Severity Flags',
                'Medium Severity Flags',
                'Low Severity Flags',
                'Analysis Date'
            ],
            'Value': [
                self.report_data.get('total_records', 0),
                len(self.report_data.get('red_flagged', [])),
                len(self.report_data.get('green_flagged', [])),
                summary.get('by_severity', {}).get('HIGH', 0),
                summary.get('by_severity', {}).get('MEDIUM', 0),
                summary.get('by_severity', {}).get('LOW', 0),
                self.report_data.get('timestamp', 'N/A')
            ]
        }
        
        return pd.DataFrame(data)
    
    def _create_red_flag_dataframe(self) -> pd.DataFrame:
        """Create dataframe of red flagged entries"""
        red_flagged = self.report_data.get('red_flagged', [])
        
        if not red_flagged:
            return pd.DataFrame()
        
        rows = []
        for entry in red_flagged:
            flag_names = ', '.join([f['flag_name'] for f in entry['flags']])
            severities = ', '.join([f.get('severity', 'N/A') for f in entry['flags']])
            descriptions = ' | '.join([f['description'] for f in entry['flags']])
            
            rows.append({
                'Excel Row No.': entry['record_index'],
                'Sr. No.': entry['sr_no'],
                'Budget Item No.': entry['budget_item_no'],
                'Name of Work': entry['name_of_work'],
                'Number of Flags': len(entry['flags']),
                'Flag Types': flag_names,
                'Severity': severities,
                'Issues Found': descriptions
            })
        
        return pd.DataFrame(rows)
    
    def _create_green_flag_dataframe(self) -> pd.DataFrame:
        """Create dataframe of green flagged entries"""
        green_flagged = self.report_data.get('green_flagged', [])
        
        if not green_flagged:
            return pd.DataFrame()
        
        rows = []
        for entry in green_flagged:
            rows.append({
                'Excel Row No.': entry['record_index'],
                'Sr. No.': entry['sr_no'],
                'Budget Item No.': entry['budget_item_no'],
                'Name of Work': entry['name_of_work'],
                'Status': 'No Issues Found'
            })
        
        return pd.DataFrame(rows)
    
    def _create_flag_summary_dataframe(self) -> pd.DataFrame:
        """Create flag type summary dataframe"""
        summary = self.report_data.get('flag_summary', {})
        by_flag_type = summary.get('by_flag_type', {})
        
        if not by_flag_type:
            return pd.DataFrame()
        
        rows = []
        for flag_type, count in by_flag_type.items():
            rows.append({
                'Flag Type': flag_type,
                'Occurrences': count,
                'Percentage': round(count / summary.get('total_red_flags', 1) * 100, 2)
            })
        
        df = pd.DataFrame(rows)
        return df.sort_values('Occurrences', ascending=False)
    
    def _create_detailed_findings_dataframe(self) -> pd.DataFrame:
        """Create detailed findings dataframe"""
        red_flagged = self.report_data.get('red_flagged', [])
        
        if not red_flagged:
            return pd.DataFrame()
        
        rows = []
        for entry in red_flagged:
            for flag in entry['flags']:
                row_data = {
                    'Excel Row No.': entry['record_index'],
                    'Budget Item No.': entry['budget_item_no'],
                    'Name of Work': entry['name_of_work'],
                    'Flag ID': flag['flag_id'],
                    'Flag Type': flag['flag_name'],
                    'Severity': flag.get('severity', 'N/A'),
                    'Description': flag['description']
                }
                
                # Add flag-specific details
                details = flag.get('details', {})
                for key, value in details.items():
                    row_data[key.replace('_', ' ').title()] = value
                
                rows.append(row_data)
        
        return pd.DataFrame(rows)
    
    def _generate_html_report(self) -> str:
        """Generate HTML report"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f'/home/claude/Red_Flag_Analysis_Report_{timestamp}.html'
        
        logger.info(f"Generating HTML report: {output_file}")
        
        html_content = self._create_html_content()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info("HTML report generated successfully")
        return output_file
    
    def _create_html_content(self) -> str:
        """Create HTML report content"""
        red_count = len(self.report_data.get('red_flagged', []))
        green_count = len(self.report_data.get('green_flagged', []))
        total = self.report_data.get('total_records', 0)
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Red Flag Analysis Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            background: #f5f5f5;
            color: #333;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .summary-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }}
        
        .card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.15);
        }}
        
        .card h3 {{
            color: #667eea;
            margin-bottom: 10px;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .card .value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #333;
        }}
        
        .card.red {{
            border-left: 4px solid #e74c3c;
        }}
        
        .card.green {{
            border-left: 4px solid #2ecc71;
        }}
        
        .card.total {{
            border-left: 4px solid #3498db;
        }}
        
        section {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        section h2 {{
            color: #667eea;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #f0f0f0;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        
        th {{
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }}
        
        td {{
            padding: 12px;
            border-bottom: 1px solid #f0f0f0;
        }}
        
        tr:hover {{
            background: #f9f9f9;
        }}
        
        .severity-high {{
            background: #e74c3c;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: bold;
        }}
        
        .severity-medium {{
            background: #f39c12;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: bold;
        }}
        
        .severity-low {{
            background: #95a5a6;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: bold;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            color: #777;
            font-size: 0.9em;
        }}
        
        @media print {{
            body {{
                background: white;
            }}
            .card {{
                break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🚩 PWD Works Red Flag Analysis Report</h1>
            <p>Generated on: {self.report_data.get('timestamp', 'N/A')}</p>
        </header>
        
        <div class="summary-cards">
            <div class="card total">
                <h3>Total Records</h3>
                <div class="value">{total}</div>
            </div>
            
            <div class="card red">
                <h3>Red Flagged</h3>
                <div class="value">{red_count}</div>
                <p style="margin-top: 10px; color: #666;">{round(red_count/total*100, 1) if total > 0 else 0}% of total</p>
            </div>
            
            <div class="card green">
                <h3>Green Flagged</h3>
                <div class="value">{green_count}</div>
                <p style="margin-top: 10px; color: #666;">{round(green_count/total*100, 1) if total > 0 else 0}% of total</p>
            </div>
        </div>
        
        {self._generate_red_flag_section()}
        
        {self._generate_flag_summary_section()}
        
        <div class="footer">
            <p>This report was automatically generated by the PWD Red Flag Analysis System</p>
            <p>For queries, contact the relevant audit department</p>
        </div>
    </div>
</body>
</html>
"""
        return html
    
    def _generate_red_flag_section(self) -> str:
        """Generate red flag entries section for HTML"""
        red_flagged = self.report_data.get('red_flagged', [])
        
        if not red_flagged:
            return '<section><h2>Red Flagged Entries</h2><p>No red flags detected!</p></section>'
        
        rows = []
        for entry in red_flagged:
            for flag in entry['flags']:
                severity_class = f"severity-{flag.get('severity', 'medium').lower()}"
                rows.append(f"""
                <tr>
                    <td>{entry['record_index']}</td>
                    <td>{entry['budget_item_no']}</td>
                    <td>{entry['name_of_work'][:100]}...</td>
                    <td>{flag['flag_name']}</td>
                    <td><span class="{severity_class}">{flag.get('severity', 'N/A')}</span></td>
                    <td>{flag['description']}</td>
                </tr>
                """)
        
        return f"""
        <section>
            <h2>🚨 Red Flagged Entries ({len(red_flagged)} entries)</h2>
            <table>
                <thead>
                    <tr>
                        <th>Row</th>
                        <th>Budget Item</th>
                        <th>Work Name</th>
                        <th>Flag Type</th>
                        <th>Severity</th>
                        <th>Description</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(rows)}
                </tbody>
            </table>
        </section>
        """
    
    def _generate_flag_summary_section(self) -> str:
        """Generate flag summary section for HTML"""
        summary = self.report_data.get('flag_summary', {})
        by_flag_type = summary.get('by_flag_type', {})
        
        if not by_flag_type:
            return ''
        
        rows = []
        for flag_type, count in sorted(by_flag_type.items(), key=lambda x: x[1], reverse=True):
            percentage = round(count / summary.get('total_red_flags', 1) * 100, 2)
            rows.append(f"""
            <tr>
                <td>{flag_type}</td>
                <td>{count}</td>
                <td>{percentage}%</td>
            </tr>
            """)
        
        return f"""
        <section>
            <h2>📊 Flag Type Distribution</h2>
            <table>
                <thead>
                    <tr>
                        <th>Flag Type</th>
                        <th>Count</th>
                        <th>Percentage</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(rows)}
                </tbody>
            </table>
        </section>
        """
    
    def _generate_json_report(self) -> str:
        """Generate JSON report"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f'/home/claude/Red_Flag_Analysis_Report_{timestamp}.json'
        
        logger.info(f"Generating JSON report: {output_file}")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.report_data, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info("JSON report generated successfully")
        return output_file
