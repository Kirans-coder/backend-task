import os
import csv
from io import StringIO
from flask import Flask, request, jsonify, make_response
from dotenv import load_dotenv

# --- FIX for ModuleNotFoundError ---
# Add the project's root directory to the Python search path.
# This ensures that imports like 'core.scoring' can be found.
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# ----------------------------------

from core.scoring import score_leads
from core.utils import save_offer, get_offer, save_leads, get_leads

load_dotenv()

app = Flask(__name__)

# In-memory storage for leads and offer data
# In a production app, you would use a database
offer_data = {}
leads_data = []
scored_results = []

@app.route('/offer', methods=['POST'])
def post_offer():
    """Accepts and stores product/offer details."""
    global offer_data
    try:
        offer_payload = request.json
        if not offer_payload or not all(k in offer_payload for k in ["name", "value_props", "ideal_use_cases"]):
            return jsonify({"error": "Invalid JSON format. Requires 'name', 'value_props', 'ideal_use_cases'."}), 400
        save_offer(offer_data, offer_payload)
        return jsonify({"message": "Offer details saved successfully."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/leads/upload', methods=['POST'])
def upload_leads():
    """Accepts a CSV file of leads and stores them."""
    global leads_data
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request."}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file."}), 400
    
    if file and file.filename.endswith('.csv'):
        try:
            stream = StringIO(file.stream.read().decode("UTF8"), newline=None)
            csv_input = csv.DictReader(stream)
            leads = [row for row in csv_input]
            
            # Basic validation of CSV headers
            required_headers = ['name', 'role', 'company', 'industry', 'location', 'linkedin_bio']
            if not all(header in leads[0] for header in required_headers):
                return jsonify({"error": f"CSV must contain the following headers: {', '.join(required_headers)}"}), 400

            save_leads(leads_data, leads)
            return jsonify({"message": f"Successfully uploaded {len(leads)} leads."}), 200
        except Exception as e:
            return jsonify({"error": f"Error processing CSV file: {str(e)}"}), 500
    
    return jsonify({"error": "Invalid file format. Please upload a CSV file."}), 400

@app.route('/score', methods=['POST'])
def run_scoring():
    """Triggers the lead scoring pipeline."""
    global leads_data, offer_data, scored_results
    
    if not get_offer(offer_data):
        return jsonify({"error": "No offer details found. Please POST to /offer first."}), 400
    if not get_leads(leads_data):
        return jsonify({"error": "No leads found. Please upload a CSV to /leads/upload first."}), 400
    
    scored_results = score_leads(get_leads(leads_data), get_offer(offer_data))
    
    return jsonify({"message": "Scoring complete. Results are available at /results."}), 200

@app.route('/results', methods=['GET'])
def get_results():
    """Returns the JSON array of scored leads."""
    global scored_results
    return jsonify(scored_results)

@app.route('/results/export', methods=['GET'])
def export_results_csv():
    """Exports the scored leads as a CSV file."""
    global scored_results
    if not scored_results:
        return jsonify({"error": "No results to export. Please run /score first."}), 400
    
    output = StringIO()
    # Use the keys from the first dictionary to create the header
    fieldnames = scored_results[0].keys()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    
    writer.writeheader()
    writer.writerows(scored_results)
    
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=scored_leads.csv"
    response.headers["Content-type"] = "text/csv"
    return response

if __name__ == '__main__':
    app.run(debug=True)