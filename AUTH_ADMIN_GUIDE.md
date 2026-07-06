# Authentication & Admin Panel Guide

Complete guide for the user authentication system and admin panel of Prize Comparison App.

## 🔐 Authentication System

### Features
- ✅ User registration with validation
- ✅ Secure login with password hashing
- ✅ Remember me functionality
- ✅ Password hashing using Werkzeug
- ✅ Session management
- ✅ Admin role support

### Routes

#### Register
- **URL:** `/register`
- **Method:** GET/POST
- **Access:** Public
- **Features:**
  - Username validation (min 3 characters)
  - Email validation (unique)
  - Password validation (min 6 characters)
  - Password confirmation
  - Duplicate account prevention

```html
<!-- Register Form -->
<form method="POST" action="/register">
    <input type="text" name="username" required>
    <input type="email" name="email" required>
    <input type="password" name="password" required>
    <input type="password" name="confirm_password" required>
    <button type="submit">Register</button>
</form>
```

#### Login
- **URL:** `/login`
- **Method:** GET/POST
- **Access:** Public (redirects if already logged in)
- **Features:**
  - Username and password authentication
  - Remember me option
  - Next page redirect support
  - Active user check

```html
<!-- Login Form -->
<form method="POST" action="/login">
    <input type="text" name="username" required>
    <input type="password" name="password" required>
    <input type="checkbox" name="remember">
    <button type="submit">Login</button>
</form>
```

#### Logout
- **URL:** `/logout`
- **Method:** GET
- **Access:** Authenticated users only
- **Redirects to:** Home page after logout

### Default Admin Account

Created automatically on first run:
```
Username: admin
Password: admin123
```

⚠️ **Important:** Change this password in production!

### User Model

```python
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    search_histories = db.relationship('SearchHistory', backref='user')
```

### Password Security
- Passwords are hashed using `werkzeug.security.generate_password_hash()`
- Hash verification using `check_password_hash()`
- Never store plain text passwords
- Passwords can only be set during registration/reset

---

## 👨‍💼 Admin Panel

### Access

- **URL:** `/admin`
- **Access:** Admin users only
- **Redirect:** Login page if not authenticated or not admin

### Admin Features

#### 1. Dashboard
- Overview of app statistics
- Quick access to all management sections
- System status information

#### 2. User Management
- View all registered users
- Search users by username or email
- Filter by admin status and active status
- Edit user details
- Delete users
- Sort by creation date and username

**Accessible at:** `/admin/user/`

**Columns:**
- ID
- Username
- Email
- Is Admin (Yes/No)
- Is Active (Yes/No)
- Created At (Date)

**Actions:**
- View details
- Edit user
- Delete user
- Search and filter

#### 3. Search History Management
- View all user searches
- Search by query term
- Filter by user and date
- See results count for each search
- View search details
- Track user activity

**Accessible at:** `/admin/searchhistory/`

**Columns:**
- ID
- User (who performed search)
- Search Query (what they searched)
- Results Count (how many results)
- Created At (when searched)

**Features:**
- View/edit searches
- Delete searches
- Advanced filtering by user
- Date range filtering
- Sort by date or results count

#### 4. Product Management
- View all scraped products
- Search by product name or query
- Filter by source (Amazon/Flipkart)
- Filter by date
- Delete products
- Product analytics

**Accessible at:** `/admin/product/`

**Columns:**
- ID
- Product Name
- Source (Amazon/Flipkart)
- Price (Original)
- Discounted Price
- Search Query
- Created At

**Features:**
- Advanced search
- Source filtering
- Date filtering
- Bulk operations

### Admin Panel User Interface

The admin panel is powered by **Flask-Admin** with customized views:

```python
# User Admin View
class UserAdminView(AuthenticatedAdminView):
    column_list = ['id', 'username', 'email', 'is_admin', 'is_active', 'created_at']
    column_searchable_list = ['username', 'email']
    column_filters = ['is_admin', 'is_active', 'created_at']
    can_delete = True
    can_edit = True

# Search History Admin View
class SearchHistoryAdminView(AuthenticatedAdminView):
    column_list = ['id', 'user', 'search_query', 'results_count', 'created_at']
    column_searchable_list = ['search_query']
    column_filters = ['created_at', 'user.username']
    can_delete = True
    can_edit = False  # Read-only

# Product Admin View
class ProductAdminView(AuthenticatedAdminView):
    column_list = ['id', 'product_name', 'source', 'price', 'discounted_price', 'search_query', 'created_at']
    column_searchable_list = ['product_name', 'search_query']
    column_filters = ['source', 'created_at']
    can_delete = True
```

---

## 📊 Search History Tracking

### SearchHistory Model

```python
class SearchHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    search_query = db.Column(db.String(255), nullable=False)
    results_count = db.Column(db.Integer, default=0)
    results_data = db.Column(db.Text)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='search_histories')
```

### Features
- ✅ Automatic search tracking
- ✅ Results count tracking
- ✅ Full results stored as JSON
- ✅ Timestamp recording
- ✅ User association
- ✅ Dashboard view for users

### User Dashboard
- **URL:** `/dashboard`
- **Access:** Authenticated users only
- **Features:**
  - View personal search history
  - Paginated results (10 per page)
  - Search query display
  - Results count badge
  - Search timestamp
  - View full results action
  - Sort by most recent

---

## 🛡️ Security Features

### Password Security
```python
from werkzeug.security import generate_password_hash, check_password_hash

# During registration
user = User(username=username, email=email)
user.set_password(password)  # Hashes the password
db.session.add(user)

# During login
user.check_password(provided_password)  # Compares with hash
```

### Session Security
```python
app.config['SESSION_COOKIE_SECURE'] = False  # Set True for HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JS access
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
```

### Authentication Checks
- Login required decorator: `@login_required`
- Admin checks: `current_user.is_admin`
- Active user validation on login
- Automatic user loading with `@login_manager.user_loader`

---

## 📱 API Endpoints (Auth Required)

### Search with History Tracking
```
POST /api/search
Authorization: Requires login
Body: { "product_name": "iPhone 16" }
Response: { "results": [...], "search_id": 1 }
```

### Get Personal Search History
```
GET /api/search/<search_id>
Authorization: Requires login
Response: { "search": {...}, "results": [...] }
```

### Dashboard
```
GET /dashboard
Authorization: Requires login
```

---

## 🚀 Getting Started

### Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Install Playwright browsers:**
```bash
playwright install
```

3. **Run the application:**
```bash
python main.py
```

4. **Access the app:**
   - Main app: `http://localhost:8000`
   - Admin panel: `http://localhost:8000/admin`
   - Login: `http://localhost:8000/login`
   - Register: `http://localhost:8000/register`

### First Time Setup

1. Default admin account is created automatically:
   - Username: `admin`
   - Password: `admin123`

2. Change admin password immediately in production

3. Create regular user accounts via `/register`

---

## 📋 Usage Examples

### Register a New User
```
POST /register
username: john_doe
email: john@example.com
password: securepass123
confirm_password: securepass123
```

### Login
```
POST /login
username: john_doe
password: securepass123
remember: yes (optional)
```

### Search for Products (Authenticated)
```
POST /api/search
Authorization: User logged in
{
  "product_name": "iPhone 16"
}
```

Response includes:
- Scraped results from Amazon and Flipkart
- Search history record created
- Search ID for retrieving results later

### View User Dashboard
```
GET /dashboard
- View personal search history
- See results count for each search
- Access full results from previous searches
```

### Admin Panel Operations
- Access: `http://localhost:8000/admin`
- View all users, searches, and products
- Manage user accounts
- Monitor app activity
- Delete old data if needed

---

## 🔧 Configuration

### Environment Variables
```python
# Set in .env or system environment
FLASK_DEBUG=True          # Development mode
DATABASE_URL=...          # Database connection
SECRET_KEY=...            # Session secret
FLASK_ENV=development
```

### Database
```python
# Default: SQLite
SQLALCHEMY_DATABASE_URI = 'sqlite:///prize_comparison.db'

# Production: Use PostgreSQL or MySQL
SQLALCHEMY_DATABASE_URI = 'postgresql://user:pass@localhost/db'
```

---

## 📊 Admin Panel Screenshots

The admin panel includes:
- User management with search and filters
- Search history analytics
- Product database management
- Statistics dashboard
- Bulk operations support
- Export capabilities (future)

---

## 🆘 Troubleshooting

### "Authentication failed" after login
- Clear browser cookies
- Check if user account is active (`is_active=True`)
- Verify password hasn't changed

### Admin panel not accessible
- Ensure logged-in user has `is_admin=True`
- Check session is still valid
- Try logging out and back in

### Search history not saving
- Ensure user is authenticated (`current_user.is_authenticated`)
- Check database connection
- Verify SearchHistory model is created

### Can't access admin panel
- Login first
- Use admin account (default: admin/admin123)
- Check if user `is_admin` field is True

---

## ✅ Security Checklist

For production deployment:
- [ ] Change default admin password
- [ ] Set `SECRET_KEY` to a strong random value
- [ ] Set `SESSION_COOKIE_SECURE = True` (if using HTTPS)
- [ ] Use HTTPS only
- [ ] Set `DEBUG = False`
- [ ] Use a production database (PostgreSQL, MySQL)
- [ ] Implement CSRF protection for forms
- [ ] Add rate limiting for login attempts
- [ ] Regular database backups
- [ ] Monitor admin panel access

---

## 📚 Additional Resources

- [Flask-Login Documentation](https://flask-login.readthedocs.io/)
- [Flask-Admin Documentation](https://flask-admin.readthedocs.io/)
- [Flask-SQLAlchemy Documentation](https://flask-sqlalchemy.palletsprojects.com/)
- [Werkzeug Security Documentation](https://werkzeug.palletsprojects.com/en/2.3.x/security/)
