# 📱 Complete Termux Installation Guide for Android

## 🚀 **Step-by-Step Installation Process**

### **Phase 1: Install and Setup Termux**

#### **Step 1: Download Termux**
```bash
# Download from F-Droid (Recommended) or Google Play Store
# F-Droid version is more up-to-date and stable
```

**📱 Download Links:**
- **F-Droid:** https://f-droid.org/en/packages/com.termux/
- **Google Play:** Search "Termux" (backup option)

#### **Step 2: First Setup**
Open Termux and run these commands:

```bash
# Update package lists
pkg update && pkg upgrade -y

# Install essential tools
pkg install python python-pip git nano wget curl -y

# Install build tools (needed for some Python packages)
pkg install build-essential libffi-dev openssl-dev -y
```

---

### **Phase 2: Clone and Setup Project**

#### **Step 3: Clone the Repository**
```bash
# Navigate to home directory
cd ~

# Clone your farmers cooperative project
git clone https://github.com/YOUR_USERNAME/farmers-cooperative-system.git

# Or if you don't have it on GitHub yet, create the directory
mkdir farmers-cooperative
cd farmers-cooperative
```

#### **Step 4: Create Project Structure**
If cloning from GitHub, skip this. Otherwise, create the structure:

```bash
# Create main directories
mkdir -p farmers_cooperative users financial equipment notifications reports templates static media logs

# Create essential files
touch manage.py requirements.txt
```

---

### **Phase 3: Python Environment Setup**

#### **Step 5: Install Python Dependencies**
```bash
# Navigate to project directory
cd ~/farmers-cooperative

# Install Django and dependencies
pip install Django==4.2.7
pip install djangorestframework==3.14.0
pip install django-cors-headers==4.3.1
pip install PyJWT==2.8.0
pip install celery==5.3.4
pip install django-extensions==3.2.3
pip install python-dotenv==1.0.0
pip install Pillow==10.4.0
pip install djangorestframework-simplejwt==5.3.0
pip install django-filter==23.5
pip install pytest==7.4.3
pip install pytest-django==4.6.0

# Or install from requirements.txt if you have it
# pip install -r requirements.txt
```

---

### **Phase 4: Database Setup**

#### **Step 6: Database Migrations**
```bash
# Make sure you're in the project directory
cd ~/farmers-cooperative

# Create initial migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser (optional - skip if you have seed data)
python manage.py createsuperuser
```

#### **Step 7: Load Sample Data**
```bash
# If you have the seed_data.py file
python seed_data.py

# Or load fixtures if available
# python manage.py loaddata initial_data.json
```

---

### **Phase 5: Run the Server**

#### **Step 8: Start Django Server**
```bash
# Run the development server
python manage.py runserver 0.0.0.0:8000

# You should see output like:
# Starting development server at http://0.0.0.0:8000/
# Quit the server with CONTROL-C.
```

#### **Step 9: Access Your App**
Open another Termux session (swipe from left edge → "New Session") or open your browser:

```bash
# Test the server in Termux
curl http://localhost:8000/

# Or open in browser
# Go to: http://localhost:8000/
```

---

### **Phase 6: Complete Project Files**

If you need to create the project from scratch, here are the essential files:

#### **Step 10: Create requirements.txt**
```bash
nano requirements.txt
```

Add this content:
```txt
Django==4.2.7
djangorestframework==3.14.0
django-cors-headers==4.3.1
PyJWT==2.8.0
celery==5.3.4
django-extensions==3.2.3
python-dotenv==1.0.0
Pillow==10.4.0
djangorestframework-simplejwt==5.3.0
django-filter==23.5
pytest==7.4.3
pytest-django==4.6.0
```

#### **Step 11: Create manage.py**
```bash
nano manage.py
```

Add this content:
```python
#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farmers_cooperative.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
```

---

### **Phase 7: Troubleshooting & Tips**

#### **Common Issues and Solutions:**

**1. Permission Denied:**
```bash
# Make manage.py executable
chmod +x manage.py
```

**2. Port Already in Use:**
```bash
# Use a different port
python manage.py runserver 0.0.0.0:8001
```

**3. Package Installation Issues:**
```bash
# Update pip
pip install --upgrade pip

# Clear pip cache
pip cache purge
```

**4. Storage Permissions:**
```bash
# Allow Termux to access storage
termux-setup-storage
```

---

### **Phase 8: Advanced Setup (Optional)**

#### **Step 12: Install Additional Tools**
```bash
# Install useful development tools
pkg install vim tree htop

# Install Redis (for Celery tasks)
pkg install redis

# Start Redis server
redis-server &
```

#### **Step 13: Setup Auto-Start Script**
```bash
# Create a startup script
nano ~/start_farmers_coop.sh
```

Add this content:
```bash
#!/bin/bash
cd ~/farmers-cooperative
echo "🌱 Starting Farmers Cooperative Management System..."
python manage.py runserver 0.0.0.0:8000
```

Make it executable:
```bash
chmod +x ~/start_farmers_coop.sh
```

Now you can start the server with:
```bash
~/start_farmers_coop.sh
```

---

## 🎯 **Quick Start Commands Summary**

Once everything is installed, these are your daily commands:

```bash
# 1. Open Termux
# 2. Navigate to project
cd ~/farmers-cooperative

# 3. Start server
python manage.py runserver 0.0.0.0:8000

# 4. Open browser and go to:
# http://localhost:8000/

# 5. Login with:
# Username: admin
# Password: admin123
```

---

## 📱 **Termux Pro Tips**

### **Essential Termux Shortcuts:**
- **Volume Down + C:** Copy
- **Volume Down + V:** Paste
- **Volume Down + Q:** Show extra keys
- **Swipe from left:** Open session menu
- **Long press:** Select text

### **Multiple Sessions:**
```bash
# Create new session: Swipe from left → "New Session"
# Switch sessions: Swipe from left → Select session
# Rename session: Long press session → Rename
```

### **File Management:**
```bash
# List files
ls -la

# Edit files
nano filename.py

# View file content
cat filename.py

# Copy files
cp source.py destination.py
```

---

## 🚀 **Success! Your System is Running on Android**

After following these steps, you'll have:

✅ **Full Django development environment on Android**
✅ **Farmers Cooperative Management System running locally**
✅ **All features accessible via mobile browser**
✅ **Ability to edit code directly on your phone**
✅ **Professional development setup**

**🎉 Access your system at: http://localhost:8000/**

**Login Credentials:**
- **Admin:** admin / admin123
- **Staff:** staff1 / staff123
- **Farmer:** farmer1 / farmer123

---

## 🔧 **Need Help?**

If you encounter any issues:

1. **Check Termux permissions:** Settings → Apps → Termux → Permissions
2. **Restart Termux:** Close and reopen the app
3. **Update packages:** `pkg update && pkg upgrade`
4. **Check logs:** Look at Django error messages
5. **Ask for help:** Share the specific error message

**🌱 Happy farming with your new digital cooperative system!**