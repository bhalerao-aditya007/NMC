# Installation & Deployment Guide
## PWD Works Red Flag Analysis System

---

## 📦 Package Contents

This package contains a complete, production-ready system for analyzing PWD works Excel files against 8 audit red flag criteria.

### Files Included:

**Core Python Modules:**
- `pipeline.py` - Main orchestration pipeline
- `excel_reader.py` - Excel file processor with multilingual support
- `red_flag_analyzer.py` - Red flag detection engine
- `report_generator.py` - Multi-format report generator
- `app.py` - Flask web application

**Web Interface:**
- `templates/index.html` - Professional web UI
- `static/css/style.css` - Styling
- `static/js/script.js` - Interactive functionality

**Documentation:**
- `README.md` - Comprehensive documentation
- `QUICKSTART.md` - Quick start guide
- `INSTALLATION.md` - This file

**Utilities:**
- `requirements.txt` - Python dependencies
- `test_system.py` - Test suite

---

## 🖥️ System Requirements

### Minimum Requirements:
- **Operating System**: Linux, macOS, or Windows
- **Python**: 3.8 or higher
- **RAM**: 2GB minimum, 4GB recommended
- **Storage**: 100MB for application + space for Excel files
- **Browser**: Modern browser (Chrome, Firefox, Safari, Edge)

### Recommended for Large Files (10,000+ records):
- **RAM**: 8GB
- **CPU**: Quad-core processor
- **Storage**: SSD for better performance

---

## 📥 Installation Methods

### Method 1: Standard Installation (Recommended)

#### Step 1: Extract Package
```bash
unzip pwd_red_flag_analyzer_complete.zip
cd pwd-red-flag-analyzer
```

#### Step 2: Install Dependencies
```bash
pip install -r requirements.txt --break-system-packages
```

Or install individually:
```bash
pip install pandas openpyxl flask werkzeug python-docx --break-system-packages
```

#### Step 3: Verify Installation
```bash
python3 test_system.py
```

Expected output:
```
🎉 All tests passed successfully!
```

#### Step 4: Start Using
Web Interface:
```bash
python3 app.py
```
Then open: http://localhost:5000

Command Line:
```bash
python3 pipeline.py your_file.xlsx
```

---

### Method 2: Virtual Environment (Isolated)

#### Step 1: Create Virtual Environment
```bash
python3 -m venv venv
```

#### Step 2: Activate Environment
Linux/macOS:
```bash
source venv/bin/activate
```

Windows:
```bash
venv\Scripts\activate
```

#### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 4: Run Application
```bash
python app.py
```

---

### Method 3: Docker Deployment (Production)

#### Create Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
```

#### Build and Run
```bash
docker build -t pwd-red-flag-analyzer .
docker run -p 5000:5000 pwd-red-flag-analyzer
```

---

## 🌐 Web Server Deployment

### Development Server (Testing)
```bash
python3 app.py
```

### Production with Gunicorn

#### Install Gunicorn
```bash
pip install gunicorn
```

#### Run
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Production with uWSGI + Nginx

#### Install uWSGI
```bash
pip install uwsgi
```

#### Create uwsgi.ini
```ini
[uwsgi]
module = app:app
master = true
processes = 4
socket = /tmp/pwd-analyzer.sock
chmod-socket = 660
vacuum = true
die-on-term = true
```

#### Nginx Configuration
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        include uwsgi_params;
        uwsgi_pass unix:/tmp/pwd-analyzer.sock;
    }

    location /static {
        alias /path/to/pwd-red-flag-analyzer/static;
    }
}
```

---

## 🔧 Configuration

### Application Settings (app.py)

#### Change Port
```python
app.run(host='0.0.0.0', port=8080)  # Default: 5000
```

#### Change Upload Size Limit
```python
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB
```

#### Change Secret Key (IMPORTANT for production)
```python
app.secret_key = 'your-super-secret-key-here-change-this'
```

### Analysis Parameters (red_flag_analyzer.py)

#### Excess Expenditure Threshold
```python
if excess_percentage > 10:  # Change to 15 for 15%
```

#### Unspent Balance Threshold
```python
if balance > 100000:  # Change to 200000 for ₹2 lakh
```

#### Work Splitting Detection
```python
if len(works) >= 3 and contract_cost < 10:  # Adjust thresholds
```

---

## 🚀 Production Deployment Checklist

### Security
- [ ] Change Flask secret key
- [ ] Enable HTTPS (SSL certificate)
- [ ] Add authentication/authorization
- [ ] Configure firewall rules
- [ ] Set up rate limiting
- [ ] Enable CORS if needed

### Performance
- [ ] Use production WSGI server (Gunicorn/uWSGI)
- [ ] Set up reverse proxy (Nginx/Apache)
- [ ] Configure caching
- [ ] Optimize database queries (if adding database)
- [ ] Set up CDN for static files

### Monitoring
- [ ] Set up logging
- [ ] Configure error tracking
- [ ] Monitor system resources
- [ ] Set up uptime monitoring
- [ ] Configure backup strategy

### Maintenance
- [ ] Schedule regular backups
- [ ] Plan for updates
- [ ] Document custom configurations
- [ ] Set up automated testing
- [ ] Create rollback plan

---

## 🐛 Troubleshooting

### Installation Issues

**Problem**: `pip install` fails
```bash
# Solution 1: Upgrade pip
python3 -m pip install --upgrade pip

# Solution 2: Use --user flag
pip install --user -r requirements.txt

# Solution 3: Use --break-system-packages
pip install -r requirements.txt --break-system-packages
```

**Problem**: Module not found
```bash
# Verify installation
pip list | grep -E "pandas|openpyxl|flask"

# Reinstall specific package
pip install pandas --force-reinstall
```

**Problem**: Permission denied
```bash
# Use sudo (Linux/macOS)
sudo pip install -r requirements.txt

# Or use --user flag
pip install --user -r requirements.txt
```

### Runtime Issues

**Problem**: Port already in use
```bash
# Find and kill process
lsof -ti:5000 | xargs kill -9

# Or use different port
python3 app.py --port 8080
```

**Problem**: File upload fails
```bash
# Check file permissions
chmod 777 uploads/

# Check disk space
df -h

# Increase upload limit in app.py
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
```

**Problem**: Out of memory
```bash
# Monitor memory
top
htop

# Increase system RAM
# Or process smaller files
# Or optimize code for memory usage
```

### Analysis Issues

**Problem**: Wrong red flags detected
```bash
# Check Excel file format
# Verify column names match expected
# Review threshold settings in red_flag_analyzer.py
```

**Problem**: Missing data in reports
```bash
# Verify Excel has all required columns
# Check for null/empty values
# Review data quality report
```

---

## 📊 Performance Optimization

### For Large Files (10,000+ records)

#### 1. Use Chunking
```python
# In excel_reader.py
df = pd.read_excel(file, chunksize=1000)
```

#### 2. Optimize Memory
```python
# Reduce memory usage
df = df.astype({
    'Budget Item No.': 'category',
    'District': 'category'
})
```

#### 3. Parallel Processing
```python
# Use multiprocessing
from multiprocessing import Pool

with Pool(4) as p:
    results = p.map(analyze_record, records)
```

#### 4. Database Backend
Consider adding SQLite/PostgreSQL for very large datasets.

---

## 🔄 Updates and Maintenance

### Updating the System

#### 1. Backup Current Version
```bash
cp -r pwd-red-flag-analyzer pwd-red-flag-analyzer-backup
```

#### 2. Update Code
```bash
# Pull new version or copy new files
# Compare changes with backup
```

#### 3. Update Dependencies
```bash
pip install -r requirements.txt --upgrade
```

#### 4. Test
```bash
python3 test_system.py
```

### Regular Maintenance Tasks

**Weekly:**
- Review error logs
- Check disk space
- Verify backups

**Monthly:**
- Update dependencies
- Review security patches
- Optimize database (if using)

**Quarterly:**
- Full system audit
- Performance testing
- Update documentation

---

## 📞 Support Resources

### Documentation
- Full README: `README.md`
- Quick Start: `QUICKSTART.md`
- This Guide: `INSTALLATION.md`

### Testing
```bash
# Run full test suite
python3 test_system.py

# Test specific module
python3 -c "from excel_reader import ExcelReader; print('OK')"
```

### Logging
```bash
# View logs
tail -f red_flag_analysis.log

# Clear logs
> red_flag_analysis.log
```

### Common Commands
```bash
# Check Python version
python3 --version

# Check installed packages
pip list

# Test web server
curl http://localhost:5000/health

# Process test file
python3 pipeline.py sample_pwd_works.xlsx
```

---

## ✅ Post-Installation Checklist

- [ ] All dependencies installed
- [ ] Test suite passes
- [ ] Web interface accessible
- [ ] Sample file processes successfully
- [ ] Reports generate correctly
- [ ] Logs are being written
- [ ] Backups configured
- [ ] Security settings reviewed
- [ ] Documentation accessible
- [ ] Users trained

---

## 🎓 Next Steps

1. **Review Documentation**
   - Read README.md for complete feature list
   - Study QUICKSTART.md for usage examples

2. **Test with Sample Data**
   - Run `python3 test_system.py`
   - Process sample_pwd_works.xlsx
   - Review generated reports

3. **Test with Real Data**
   - Start with small file (< 100 records)
   - Verify accuracy of red flags
   - Review all report formats

4. **Deploy for Users**
   - Choose deployment method
   - Configure security settings
   - Set up monitoring
   - Train end users

5. **Customize as Needed**
   - Adjust thresholds
   - Add custom flags
   - Modify UI branding
   - Integrate with existing systems

---

## 📧 Getting Help

For issues or questions:
1. Check this installation guide
2. Review troubleshooting section
3. Check logs: `red_flag_analysis.log`
4. Run test suite: `python3 test_system.py`
5. Contact system administrator

---

**Deployment Version**: 1.0.0  
**Last Updated**: February 4, 2026  
**Minimum Python**: 3.8  
**Tested On**: Linux (Ubuntu 24), macOS, Windows 10/11  

---

**Ready to deploy?** Follow the checklist above and start with the web interface! 🚀
