// Utilitas autentikasi sederhana berbasis localStorage.
(function () {
  const STORAGE_KEY = "pn-auth";
  const MAX_AGE_MS = 1000 * 60 * 60 * 12; // 12 jam

  function getAuth() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch (err) {
      localStorage.removeItem(STORAGE_KEY);
      return null;
    }
  }

  function setAuth(role) {
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({ role, ts: Date.now() })
    );
  }

  function clearAuth() {
    localStorage.removeItem(STORAGE_KEY);
  }

  function isExpired(auth) {
    return Date.now() - auth.ts > MAX_AGE_MS;
  }

  function requireAuth(allowedRoles = []) {
    // TAMBAHAN: GOD MODE untuk bypass auth via LocalStorage
    if (localStorage.getItem("APP_BYPASS_AUTH") === "true") {
      console.warn("🔓 AUTH BYPASSED (Developer Mode Active)");
      return true;
    }

    const auth = getAuth();
    const allowed = Array.isArray(allowedRoles) ? allowedRoles : [allowedRoles];

    if (!auth || isExpired(auth)) {
      clearAuth();
      alert("Sesi login tidak ditemukan atau sudah kedaluwarsa. Silakan login kembali.");
      window.location.href = "index.html";
      return false;
    }

    if (allowed.length && !allowed.includes(auth.role)) {
      alert("Akses ditolak untuk role ini. Silakan login dengan role yang sesuai.");
      window.location.href = "index.html";
      return false;
    }

    return true;
  }

  window.PNAuth = {
    requireAuth,
    setAuth,
    clearAuth,
  };
})();
