# Quick Start Guide - PWD Red Flag Analyzer

## 🚀 Getting Started in 3 Steps

### Step 1: Install Dependencies
```bash
pip install pandas openpyxl flask werkzeug python-docx --break-system-packages
```

### Step 2: Test the System
```bash
python3 test_system.py
```

You should see:
```
🎉 All tests passed successfully!
```

### Step 3: Start Using

#### Option A: Web Interface (Easiest)
```bash
python3 app.py
```
Then open: http://localhost:5000

#### Option B: Command Line
```bash
python3 pipeline.py your_file.xlsx
```

#### Option C: Python Code
```python
from pipeline import RedFlagPipeline

pipeline = RedFlagPipeline()
result = pipeline.run('your_file.xlsx')
print(result)
```

## 📁 File Structure

```
pwd-red-flag-analyzer/
├── app.py                    # Web application (run this for UI)
├── pipeline.py               # Main pipeline (CLI entry point)
├── excel_reader.py           # Excel file processor
├── red_flag_analyzer.py      # Red flag detection logic
├── report_generator.py       # Report generation
├── test_system.py            # Test suite
├── requirements.txt          # Dependencies
├── README.md                 # Full documentation
├── QUICKSTART.md            # This file
├── templates/
│   └── index.html           # Web UI template
└── static/
    ├── css/style.css        # Styling
    └── js/script.js         # JavaScript

```

## 📊 What Files to Use

### Your Input
- **Excel file** (.xlsx or .xls) with PWD works data
- Must have columns like: Budget Item No., Name of work, AA Cost, Total Expenditure, etc.

### System Output
Three types of reports are generated:

1. **Excel Report** (.xlsx) - Detailed multi-sheet workbook
   - Summary statistics
   - Red flagged entries with full details
   - Green flagged entries
   - Flag type distribution

2. **HTML Report** (.html) - Professional web-based report
   - Visual summary cards
   - Color-coded severity levels
   - Can be opened in any browser
   - Print-ready

3. **JSON Data** (.json) - Machine-readable format
   - For further processing
   - API integration
   - Data archival

## 🎯 How It Works

The system checks for 8 red flags:

1. **Diversion of Funds** - Unauthorized fund transfers
2. **Wasteful Survey Expenditure** - Improper survey spending
3. **Excess Expenditure** - Over 10% above AA
4. **Overlapping Works** - Duplicate work on same road
5. **Delay in Completion** - Work not finished on time
6. **Splitting of Works** - Avoiding e-tender by splitting
7. **Non-recovery of Centage** - Missing 5% charges
8. **Unspent Balance** - Not returned after completion

## 🌐 Web Interface Guide

1. **Upload File**
   - Click "Choose Excel File" or drag-and-drop
   - Select your .xlsx file

2. **Choose Formats**
   - Check boxes for desired output formats
   - Excel, HTML, and/or JSON

3. **Analyze**
   - Click "Analyze File"
   - Wait for processing (5-60 seconds)

4. **Download Reports**
   - Click download buttons for each format
   - Save to your computer

## 💡 Tips for Best Results

### Prepare Your Excel File
✅ Remove blank rows
✅ Single header row (no merged cells)
✅ Dates in DD/MM/YYYY format
✅ Numbers without text
✅ All costs in Lakhs (consistent units)

### Common Issues
❌ File too large → Keep under 50MB
❌ Wrong extension → Use .xlsx or .xls
❌ Missing columns → Check required columns
❌ Corrupted file → Re-export from source

## 🔧 Troubleshooting

### "Module not found" error
```bash
pip install [module-name] --break-system-packages
```

### "File not found" error
- Check file path is correct
- Use absolute path: `/full/path/to/file.xlsx`

### "No data loaded" error
- Verify Excel file has data
- Check header row is present
- Ensure no empty sheets

### Web interface not starting
```bash
# Kill any existing process on port 5000
lsof -ti:5000 | xargs kill -9

# Restart
python3 app.py
```

## 📞 Getting Help

1. Check the full README.md for detailed documentation
2. Run tests: `python3 test_system.py`
3. Check logs: `tail -f red_flag_analysis.log`
4. Review sample files in the examples

## 🎓 Examples

### Example 1: Simple Analysis
```bash
python3 pipeline.py my_pwd_data.xlsx
```

### Example 2: Choose Specific Sheet
```bash
python3 pipeline.py data.xlsx --sheet "January 2026"
```

### Example 3: Only Excel Report
```bash
python3 pipeline.py data.xlsx --formats excel
```

### Example 4: All Formats
```bash
python3 pipeline.py data.xlsx --formats excel html json
```

### Example 5: Using Python
```python
from pipeline import RedFlagPipeline

# Initialize
pipeline = RedFlagPipeline()

# Analyze
result = pipeline.run(
    excel_file_path='data.xlsx',
    sheet_name='Sheet1',
    output_formats=['excel', 'html']
)

# Check results
if result['success']:
    print(f"Red flags: {len(result['results']['red_flagged'])}")
    for fmt, path in result['output_files'].items():
        print(f"{fmt}: {path}")
```

## ⚡ Performance Tips

- **Small files** (<1000 rows): ~5 seconds
- **Medium files** (1000-5000 rows): ~30 seconds
- **Large files** (5000-10000 rows): ~60 seconds

To speed up:
- Close other applications
- Use SSD storage
- Latest Python version
- Sufficient RAM (2GB+)

## 🔒 Security Notes

For production use:
1. Change secret key in app.py
2. Enable HTTPS
3. Add authentication
4. Limit file upload size
5. Sanitize inputs (already implemented)

## ✨ Features at a Glance

✓ Multilingual (English/Hindi/Marathi)
✓ 8 audit criteria automated
✓ Multiple report formats
✓ Web + CLI interfaces
✓ Batch processing capable
✓ Data quality validation
✓ Professional UI
✓ Production-ready code
✓ Comprehensive logging
✓ Error handling
✓ Extensible architecture

---

**Ready to analyze?** Run `python3 app.py` and open http://localhost:5000 🎉
