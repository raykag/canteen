# 📱 Quick Termux Setup - Copy & Paste Commands

## 🚀 **1-Minute Setup Commands**

Copy and paste these commands one by one in Termux:

### **Step 1: Basic Setup**
```bash
pkg update && pkg upgrade -y
pkg install python python-pip git nano wget curl build-essential libffi-dev openssl-dev -y
```

### **Step 2: Create Project**
```bash
cd ~
mkdir farmers-cooperative
cd farmers-cooperative
```

### **Step 3: Install Django**
```bash
pip install Django==4.2.7 djangorestframework==3.14.0 django-cors-headers==4.3.1 PyJWT==2.8.0 celery==5.3.4 django-extensions==3.2.3 python-dotenv==1.0.0 Pillow==10.4.0 djangorestframework-simplejwt==5.3.0 django-filter==23.5
```

### **Step 4: Create Django Project**
```bash
django-admin startproject farmers_cooperative .
python manage.py startapp users
python manage.py startapp financial
python manage.py startapp equipment
python manage.py startapp notifications
python manage.py startapp reports
```

### **Step 5: Setup Database**
```bash
python manage.py migrate
python manage.py createsuperuser
```

### **Step 6: Run Server**
```bash
python manage.py runserver 0.0.0.0:8000
```

### **Step 7: Access**
Open browser and go to: `http://localhost:8000/`

---

## 🎯 **Alternative: Clone Existing Project**

If you have the project on GitHub:

```bash
cd ~
git clone YOUR_GITHUB_REPO_URL farmers-cooperative
cd farmers-cooperative
pip install -r requirements.txt
python manage.py migrate
python seed_data.py
python manage.py runserver 0.0.0.0:8000
```

---

## 📱 **Daily Use Commands**

```bash
# Start working
cd ~/farmers-cooperative
python manage.py runserver 0.0.0.0:8000

# Access in browser
# http://localhost:8000/
```

**🌱 That's it! Your Farmers Cooperative System is running on Android!**