# Daily Location Tracking System - Implementation Guide

## Overview
The employee location tracking system has been enhanced to track a **maximum of 6 locations per day** with **day-wise summaries** showing total distance travelled and interactive route maps.

---

## System Architecture

### 1. Location Tracking Strategy

**Daily Location Limit: 6 Points Maximum**

1. **Check-In** (1st location) - When employee starts work
2. **Hourly Ping #1** (2nd location) - 1 hour after check-in
3. **Hourly Ping #2** (3rd location) - 2 hours after check-in
4. **Hourly Ping #3** (4th location) - 3 hours after check-in
5. **Hourly Ping #4** (5th location) - 4 hours after check-in
6. **Check-Out** (6th location) - When employee ends work

**Note:** After 4 hourly pings, automatic tracking stops. The final location is captured only at check-out.

---

## Database Models

### LocationTracking Model
**Purpose:** Store individual location pings

**Key Fields:**
- `user` - Employee reference
- `checkin` - Associated check-in session
- `ping_time` - Timestamp of location capture
- `latitude` / `longitude` - GPS coordinates
- `location_address` - Reverse geocoded address
- `ping_type` - Type: `checkin`, `hourly`, `checkout`, `recovery`
- `is_location_available` - Location availability status
- `coverage_gap_seconds` - Gap duration before this ping
- `accuracy` - GPS accuracy in meters
- `device_info` - Browser/Device details

**New Methods:**
```python
# Calculate distance between two GPS coordinates (Haversine formula)
LocationTracking.calculate_distance(lat1, lon1, lat2, lon2)  # Returns km

# Get all locations for a specific day
LocationTracking.get_daily_locations(user, date)

# Calculate total distance for a day
LocationTracking.calculate_daily_distance(user, date)
```

### DailyTravelSummary Model (NEW)
**Purpose:** Store aggregated day-wise travel data

**Key Fields:**
- `user` - Employee reference  
- `date` - Date of travel
- `total_distance_km` - Total distance travelled (calculated)
- `location_count` - Number of location pings (max 6)
- `first_ping_time` - Check-in time
- `last_ping_time` - Check-out time
- `work_duration_hours` - Total work hours
- `start_location` / `end_location` - Address strings
- `checkin` - Reference to CheckInOut session

**Key Methods:**
```python
# Generate or update daily summary for a date
summary = DailyTravelSummary.generate_summary(user, date)

# Get all location pings for this day
locations = summary.get_all_locations()

# Generate Google Maps route URL for the day
url = summary.get_maps_route_url()
```

---

## Views & URLs

### 1. Daily Travel Summary View
**URL:** `/travel/daily-summary/` or `/travel/daily-summary/<username>/`  
**Name:** `forms:daily_travel_summary`  
**Access:** MuktaParanjhpe + Superusers only

**Features:**
- Day-wise list of travel records
- Total distance per day displayed
- Date range filters (7, 15, 30, 60, 90, 120 days)
- Employee selector dropdown
- "View Route" button for each day
- Statistics: Total days, total distance, avg distance, total locations
- Pagination (20 records per page)

### 2. Day Route Map View
**URL:** `/travel/map/<username>/<date>/`  
**Name:** `forms:day_route_map`  
**Access:** MuktaParanjhpe + Superusers only

**Features:**
- Interactive map with Leaflet.js
- Shows all 6 locations with numbered markers
- Polyline connecting locations to show route
- Color-coded markers:
  - Green: Check-in
  - Purple: Hourly pings
  - Red: Check-out
- Location timeline with addresses and times
- Total distance and duration displayed

### 3. Enhanced Location Tracking
**JavaScript Changes in `checkin.html`:**
```javascript
let hourlyPingCount = 0;  // Track pings sent
const MAX_HOURLY_PINGS = 4;  // Maximum 4 hourly pings

function startLocationTracking() {
    hourlyPingCount = 0;  // Reset on check-in
    
    locationInterval = setInterval(function() {
        if (hourlyPingCount >= MAX_HOURLY_PINGS) {
            console.log('Maximum hourly pings reached');
            stopLocationTracking();
            return;
        }
        
        recordLocationPing('hourly');
        hourlyPingCount++;
    }, 3600000);  // Every 1 hour
}
```

### 4. Automatic Summary Generation
**On Check-Out:**
```python
# In checkout_submit view
DailyTravelSummary.generate_summary(request.user, checkin.date)
```
This automatically calculates and stores the day's travel summary when employee checks out.

---

## Admin Interface

### CheckInOut Admin
- List display: Employee, Date, Check-in/out times, Duration, Status
- Filters: Date, User
- Search: Username, Location addresses
- Date hierarchy by date

### LocationTracking Admin
- List display: Employee, Time, Type, Location status, Address, Accuracy
- Filters: Type, Availability, Time, User
- Search: Username, Address
- Date hierarchy by ping time
- View on Maps link for each location

### DailyTravelSummary Admin
- List display: Employee, Date, Distance, Locations, Duration, View Route
- Filters: Date, User
- Search: Username, Locations
- Date hierarchy by date
- **Custom Action:** "Regenerate selected summaries" - Recalculates distance and updates summary

---

## Usage Workflow

### For Employees:
1. **Check-In:**
   - Go to Check-In page
   - Allow location access
   - Click "Check In" button
   - System records location #1

2. **During Work:**
   - System automatically records location every hour (max 4 pings)
   - No action needed from employee

3. **Check-Out:**
   - Click "Check Out" button
   - System records location #6
   - Daily summary is automatically generated

### For Managers (MuktaParanjhpe/Superusers):
1. **View Daily Summary:**
   - Navigate to "Daily Travel Summary" from check-in page
   - Select employee from dropdown
   - Choose date range
   - View day-wise list with distances

2. **View Route Map:**
   - Click "View Route" button for any day
   - See interactive map with all 6 locations
   - View polyline showing travel route
   - See location timeline with times

3. **Export/Reports:**
   - Use admin interface to export daily summaries
   - Regenerate summaries if needed using admin action

---

## Distance Calculation

**Haversine Formula Implementation:**
```python
def calculate_distance(lat1, lon1, lat2, lon2):
    # Convert coordinates to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    # Earth radius = 6371 km
    distance = 6371.0 * c
    return round(distance, 2)  # Returns kilometers
```

**Total Distance Calculation:**
- Sum of distances between consecutive location points
- Example: If locations are L1, L2, L3, L4, L5, L6:
  - Total Distance = dist(L1→L2) + dist(L2→L3) + dist(L3→L4) + dist(L4→L5) + dist(L5→L6)

---

## Data Retention

- **LocationTracking:** 4 months (120 days)
- **DailyTravelSummary:** Permanent (or as per policy)
- Old location pings auto-deleted via cleanup method

---

## Migration Applied

**Migration:** `0041_dailytravelsummary.py`

**Changes:**
- Created `daily_travel_summary` table
- Added indexes on (user, date) and (date)
- Unique constraint on (user, date)

---

## Files Modified/Created

### Models:
- ✅ `forms/models.py` - Added DailyTravelSummary, distance calculation methods

### Views:
- ✅ `forms/views.py` - Added daily_travel_summary_view, day_route_map_view
- ✅ `forms/views.py` - Updated checkout_submit to generate summary

### URLs:
- ✅ `forms/urls.py` - Added routes for summary and map views

### Templates:
- ✅ `forms/templates/forms/daily_travel_summary.html` - Day-wise list view
- ✅ `forms/templates/forms/day_route_map.html` - Interactive map view
- ✅ `forms/templates/forms/checkin.html` - Added 4-ping limit, new navigation link

### Admin:
- ✅ `forms/admin.py` - Registered new models with custom admin classes

---

## Testing Checklist

- [ ] Check-in records location
- [ ] Hourly pings recorded (max 4)
- [ ] Check-out records final location
- [ ] Daily summary generated on check-out
- [ ] Distance calculated correctly
- [ ] Map shows all locations with route
- [ ] Admin interface accessible
- [ ] Access control working (MuktaParanjhpe/superuser only)
- [ ] Pagination working
- [ ] Filters working (employee, date range)

---

## Troubleshooting

**Issue:** Locations not recording
- Check browser location permissions
- Verify HTTPS connection (required for geolocation API)
- Check browser console for errors

**Issue:** Distance showing as 0
- Ensure all locations have valid lat/lng coordinates
- Check if minimum 2 locations recorded for the day
- Regenerate summary from admin if needed

**Issue:** Map not displaying
- Verify Leaflet.js CDN is accessible
- Check browser console for JavaScript errors
- Ensure location data passed correctly from view

**Issue:** Summary not generating
- Check if employee checked out (summary only generates on checkout)
- Manually generate from admin using "Regenerate summaries" action
- Verify LocationTracking records exist for that day

---

## Future Enhancements (Optional)

1. **Geofencing:** Alert if employee goes outside designated area
2. **Route Optimization:** Suggest optimal routes between points
3. **Offline Support:** Cache locations when offline, sync later
4. **Export to PDF:** Generate printable travel reports
5. **SMS Alerts:** Notify manager of coverage gaps
6. **Mobile App:** Native Android/iOS app with background tracking
7. **Analytics Dashboard:** Charts showing travel patterns, trends

---

## API Endpoints

### Save Location Ping
```
POST /api/location/ping/
Content-Type: application/json

{
  "ping_type": "hourly",
  "latitude": 28.6139,
  "longitude": 77.2090,
  "location": "Connaught Place, New Delhi",
  "accuracy": 10.5,
  "device_info": "Chrome/Windows",
  "coverage_gap_seconds": 0
}
```

**Response:**
```json
{
  "success": true,
  "message": "Location ping saved successfully",
  "ping_id": 123,
  "ping_time": "02:30 PM",
  "is_available": true
}
```

---

## Performance Optimization

1. **Indexes:** Added on frequently queried fields (user, date, ping_time)
2. **Select Related:** Views use select_related to reduce database queries
3. **Pagination:** Large datasets paginated (20-50 per page)
4. **Caching:** Consider adding Redis cache for summary statistics

---

## Security Considerations

1. **Access Control:** Only authorized users can view travel data
2. **CSRF Protection:** All forms include CSRF tokens
3. **SQL Injection:** Using Django ORM prevents SQL injection
4. **XSS Protection:** All user inputs escaped in templates
5. **HTTPS:** Required for geolocation API

---

## Support & Maintenance

**Contact:** System Administrator / IT Department  
**Documentation Version:** 1.0  
**Last Updated:** February 2026

---

**End of Documentation**
