# Farmers Cooperative Management System

A comprehensive digital platform designed specifically for managing rural agricultural cooperative societies, such as the Ngara Farmers Cooperative. This system provides centralized management for members, financial transactions, equipment distribution, notifications, and reporting.

## 🌟 Features

### User Management
- **Role-based Access Control**: Admin, Staff, and Farmer roles with different permission levels
- **Member Registration**: Complete farmer profiles with farm details
- **Authentication**: JWT-based secure authentication system
- **Profile Management**: Comprehensive user profiles with emergency contacts

### Financial Management
- **Contributions Tracking**: Monthly, special, share capital, and registration fee tracking
- **Loan Management**: Complete loan lifecycle from application to repayment
- **Account Management**: Multiple financial accounts (cash, bank, shares, loans)
- **Transaction Records**: Detailed financial transaction logging
- **Interest Calculations**: Automatic loan interest and payment calculations

### Equipment Distribution
- **Equipment Inventory**: Track tractors, ploughs, and other agricultural equipment
- **Allocation System**: Fair equipment distribution among farmers
- **Maintenance Records**: Equipment maintenance tracking and scheduling
- **Request System**: Farmers can request new equipment purchases

### Communication & Notifications
- **Announcement System**: Broadcast important messages to specific user groups
- **Email/SMS Integration**: Multi-channel notification delivery
- **User Preferences**: Customizable notification settings
- **Dashboard Alerts**: Real-time notifications in the web interface

### Reports & Analytics
- **Financial Reports**: Contributions, loans, and account statements
- **Member Reports**: Membership analytics and activity reports
- **Equipment Reports**: Utilization and maintenance reports
- **Custom Dashboards**: Role-specific dashboard views with charts
- **Scheduled Reports**: Automated report generation and delivery

## 🏗️ Architecture

### Three-Tier Architecture
1. **Presentation Layer**: Modern web interface with Bootstrap and Chart.js
2. **Application Layer**: Django REST Framework with business logic
3. **Data Layer**: SQLite database with Django ORM

### Technology Stack
- **Backend**: Django 4.2.7, Django REST Framework
- **Frontend**: HTML5, Bootstrap 5, JavaScript, Chart.js
- **Database**: SQLite (easily upgradeable to PostgreSQL/MySQL)
- **Authentication**: JWT with djangorestframework-simplejwt
- **Async Tasks**: Celery with Redis
- **API Documentation**: Integrated with DRF

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd farmers-cooperative-system
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv farmers_coop_env
   source farmers_coop_env/bin/activate  # Linux/Mac
   # or
   farmers_coop_env\Scripts\activate  # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run database migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create sample data**
   ```bash
   python seed_data.py
   ```

6. **Start the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Web Interface: http://127.0.0.1:8000/
   - Admin Panel: http://127.0.0.1:8000/admin/
   - API Endpoints: http://127.0.0.1:8000/api/

### Demo Credentials

| Role  | Username | Password |
|-------|----------|----------|
| Admin | admin    | admin123 |
| Staff | staff1   | staff123 |
| Farmer| farmer1  | farmer123 |

## 📊 Sample Data

The system comes pre-populated with realistic sample data:

- **8 Users**: 1 Admin, 2 Staff members, 5 Farmers
- **Financial Accounts**: Cash, Bank, Shares, and Loans accounts
- **Contributions**: 6 months of member contributions
- **Equipment**: 2 Tractors and 2 Ploughs with detailed specifications
- **Loans**: Active and pending loans with repayment schedules
- **Announcements**: Sample cooperative announcements

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/login/` - User login
- `POST /api/auth/refresh/` - Refresh JWT token
- `POST /api/auth/logout/` - User logout

### Users
- `GET /api/users/users/` - List all users
- `POST /api/users/users/` - Create new user
- `GET /api/users/users/{id}/` - Get user details
- `PUT /api/users/users/{id}/` - Update user
- `GET /api/users/users/{id}/stats/` - User statistics

### Financial
- `GET /api/financial/contributions/` - List contributions
- `POST /api/financial/contributions/` - Record contribution
- `GET /api/financial/loans/` - List loans
- `POST /api/financial/loans/` - Create loan application

### Equipment
- `GET /api/equipment/equipment/` - List equipment
- `POST /api/equipment/allocations/` - Allocate equipment
- `GET /api/equipment/maintenance/` - Maintenance records

## 🎨 User Interface

### Dashboard Features
- **Overview Dashboard**: Statistics, charts, and recent activities
- **Member Management**: User listing, creation, and profile management
- **Financial Dashboard**: Contributions, loans, and account summaries
- **Equipment Tracking**: Equipment status and allocation management
- **Notifications Center**: Announcements and communication tools
- **Reports Section**: Generate and download various reports

### Responsive Design
- Mobile-friendly interface
- Modern Bootstrap 5 styling
- Interactive charts with Chart.js
- Intuitive navigation and user experience

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@ngara-farmers.co.ke
```

### Celery Configuration (Optional)
For production environments with email/SMS notifications:

1. **Install Redis**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install redis-server
   
   # macOS
   brew install redis
   ```

2. **Start Celery worker**
   ```bash
   celery -A farmers_cooperative worker --loglevel=info
   ```

## 📈 System Requirements

### Minimum Requirements
- **Processor**: 1 GHz single-core
- **Memory**: 2 GB RAM
- **Storage**: 5 GB available space
- **Network**: Internet connection for external APIs

### Recommended Requirements
- **Processor**: 2 GHz dual-core
- **Memory**: 4 GB RAM
- **Storage**: 10 GB available space
- **Concurrent Users**: Supports up to 50 concurrent users

### Performance Specifications
- **Response Time**: < 2 seconds for standard operations
- **Database**: SQLite (suitable for small to medium cooperatives)
- **Scalability**: Can be upgraded to PostgreSQL/MySQL for larger deployments

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Role-based Access Control**: Granular permission system
- **Input Validation**: Comprehensive data validation
- **CSRF Protection**: Built-in Django CSRF protection
- **SQL Injection Prevention**: Django ORM protection
- **Password Security**: Strong password requirements

## 🌍 Localization

The system is designed for Kenyan agricultural cooperatives with:
- **Currency**: Kenya Shillings (KES)
- **Phone Numbers**: Kenyan format (+254)
- **Timezone**: Africa/Nairobi
- **Cultural Context**: Designed for rural farming communities

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support and questions:
- **Documentation**: See the `/docs` folder (when available)
- **Issues**: Create an issue on GitHub
- **Email**: Contact the development team

## 🏆 Acknowledgments

- **Target Organization**: Ngara Farmers Cooperative, Nakuru County, Kenya
- **Technology**: Built with Django and modern web technologies
- **Community**: Designed to serve rural agricultural communities

---

**Farmers Cooperative Management System** - Empowering rural agricultural communities through digital innovation.