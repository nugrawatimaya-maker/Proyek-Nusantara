// ==========================================
// KONFIGURASI PUSAT (ENVIRONMENT SWITCHER)
// ==========================================

// 1. LOGIKA SAKLAR OTOMATIS
// Prioritas: URL Parameter '?mode=dev' > Pengaturan di Admin Panel > Default ke PROD
const urlParams = new URLSearchParams(window.location.search);
const urlWantsDev = urlParams.get('mode') === 'dev';
const storageWantsDev = localStorage.getItem('APP_DEV_MODE') === 'true';

const CURRENT_ENV = (urlWantsDev || storageWantsDev) ? 'DEV' : 'PROD';

// 2. DAFTAR KREDENSIAL
const CONFIG = {
    PROD: {
        URL: "https://nbpxmramqufvxiikxbve.supabase.co",
        KEY: "sb_publishable_peLRGV8YGA5djczYBgLnkQ_buXXBknN",
        THEME: "normal",
        PYTHON_API_URL: "http://localhost:8000" // Sesuaikan jika production beda
    },
    DEV: {
        URL: "https://drpnegmcazqnxmbonhwq.supabase.co",
        // ⚠️ PASTIKAN KEY INI ADALAH 'anon public' KEY YANG PANJANG (JWT) DARI SUPABASE
        KEY: "sb_publishable_RDhFfphNpQCg4iYStiI8Ug_3PIWUSip",
        THEME: "warning",
        PYTHON_API_URL: "http://localhost:8000"
    }
};

// ==========================================
// SYSTEM LOGIC
// ==========================================
// Cek apakah library Supabase sudah dimuat?
if (typeof supabase === 'undefined') {
    alert("CRITICAL ERROR: Library Supabase belum dimuat di HTML!");
    throw new Error("Supabase library missing");
}

const activeConfig = CONFIG[CURRENT_ENV];
console.log(`🔌 Menghubungkan ke Database: ${CURRENT_ENV}`);

// Inisialisasi Koneksi Asli
// Inisialisasi Koneksi Asli
const _realClient = supabase.createClient(activeConfig.URL, activeConfig.KEY);
// Expose ke Global (PENTING AGAR AUTH TERJAGA)
// Expose ke Global (PENTING AGAR AUTH TERJAGA)
window.client = _realClient;


const fmt = (n) => new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0
}).format(n);

// EXPLICIT GLOBAL EXPORT
window.activeConfig = activeConfig;
window.fmt = fmt;

// Banner Mode DEV
document.addEventListener("DOMContentLoaded", () => {
    if (CURRENT_ENV === 'DEV') {
        document.title = "[DEV] " + document.title;
        const banner = document.createElement("div");
        banner.innerHTML = `
            <div style="position: fixed; bottom: 0; left: 0; right: 0; 
            background: repeating-linear-gradient(45deg, #fbbf24, #fbbf24 10px, #f59e0b 10px, #f59e0b 20px); 
            color: black; text-align: center; font-weight: bold; font-size: 14px; padding: 12px; z-index: 99999; 
            border-top: 4px solid black; box-shadow: 0 -4px 15px rgba(0,0,0,0.3); height: 60px; display: flex; align-items: center; justify-content: center;">
                <span>🚧 MODE DEVELOPMENT (Nusantara_dev) - DATA AMAN DIHAPUS 🚧</span>
            </div>
        `;
        document.body.appendChild(banner);
    }
});

// ==========================================
// JEMBATAN PENGHUBUNG (INI YANG HILANG TADI)
// ==========================================
window.client = {
    from: (table) => _realClient.from(table),
    storage: _realClient.storage,
    rpc: (fn, args) => _realClient.rpc(fn, args),
    auth: _realClient.auth
};

console.log("✅ app_config.js Siap. Variable 'client' sudah aktif.");

// ==========================================
// 3. GLOBAL UTILITIES
// ==========================================
window.catatLog = async function (tipe, pesan, icon = 'fa-info-circle') {
    let user = "SYSTEM";
    // Coba ambil user dari PNAuth (auth.js) jika sudah diload
    if (typeof PNAuth !== 'undefined' && PNAuth.getSession) {
        const session = PNAuth.getSession();
        if (session && session.user) {
            user = session.user.full_name || session.user.username;
        }
    }

    try {
        // Gunakan _realClient atau window.client
        const { error } = await _realClient.from('activity_logs').insert([{
            user_name: user,
            tipe: tipe,
            aktivitas: pesan,
            icon: icon
        }]);

        if (error) console.error("⚠️ Gagal mencatat log:", error.message);
    } catch (e) {
        console.error("⚠️ Sistem Log Error:", e);
    }
};