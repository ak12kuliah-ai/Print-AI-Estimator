import fitz  # PyMuPDF
from PIL import Image
import io
import numpy as np

def analyze_color_presence(image_bytes):
    """
    Mendeteksi apakah piksel itu berwarna atau grayscale berdasarkan selisih RGB.
    - Text Hitam = RGB values mirip (R=G=B), selisih rendah -> Dianggap BW
    - Link Biru/Gambar = RGB values timpang, selisih tinggi -> Dianggap Color
    """
    try:
        # 1. Buka Gambar & Resize (Ukuran sedang agar cepat tapi akurat)
        img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        img = img.resize((800, int(800 * img.height / img.width))) 
        
        # 2. Ubah ke Array Angka
        data = np.array(img) # Shape: (Height, Width, 3)
        
        # 3. Hitung Selisih antara Max RGB dan Min RGB (Saturation)
        # Hitam/Putih/Abu punya selisih (ptp) mendekati 0.
        # Merah/Biru/Hijau punya selisih tinggi.
        rgb_range = np.ptp(data, axis=2) 
        
        # 4. Tentukan Ambang Batas Warna (Sensitivity)
        # Jika selisih RGB > 30, maka itu adalah PIKSEL WARNA.
        # Angka 30 cukup untuk membedakan link biru dari artefak kompresi abu-abu.
        COLOR_PIXEL_THRESHOLD = 30 
        
        # Hitung piksel yang dianggap "Berwarna"
        color_pixels = np.count_nonzero(rgb_range > COLOR_PIXEL_THRESHOLD)
        total_pixels = data.shape[0] * data.shape[1]
        
        # 5. Persentase Area Warna
        color_percentage = (color_pixels / total_pixels) * 100
        
        # Breakdown kasar (Approximation untuk visualisasi saja)
        # Kita tidak pakai CMYK murni agar tidak error Rich Black lagi.
        # Kita pakai channel RGB dominan.
        r_dom = np.count_nonzero((data[:,:,0] > data[:,:,1]) & (data[:,:,0] > data[:,:,2]) & (rgb_range > COLOR_PIXEL_THRESHOLD))
        g_dom = np.count_nonzero((data[:,:,1] > data[:,:,0]) & (data[:,:,1] > data[:,:,2]) & (rgb_range > COLOR_PIXEL_THRESHOLD))
        b_dom = np.count_nonzero((data[:,:,2] > data[:,:,0]) & (data[:,:,2] > data[:,:,1]) & (rgb_range > COLOR_PIXEL_THRESHOLD))
        
        # Normalisasi untuk tampilan chart (sekadar proporsi)
        total_dom = r_dom + g_dom + b_dom + 1 # +1 avoid div zero
        
        return {
            "total_color_coverage": round(color_percentage, 4), # Presisi 4 desimal
            "approx_r": round((r_dom/total_pixels)*100, 2),
            "approx_g": round((g_dom/total_pixels)*100, 2),
            "approx_b": round((b_dom/total_pixels)*100, 2)
        }

    except Exception as e:
        print(f"Error Processing: {e}")
        return {"total_color_coverage": 0, "approx_r":0, "approx_g":0, "approx_b":0}

def process_document(file_stream, filename):
    results = []
    
    if filename.lower().endswith('.pdf'):
        doc = fitz.open(stream=file_stream.read(), filetype="pdf")
        for i in range(len(doc)):
            page = doc.load_page(i)
            pix = page.get_pixmap(dpi=100) # DPI 100 cukup
            img_bytes = pix.tobytes("png")
            
            analysis = analyze_color_presence(img_bytes)
            results.append({"page": i + 1, "analysis": analysis})
            
    else:
        img_bytes = file_stream.read()
        analysis = analyze_color_presence(img_bytes)
        results.append({"page": 1, "analysis": analysis})
        
    return results