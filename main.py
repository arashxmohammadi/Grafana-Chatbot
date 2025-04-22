from fastapi import FastAPI, HTTPException, Depends, Request, Form
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from datetime import datetime, timedelta
import requests
import os
from dotenv import load_dotenv

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Load environment variables
load_dotenv()

# Grafana configuration
GRAFANA_URL = os.getenv('GRAFANA_URL', 'http://localhost:3000')
GRAFANA_API_KEY = os.getenv('GRAFANA_API_KEY')

class GrafanaAPI:
    def __init__(self):
        self.base_url = GRAFANA_URL
        self.headers = {
            'Authorization': f'Bearer {GRAFANA_API_KEY}',
            'Content-Type': 'application/json'
        }

    def _check_auth(self):
        if not GRAFANA_API_KEY:
            raise HTTPException(status_code=401, detail='Grafana API key not configured')

    def search_dashboards(self, query):
        self._check_auth()
        # Define common metric aliases with expanded terms
        metric_aliases = {
            'cpu': ['cpu', 'processor', 'cpu utilization', 'cpu usage', 'processor usage', 'core', 'load', 'processing'],
            'memory': ['memory', 'mem', 'ram', 'memory usage', 'swap', 'heap', 'buffer', 'cache'],
            'disk': ['disk', 'storage', 'disk usage', 'disk utilization', 'io', 'filesystem', 'volume', 'partition', 'drive'],
            'network': ['network', 'net', 'network usage', 'bandwidth', 'interface', 'traffic', 'throughput', 'connection', 'packet', 'network traffic', 'network io', 'network throughput', 'network bandwidth', 'network utilization', 'network performance', 'network stats', 'network metrics', 'network monitoring', 'network analysis', 'network load', 'network speed', 'network data', 'network transfer', 'network flow', 'network usage', 'network activity', 'network statistics', 'network measurement', 'network rate', 'eth', 'ethernet', 'interface traffic', 'bytes sent', 'bytes received', 'packets sent', 'packets received', 'network errors', 'network drops', 'network collisions'],
            'ubuntu': ['ubuntu', 'vm', 'ubuntu-vm', 'virtual machine', 'linux', 'system', 'host', 'server', 'instance']
        }
        

        
        # Normalize query
        query_lower = query.lower()
        
        # Check if query matches any aliases
        search_terms = [query]
        for category, aliases in metric_aliases.items():
            if any(term in query_lower for term in aliases):
                search_terms.extend([category, f"{category} usage", f"{category} utilization"])
        
        # Include the specific Ubuntu VM dashboard
        ubuntu_vm_dashboard = {
            'uid': 'fejd03chh2ozkb',
            'title': 'Ubuntu VM Dashboard',
            'url': '/d/fejd03chh2ozkb/ubuntu-vm'
        }
        
        # Start with the Ubuntu VM dashboard if query matches
        results = []
        if any(term in query_lower for term in metric_aliases['ubuntu']):
            results.append(ubuntu_vm_dashboard)
        
        # Search for additional matching dashboards
        for term in search_terms:
            endpoint = f"{self.base_url}/api/search"
            params = {'query': term}
            response = requests.get(endpoint, headers=self.headers, params=params)
            if response.status_code == 401:
                raise HTTPException(status_code=401, detail='Unauthorized access to Grafana API')
            elif response.status_code == 200:
                results.extend(response.json())
            else:
                raise HTTPException(status_code=response.status_code, detail=f'Grafana API error: {response.text}')
        
        # Remove duplicates based on uid
        seen = set()
        unique_results = []
        for item in results:
            if item['uid'] not in seen:
                seen.add(item['uid'])
                unique_results.append(item)
        
        return unique_results

    def get_dashboard(self, uid):
        self._check_auth()
        endpoint = f"{self.base_url}/api/dashboards/uid/{uid}"
        response = requests.get(endpoint, headers=self.headers)
        if response.status_code == 401:
            raise HTTPException(status_code=401, detail='Unauthorized access to Grafana API')
        elif response.status_code == 200:
            return response.json()
        raise HTTPException(status_code=response.status_code, detail=f'Failed to get dashboard: {response.text}')

    def get_panel_image(self, dashboard_uid, panel_id, time_range):
        self._check_auth()
        endpoint = f"{self.base_url}/render/d-solo/{dashboard_uid}"
        params = {
            'panelId': panel_id,
            'from': time_range['from'],
            'to': time_range['to'],
            'width': 800,
            'height': 400
        }
        response = requests.get(endpoint, headers=self.headers, params=params)
        if response.status_code == 401:
            raise HTTPException(status_code=401, detail='Unauthorized access to Grafana API')
        elif response.status_code == 200:
            return response.content
        raise HTTPException(status_code=response.status_code, detail=f'Failed to get panel image: {response.text}')

grafana = GrafanaAPI()

@app.get('/', response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

@app.post('/search')
async def search_graphs(query: str = Form(...), time_from: str = Form(None), time_to: str = Form(None)):
    try:
        # Validate query
        if not query or not query.strip():
            raise HTTPException(status_code=400, detail='Search query cannot be empty')
            
        # Search for dashboards matching the query
        try:
            dashboards = grafana.search_dashboards(query)
        except requests.exceptions.RequestException as e:
            print(f"Grafana API Error: {str(e)}")
            raise HTTPException(status_code=502, detail='Failed to connect to Grafana API')
        
        # Process time range
        if not time_from:
            # Extract time range from query
            import re
            time_match = re.search(r'(?:last|past)\s*(\d+)\s*([hdwmy])', query.lower())
            if time_match:
                value, unit = time_match.groups()
                # Convert units to proper format
                unit_map = {'h': 'h', 'd': 'd', 'w': 'w', 'm': 'm', 'y': 'y'}
                time_from = f'now-{value}{unit_map[unit]}'
            else:
                time_from = 'now-6h'  # Default to last 6 hours if no time specified
        
        if not time_to:
            time_to = 'now'

        # Normalize query for matching
        query_terms = query.lower().split()
        
        results = []
        for dashboard in dashboards:
            dashboard_data = grafana.get_dashboard(dashboard['uid'])
            if 'dashboard' in dashboard_data:
                for panel in dashboard_data['dashboard'].get('panels', []):
                    panel_title = panel.get('title', '').lower()
                    panel_description = panel.get('description', '').lower()
                    panel_targets = [target.get('expr', '').lower() for target in panel.get('targets', [])]
                    
                    # Check if query terms match title, description, or targets
                    matches_query = any(
                        term in panel_title or 
                        term in panel_description or
                        any(term in target for target in panel_targets)
                        for term in query_terms
                    )
                    
                    # Only include panels that match the query
                    if matches_query:
                        results.append({
                            'dashboard_uid': dashboard['uid'],
                            'panel_id': panel['id'],
                            'title': panel['title'],
                            'time_range': {'from': time_from, 'to': time_to}
                        })

        return {'results': results}
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Unexpected error in search_graphs: {str(e)}")
        raise HTTPException(status_code=500, detail='Internal server error occurred')

@app.get('/render/{dashboard_uid}/{panel_id}')
async def render_panel(dashboard_uid: str, panel_id: int, time_from: str = 'now-6h', time_to: str = 'now'):
    try:
        image_data = grafana.get_panel_image(
            dashboard_uid,
            panel_id,
            {'from': time_from, 'to': time_to}
        )
        return Response(content=image_data, media_type='image/png')
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Unexpected error in search_graphs: {str(e)}")
        raise HTTPException(status_code=500, detail='Internal server error occurred')

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)