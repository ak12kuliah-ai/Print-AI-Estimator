from flask import Flask, render_template, request, jsonify
from utils.ai_processing import process_document

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files: return jsonify({"error": "No file"}), 400
    file = request.files['file']
    if file.filename == '': return jsonify({"error": "No selected file"}), 400

    try:
        analysis_result = process_document(file, file.filename)
        final_data = []
        total_harga = 0
        
        HARGA_BW = 500
        HARGA_COLOR = 1000 
        
        # --- SETTING SENSITIVITAS ---
        # 0.5% adalah batas wajar.
        # Hyperlink biru biasanya cuma 0.05% - 0.2% dari halaman.
        # Logo kecil biasanya 1% - 5%.
        COLOR_THRESHOLD_PERCENT = 0.5 

        for item in analysis_result:
            data = item['analysis']
            coverage = data['total_color_coverage']
            
            # Logika Keputusan
            if coverage > COLOR_THRESHOLD_PERCENT:
                tipe = "Color"
                biaya = HARGA_COLOR
                alasan = f"Warna Terdeteksi ({coverage}%)"
            else:
                tipe = "BW"
                biaya = HARGA_BW
                if coverage > 0:
                    alasan = f"Warna Diabaikan ({coverage}% - Link/Noda)"
                else:
                    alasan = "Hitam Putih Murni"

            final_data.append({
                "page": item['page'],
                "tipe": tipe,
                "coverage": coverage,
                "details": data,
                "alasan": alasan,
                "biaya": biaya
            })
            total_harga += biaya

        return jsonify({
            "status": "success",
            "filename": file.filename,
            "total_biaya": total_harga,
            "detail": final_data
        })

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)