# Data Warehouse API

A comprehensive Flask-based REST API for managing insurance data warehouse operations including users, quotes, policies, and payment transactions.

## 🏗️ Architecture

This project follows a clean, modular architecture with clear separation of concerns:

```
warehouse/
├── 📁 app/                          # Main application package
│   ├── __init__.py                  # Flask app factory
│   ├── config.py                    # Configuration settings
│   ├── 📁 models/                   # Database models
│   ├── 📁 api/                      # API layer (schemas & resources)
│   ├── 📁 services/                 # Business logic layer
│   └── 📁 utils/                    # Utility functions
├── 📁 scripts/                      # Management scripts
├── 📁 tests/                        # Test suite
├── 📁 docs/                         # Documentation
├── 📁 data/                         # Data files & backups
└── app.py                           # Application entry point
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip or pipenv

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd warehouse
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment (optional)**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Initialize the database**
   ```bash
   python -c "from app import create_app; app = create_app(); app.app_context().push(); from app.models import db; db.create_all()"
   ```

5. **Seed with sample data (optional)**
   ```bash
   python scripts/seed_data.py
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

The API will be available at `http://localhost:25000` with Swagger documentation at `http://localhost:25000/swagger/`.

## 📊 API Endpoints

### Users
- `GET /api/v1/users/` - List all users
- `POST /api/v1/users/` - Create a new user
- `GET /api/v1/users/{id}` - Get user by ID
- `PUT /api/v1/users/{id}` - Update user
- `DELETE /api/v1/users/{id}` - Delete user

### Quotes
- `GET /api/v1/quotes/` - List all quotes
- `POST /api/v1/quotes/` - Create a new quote
- `GET /api/v1/quotes/{id}` - Get quote by ID
- `PATCH /api/v1/quotes/{id}` - Bind a quote

### Policies
- `GET /api/v1/policies/` - List all policies
- `POST /api/v1/policies/` - Create a new policy
- `GET /api/v1/policies/{id}` - Get policy by ID

### Payments
- `GET /api/v1/payments/` - List all payment transactions
- `POST /api/v1/payments/` - Create a new payment transaction
- `GET /api/v1/payments/{id}` - Get payment by ID

### Analytics
- `GET /api/v1/analytics/stats` - General statistics
- `GET /api/v1/analytics/payment-stats` - Payment statistics by type
- `GET /api/v1/analytics/user-stats` - User-related statistics

## 🧪 Testing

### Run all tests
```bash
pytest
```

### Run specific test categories
```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# With coverage
pytest --cov=app tests/
```

### Test Structure
- **Unit Tests**: Test individual components (models, services, utilities)
- **Integration Tests**: Test API endpoints and database interactions
- **Fixtures**: Reusable test data in `tests/conftest.py`

## 🛠️ Development

### Project Structure

#### Models (`app/models/`)
Database models with SQLAlchemy ORM:
- `User`: Customer information
- `Quote`: Insurance quotes
- `Policy`: Insurance policies
- `PaymentTransaction`: Payment attempts

#### Services (`app/services/`)
Business logic layer:
- `UserService`: User management operations
- `QuoteService`: Quote creation and binding
- `PolicyService`: Policy management
- `PaymentService`: Payment processing
- `AnalyticsService`: Statistics and reporting

#### API Layer (`app/api/`)
- `schemas.py`: Request/response validation schemas
- `resources/`: API endpoint implementations

#### Configuration (`app/config.py`)
Environment-based configuration with support for:
- Development
- Testing  
- Production

### Scripts (`scripts/`)

#### Database Backup
```bash
# Create backup
python scripts/backup_db.py backup

# List backups
python scripts/backup_db.py list

# Restore from backup
python scripts/backup_db.py restore <backup_file>
```

#### Seed Data
```bash
# Add sample data
python scripts/seed_data.py

# Clear existing data and reseed
python scripts/seed_data.py --clear
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Environment (development/testing/production) | `development` |
| `SECRET_KEY` | Flask secret key | `dev-secret-key-change-in-production` |
| `DATABASE_PATH` | Database file path | `data/data_warehouse.db` |
| `BACKUP_DIR` | Backup directory | `data/backups` |
| `MAX_BACKUPS` | Maximum backups to keep | `10` |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `25000` |

## 📈 Data Flow

1. **Users** are created in the system
2. **Quotes** are generated for users
3. Quotes can be **bound** when ready
4. **Policies** are created from bound quotes
5. **Payment transactions** are processed for policies
6. **Analytics** provide insights across all data

## 🔧 Utilities

### Database Operations
- Backup and restore functionality
- Database initialization and recreation
- Automatic cleanup of old backups

### Validation
- Email format validation
- Name format validation
- Input sanitization
- Type validation

## 📚 Documentation

Additional documentation is available in the `docs/` folder:
- [Database Management](docs/README_DATABASE_MANAGEMENT.md)
- [Backup & Restore](docs/README_BACKUP_RESTORE.md)
- [Migrations](docs/README_MIGRATIONS.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For questions or issues:
1. Check the documentation in the `docs/` folder
2. Review the API documentation at `/swagger/`
3. Run tests to ensure everything is working
4. Create an issue in the repository
