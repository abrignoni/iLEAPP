# 🛠️ Panduan Pengembangan iLEAPP dengan Makefile

Dokumen ini menjelaskan cara menggunakan `Makefile` yang disertakan dalam repository ini untuk mempercepat proses pengembangan (development), testing, dan penggunaan iLEAPP secara *cross-platform* (Windows, Linux, macOS).

## 📋 Prasyarat

Sebelum memulai, pastikan Anda telah menginstal:

1.  **Python 3.9+**: Pastikan terdaftar di PATH system.
2.  **GNU Make**:
    * **Linux/macOS**: Biasanya sudah terinstall (atau via `sudo apt install make` / `xcode-select --install`).
    * **Windows**:
        * Jika menggunakan **Git Bash**, `make` biasanya sudah termasuk.
        * Jika menggunakan **CMD/PowerShell**, instal via Chocolatey: `choco install make`.

---

## 🚀 Perintah Dasar (Workflow)

Berikut adalah urutan perintah dari persiapan hingga menjalankan aplikasi.

### 1. Persiapan Lingkungan (`Setup`)

Tidak perlu membuat virtual environment (venv) secara manual. Cukup jalankan satu perintah ini pertama kali:

```bash
make install
```
Apa yang dilakukan perintah ini?
1. Mengecek apakah `.venv` sudah ada. Jika belum, akan dibuatkan secara otomatis (target `make env`).
2. Meng-upgrade `pip`.
3. Menginstal seluruh dependensi dari `requirements.txt`.
4. Menginstal development tools tambahan (`black`, `isort`, `flake8`) untuk menjaga kerapian kode.

---

### 2. Pengembangan Parser (`Development`)

Saat Anda membuat parser artifak baru, Anda tidak perlu membuka GUI berulang kali. Gunakan mode CLI testing untuk melihat log error secara langsung.

Command:
```Bash
make test-parser IN=<path_input> OUT=<path_output> ART=<nama_artifak>
```
Penjelasan Parameter:
- `IN` : Path ke folder/file sampel data (ekstraksi iOS). Default: `./input_data`
- `OUT`: Path folder tujuan laporan. Default: `./output_report`
- `ART`: Nama artifak yang ingin ditest (sesuai nama di script). Default: `*` (Semua).


Contoh Penggunaan Nyata: Mengetes parser WhatsApp dengan data sampel yang ada di folder `sampel_wa`:

```Bash
make test-parser IN=./sampel_wa OUT=./laporan_test ART=WhatsApp
```
Tips: Perintah ini menggunakan flag `--t` (text/tsv only) agar proses testing lebih cepat tanpa generate HTML yang berat.

---

### 3. Menjalankan Aplikasi (`Running`)

Setelah parser dirasa aman, jalankan aplikasi dalam mode GUI atau cek Help menu CLI.

Menjalankan GUI: Membuka antarmuka grafis iLEAPP (`ileappGUI.py`):
```Bash
make run
```
Melihat Menu CLI: Melihat opsi bantuan command line (`ileapp.py --help`):
```Bash
make run-cli
```

---

### 4. Kualitas Kode (`Code Quality`)

Sebelum melakukan Commit atau Pull Request, pastikan kode Anda rapi dan sesuai standar Python (PEP8).

Format Otomatis: Merapikan kode di folder `scripts/artifacts/` menggunakan black dan isort:
```Bash
make format
```
Cek Error/Linting: Mencari potensi error syntax atau variabel yang tidak terpakai menggunakan `flake8`:
```Bash
make lint
```

---

### 5. Bersih-bersih (`Cleanup`)

Jika terjadi error pada library atau ingin mengulang setup dari awal:
```Bash
make clean
```
Perintah ini akan menghapus folder `.venv`, folder cache pyc, cache pytest, dan file temporary lainnya.

---

### 💡 Catatan Khusus Windows
Makefile ini dirancang agar kompatibel dengan Command Prompt (CMD), PowerShell, dan Git Bash.
- Jika menggunakan CMD/PowerShell, Makefile akan otomatis mendeteksi OS dan menggunakan perintah Windows (seperti `rmdir` dan backslash `\`).
- Jika menggunakan Git Bash, Makefile akan menggunakan perintah Unix (seperti `rm -rf`).

Jika Anda mengalami error `make: command not found` di Windows, pastikan binary Make sudah masuk ke dalam System PATH environment variable.

---
