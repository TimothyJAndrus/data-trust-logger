import requests

def _get_endpoint_status(api_ep: str):
    try:
        response = requests.get(ap_ep)
        status = response.status_code
    except Exception:
        # TODO: Is this the best error?
        status = 'API error'
    
    return status

def _get_endpoint_record_count(engine, endpoint: str):
    try:
        result = engine.execute(f"SELECT COUNT(*) from {endpoint}")
        count, = result.fetchone()
    except Exception:
        # TODO: Is this the best error?
        count = "Database error"
    
    return count

def generate_endpoints_blob(engine, api_url: str, endpoints: list, mappings={}):
    endpoints_blob = {'endpoints': []}
    for endpoint in endpoints:
        try:
            tablename = mappings[endpoint]
        except KeyError:
            tablename = endpoint
        
        status = _get_endpoint_status(f"{api_url}/{endpoint}")
        count = _get_endpoint_record_count(engine, tablename)
        
        endpoints_blob['endpoints'].append({
            'endpoint': endpoint,
            'record_count': count,
            'endpoint_health': status
        })
    
    return endpoints_blob