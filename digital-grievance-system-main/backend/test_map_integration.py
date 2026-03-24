from run import app

def test_map_integration():
    with app.test_client() as client:
        # Test complaint form access (should redirect to login)
        response = client.get('/citizen/submit')
        print('Complaint form status:', response.status_code)

        # Test with session
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['role'] = 'citizen'

        response = client.get('/citizen/submit')
        print('Complaint form with session status:', response.status_code)

        if response.status_code == 200:
            html = response.data.decode('utf-8')
            has_map = 'id="map"' in html
            has_leaflet = 'leaflet' in html.lower()
            has_lat_field = 'name="latitude"' in html
            has_lng_field = 'name="longitude"' in html
            print('Has map div:', has_map)
            print('Has Leaflet:', has_leaflet)
            print('Has latitude field:', has_lat_field)
            print('Has longitude field:', has_lng_field)

        # Test officer dashboard
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['role'] = 'officer'

        response = client.get('/officer/dashboard')
        print('Officer dashboard status:', response.status_code)

        if response.status_code == 200:
            html = response.data.decode('utf-8')
            has_complaints_map = 'id="complaints-map"' in html
            print('Has complaints map:', has_complaints_map)

if __name__ == '__main__':
    test_map_integration()