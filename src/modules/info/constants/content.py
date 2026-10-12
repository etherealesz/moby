from modules.info.schemas.info import SInfoPageResponse, SInfoSectionResponse

ABOUT_PAGE = SInfoPageResponse(
    title="Tentang MOBY",
    sections=[
        SInfoSectionResponse(
            title="Latar Belakang",
            paragraphs=[
                "MOBY membantu masyarakat memilah sampah rumah tangga ke dalam "
                "empat kategori (Anorganik, B3, Organik, Residu) dan menemukan "
                "fasilitas pengelolaan sampah terdekat yang sesuai.",
                "Wilayah layanan meliputi Provinsi DKI Jakarta, Kota Tangerang, "
                "Kota Depok, dan Kota Bekasi.",
            ],
        ),
        SInfoSectionResponse(
            title="Metode dan Teknologi",
            paragraphs=[
                "Setiap frame kamera ditingkatkan kontrasnya dengan CLAHE pada "
                "kanal L* ruang warna CIELAB.",
                "Objek sampah dideteksi dengan YOLO26, lalu setiap objek "
                "diklasifikasikan dengan MobileNetV4-Conv-S. Hasil antar-frame "
                "dihaluskan agar label dan kotak tidak berkedip.",
                "Rute ke fasilitas dicari dengan algoritma A* Search di atas graf "
                "jalan OpenStreetMap dengan heuristik jarak Haversine.",
                "Backend dibangun dengan FastAPI dan PostgreSQL; antarmuka dengan "
                "Next.js dan Mantine.",
            ],
        ),
        SInfoSectionResponse(
            title="Profil Pengembang",
            paragraphs=[
                "Enardo Stefanus (NIM 535230072), Program Studi Teknik Informatika, "
                "Universitas Tarumanagara, 2026.",
            ],
        ),
    ],
)

HELP_PAGE = SInfoPageResponse(
    title="Bantuan",
    sections=[
        SInfoSectionResponse(
            title="Panduan Operasional",
            paragraphs=[
                "Buka halaman Klasifikasi dan izinkan akses kamera.",
                "Arahkan kamera ke sampah. Kotak, label kategori, dan skor "
                "keyakinan muncul di atas video.",
                "Pilih objek, lalu tekan tombol navigasi untuk mencari fasilitas "
                "terdekat sesuai kategorinya.",
            ],
        ),
        SInfoSectionResponse(
            title="Alur Antarmodul",
            paragraphs=[
                "Klasifikasi menghasilkan kategori sampah. Navigasi memakai "
                "kategori tersebut dan lokasi GPS Anda untuk memilih fasilitas "
                "dan menghitung rute.",
            ],
        ),
        SInfoSectionResponse(
            title="Penjelasan Kategori",
            paragraphs=[
                "Anorganik: plastik, kertas dan karton, kaca, logam, tekstil. "
                "Diarahkan ke Bank Sampah.",
                "Organik: sisa makanan, kulit buah, sisa bahan dapur, daun dan "
                "ranting. Diarahkan ke TPS3R.",
                "B3: baterai, elektronik kecil, lampu, kemasan bertekanan. "
                "Diarahkan ke TPST atau TPA.",
                "Residu: produk sanitasi sekali pakai, kemasan saset, styrofoam, "
                "puntung rokok. Diarahkan ke TPST atau TPA.",
            ],
        ),
        SInfoSectionResponse(
            title="Petunjuk Peta",
            paragraphs=[
                "Penanda biru menunjukkan posisi Anda; garis menunjukkan rute ke "
                "fasilitas tujuan beserta estimasi jarak tempuh.",
                "Pilih moda berjalan kaki atau berkendara. Rute tidak "
                "memperhitungkan kondisi lalu lintas real-time.",
            ],
        ),
    ],
)
