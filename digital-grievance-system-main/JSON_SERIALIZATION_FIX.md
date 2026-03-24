# JSON Serialization Fix for Complaint Objects

## Problem
Error: `TypeError: Object of type Complaint is not JSON serializable`

### Root Cause
SQLAlchemy model objects cannot be directly serialized to JSON. When the template tries to use the `tojson` filter on a list of Complaint objects, it fails because SQLAlchemy objects lack JSON serialization support.

**Affected Template:**
- `app/templates/officer_dashboard.html` (Line 400)

**Affected Code:**
```python
# In officer_routes.py - before fix
complaints = Complaint.query.filter_by(...).all()  # SQLAlchemy objects
return render_template('officer_dashboard.html', complaints=complaints)

# In template - causes error
const complaints = {{ complaints | tojson }};  // Can't serialize SQLAlchemy object
```

---

## Solution

### 1. Added `to_dict()` Method to Complaint Model (models.py)

**Location:** Line 74-96 in `models.py`

```python
def to_dict(self):
    """Convert complaint to JSON-serializable dictionary"""
    return {
        'id': self.id,
        'user_id': self.user_id,
        'title': self.title,
        'description': self.description,
        'category': self.category,
        'location': self.location,
        'location_link': self.location_link,
        'latitude': self.latitude,
        'longitude': self.longitude,
        'image_path': self.image_path,
        'estimated_resolution_days': self.estimated_resolution_days,
        'status': self.status,
        'priority': self.priority,
        'worker_name': self.worker_name,
        'worker_contact': self.worker_contact,
        'estimated_resolution_time': self.estimated_resolution_time,
        'assigned_officer': self.assigned_officer,
        'escalation_level': self.escalation_level,
        'last_updated': self.last_updated.isoformat() if self.last_updated else None,
        'created_at': self.created_at.isoformat() if self.created_at else None,
        'deadline': self.deadline.isoformat() if self.deadline else None
    }
```

**Key Features:**
- All 21 fields converted to JSON-compatible types
- DateTime objects converted to ISO format strings (JSON serializable)
- None values handled properly
- No modifications to database structure

### 2. Updated Officer Dashboard Route (officer_routes.py)

**Location:** Lines 85-99 in `officer_routes.py`

**Before:**
```python
return render_template('officer_dashboard.html', 
                     complaints=complaints,  # SQLAlchemy objects
                     ...)
```

**After:**
```python
# Convert complaints to JSON-serializable dictionaries
complaints_dict = [c.to_dict() for c in complaints]

return render_template('officer_dashboard.html', 
                     complaints=complaints_dict,  # Plain Python dicts
                     ...)
```

**What Changed:**
- Added 2 lines to convert SQLAlchemy objects to dictionaries
- Template now receives pure Python dictionaries instead of ORM objects
- All JSON filters in templates now work without errors

---

## Benefits

✓ **No More TypeError** - Complaints can now be serialized  
✓ **Template Safety** - `tojson` filter works correctly  
✓ **Data Consistency** - All 21 fields included in serialization  
✓ **DateTime Handling** - Properly converts dates to ISO format strings  
✓ **ORM Compatibility** - Works with any SQLAlchemy version  
✓ **Scalability** - Easy to apply to other models if needed  

---

## Files Modified

1. **models.py** - Added `to_dict()` method to Complaint class
2. **officer_routes.py** - Convert complaints to dicts before template rendering

---

## Testing

### Test Results
All tests passed successfully:

```
✓ Complaint.to_dict() converts SQLAlchemy objects to dicts
✓ All fields are JSON-serializable (including datetime)
✓ Officer dashboard can convert complaints safely
✓ Templates can use tojson filter without errors
✓ Officer dashboard has all required fields
✓ JavaScript can parse the JSON output
```

### Test Command
```bash
python test_json_serialization.py
```

---

## Affected Endpoints

### Officer Dashboard
- **Route:** `/officer/dashboard`
- **Template:** `app/templates/officer_dashboard.html`
- **JavaScript Usage:** Maps, charts, data visualization
- **Status:** ✓ Fixed

### Other Routes
- **Citizen Dashboard:** Uses template filters only (not affected)
- **Admin Dashboard:** Uses Python iteration only (not affected)

---

## How the Fix Works

### Before (Error):
```
Complaint Object
     ↓
render_template()  ← OK (Python)
     ↓
Template (HTML)
     ↓
{{ complaints | tojson }}  ← ERROR! Can't serialize SQLAlchemy object
```

### After (Fixed):
```
Complaint Object
     ↓
to_dict() method
     ↓
Plain Python Dict
     ↓
render_template()  ← OK (Python)
     ↓
Template (HTML)
     ↓
{{ complaints | tojson }}  ← SUCCESS! Dictionary is JSON serializable
     ↓
JavaScript receives valid JSON
```

---

## Integration with Templates

The template code remains unchanged:

```html
<script>
    const complaints = {{ complaints | tojson }};
    
    complaints.forEach(function (complaint) {
        if (complaint.latitude && complaint.longitude) {
            // Add marker on map
            L.marker([complaint.latitude, complaint.longitude])
        }
    });
</script>
```

Now works because:
- `complaints` is a list of plain dictionaries
- Each dictionary has all required fields (id, latitude, longitude, etc.)
- JSON serialization of dictionaries always succeeds
- JavaScript receives valid JSON array

---

## Best Practices

### For Similar Issues
If other models need JSON serialization:

```python
class MyModel(db.Model):
    def to_dict(self):
        return {
            'field1': self.field1,
            'field2': self.field2,
            'date_field': self.date_field.isoformat() if self.date_field else None,
        }
```

### In Routes
```python
# Convert objects before template rendering
objects = MyModel.query.all()
objects_dict = [o.to_dict() for o in objects]
return render_template('template.html', objects=objects_dict)
```

---

## Backward Compatibility

✓ **No Breaking Changes**
- Database schema unchanged
- Model structure unchanged
- Template HTML unchanged
- No function signatures changed
- Other routes unaffected

✓ **Fully Backward Compatible**
- Existing complaints still work
- Historical data unaffected
- No migrations needed

---

## Summary

The JSON serialization error has been completely resolved by:
1. Adding a `to_dict()` method to convert SQLAlchemy Complaint objects to dictionaries
2. Converting complaints to dictionaries in the officer_routes dashboard before template rendering
3. Ensuring all datetime fields are properly serialized to ISO format strings

The fix is minimal, non-invasive, and allows the template's `tojson` filter to work correctly without any errors.

---
