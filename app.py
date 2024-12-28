# Import library yang dibutuhkan
from flask import Flask, render_template, request  # Framework web Flask
import numpy as np      # Library untuk komputasi numerik
from PIL import Image   # Library untuk manipulasi gambar
import io              # Library untuk operasi input/output
import math            # Library untuk fungsi matematika
import base64          # Library untuk encoding data ke base64

# Inisialisasi aplikasi Flask
app = Flask(__name__)

def calculate_mse(img1_array, img2_array):
    """Menghitung Mean Square Error (MSE) antara dua gambar"""
    # Validasi: memastikan kedua gambar memiliki dimensi yang sama
    if img1_array.shape != img2_array.shape:
        raise ValueError("Kedua gambar harus memiliki dimensi yang sama")
    
    # Konversi array gambar ke tipe float untuk perhitungan yang lebih akurat
    img1_array = img1_array.astype(float)
    img2_array = img2_array.astype(float)
    
    # Hitung MSE: rata-rata dari kuadrat selisih nilai pixel
    # Formula: MSE = (1/n) * Σ(x1-x2)²
    mse = np.mean((img1_array - img2_array) ** 2)
    return mse

def calculate_psnr(mse, max_pixel=255.0):
    """Menghitung Peak Signal-to-Noise Ratio (PSNR)"""
    # Jika MSE = 0, artinya gambar identik, PSNR = infinity
    if mse == 0:
        return float('inf')
    
    # Hitung PSNR menggunakan rumus: PSNR = 20 * log10(MAX) - 10 * log10(MSE)
    # di mana MAX adalah nilai maksimum pixel (255 untuk gambar 8-bit)
    psnr = 20 * math.log10(max_pixel) - 10 * math.log10(mse)
    return psnr

# Route untuk halaman utama
@app.route('/')
def index():
    # Render template HTML utama
    return render_template('index.html')

# Route untuk memproses perhitungan, hanya menerima metode POST
@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        # Ambil file gambar yang diupload dari form
        img1_file = request.files['image1']
        img2_file = request.files['image2']

        # Baca gambar menggunakan PIL dan konversi ke mode RGB
        # BytesIO digunakan untuk membaca file dari memory
        img1 = Image.open(io.BytesIO(img1_file.read())).convert('RGB')
        img2 = Image.open(io.BytesIO(img2_file.read())).convert('RGB')

        # Validasi: periksa apakah kedua gambar memiliki dimensi yang sama
        if img1.size != img2.size:
            return render_template('index.html', 
                                error="Kedua gambar harus memiliki dimensi yang sama")

        # Konversi gambar ke array numpy untuk perhitungan
        img1_array = np.array(img1)
        img2_array = np.array(img2)

        # Hitung nilai MSE
        mse = calculate_mse(img1_array, img2_array)
        
        # Hitung nilai PSNR
        psnr = calculate_psnr(mse)

        # Format hasil MSE untuk ditampilkan
        # Gunakan notasi scientific untuk nilai yang sangat kecil
        if mse < 0.01:
            mse_formatted = f"{mse:.2e}"  # Format scientific dengan 2 desimal
        else:
            mse_formatted = f"{mse:.2f}"  # Format desimal biasa dengan 2 angka di belakang koma

        # Format hasil PSNR untuk ditampilkan
        if psnr == float('inf'):
            psnr_formatted = "∞ dB"  # Tampilkan simbol infinity
        else:
            psnr_formatted = f"{psnr:.2f} dB"  # Format dengan 2 desimal dan tambahkan satuan dB

        # Konversi gambar ke format base64 untuk ditampilkan di browser
        # Menggunakan buffer memory untuk menyimpan gambar sementara
        img1_buffer = io.BytesIO()
        img2_buffer = io.BytesIO()
        
        # Simpan gambar ke buffer dalam format PNG
        img1.save(img1_buffer, format='PNG')
        img2.save(img2_buffer, format='PNG')
        
        # Konversi gambar ke string base64 dan tambahkan header data URL
        img1_data = f"data:image/png;base64,{base64.b64encode(img1_buffer.getvalue()).decode()}"
        img2_data = f"data:image/png;base64,{base64.b64encode(img2_buffer.getvalue()).decode()}"

        # Render template dengan hasil perhitungan dan gambar
        return render_template('index.html', 
                             mse=mse_formatted, 
                             psnr=psnr_formatted,
                             img1_data=img1_data,
                             img2_data=img2_data)

    except Exception as e:
        # Tangani error yang mungkin terjadi dan tampilkan pesan error
        return render_template('index.html', 
                             error=f"Error: {str(e)}")

# Jalankan aplikasi jika file ini dijalankan langsung
if __name__ == '__main__':
    # Jalankan server Flask dalam mode debug
    app.run(debug=True)
