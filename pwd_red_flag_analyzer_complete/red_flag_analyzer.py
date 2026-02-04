"""
Red Flag Analyzer for PWD Works
Implements 8 red flag detection criteria based on audit parameters
"""

import pandas as pd
import re
from datetime import datetime
from typing import Dict, List, Tuple, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class RedFlagAnalyzer:
    """
    Analyzes PWD works data against 8 red flag criteria
    """
    
    def __init__(self):
        self.red_flags = []
        self.green_flags = []
        self.current_date = datetime.now()
        
    def analyze_all_flags(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze all red flag criteria
        
        Args:
            df: DataFrame containing PWD works data
            
        Returns:
            Dictionary containing analysis results
        """
        logger.info(f"Starting analysis of {len(df)} records")
        
        results = {
            'total_records': len(df),
            'red_flagged': [],
            'green_flagged': [],
            'flag_summary': {},
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        for idx, row in df.iterrows():
            record_flags = self._analyze_single_record(row, idx)
            
            if record_flags:
                results['red_flagged'].append({
                    'record_index': idx + 2,  # +2 because Excel is 1-indexed and has header
                    'sr_no': row.get('Sr.', idx),
                    'budget_item_no': row.get('Budget Item No.', 'N/A'),
                    'name_of_work': row.get('Name of the work', 'N/A'),
                    'flags': record_flags
                })
            else:
                results['green_flagged'].append({
                    'record_index': idx + 2,
                    'sr_no': row.get('Sr.', idx),
                    'budget_item_no': row.get('Budget Item No.', 'N/A'),
                    'name_of_work': row.get('Name of the work', 'N/A')
                })
        
        # Calculate summary statistics
        results['flag_summary'] = self._calculate_summary(results['red_flagged'])
        
        logger.info(f"Analysis complete: {len(results['red_flagged'])} red flags, {len(results['green_flagged'])} green flags")
        
        return results
    
    def _analyze_single_record(self, row: pd.Series, idx: int) -> List[Dict[str, Any]]:
        """Analyze a single record against all criteria"""
        flags = []
        
        # Flag 1: Diversion of funds (requires Remark field - not in current schema)
        # Skip for now as requires additional data
        
        # Flag 2: Wasteful expenditure on survey works
        flag2 = self._check_survey_wastage(row)
        if flag2:
            flags.append(flag2)
        
        # Flag 3: Excess expenditure without approval (>10% of AA)
        flag3 = self._check_excess_expenditure(row)
        if flag3:
            flags.append(flag3)
        
        # Flag 4: Overlapping of work (requires comparison with other records)
        # Will be handled in batch analysis
        
        # Flag 5: Delay in completion of work
        flag5 = self._check_delay_in_completion(row)
        if flag5:
            flags.append(flag5)
        
        # Flag 6: Splitting of work (requires comparison with other records)
        # Will be handled in batch analysis
        
        # Flag 7: Non-recovery of centage charges (requires additional deposit work data)
        # Skip for now as requires additional data
        
        # Flag 8: Unspent balance not returned (requires additional deposit work data)
        # Skip for now as requires additional data
        
        return flags
    
    def _check_survey_wastage(self, row: pd.Series) -> Dict[str, Any]:
        """
        Flag 2: Check for wasteful expenditure on survey works
        If remark includes survey works but other items have nil payment
        """
        # This requires additional data fields not in current schema
        # Placeholder for when data is available
        return None
    
    def _check_excess_expenditure(self, row: pd.Series) -> Dict[str, Any]:
        """
        Flag 3: Check if expenditure exceeds AA by more than 10%
        """
        try:
            aa_cost = self._safe_float(row.get('Administrative Approval Cost (Lakh)', 0))
            total_exp = self._safe_float(row.get('Total Expenditure (Lakhs)', 0))
            
            if aa_cost > 0:
                excess_percentage = ((total_exp - aa_cost) / aa_cost) * 100
                
                if excess_percentage > 10:
                    return {
                        'flag_id': 3,
                        'flag_name': 'Excess Expenditure Without Approval',
                        'severity': 'HIGH',
                        'description': f'Expenditure exceeds Administrative Approval by {excess_percentage:.2f}%',
                        'details': {
                            'aa_cost_lakh': aa_cost,
                            'total_expenditure_lakh': total_exp,
                            'excess_amount_lakh': total_exp - aa_cost,
                            'excess_percentage': round(excess_percentage, 2)
                        }
                    }
        except Exception as e:
            logger.warning(f"Error checking excess expenditure: {e}")
        
        return None
    
    def _check_delay_in_completion(self, row: pd.Series) -> Dict[str, Any]:
        """
        Flag 5: Check if work is delayed beyond stipulated period
        """
        try:
            work_order_date = self._parse_date(row.get('Date of Work_Order'))
            time_limit_days = self._safe_int(row.get('Original Time Limit in Days', 0))
            physical_progress = self._safe_float(row.get('Physical Progress', 0))
            
            if work_order_date and time_limit_days > 0:
                expected_completion = work_order_date + pd.Timedelta(days=time_limit_days)
                
                # Check if work is delayed and not 100% complete
                if self.current_date > expected_completion and physical_progress < 100:
                    delay_days = (self.current_date - expected_completion).days
                    
                    return {
                        'flag_id': 5,
                        'flag_name': 'Delay in Completion of Work',
                        'severity': 'MEDIUM',
                        'description': f'Work delayed by {delay_days} days, physical progress: {physical_progress}%',
                        'details': {
                            'work_order_date': work_order_date.strftime('%Y-%m-%d'),
                            'time_limit_days': time_limit_days,
                            'expected_completion': expected_completion.strftime('%Y-%m-%d'),
                            'current_date': self.current_date.strftime('%Y-%m-%d'),
                            'delay_days': delay_days,
                            'physical_progress_percent': physical_progress
                        }
                    }
        except Exception as e:
            logger.warning(f"Error checking delay: {e}")
        
        return None
    
    def analyze_batch_flags(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Analyze flags that require comparison across multiple records
        Flag 4: Overlapping of work
        Flag 6: Splitting of work
        """
        batch_flags = []
        
        # Flag 4: Check for overlapping works
        batch_flags.extend(self._check_overlapping_works(df))
        
        # Flag 6: Check for splitting of works
        batch_flags.extend(self._check_splitting_of_works(df))
        
        return batch_flags
    
    def _check_overlapping_works(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Flag 4: Check for overlapping works with same road number and chainage
        """
        overlapping_flags = []
        
        # Group by road category and check for chainage overlaps
        for road_cat in df['Road Category'].dropna().unique():
            if pd.isna(road_cat):
                continue
                
            road_works = df[df['Road Category'] == road_cat].copy()
            
            # Extract road number (SH, MDR, NH, etc.)
            for idx1, row1 in road_works.iterrows():
                name1 = str(row1.get('Name of the work', '')).upper()
                from1 = self._safe_float(row1.get('Chainage From', 0))
                to1 = self._safe_float(row1.get('Chainage To', 0))
                
                if from1 == 0 and to1 == 0:
                    continue
                
                # Check against other works
                for idx2, row2 in road_works.iterrows():
                    if idx1 >= idx2:  # Avoid duplicate comparisons
                        continue
                    
                    name2 = str(row2.get('Name of the work', '')).upper()
                    from2 = self._safe_float(row2.get('Chainage From', 0))
                    to2 = self._safe_float(row2.get('Chainage To', 0))
                    
                    if from2 == 0 and to2 == 0:
                        continue
                    
                    # Check if chainages overlap
                    if self._chainages_overlap(from1, to1, from2, to2):
                        # Check if road numbers match
                        road_num1 = self._extract_road_number(name1)
                        road_num2 = self._extract_road_number(name2)
                        
                        if road_num1 and road_num2 and road_num1 == road_num2:
                            overlapping_flags.append({
                                'flag_id': 4,
                                'flag_name': 'Overlapping of Work',
                                'severity': 'HIGH',
                                'description': f'Works overlap on {road_num1}',
                                'affected_records': [
                                    {
                                        'record_index': idx1 + 2,
                                        'budget_item_no': row1.get('Budget Item No.', 'N/A'),
                                        'chainage': f"{from1} to {to1}"
                                    },
                                    {
                                        'record_index': idx2 + 2,
                                        'budget_item_no': row2.get('Budget Item No.', 'N/A'),
                                        'chainage': f"{from2} to {to2}"
                                    }
                                ]
                            })
        
        return overlapping_flags
    
    def _check_splitting_of_works(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Flag 6: Check for splitting of works
        Similar works with same road number awarded to same contractor in same year, each < 10 lakh
        """
        splitting_flags = []
        
        # This requires Agreement Register data with contractor information
        # For now, we'll check based on available data: same road, similar chainage, cost < 10 lakh
        
        # Group by year (from work order date)
        df_copy = df.copy()
        df_copy['year'] = pd.to_datetime(df_copy['Date of Work_Order'], errors='coerce').dt.year
        
        for year in df_copy['year'].dropna().unique():
            year_works = df_copy[df_copy['year'] == year]
            
            # Group by road category
            for road_cat in year_works['Road Category'].dropna().unique():
                road_works = year_works[year_works['Road Category'] == road_cat]
                
                # Find groups of works with similar road numbers and continuous chainage
                road_groups = {}
                
                for idx, row in road_works.iterrows():
                    name = str(row.get('Name of the work', '')).upper()
                    road_num = self._extract_road_number(name)
                    contract_cost = self._safe_float(row.get('Contract Agreement Cost (Lakh)', 0))
                    
                    if road_num and contract_cost > 0 and contract_cost < 10:
                        if road_num not in road_groups:
                            road_groups[road_num] = []
                        
                        road_groups[road_num].append({
                            'index': idx,
                            'row': row,
                            'contract_cost': contract_cost,
                            'from': self._safe_float(row.get('Chainage From', 0)),
                            'to': self._safe_float(row.get('Chainage To', 0))
                        })
                
                # Check for suspicious patterns (3+ works on same road, each < 10 lakh)
                for road_num, works in road_groups.items():
                    if len(works) >= 3:
                        # Check if chainages are continuous or overlapping
                        works_sorted = sorted(works, key=lambda x: x['from'])
                        
                        # If works are in continuation, flag for splitting
                        continuous = True
                        for i in range(len(works_sorted) - 1):
                            gap = works_sorted[i+1]['from'] - works_sorted[i]['to']
                            if gap > 5:  # More than 5 km gap
                                continuous = False
                                break
                        
                        if continuous:
                            splitting_flags.append({
                                'flag_id': 6,
                                'flag_name': 'Splitting of Work',
                                'severity': 'HIGH',
                                'description': f'Potential work splitting detected on {road_num} in year {int(year)}',
                                'affected_records': [
                                    {
                                        'record_index': w['index'] + 2,
                                        'budget_item_no': w['row'].get('Budget Item No.', 'N/A'),
                                        'contract_cost_lakh': w['contract_cost'],
                                        'chainage': f"{w['from']} to {w['to']}"
                                    }
                                    for w in works_sorted
                                ],
                                'total_cost': sum(w['contract_cost'] for w in works_sorted)
                            })
        
        return splitting_flags
    
    def _chainages_overlap(self, from1: float, to1: float, from2: float, to2: float) -> bool:
        """Check if two chainage ranges overlap"""
        return not (to1 < from2 or to2 < from1)
    
    def _extract_road_number(self, work_name: str) -> str:
        """Extract road number from work name (SH-XX, MDR-XX, NH-XX)"""
        patterns = [
            r'SH-?\s*(\d+)',
            r'MDR-?\s*(\d+)',
            r'NH-?\s*(\d+)',
            r'SH\s*(\d+)',
            r'MDR\s*(\d+)',
            r'NH\s*(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, work_name, re.IGNORECASE)
            if match:
                road_type = pattern.split('(')[0].replace('-?', '').replace('\\s*', '').strip()
                return f"{road_type}{match.group(1)}"
        
        return None
    
    def _calculate_summary(self, red_flagged: List[Dict]) -> Dict[str, Any]:
        """Calculate summary statistics of red flags"""
        summary = {
            'total_red_flags': len(red_flagged),
            'by_flag_type': {},
            'by_severity': {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        }
        
        for record in red_flagged:
            for flag in record['flags']:
                flag_name = flag['flag_name']
                severity = flag.get('severity', 'MEDIUM')
                
                summary['by_flag_type'][flag_name] = summary['by_flag_type'].get(flag_name, 0) + 1
                summary['by_severity'][severity] += 1
        
        return summary
    
    # Utility methods
    def _safe_float(self, value: Any) -> float:
        """Safely convert value to float"""
        try:
            if pd.isna(value) or value == '':
                return 0.0
            return float(value)
        except (ValueError, TypeError):
            return 0.0
    
    def _safe_int(self, value: Any) -> int:
        """Safely convert value to int"""
        try:
            if pd.isna(value) or value == '':
                return 0
            return int(float(value))
        except (ValueError, TypeError):
            return 0
    
    def _parse_date(self, date_value: Any) -> pd.Timestamp:
        """Parse date from various formats"""
        try:
            if pd.isna(date_value):
                return None
            return pd.to_datetime(date_value, errors='coerce')
        except Exception:
            return None
