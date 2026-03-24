# Quick Start Guide for Smart Civic Grievance System

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

## Installation Steps

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Navigate to Backend
```bash
cd backend
```

### 3. Run the Application
```bash
python run.py
```

You should see:
```
Database initialized!
 * Running on http://127.0.0.1:5000
```

### 4. Access the Application
Open your browser and go to:
```
http://127.0.0.1:5000
```

## Creating Test Accounts

### Method 1: Using Registration Page
1. Visit `http://127.0.0.1:5000/register`
2. Fill in the form with:
   - Full Name
   - Email
   - Password
   - Select Role (Citizen, Officer, or Worker)
3. Click Register

### Method 2: Test Flow

**Create Citizen Account:**
- Name: John Citizen
- Email: citizen@example.com
- Password: password123
- Role: Citizen

**Create Officer Account:**
- Name: Jane Officer
- Email: officer@example.com
- Password: password123
- Role: Officer

**Create Worker Account:**
- Name: Bob Worker
- Email: worker@example.com
- Password: password123
- Role: Worker

## Testing Workflow

### As Citizen:
1. Login with citizen account
2. Click "New Complaint" on dashboard
3. Fill complaint form (at least one complaint required)
4. Submit complaint
5. View complaint status on dashboard

### As Officer:
1. Login with officer account
2. View all complaints on dashboard
3. Use filters to filter by category and status
4. Click "Eye" icon to view complaint details
5. Use dropdown to assign to a worker
6. Use select to update complaint status

### As Worker:
1. Login with worker account
2. View assigned complaints
3. Update status to "In Progress" or "Resolved"
4. Optionally upload completion photo
5. Click Update

## Features Overview

### Dashboard Features
- **Citizen**: View complaints, check status, submit new
- **Officer**: Manage all complaints, filter, assign, update status
- **Worker**: View and update assigned complaints

### Complaint Lifecycle
```
Pending → Assigned → In Progress → Resolved
```

### Categories Available
- Roads
- Garbage
- Water
- Electricity
- Streetlights
- Drainage

## Database

SQLite database (`database.db`) is automatically created in the `backend/` directory on first run.

Tables created:
- `user`: User accounts and authentication
- `complaint`: Citizen complaints
- `assignment`: Worker assignments

## Troubleshooting

### Port Already in Use
If port 5000 is already in use, modify `backend/run.py`:
```python
app.run(debug=True, port=5001)  # Change 5000 to another port
```

### Database Issues
To reset the database, delete `backend/database.db` and restart the application.

### Import Errors
Make sure you're in the correct directory:
```bash
cd backend
python run.py
```

## File Upload

- Supported formats: PNG, JPG, JPEG, GIF
- Maximum file size: Adjustable in `citizen_routes.py`
- Upload location: `app/static/uploads/`

## Security Notes

⚠️ **Important**: Before deploying to production:
1. Change `SECRET_KEY` in `backend/run.py`
2. Set `debug=False` in `backend/run.py`
3. Use a production database (PostgreSQL recommended)
4. Configure proper session handling
5. Enable HTTPS

## Project Structure
```
grievance-system/
├── backend/
│   ├── auth.py              # Authentication routes
│   ├── citizen_routes.py    # Citizen dashboard & complaint submission
│   ├── officer_routes.py    # Officer dashboard & management
│   ├── worker_routes.py     # Worker dashboard & updates
│   ├── models.py            # Database models
│   ├── routes.py            # Main routes
│   ├── run.py               # Application entry point
│   └── database.db          # SQLite database (auto-created)
├── app/
│   ├── templates/           # HTML templates
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── citizen_dashboard.html
│   │   ├── officer_dashboard.html
│   │   ├── worker_dashboard.html
│   │   ├── complaint_form.html
│   │   └── complaint_details.html
│   └── static/
│       ├── css/style.css
│       ├── js/script.js
│       └── uploads/         # User-uploaded images
├── requirements.txt
├── README.md
└── QUICKSTART.md
```

## Tips

1. Use responsive design - test on mobile devices
2. Refresh browser if styles not loading
3. Check browser console for JavaScript errors
4. Use browser developer tools for debugging

## Support

For issues or questions, refer to README.md or check the code comments in the respective route files.

Enjoy using the Smart Civic Grievance System!
