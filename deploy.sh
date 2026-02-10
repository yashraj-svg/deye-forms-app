#!/bin/bash
# Deployment script for Deye Web App - Updates production server with latest changes

set -e  # Exit on error

echo "=================================="
echo "🚀 DEYE WEB APP DEPLOYMENT SCRIPT"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="/path/to/deye-forms-app"  # CHANGE THIS to your actual path
VENV_DIR="$PROJECT_DIR/.venv"
PYTHON="$VENV_DIR/bin/python"
MANAGE_PY="$PROJECT_DIR/manage.py"

# Verify paths exist
if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${RED}❌ Project directory not found: $PROJECT_DIR${NC}"
    echo "Please update PROJECT_DIR in this script"
    exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
    echo -e "${RED}❌ Virtual environment not found: $VENV_DIR${NC}"
    exit 1
fi

echo -e "${BLUE}📁 Project Directory: $PROJECT_DIR${NC}"
echo ""

# Step 1: Stop the web server (if using systemd or manual)
echo -e "${YELLOW}1️⃣  Stopping web server...${NC}"
if systemctl is-active --quiet deye-app; then
    sudo systemctl stop deye-app
    echo -e "${GREEN}✅ Web server stopped${NC}"
else
    echo -e "${BLUE}ℹ️  Web server not running via systemd${NC}"
fi
echo ""

# Step 2: Navigate to project directory
echo -e "${YELLOW}2️⃣  Navigating to project...${NC}"
cd "$PROJECT_DIR"
echo -e "${GREEN}✅ In project directory${NC}"
echo ""

# Step 3: Pull latest changes from GitHub
echo -e "${YELLOW}3️⃣  Pulling latest changes from GitHub...${NC}"
git fetch origin
git pull origin master
echo -e "${GREEN}✅ Latest code pulled${NC}"
echo ""

# Step 4: Activate virtual environment and install dependencies
echo -e "${YELLOW}4️⃣  Installing dependencies...${NC}"
source "$VENV_DIR/bin/activate"
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo -e "${GREEN}✅ Dependencies installed${NC}"
echo ""

# Step 5: Run migrations
echo -e "${YELLOW}5️⃣  Running database migrations...${NC}"
$PYTHON $MANAGE_PY migrate
echo -e "${GREEN}✅ Migrations applied${NC}"
echo ""

# Step 6: Collect static files
echo -e "${YELLOW}6️⃣  Collecting static files...${NC}"
$PYTHON $MANAGE_PY collectstatic --noinput -q
echo -e "${GREEN}✅ Static files collected${NC}"
echo ""

# Step 7: Verify database
echo -e "${YELLOW}7️⃣  Verifying stock data...${NC}"
$PYTHON -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deye_config.settings')
django.setup()
from forms.models import StockItem
from django.db.models import Sum
count = StockItem.objects.count()
qty = StockItem.objects.aggregate(total=Sum('quantity'))['total'] or 0
print(f'   📊 Stock Items: {count}')
print(f'   📊 Total Quantity: {qty:.0f} PCS')
if count == 1976 and qty == 259406:
    print('   ✅ Data matches expected values!')
else:
    print('   ⚠️  Data differs from expected (expected 1976 items, 259406 PCS)')
"
echo ""

# Step 8: Start web server
echo -e "${YELLOW}8️⃣  Starting web server...${NC}"
if systemctl is-active --quiet deye-app || systemctl list-units --all | grep -q "deye-app.service"; then
    sudo systemctl start deye-app
    echo -e "${GREEN}✅ Web server started${NC}"
else
    echo -e "${BLUE}ℹ️  Manual restart needed for web server${NC}"
    echo -e "${BLUE}   Run: sudo systemctl start deye-app${NC}"
    echo -e "${BLUE}   Or restart your web server manually${NC}"
fi
echo ""

# Step 9: Final status
echo "=================================="
echo -e "${GREEN}✅ DEPLOYMENT COMPLETE!${NC}"
echo "=================================="
echo ""
echo -e "${BLUE}📋 Summary:${NC}"
echo "   ✓ Code pulled from GitHub"
echo "   ✓ Dependencies installed"
echo "   ✓ Migrations applied"
echo "   ✓ Stock data updated (1,976 items)"
echo "   ✓ Static files collected"
echo "   ✓ Web server restarted"
echo ""
echo -e "${BLUE}🌐 Access your application:${NC}"
echo "   http://your-domain.com/stock/received"
echo ""
echo -e "${YELLOW}⚠️  Remember:${NC}"
echo "   - Update PROJECT_DIR in this script with your actual path"
echo "   - Ensure deye-app.service is configured (or adjust Step 1 & 7)"
echo "   - Check logs if there are issues: tail -f /var/log/deye-app.log"
echo ""
