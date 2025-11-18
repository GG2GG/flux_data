from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/run_demo", methods=['POST'])
def run_demo():
    print("--- API CALL RECEIVED ---")
    data = request.json
    print(f"Category: {data.get('category')}")
    print(f"Row: {data.get('row')}")
    print("--- RUNNING FLUX_DATA DEMO (SIMULATED) ---")

    # This is where you would call your flux_data.demo.run()

    print("--- DEMO COMPLETE ---")
    return jsonify({"status": "success", "message": "Demo ran successfully"}), 200

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8000, debug=True)
