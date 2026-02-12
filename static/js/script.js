document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const loadingArea = document.getElementById('loading-area');
    const resultArea = document.getElementById('result-area');
    const previewContainer = document.getElementById('file-preview-container');
    const tableBody = document.getElementById('detail-table-body');
    const totalPriceEl = document.getElementById('total-price');
    const totalPagesEl = document.getElementById('total-pages');
    const btnPrint = document.getElementById('btn-print'); // <--- Baru

    let currentFileURL = null; // Variabel global untuk simpan link file

    // --- Event Listeners Drag & Drop ---
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.firstElementChild.classList.add('drag-over');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.firstElementChild.classList.remove('drag-over');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.firstElementChild.classList.remove('drag-over');
        if (e.dataTransfer.files.length > 0) handleFile(e.dataTransfer.files[0]);
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) handleFile(e.target.files[0]);
    });

    // --- Event Listener Tombol Print (BARU) ---
    btnPrint.addEventListener('click', () => {
        if (currentFileURL) {
            // Buka file di tab baru, lalu trigger print browser
            const printWindow = window.open(currentFileURL, '_blank');
            // Catatan: window.print() otomatis mungkin diblokir browser, 
            // jadi user tetap harus tekan Ctrl+P di tab baru tersebut.
            printWindow.focus();
        } else {
            alert("Belum ada file yang diupload!");
        }
    });

    // --- Fungsi Utama ---
    function handleFile(file) {
        showPreview(file);
        uploadFile(file);
    }

    function showPreview(file) {
        previewContainer.innerHTML = '';
        
        // Simpan URL ke variabel global agar bisa dipakai tombol print
        if (currentFileURL) URL.revokeObjectURL(currentFileURL); // Hapus memori lama
        currentFileURL = URL.createObjectURL(file);
        
        let element;
        if (file.type === 'application/pdf') {
            element = document.createElement('embed');
            element.src = currentFileURL;
            element.type = 'application/pdf';
            element.className = 'w-full h-full object-contain';
        } else {
            element = document.createElement('img');
            element.src = currentFileURL;
            element.className = 'w-full h-full object-contain';
        }
        previewContainer.appendChild(element);
    }

    async function uploadFile(file) {
        dropZone.classList.add('hidden');
        resultArea.classList.add('hidden');
        loadingArea.classList.remove('hidden');

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (!response.ok) throw new Error(data.error || 'Terjadi kesalahan');

            renderResults(data);
            loadingArea.classList.add('hidden');
            resultArea.classList.remove('hidden');

        } catch (error) {
            console.error(error);
            alert('Gagal menganalisis: ' + error.message);
            loadingArea.classList.add('hidden');
            dropZone.classList.remove('hidden');
        }
    }

    function renderResults(data) {
        totalPriceEl.textContent = formatRupiah(data.total_biaya);
        totalPagesEl.textContent = data.detail.length + ' Hal';
        tableBody.innerHTML = '';
        
        data.detail.forEach(row => {
            const isColor = row.tipe === 'Color';
            const badgeColor = isColor ? 'bg-blue-100 text-blue-700 border-blue-200' : 'bg-gray-100 text-gray-700 border-gray-200';
            
            // Visualisasi Bar CMYK
            // Kita buat bar kecil untuk masing-masing warna
            const cmykBars = `
                <div class="flex flex-col gap-1 w-24 mx-auto text-[10px] text-gray-500">
                    <div class="flex items-center gap-1">
                        <span class="w-2 h-2 bg-red-500 rounded-full"></span>
                        <span class="w-6">R:${row.details.approx_r}%</span>
                    </div>
                    <div class="flex items-center gap-1">
                        <span class="w-2 h-2 bg-green-500 rounded-full"></span>
                        <span class="w-6">G:${row.details.approx_g}%</span>
                    </div>
                    <div class="flex items-center gap-1">
                        <span class="w-2 h-2 bg-blue-500 rounded-full"></span>
                        <span class="w-6">B:${row.details.approx_b}%</span>
                    </div>
                </div>
            `;

            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td class="px-6 py-4 font-medium">${row.page}</td>
                <td class="px-6 py-4">
                    <span class="px-2 py-1 rounded-md text-xs font-bold border ${badgeColor}">
                        ${row.tipe}
                    </span>
                    <p class="text-xs text-gray-400 mt-1">${row.alasan}</p>
                </td>
                <td class="px-6 py-4 text-center">
                    ${cmykBars}
                </td>
                <td class="px-6 py-4 text-right font-semibold">${formatRupiah(row.biaya)}</td>
            `;
            tableBody.appendChild(tr);
        });
    }

    function formatRupiah(angka) {
        return new Intl.NumberFormat('id-ID', {
            style: 'currency',
            currency: 'IDR',
            minimumFractionDigits: 0
        }).format(angka);
    }
});