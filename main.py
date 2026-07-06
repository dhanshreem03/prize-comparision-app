from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from module.models import db, Product, User, SearchHistory
from ScraperEngine import AmazonScraper, FlipkartScraper
import json
import os

app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 'sqlite:///prize_comparison.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get(
    'SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login."""
    return User.query.get(int(user_id))


# Create database tables and default admin user
with app.app_context():
    db.create_all()
    # Create default admin if not exists
    if not User.query.filter_by(username='admin').first():
        admin_user = User(
            username='admin',
            email='admin@prizecomparison.com',
            is_admin=True,
            is_active=True
        )
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        db.session.commit()
        print("Default admin user created: username='admin', password='admin123'")


# Custom Admin Classes for Flask-Admin
class AuthenticatedAdminView(ModelView):
    """Base admin view with authentication."""

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login', next=request.url))


class UserAdminView(AuthenticatedAdminView):
    """Admin view for Users."""
    column_list = ['id', 'username', 'email',
                   'is_admin', 'is_active', 'created_at']
    column_searchable_list = ['username', 'email']
    column_filters = ['is_admin', 'is_active', 'created_at']
    column_sortable_list = ['created_at', 'username']
    can_delete = True
    can_edit = True


class SearchHistoryAdminView(AuthenticatedAdminView):
    """Admin view for Search History."""
    column_list = ['id', 'user', 'search_query', 'results_count', 'created_at']
    column_searchable_list = ['search_query']
    column_filters = ['created_at', 'user.username']
    column_sortable_list = ['created_at', 'results_count']
    can_delete = True
    can_edit = False  # Prevent editing search history


class ProductAdminView(AuthenticatedAdminView):
    """Admin view for Products."""
    column_list = ['id', 'product_name', 'source', 'price',
                   'discounted_price', 'search_query', 'created_at']
    column_searchable_list = ['product_name', 'search_query']
    column_filters = ['source', 'created_at']
    column_sortable_list = ['created_at', 'product_name']
    can_delete = True


class CustomAdminIndexView(AdminIndexView):
    """Custom admin home page."""

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login', next=request.url))


# Setup Flask-Admin
admin = Admin(app, name='Prize Comparison Admin',
              index_view=CustomAdminIndexView())
admin.add_view(UserAdminView(User, db.session, name='Users'))
admin.add_view(SearchHistoryAdminView(
    SearchHistory, db.session, name='Search History'))
admin.add_view(ProductAdminView(Product, db.session, name='Products'))


# ===== Authentication Routes =====

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        # Validation
        if not username or not email or not password:
            flash('All fields are required', 'error')
            return redirect(url_for('register'))

        if len(username) < 3:
            flash('Username must be at least 3 characters', 'error')
            return redirect(url_for('register'))

        if len(password) < 6:
            flash('Password must be at least 6 characters', 'error')
            return redirect(url_for('register'))

        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('register'))

        # Check if user exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('register'))

        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        remember = request.form.get('remember', False)

        if not username or not password:
            flash('Username and password are required', 'error')
            return redirect(url_for('login'))

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password) and user.is_active:
            login_user(user, remember=remember)
            flash(f'Welcome back, {user.username}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))

        flash('Invalid username or password', 'error')
        return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """User logout."""
    username = current_user.username
    logout_user()
    flash(f'You have been logged out. Goodbye, {username}!', 'info')
    return redirect(url_for('index'))


# ===== Main Routes =====

@app.route('/')
def index():
    """Home page - accessible to all."""
    return render_template('index.html')


@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard with search history."""
    page = request.args.get('page', 1, type=int)
    search_history = SearchHistory.query.filter_by(
        user_id=current_user.id
    ).order_by(SearchHistory.created_at.desc()).paginate(page=page, per_page=10)

    return render_template('dashboard.html', search_history=search_history)


# ===== API Routes =====

@app.route('/api/search', methods=['POST'])
@login_required
def search_products():
    """Search for products across all scrapers and track history."""
    try:
        data = request.get_json()
        product_name = data.get('product_name', '').strip()

        if not product_name:
            return jsonify({'error': 'Product name is required'}), 400

        results = []

        # Amazon scraper
        try:
            amazon = AmazonScraper(headless=True)
            amazon_products = amazon.scrape(product_name)
            for product in amazon_products:
                product['source'] = 'Amazon'
                results.append(product)
                # Store in database
                db_product = Product(
                    product_name=product.get('product_name'),
                    source='Amazon',
                    price=product.get('price'),
                    discounted_price=product.get('discounted_price'),
                    image_url=product.get('image_url'),
                    product_url=product.get('product_url'),
                    search_query=product_name
                )
                db.session.add(db_product)
        except Exception as e:
            print(f"Amazon scraper error: {e}")

        # Flipkart scraper
        try:
            flipkart = FlipkartScraper(headless=True)
            flipkart_products = flipkart.scrape(product_name)
            for product in flipkart_products:
                product['source'] = 'Flipkart'
                results.append(product)
                # Store in database
                db_product = Product(
                    product_name=product.get('product_name'),
                    source='Flipkart',
                    price=product.get('price'),
                    discounted_price=product.get('discounted_price'),
                    image_url=product.get('image_url'),
                    product_url=product.get('product_url'),
                    search_query=product_name
                )
                db.session.add(db_product)
        except Exception as e:
            print(f"Flipkart scraper error: {e}")

        db.session.commit()

        # Track search history
        search_history = SearchHistory(
            user_id=current_user.id,
            search_query=product_name,
            results_count=len(results),
            results_data=json.dumps(results)
        )
        db.session.add(search_history)
        db.session.commit()

        return jsonify({
            'success': True,
            'product_name': product_name,
            'results': results,
            'total': len(results),
            'search_id': search_history.id
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/search/<int:search_id>')
@login_required
def get_search_details(search_id):
    """Get details of a specific search."""
    search = SearchHistory.query.get(search_id)

    if not search:
        return jsonify({'error': 'Search not found'}), 404

    if search.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403

    try:
        results = json.loads(
            search.results_data) if search.results_data else []
    except:
        results = []

    return jsonify({
        'success': True,
        'search': search.to_dict(),
        'results': results
    })


@app.route('/api/products', methods=['GET'])
def get_products():
    """Get products (public endpoint)."""
    try:
        search_query = request.args.get('search_query', '')
        page = request.args.get('page', 1, type=int)

        query = Product.query
        if search_query:
            query = query.filter(
                Product.search_query.ilike(f'%{search_query}%'))

        products = query.order_by(Product.created_at.desc()).paginate(
            page=page, per_page=20)

        return jsonify({
            'success': True,
            'products': [product.to_dict() for product in products.items],
            'total': products.total,
            'pages': products.pages,
            'current_page': page
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get a specific product by ID."""
    try:
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'error': 'Product not found'}), 404

        return jsonify({
            'success': True,
            'product': product.to_dict()
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats')
def get_stats():
    """Get app statistics."""
    total_users = User.query.count()
    total_searches = SearchHistory.query.count()
    total_products = Product.query.count()

    return jsonify({
        'total_users': total_users,
        'total_searches': total_searches,
        'total_products': total_products
    })


# ===== Error Handlers =====

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
