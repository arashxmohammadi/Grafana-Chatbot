# Grafana Chat Bot

A Python-based chatbot that connects to Grafana for searching graphs and KPIs, with customizable time ranges.

## Setup Instructions

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure Grafana Connection:
   - Open `.env` file
   - Set your Grafana server URL (default: http://localhost:3000)
   - Add your Grafana API key

   To generate a Grafana API key:
   - Log into your Grafana instance
   - Go to Configuration > API Keys
   - Create a new API key with "Admin" role
   - Copy the generated key to `.env` file

3. Start the server:
   ```bash
   python main.py
   ```

## API Endpoints

- `GET /`: Health check endpoint
- `POST /search`: Search for graphs and KPIs
  - Parameters:
    - `query`: Search term
    - `time_from`: Start time (optional, default: now-6h)
    - `time_to`: End time (optional, default: now)
- `GET /render/{dashboard_uid}/{panel_id}`: Render panel image
  - Parameters:
    - `dashboard_uid`: Dashboard UID
    - `panel_id`: Panel ID
    - `time_from`: Start time (optional)
    - `time_to`: End time (optional)

## Time Range Formats

Supported time range formats:
- Relative: `now-6h`, `now-1d`, `now-1w`
- Absolute: `2023-01-01`, `2023-01-01 13:00:00`

## Example Usage

1. Search for CPU metrics:
   ```bash
   curl -X POST "http://localhost:8000/search" \
     -F "query=CPU" \
     -F "time_from=now-1h" \
     -F "time_to=now"
   ```

2. Render a specific panel:
   ```bash
   curl "http://localhost:8000/render/{dashboard_uid}/{panel_id}?time_from=now-1h&time_to=now"
   ```