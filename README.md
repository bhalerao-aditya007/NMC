# PWD Works Red Flag Analysis System

A comprehensive, production-ready system for analyzing Public Works Department (PWD) Excel files against 8 audit red flag criteria. Supports multilingual content (English, Hindi, Marathi).

## Features

### 🎯 Core Capabilities
- **Automated Red Flag Detection**: Analyzes 8 audit criteria automatically
- **Multilingual Support**: Handles English, Hindi, and Marathi text seamlessly
- **Excel Processing**: Robust reading with data validation and quality checks
- **Multiple Report Formats**: Generate Excel, HTML, and JSON reports
- **Professional Web Interface**: User-friendly interface for easy file upload and analysis
- **Batch Analysis**: Detects cross-record issues like work splitting and overlapping

### 📊 Red Flag Criteria

1. **Diversion of Funds**: Detects unauthorized fund transfers between deposit works
2. **Wasteful Survey Expenditure**: Identifies improper survey work spending
3. **Excess Expenditure**: Flags expenditure exceeding Administrative Approval by >10%
4. **Overlapping Works**: Finds maintenance work overlaps during DLP
5. **Delay in Completion**: Identifies works not completed within time limits
6. **Splitting of Works**: Detects artificially split works to avoid e-tendering
7. **Non-recovery of Centage**: Checks for missing 5% centage charges on deposit works
8. **Unspent Balance**: Flags unspent deposits (>₹1 lakh) not returned after completion

## System Architecture

```
├── pipeline.py              # Main orchestration pipeline
├── excel_reader.py          # Excel file reading with multilingual support
├── red_flag_analyzer.py     # Red flag detection logic
├── report_generator.py      # Multi-format report generation
├── app.py                   # Flask web application
├── templates/
│   └── index.html          # Web interface template
├── static/
│   ├── css/
│   │   └── style.css       # Professional styling
│   └── js/
│       └── script.js       # Interactive functionality
└── uploads/                # Temporary file storage
```

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Step 1: Install Dependencies

```bash
pip install pandas openpyxl flask werkzeug --break-system-packages
```

### Step 2: Verify Installation

```bash
python3 -c "import pandas, openpyxl, flask; print('All dependencies installed successfully')"
```

## Usage

### Option 1: Web Interface (Recommended)

1. **Start the web server:**
```bash
python3 app.py
```

2. **Open your browser:**
Navigate to: `http://localhost:5000`

3. **Upload and analyze:**
   - Click "Choose Excel File" or drag-and-drop your Excel file
   - Select desired output formats (Excel, HTML, JSON)
   - Click "Analyze File"
   - Download generated reports

### Option 2: Command Line Interface

```bash
# Basic usage
python3 pipeline.py your_file.xlsx

# Specify sheet name
python3 pipeline.py your_file.xlsx --sheet "Sheet1"

# Choose output formats
python3 pipeline.py your_file.xlsx --formats excel html json

# Full example
python3 pipeline.py /path/to/pwd_works.xlsx --sheet "Works Data" --formats excel html
```

### Option 3: Python API

```python
from pipeline import RedFlagPipeline

# Create pipeline instance
pipeline = RedFlagPipeline()

# Run analysis
result = pipeline.run(
    excel_file_path='path/to/your/file.xlsx',
    sheet_name='Sheet1',  # Optional
    output_formats=['excel', 'html', 'json']
)

# Check results
if result['success']:
    print(f"Red flagged: {len(result['results']['red_flagged'])}")
    print(f"Green flagged: {len(result['results']['green_flagged'])}")
    print(f"Reports generated: {result['output_files']}")
else:
    print(f"Error: {result['error']}")
```

## Excel File Format

### Required Columns
The system expects the following columns (flexible matching):

| Column Name | Description |
|------------|-------------|
| Sr. | Serial number |
| Budget Item No. | Budget item identifier |
| Name of the work | Work name in English |
| Name Of The Work (In Marathi) | Work name in Marathi |
| Administrative Approval Cost (Lakh) | AA cost |
| Administrative Approval Date | AA approval date |
| Contract Agreement Cost (Lakh) | Contract cost |
| Total Expenditure (Lakhs) | Total expenditure |
| Physical Progress | Progress percentage |
| Date of Work_Order | Work order date |
| Original Time Limit in Days | Completion time limit |
| Road Category | Road type (SH/MDR/NH) |
| Chainage From | Starting chainage |
| Chainage To | Ending chainage |

### Data Quality Tips
- Remove any blank rows or duplicate headers
- Ensure dates are in a recognizable format (DD/MM/YYYY or YYYY-MM-DD)
- Numeric values should not contain text (except for negative signs)
- Use consistent units (all costs in Lakhs)

## Output Reports

### Excel Report
Multi-sheet workbook containing:
- **Summary**: Overall statistics
- **Red Flagged Entries**: Detailed list of issues
- **Green Flagged Entries**: Clean records
- **Flag Type Summary**: Distribution by flag type
- **Detailed Findings**: Complete analysis with all details

### HTML Report
Professional web-based report with:
- Interactive summary cards
- Color-coded severity levels
- Searchable tables
- Print-ready format

### JSON Report
Machine-readable format for:
- Integration with other systems
- Custom processing
- Data archival

## Configuration

### Modify Analysis Parameters

Edit `red_flag_analyzer.py` to customize thresholds:

```python
# Excess expenditure threshold (default: 10%)
if excess_percentage > 10:  # Change this value

# Unspent balance threshold (default: ₹1 lakh)
if balance > 100000:  # Change this value

# Work splitting detection (default: 3+ works, <₹10 lakh each)
if len(works) >= 3 and contract_cost < 10:  # Change these values
```

### Customize Web Interface

Edit files in `static/` folder:
- `static/css/style.css` - Modify colors, fonts, layout
- `static/js/script.js` - Change behavior and interactions
- `templates/index.html` - Modify structure and content

## Troubleshooting

### Common Issues

**1. File upload fails**
- Check file size (<50MB)
- Ensure file has .xlsx or .xls extension
- Verify file is not corrupted

**2. Missing columns error**
- Review required columns list
- Check for typos in column headers
- Ensure no merged cells in header row

**3. Date parsing errors**
- Use standard date formats (DD/MM/YYYY or YYYY-MM-DD)
- Ensure dates are actual date values, not text

**4. Multilingual text issues**
- Save Excel file with UTF-8 encoding
- Ensure fonts support Hindi/Marathi characters

### Logs

Check logs for detailed error information:
```bash
tail -f red_flag_analysis.log
```

## Advanced Features

### Custom Red Flag Rules

Add new detection rules in `red_flag_analyzer.py`:

```python
def _check_custom_flag(self, row: pd.Series) -> Dict[str, Any]:
    """Your custom flag logic"""
    if your_condition:
        return {
            'flag_id': 9,
            'flag_name': 'Custom Flag',
            'severity': 'HIGH',
            'description': 'Description of issue',
            'details': {
                'key': 'value'
            }
        }
    return None
```

Then add to `_analyze_single_record()`:
```python
flag9 = self._check_custom_flag(row)
if flag9:
    flags.append(flag9)
```

### Batch Processing

Process multiple files:

```python
from pipeline import RedFlagPipeline
import glob

pipeline = RedFlagPipeline()

for file in glob.glob('*.xlsx'):
    print(f"Processing {file}...")
    result = pipeline.run(file)
    if result['success']:
        print(f"✓ {file} completed")
    else:
        print(f"✗ {file} failed: {result['error']}")
```

## Performance

### Benchmarks
- Small files (<1000 records): < 5 seconds
- Medium files (1000-5000 records): 10-30 seconds
- Large files (5000-10000 records): 30-60 seconds

### Optimization Tips
- Use latest version of Python 3.x
- Ensure sufficient RAM (minimum 2GB recommended)
- Close other applications during large file processing

## Security Considerations

### Production Deployment

1. **Change secret key** in `app.py`:
```python
app.secret_key = 'use-a-strong-random-secret-key'
```

2. **Enable HTTPS**:
```python
app.run(ssl_context='adhoc')  # For development
# Use proper certificates in production
```

3. **Add authentication**:
Implement user authentication before allowing uploads

4. **File validation**:
System already validates file types and sizes

5. **Input sanitization**:
Excel data is automatically sanitized during processing

## Support & Contribution

### Reporting Issues
- Include Excel file sample (anonymized if sensitive)
- Provide error logs
- Describe expected vs actual behavior

### Feature Requests
- Clearly describe the new feature
- Explain use case and benefits
- Provide examples if applicable

## License

This system is developed for Public Works Department audit analysis.

## Version History

- **v1.0.0** (2026-02-04)
  - Initial release
  - 8 red flag criteria implemented
  - Multilingual support (English, Hindi, Marathi)
  - Web interface and CLI
  - Multiple report formats

## Credits

Developed for automating PWD audit compliance analysis based on established audit parameters and public works manual guidelines.
