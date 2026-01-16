// Utilitas autentikasi CUSTOM BASE (Table employees + RPC)
(function () {

  const STORAGE_KEY = "pn_session_v2";

  // --- SESSION MANAGE ---
  function setSession(userData) {
    const session = {
      user: userData, // { id, full_name, role, session_token }
      ts: Date.now()
    };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(session));
    startHeartbeat(); // Start monitoring immediately
  }

  function getSession() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return null;
      const session = JSON.parse(raw);

      // Expire setelah 24 jam (Client Side Fallback)
      const TWENTY_FOUR_HOURS = 24 * 60 * 60 * 1000;
      if (Date.now() - session.ts > TWENTY_FOUR_HOURS) {
        logout();
        return null;
      }
      return session;
    } catch (e) {
      return null;
    }
  }

  // --- SECURITY HEARTBEAT & IDLE CHECK ---
  let heartbeatInterval = null;
  let lastActivity = Date.now();
  const IDLE_LIMIT = 60 * 60 * 1000; // 1 Jam (in ms)

  function updateActivity() {
    lastActivity = Date.now();
  }

  // Listeners untuk mendeteksi aktivitas user
  if (typeof window !== 'undefined') {
    ['mousemove', 'mousedown', 'keypress', 'touchmove', 'scroll'].forEach(evt => {
      window.addEventListener(evt, updateActivity, { passive: true });
    });
  }

  async function checkSession() {
    const s = getSession();
    if (!s) return;

    // 1. Cek Idle Time (Client Side)
    const idleTime = Date.now() - lastActivity;
    if (idleTime > IDLE_LIMIT) {
      // Time's up!
      alert("Waktu Habis! Anda tidak aktif selama 1 jam.\nSilakan login kembali.");
      logout();
      return;
    }

    // 2. Cek Validitas Token di Server (Server Side)
    if (!s.user.session_token) return;
    if (s.user.role === 'superadmin') return;

    try {
      const { data, error } = await window.client.rpc('check_session_validity', {
        p_user_id: s.user.id,
        p_token: s.user.session_token
      });

      if (data === false) {
        alert("SESI BERAKHIR!\n\nAkun Anda telah dikunci karena terdeteksi login di perangkat lain, atau sesi telah kadaluarsa.");
        logout();
      }
    } catch (e) {
      console.warn("Heartbeat check failed:", e);
    }
  }

  function startHeartbeat() {
    if (heartbeatInterval) clearInterval(heartbeatInterval);
    // Cek setiap 30 detik
    heartbeatInterval = setInterval(checkSession, 30000);
  }

  // Auto start if logged in
  if (getSession()) {
    startHeartbeat();
    updateActivity(); // Init time
  }

  // --- UTILS ---
  async function logActivity(aktivitas, tipe = 'UMUM', icon = 'fa-info-circle') {
    try {
      const session = getSession();
      if (!session) return;

      // Insert ke tabel activity_logs dengan user_name
      // Note: Kita gunakan user_name sebagai identifier utama di log
      // karena user_id di activity_logs mungkin merujuk ke tabel auth.users yang berbeda tipe datanya
      // Kita abaikan user_id insert, atau isi null.

      const payload = {
        user_name: session.user.full_name,
        aktivitas: aktivitas,
        tipe: tipe,
        icon: icon
        // user_id: session.user.id  <-- Jika tabel activity_logs kolom user_id bertipe UUID, jangan kirim INT.
      };

      const { error } = await window.client
        .from('activity_logs')
        .insert(payload);

      if (error) console.warn("Log warning:", error.message);

    } catch (err) {
      console.error("Err logging:", err);
    }
  }

  async function logout() {
    // Log before clearing
    const s = getSession();
    if (s) {
      // Fire and forget log
      logActivity(`${s.user.full_name} Logout`, 'LOGOUT', 'fa-sign-out-alt');
    }

    localStorage.removeItem(STORAGE_KEY);
    // Juga signout supabase just in case (biar bersih)
    if (window.client && window.client.auth) {
      await window.client.auth.signOut();
    }

    window.location.href = "login.html";
  }

  // --- MAIN AUTH CHECK ---
  async function requireAuth(allowedRoles = []) {
    // 1. Cek User Session (LocalStorage)
    const session = getSession();

    if (!session) {
      window.location.href = "login.html";
      return false;
    }

    // 2. Cek Role
    if (allowedRoles.length > 0) {
      if (!allowedRoles.includes(session.user.role)) {
        alert(`Akses Ditolak.\nRole Anda: ${session.user.role}\nButuh: ${allowedRoles.join(', ')}`);

        // Redirect ke dashboard yang sesuai milik dia
        const r = session.user.role;
        if (r === 'direksi') window.location.href = 'dashboard_direksi.html';
        else if (r === 'finance') window.location.href = 'dashboard_finance.html';
        else if (r === 'marketing') window.location.href = 'dashboard_marketing.html';
        else if (r === 'hr') window.location.href = 'dashboard_hr.html';
        else if (r === 'operasional') window.location.href = 'dashboard_operasional.html';
        else if (r === 'superadmin') window.location.href = 'admin_karyawan.html';
        else window.location.href = "login.html";

        return false;
      }
    }

    // 3. Update User UI 
    const display = document.getElementById('user-display');
    if (display) {
      display.innerText = session.user.full_name;
    }

    // --- SPESIFIK RESTRICTION: HALIMI (330428) ---
    // User ini HANYA boleh akses pengajuan_biaya.html
    const restrictedIds = ['330428']; // Bisa tambah ID lain jika perlu
    // NOTE: Cek apakah ID user dari session match (user.id atau user.employee_id tergantung struktur)
    // Asumsi user.id menyimpan employee ID atau string unik.
    // Kita juga cek username/full_name just in case ID structure varied.

    // Check by ID or Name specific for Halimi
    const isRestrictedUser =
      (session.user.id == '330428') ||
      (session.user.full_name && session.user.full_name.toLowerCase().includes('halimi'));

    if (isRestrictedUser) {
      const path = window.location.pathname;
      const allowedPage = 'pengajuan_biaya.html';

      // Allow login.html too obviously
      if (!path.includes(allowedPage) && !path.includes('login') && path !== '/' && path !== '') {
        // Prevent redirect loop if already there
        console.warn("Restricted User: Redirecting to Access Page");
        window.location.href = allowedPage;
        return false;
      }
    }

    return true;
  }

  // --- EXPORT GLOBAL ---
  window.PNAuth = {
    requireAuth,
    logout,
    logActivity,
    setSession, // Exposed for login.html
    getSession
  };

})();
