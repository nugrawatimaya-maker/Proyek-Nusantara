// ==========================================
// KONFIGURASI PUSAT (ENVIRONMENT SWITCHER)
// ==========================================

// 1. LOGIKA SAKLAR OTOMATIS
const isSimulationActive = localStorage.getItem('APP_TEST_MODE') === 'true';
const CURRENT_ENV = isSimulationActive ? 'DEV' : 'PROD'; 

// 2. DAFTAR KREDENSIAL
const CONFIG = {
    PROD: {
        URL: "https://nbpxmramqufvxiikxbve.supabase.co", 
        KEY: "sb_publishable_peLRGV8YGA5djczYBgLnkQ_buXXBknN", 
        THEME: "normal"
    },
    DEV: {
        URL: "https://drpnegmcazqnxmbonhwq.supabase.co", 
        KEY: "sb_publishable_RDhFfphNpQCg4iYStiI8Ug_3PIWUSip",
        THEME: "warning"
    }
};

// ==========================================
// SYSTEM LOGIC
// ==========================================
const activeConfig = CONFIG[CURRENT_ENV];
const _realClient = supabase.createClient(activeConfig.URL, activeConfig.KEY);

const fmt = (n) => new Intl.NumberFormat('id-ID', {
    style:'currency',
    currency:'IDR',
    minimumFractionDigits:0
}).format(n);

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

        const actionBar = document.getElementById('actionBar');
        if (actionBar) {
            actionBar.style.transition = "bottom 0.3s ease";
            actionBar.style.bottom = "70px";
            actionBar.style.borderTop = "4px solid #cbd5e1";
        }

        const adminBtn = document.querySelector('.stealth-admin-btn');
        if (adminBtn) {
            adminBtn.style.bottom = "80px";
        }
    }
});

const client = {
    from: (table) => _realClient.from(table),
    storage: _realClient.storage
};
