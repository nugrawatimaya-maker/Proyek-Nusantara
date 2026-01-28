// ==========================================
// DASHBOARD KOST LOGIC (Refactored)
// ==========================================

// --- Toast Notification System ---
const Toast = {
    container: null,
    init() {
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.id = 'toast-container';
            this.container.className = 'fixed top-4 right-4 z-[9999] flex flex-col gap-3 pointer-events-none';
            document.body.appendChild(this.container);

            // Add styles for animation if not present
            if (!document.getElementById('toast-style')) {
                const style = document.createElement('style');
                style.id = 'toast-style';
                style.innerHTML = `
                    @keyframes slideIn { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
                    @keyframes fadeOut { from { opacity: 1; } to { opacity: 0; } }
                    .toast-enter { animation: slideIn 0.3s ease-out forwards; }
                    .toast-exit { animation: fadeOut 0.3s ease-in forwards; }
                `;
                document.head.appendChild(style);
            }
        }
    },
    show(message, type = 'info') {
        this.init();

        const el = document.createElement('div');
        el.className = `toast-enter pointer-events-auto min-w-[300px] max-w-sm p-4 rounded-xl shadow-lg border-l-4 flex items-start gap-3 bg-white transform transition-all duration-300`;

        let icon = 'fa-info-circle';
        let colorClass = 'border-blue-500 text-blue-600';
        let bgIcon = 'bg-blue-50';

        if (type === 'success') {
            icon = 'fa-check-circle';
            colorClass = 'border-emerald-500 text-emerald-600';
            bgIcon = 'bg-emerald-50';
        } else if (type === 'error') {
            icon = 'fa-exclamation-circle';
            colorClass = 'border-red-500 text-red-600';
            bgIcon = 'bg-red-50';
        } else if (type === 'warning') {
            icon = 'fa-exclamation-triangle';
            colorClass = 'border-amber-500 text-amber-600';
            bgIcon = 'bg-amber-50';
        }

        el.innerHTML = `
            <div class="shrink-0 w-8 h-8 rounded-full ${bgIcon} ${colorClass} flex items-center justify-center">
                <i class="fas ${icon}"></i>
            </div>
            <div class="flex-1 pt-1">
                <p class="text-sm font-medium text-slate-800 leading-snug">${message}</p>
            </div>
            <button onclick="this.parentElement.remove()" class="text-slate-400 hover:text-slate-600 transition">
                <i class="fas fa-times"></i>
            </button>
        `;

        // Style border
        el.classList.add(colorClass.split(' ')[0]); // Add border color class

        this.container.appendChild(el);

        // Auto remove
        setTimeout(() => {
            el.classList.remove('toast-enter');
            el.classList.add('toast-exit');
            el.addEventListener('animationend', () => el.remove());
        }, 5000);
    }
};

// Global Shortcuts for Toast
window.showSuccess = (msg) => Toast.show(msg, 'success');
window.showError = (msg) => Toast.show(msg, 'error');
window.showInfo = (msg) => Toast.show(msg, 'info');

// Overwrite Native Alert with Toast (Optional, but safer to use explicit calls)
// window.alert = (msg) => Toast.show(msg, 'info'); 


// --- Init Auth & Page ---
document.addEventListener('DOMContentLoaded', () => {
    const project = sessionStorage.getItem('active_project_name');
    if (!project) {
        // Use native alert here as fallback or just redirect
        Toast.show("Tidak ada proyek yang dipilih! Mengalihkan...", "warning");
        setTimeout(() => window.location.href = 'portal_proyek.html', 1500);
        return;
    }

    const headerName = document.getElementById('headerProjectName');
    if (headerName) headerName.textContent = project;

    renderRoomGrid();
    updateDashboardStats();
    renderCheckoutHistory();
    renderDueSoon();
});

// --- UI Rendering Functions ---

function renderRoomGrid() {
    const container = document.getElementById('roomGrid');
    if (!container) return;

    const projectName = sessionStorage.getItem('active_project_name') || '';
    const isBantaeng = projectName.toLowerCase().includes('banta');

    // Dynamic Config via Window State (set by updateDashboardStats)
    let totalRooms = window.currentProjectTotalRooms || (isBantaeng ? 9 : 10);
    let roomPrefix = 'Kamar ';

    // Legacy fallbacks just in case
    if (isBantaeng && !window.currentProjectTotalRooms) totalRooms = 9;
    if (projectName.toLowerCase().includes('faisal') && !window.currentProjectTotalRooms) totalRooms = 10;

    let html = '';

    // Logic for Modal Dropdown
    const selectOptions = document.getElementById('roomSelect');
    if (selectOptions) selectOptions.innerHTML = '<option value="">Pilih Kamar...</option>';

    for (let i = 1; i <= totalRooms; i++) {
        let label = isBantaeng ? `Kamar ${i}` : `${roomPrefix}${i}`;

        // Find tenant for this room (robust matching)
        const tenant = window.activeTenants ? window.activeTenants.find(t => t.room_number == i || t.room_number === String(i)) : null;

        let status = 0; // Default Empty
        if (tenant) {
            if (tenant.status === 'MAINTENANCE' || tenant.name === 'MAINTENANCE') {
                status = 2; // Maintenance
            } else if (tenant.status === 'BOOKED') {
                status = 3; // Booked
            } else {
                status = 1; // Occupied
            }
        }

        // Add to Modal Select
        if (selectOptions) {
            const opt = document.createElement('option');
            opt.value = i;
            let dropdownText = `${label} (Kosong)`;
            if (status === 1) dropdownText = `${label} (Terisi - ${tenant.name})`;
            if (status === 2) dropdownText = `${label} (Perbaikan)`;
            if (status === 3) dropdownText = `${label} (Booked - ${tenant.name})`;

            opt.textContent = dropdownText;
            if (status !== 0) opt.disabled = true;
            selectOptions.appendChild(opt);
        }

        let colorClass = '';
        let icon = '';
        let statusText = '';
        let clickAction = '';

        if (status === 0) {
            colorClass = 'bg-emerald-500 text-white border-emerald-600 hover:bg-emerald-600 cursor-pointer transition';
            icon = 'fa-door-open';
            statusText = 'KOSONG';
            clickAction = `onclick="openEmptyRoomOptions(${i})"`;
        } else if (status === 1) {
            colorClass = 'bg-red-500 text-white border-red-600 hover:bg-red-600 cursor-pointer transition';
            icon = 'fa-user';
            statusText = 'TERISI';
            clickAction = `onclick="openRoomDetail('${tenant?.id}')"`;
        } else if (status === 2) {
            colorClass = 'bg-slate-500 text-white border-slate-600 hover:bg-slate-600 cursor-pointer transition';
            icon = 'fa-tools';
            statusText = 'PERBAIKAN';
            clickAction = `onclick="openMaintenanceOptions(${i})"`;
        } else if (status === 3) {
            colorClass = 'bg-amber-500 text-white border-amber-600 hover:bg-amber-600 cursor-pointer transition';
            icon = 'fa-user-clock';
            statusText = 'BOOKED';
            clickAction = `onclick="openRoomDetail('${tenant?.id}')"`;
        }

        html += `
            <div ${clickAction} class="room-card relative aspect-[4/3] rounded-2xl p-4 flex flex-col justify-between ${colorClass} border-b-4 shadow-lg group">
                <div class="flex justify-between items-start">
                     <i class="fas ${icon} text-2xl opacity-90"></i>
                     <span class="text-3xl font-black opacity-30 italic">#${i}</span>
                </div>
                <div>
                    <h3 class="font-bold text-lg tracking-wide leading-tight">${statusText}</h3>
                    ${tenant ? `<p class="text-xs font-medium opacity-90 truncate mt-1">${tenant.name === 'MAINTENANCE' ? 'Sedang Diperbaiki' : tenant.name}</p>` : ''}
                </div>
                 <!-- Hover Effect Overlay -->
                <div class="absolute inset-0 bg-black/10 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none"></div>
            </div>
        `;
    }
    container.innerHTML = html;
}

// --- Dashboard Statistics Logic ---
async function updateDashboardStats() {
    const rawProjectName = sessionStorage.getItem('active_project_name') || '';
    const isBantaeng = rawProjectName.toLowerCase().includes('banta');

    // 1. Determine Total Rooms (Dynamic from DB)
    let totalRooms = isBantaeng ? 9 : 10; // Default fallback

    try {
        const { data: projData } = await client
            .from('projects')
            .select('total_rooms')
            .eq('name', rawProjectName)
            .single();

        if (projData) {
            totalRooms = projData.total_rooms;
        }
    } catch (e) {
        console.warn("Failed to fetch dynamic room count, using default:", e);
    }

    // Set Global for Grid Render reuse
    window.currentProjectTotalRooms = totalRooms;
    const statTotalEl = document.getElementById('stat-total-rooms');
    if (statTotalEl) statTotalEl.textContent = totalRooms;

    try {
        // 2. Fetch ALL Tenants (Active & Maintenance)
        // Exclude CHECKED_OUT for logic
        const { data, error } = await client
            .from('tenants')
            .select('*')
            .eq('project_name', rawProjectName);

        if (error) throw error;

        // UPDATE GLOBAL STATE
        window.activeTenants = (data || []).filter(t => t.status === 'ACTIVE' || t.status === 'MAINTENANCE' || t.status === 'BOOKED');

        // Filter for Statistics
        const validTenants = data.filter(t => t.status === 'ACTIVE');
        const activeCount = validTenants.length;

        const maintenanceCount = data.filter(t => t.status === 'MAINTENANCE').length;
        // Occupied includes Active + Maintenance for availability calculation
        const realOccupied = activeCount + maintenanceCount;

        const availableCount = Math.max(0, totalRooms - realOccupied);

        // Sum Revenue (Rent Amount) from valid tenants
        const totalRevenue = validTenants.reduce((sum, tenant) => sum + (tenant.rent_amount || 0), 0);

        // 3. Update UI
        const occupiedEl = document.getElementById('stat-occupied');
        if (occupiedEl) {
            occupiedEl.textContent = activeCount;
            // Update Occupancy Percentage
            const occRate = Math.round((activeCount / totalRooms) * 100);
            const occParent = occupiedEl.parentElement;
            const occTextEl = occParent ? occParent.querySelector('p.text-xs') : null;
            if (occTextEl) {
                occTextEl.innerHTML = `<i class="fas fa-chart-pie"></i> ${occRate}% Terisi`;
            }
        }

        const availEl = document.getElementById('stat-available');
        if (availEl) availEl.textContent = availableCount;

        // Revenue Formatter
        const fmt = new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', maximumFractionDigits: 0 });
        const revEl = document.getElementById('stat-revenue');
        if (revEl) revEl.textContent = fmt.format(totalRevenue);

        // 4. Update Grid UI
        renderRoomGrid();

    } catch (err) {
        console.error("Error updating stats:", err);
    }
}

// --- Tenant Operations ---

function openAddTenantModal() {
    document.getElementById('addTenantModal').classList.remove('hidden');
}

function closeAddTenantModal() {
    document.getElementById('addTenantModal').classList.add('hidden');
}

async function saveTenantToSupabase() {
    const name = document.getElementById('tenantName').value;
    const nik = document.getElementById('tenantNik').value;
    const marital = document.getElementById('tenantMarital').value;
    const phone = document.getElementById('tenantPhone').value;
    const roomIndex = document.getElementById('roomSelect').value;
    const rentAmount = document.getElementById('tenantRent').value;
    const proofFile = document.getElementById('tenantProof').files[0];
    const ktpFile = document.getElementById('ktpFile').files[0];

    const rawProjectName = sessionStorage.getItem('active_project_name') || 'project_umum';
    const safeFolderName = rawProjectName
        .replace(/\s+/g, '_')
        .replace(/[^a-zA-Z0-9_]/g, '')
        .toLowerCase();

    if (!name || !roomIndex) {
        showError("Mohon lengkapi Nama dan Pilih Kamar!");
        return;
    }

    // Saving indicator
    const btn = document.querySelector('button[onclick="saveTenantToSupabase()"]');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<i class="fas fa-circle-notch fa-spin"></i> Uploading & Saving...';
    btn.disabled = true;

    try {
        let proofUrl = null;
        let ktpUrl = null;
        const cleanName = name.replace(/[^a-zA-Z0-9]/g, '_').toLowerCase();
        const timestamp = Date.now();

        // 1. Upload Proof if exists
        if (proofFile) {
            try {
                const fileName = `proof_${cleanName}_${timestamp}.${proofFile.name.split('.').pop()}`;
                proofUrl = await uploadToImageKit(
                    proofFile,
                    fileName,
                    `/${safeFolderName}/payment_proofs`
                );
            } catch (e) {
                console.warn("Proof Upload Failed:", e);
                // We'll proceed but warn the user? Or just log.
                showInfo("Gagal upload Bukti Transfer, namun data akan tetap disimpan.");
            }
        }

        // 2. Upload KTP if exists
        if (ktpFile) {
            try {
                const fileName = `ktp_${cleanName}_${timestamp}.${ktpFile.name.split('.').pop()}`;
                ktpUrl = await uploadToImageKit(
                    ktpFile,
                    fileName,
                    `/${safeFolderName}/ktp_docs`
                );
            } catch (e) {
                console.warn("KTP Upload Failed:", e);
            }
        }

        // 3. Insert to Supabase
        const { data, error } = await client
            .from('tenants')
            .insert([
                {
                    project_name: rawProjectName,
                    room_number: roomIndex,
                    nik: nik,
                    name: name,
                    marital_status: marital,
                    phone: phone,
                    status: 'ACTIVE',
                    check_in_date: document.getElementById('tenantCheckInDate').value,
                    check_out_date: document.getElementById('tenantCheckOutDate').value,
                    duration: document.getElementById('tenantDuration').value,
                    rent_amount: rentAmount || 0,
                    payment_proof_url: proofUrl,
                    ktp_photo_url: ktpUrl
                }
            ])
            .select();

        if (error) throw error;

        // 3b. Insert Payment Transaction
        if (data && data.length > 0) {
            const newTenant = data[0];
            await client.from('payment_transactions').insert({
                tenant_id: newTenant.id,
                project_name: rawProjectName,
                room_number: roomIndex,
                tenant_name: name,
                amount: rentAmount || 0,
                description: `Pembayaran Awal Sewa (Check-In)`,
                category: 'RENT',
                proof_url: proofUrl
            });
        }

        showSuccess("Data Penghuni Berhasil Disimpan!");
        closeAddTenantModal();

        // Refresh Grid
        updateDashboardStats();

    } catch (err) {
        console.error('Error saving tenant:', err);
        showError("Gagal menyimpan: " + err.message);
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

// --- ImageKit Upload Helper ---
async function uploadToImageKit(file, fileName, folder) {
    const publicKey = "public_ZzBxgXWQzaOlUvj+11M6G39Si4s=";
    const privateKey = "private_d1MgRwtWJzF4hasu3e0ZhaC+e3Q="; // User Requested to Keep Frontend Key

    // 1. Generate Auth
    const token = "token-" + Math.random().toString(36).substring(7) + "-" + Date.now();
    const expire = parseInt(Date.now() / 1000) + 1800; // 30 mins
    const signature = CryptoJS.HmacSHA1(token + expire, privateKey).toString();

    // 2. Prepare Form Data
    const formData = new FormData();
    formData.append("file", file);
    formData.append("fileName", fileName);
    formData.append("publicKey", publicKey);
    formData.append("signature", signature);
    formData.append("expire", expire);
    formData.append("token", token);
    formData.append("folder", folder);
    formData.append("useUniqueFileName", "false");

    // 3. Send Request
    const response = await fetch("https://upload.imagekit.io/api/v1/files/upload", {
        method: "POST",
        body: formData
    });

    if (!response.ok) {
        const err = await response.json();
        throw new Error(err.message || JSON.stringify(err));
    }

    const data = await response.json();
    return data.url;
}

// --- Expenses ---

function openExpenseModal() {
    const el = document.getElementById('expenseDate');
    if (el) el.value = new Date().toISOString().split('T')[0];
    document.getElementById('addExpenseModal').classList.remove('hidden');
}

function closeExpenseModal() {
    document.getElementById('addExpenseModal').classList.add('hidden');
}

async function saveExpenseToSupabase() {
    const date = document.getElementById('expenseDate').value;
    const category = document.getElementById('expenseCategory').value;
    const amount = document.getElementById('expenseAmount').value;
    const desc = document.getElementById('expenseDesc').value;
    const proofFile = document.getElementById('expenseProof').files[0];
    const rawProjectName = sessionStorage.getItem('active_project_name') || 'project_umum';

    if (!amount || amount <= 0) {
        showError("Mohon isi nominal pengeluaran yang valid.");
        return;
    }

    const btn = document.querySelector('button[onclick="saveExpenseToSupabase()"]');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<i class="fas fa-circle-notch fa-spin"></i> Saving...';
    btn.disabled = true;

    try {
        let proofUrl = null;
        // Upload Proof
        if (proofFile) {
            const safeFolderName = rawProjectName.replace(/\s+/g, '_').replace(/[^a-zA-Z0-9_]/g, '').toLowerCase();
            const fileName = `expense_${Date.now()}.${proofFile.name.split('.').pop()}`;
            proofUrl = await uploadToImageKit(proofFile, fileName, `/${safeFolderName}/expenses`);
        }

        // Insert DB
        const { error } = await client
            .from('expenses')
            .insert([{
                project_name: rawProjectName,
                expense_date: date,
                category: category,
                amount: amount,
                description: desc,
                proof_url: proofUrl
            }]);

        if (error) throw error;

        showSuccess("Pengeluaran berhasil dicatat!");
        closeExpenseModal();
        // Clear form
        document.getElementById('expenseAmount').value = '';
        document.getElementById('expenseDesc').value = '';
        const proofInput = document.getElementById('expenseProof');
        if (proofInput) proofInput.value = '';

    } catch (e) {
        console.error("Expense Error:", e);
        showError("Gagal menyimpan pengeluaran: " + e.message);
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

// --- Tenant Interaction (Checkout, Detail, Extend) ---

function openRoomDetail(tenantId) {
    if (!tenantId || tenantId === 'undefined') return;

    const tenant = window.activeTenants ? window.activeTenants.find(t => t.id == tenantId) : null;

    if (!tenant) {
        console.warn("Tenant not found in memory (refresh recommended)");
        return;
    }

    // Populate Modal
    document.getElementById('detailRoomNumber').textContent = `Kamar ${tenant.room_number}`;
    document.getElementById('detailName').textContent = tenant.name;
    document.getElementById('detailPhone').textContent = tenant.phone || '-';
    document.getElementById('detailCheckIn').textContent = tenant.check_in_date;
    document.getElementById('detailCheckOut').textContent = tenant.check_out_date;
    document.getElementById('detailStatus').innerHTML = tenant.status === 'ACTIVE'
        ? '<span class="bg-green-100 text-green-700 px-2 py-1 rounded text-xs font-bold">LUNAS</span>'
        : `<span class="bg-amber-100 text-amber-700 px-2 py-1 rounded text-xs font-bold">${tenant.status}</span>`;

    // Links
    const btnKtp = document.getElementById('btnViewKtp');
    if (tenant.ktp_photo_url) {
        btnKtp.onclick = () => window.open(tenant.ktp_photo_url, '_blank');
        btnKtp.classList.remove('hidden');
        btnKtp.style.display = 'flex';
    } else {
        btnKtp.classList.add('hidden');
        btnKtp.style.display = 'none';
    }

    const btnProof = document.getElementById('btnViewProof');
    if (tenant.payment_proof_url) {
        btnProof.onclick = () => window.open(tenant.payment_proof_url, '_blank');
        btnProof.classList.remove('hidden');
        btnProof.style.display = 'flex';
    } else {
        btnProof.classList.add('hidden');
        btnProof.style.display = 'none';
    }

    // Store Tenant ID for Actions
    document.getElementById('detailTenantId').value = tenant.id;

    // Show Modal
    document.getElementById('tenantDetailModal').classList.remove('hidden');
}

function closeTenantDetailModal() {
    document.getElementById('tenantDetailModal').classList.add('hidden');
}

function openEmptyRoomOptions(roomIndex) {
    document.getElementById('selectedRoomIndex').value = roomIndex;
    document.getElementById('emptyRoomTitle').textContent = `Kamar ${roomIndex}`;
    document.getElementById('emptyRoomOptionsModal').classList.remove('hidden');
}

function chooseNewTenant() {
    const roomIndex = document.getElementById('selectedRoomIndex').value;
    document.getElementById('emptyRoomOptionsModal').classList.add('hidden');
    openAddTenantModal();
    // Pre-select room
    setTimeout(() => {
        const select = document.getElementById('roomSelect');
        if (select) select.value = roomIndex;
    }, 100);
}

// --- Maintenance Logic ---

async function setMaintenance() {
    const roomIndex = document.getElementById('selectedRoomIndex').value;
    const rawProjectName = sessionStorage.getItem('active_project_name') || 'project_umum';

    if (!confirm(`Set Kamar ${roomIndex} ke status Maintenance?`)) return;

    document.getElementById('emptyRoomOptionsModal').classList.add('hidden');

    try {
        const { error } = await client
            .from('tenants')
            .insert([
                {
                    project_name: rawProjectName,
                    room_number: roomIndex,
                    name: 'MAINTENANCE',
                    status: 'MAINTENANCE',
                    check_in_date: new Date().toISOString().split('T')[0],
                    check_out_date: new Date().toISOString().split('T')[0],
                    duration: 0
                }
            ]);

        if (error) throw error;

        showSuccess(`Kamar ${roomIndex} sekarang dalam perbaikan.`);
        await updateDashboardStats();

    } catch (e) {
        console.error(e);
        showError("Gagal update status: " + e.message);
    }
}

function openMaintenanceOptions(roomIndex) {
    document.getElementById('selectedRoomIndex').value = roomIndex;
    const title = document.getElementById('maintenanceRoomTitle');
    if (title) title.textContent = `Kamar ${roomIndex} (Perbaikan)`;
    document.getElementById('maintenanceOptionsModal').classList.remove('hidden');
}

async function readyForRent() {
    const roomIndex = document.getElementById('selectedRoomIndex').value;
    document.getElementById('maintenanceOptionsModal').classList.add('hidden');

    try {
        const tenant = window.activeTenants.find(t => t.room_number == roomIndex && (t.status === 'MAINTENANCE' || t.name === 'MAINTENANCE'));
        if (!tenant) {
            showError("Data maintenance tidak ditemukan");
            return;
        }

        const { error } = await client
            .from('tenants')
            .delete()
            .eq('id', tenant.id);

        if (error) throw error;

        showSuccess(`Kamar ${roomIndex} siap disewa kembali!`);
        updateDashboardStats();

    } catch (e) {
        console.error(e);
        showError("Error: " + e.message);
    }
}

// --- Checkout History & Due Soon ---

async function renderCheckoutHistory() {
    const rawProjectName = sessionStorage.getItem('active_project_name') || '';
    const tableBody = document.getElementById('checkoutHistoryTable');
    if (!tableBody) return;

    try {
        const { data, error } = await client
            .from('tenants')
            .select('*')
            .eq('project_name', rawProjectName)
            .eq('status', 'CHECKED_OUT')
            .order('check_out_date', { ascending: false })
            .limit(7);

        if (error) throw error;

        if (!data || data.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="5" class="text-center py-4 text-slate-500">Belum ada riwayat checkout.</td></tr>';
            return;
        }

        let html = '';

        data.forEach(t => {
            const dateObj = new Date(t.check_out_date);
            const dateStr = dateObj.toLocaleDateString('id-ID', { day: 'numeric', month: 'short', year: 'numeric' });
            const displayRoom = `Kamar ${t.room_number || '-'}`;

            let docsHtml = '<div class="flex gap-2">';
            if (t.ktp_photo_url) {
                docsHtml += `<a href="${t.ktp_photo_url}" target="_blank" class="text-indigo-600 hover:text-indigo-800" title="Foto KTP"><i class="fas fa-id-card"></i></a>`;
            }
            if (t.payment_proof_url) {
                docsHtml += `<a href="${t.payment_proof_url}" target="_blank" class="text-emerald-600 hover:text-emerald-800" title="Bukti Transfer"><i class="fas fa-receipt"></i></a>`;
            }
            if (!t.ktp_photo_url && !t.payment_proof_url) {
                docsHtml += `<span class="text-slate-300">-</span>`;
            }
            docsHtml += '</div>';

            html += `
                <tr class="hover:bg-slate-50 transition">
                    <td class="px-4 py-3 font-medium text-slate-600">${dateStr}</td>
                    <td class="px-4 py-3 font-bold text-slate-800">${t.name}</td>
                    <td class="px-4 py-3 text-slate-500">${displayRoom}</td>
                    <td class="px-4 py-3 text-slate-500 text-xs font-mono">${t.phone || '-'}</td>
                    <td class="px-4 py-3">${docsHtml}</td>
                </tr>
            `;
        });

        tableBody.innerHTML = html;

    } catch (err) {
        console.error(err);
        tableBody.innerHTML = '<tr><td colspan="5" class="text-center py-4 text-red-500">Gagal memuat data.</td></tr>';
    }
}

async function renderDueSoon() {
    const container = document.getElementById('dueSoonContainer');
    if (!container) return;

    container.innerHTML = '<div class="text-center py-4"><i class="fas fa-circle-notch fa-spin text-indigo-500"></i></div>';

    const rawProjectName = sessionStorage.getItem('active_project_name') || '';

    try {
        const { data, error } = await client
            .from('tenants')
            .select('*')
            .eq('project_name', rawProjectName)
            .eq('status', 'ACTIVE');

        if (error) throw error;

        const today = new Date();
        today.setHours(0, 0, 0, 0);

        const upcoming = data.map(t => {
            const dueDate = new Date(t.check_out_date);
            dueDate.setHours(0, 0, 0, 0);
            const diffTime = dueDate - today;
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
            return { ...t, diffDays, dueDate };
        }).filter(t => t.diffDays <= 7)
            .sort((a, b) => a.diffDays - b.diffDays);

        if (upcoming.length === 0) {
            container.innerHTML = '<p class="text-xs text-slate-400 text-center py-2">Tidak ada yang jatuh tempo dekat.</p>';
            return;
        }

        let html = '';
        upcoming.forEach(t => {
            let statusColor = 'bg-slate-100 text-slate-500';
            let timeText = '';
            let dateText = t.dueDate.toLocaleDateString('id-ID', { day: 'numeric', month: 'short' });

            if (t.diffDays < 0) {
                statusColor = 'bg-red-100 text-red-600';
                timeText = `Lewat ${Math.abs(t.diffDays)} Hari`;
            } else if (t.diffDays === 0) {
                statusColor = 'bg-orange-100 text-orange-600';
                timeText = 'Hari Ini';
            } else if (t.diffDays === 1) {
                statusColor = 'bg-orange-50 text-orange-600';
                timeText = 'Besok';
            } else {
                statusColor = 'bg-slate-50 text-slate-600';
                timeText = `${t.diffDays} Hari`;
            }

            const initial = t.name.charAt(0).toUpperCase();

            html += `
                <div class="flex items-center justify-between p-3 rounded-xl hover:bg-slate-50 border border-slate-100 transition mb-2">
                    <div class="flex items-center gap-3">
                        <div class="w-10 h-10 rounded-full bg-indigo-50 flex items-center justify-center text-indigo-600 font-bold border border-indigo-100">
                            ${initial}
                        </div>
                        <div>
                            <p class="text-sm font-bold text-slate-800">Kamar ${t.room_number}</p>
                            <p class="text-xs text-slate-500 truncate max-w-[100px]">${t.name}</p>
                        </div>
                    </div>
                    <div class="text-right">
                        <span class="px-2 py-1 rounded-lg text-[10px] font-bold ${statusColor}">${timeText}</span>
                        <p class="text-[10px] text-slate-400 mt-1">${dateText}</p>
                    </div>
                </div>
            `;
        });

        container.innerHTML = html;

    } catch (e) {
        console.error(e);
        container.innerHTML = '<p class="text-xs text-red-400 text-center">Gagal memuat data.</p>';
    }
}

// --- Checkout Logic ---
async function checkOut() {
    const tenantId = document.getElementById('detailTenantId').value;
    const tenantName = document.getElementById('detailName').textContent;

    if (!confirm(`Apakah penghuni ${tenantName} yakin ingin Check Out?`)) {
        return;
    }

    const btn = document.querySelector('button[onclick="checkOut()"]');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
    btn.disabled = true;

    try {
        const { error } = await client
            .from('tenants')
            .update({ status: 'CHECKED_OUT' })
            .eq('id', tenantId);

        if (error) throw error;

        showSuccess("Check Out Berhasil! Kamar sekarang kosong.");
        closeTenantDetailModal();
        renderRoomGrid();
        updateDashboardStats();

    } catch (e) {
        console.error("Check Out Error:", e);
        showError("Gagal melakukan Check Out: " + e.message);
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}


// --- QR & Share Logic ---

function openShareModal() {
    const project = sessionStorage.getItem('active_project_name') || 'project_umum';

    // Check local dev vs prod
    const currentPath = window.location.pathname;
    const dir = currentPath.substring(0, currentPath.lastIndexOf('/'));
    const protocol = window.location.protocol;
    const host = window.location.host;

    // Full URL to public_booking.html
    const link = `${protocol}//${host}${dir}/public_booking.html?project=${encodeURIComponent(project)}`;

    document.getElementById('shareProjectName').textContent = project;
    document.getElementById('shareLinkInput').value = link;
    document.getElementById('shareModal').classList.remove('hidden');

    const qrContainer = document.getElementById('qrcode');
    qrContainer.innerHTML = '';
    new QRCode(qrContainer, {
        text: link,
        width: 160,
        height: 160,
        colorDark: "#4f46e5",
        colorLight: "#ffffff",
        correctLevel: QRCode.CorrectLevel.H
    });
}

function copyShareLink() {
    const copyText = document.getElementById("shareLinkInput");
    copyText.select();
    copyText.setSelectionRange(0, 99999);

    navigator.clipboard.writeText(copyText.value).then(() => {
        showSuccess("Link berhasil disalin!");
    }).catch(err => {
        showError("Gagal menyalin link.");
        alert("Link: " + copyText.value);
    });
}

// --- Date Calculation Logic ---
function updateCheckOutDate() {
    const startDateStr = document.getElementById('tenantCheckInDate').value;
    const durationStr = document.getElementById('tenantDuration').value;

    if (startDateStr && durationStr) {
        const startDate = new Date(startDateStr);
        const duration = parseInt(durationStr, 10);

        if (!isNaN(startDate.getTime()) && !isNaN(duration)) {
            startDate.setDate(startDate.getDate() + duration);
            const year = startDate.getFullYear();
            const month = String(startDate.getMonth() + 1).padStart(2, '0');
            const day = String(startDate.getDate()).padStart(2, '0');
            document.getElementById('tenantCheckOutDate').value = `${year}-${month}-${day}`;
        }
    }
}

// Auto-run this whenever script loads? No, safer in DOMContentLoaded or explicitly called.
document.addEventListener('DOMContentLoaded', () => {
    const checkInInput = document.getElementById('tenantCheckInDate');
    const durationInput = document.getElementById('tenantDuration');

    if (checkInInput && !checkInInput.value) {
        checkInInput.value = new Date().toISOString().split('T')[0];
    }

    if (checkInInput) checkInInput.addEventListener('change', updateCheckOutDate);
    if (durationInput) durationInput.addEventListener('input', updateCheckOutDate);

    updateCheckOutDate();
});

// --- OCR Scanner (Gemini) ---
async function scanKTP() {
    const fileInput = document.getElementById('ktpFile');
    const file = fileInput.files[0];
    if (!file) {
        showWarning("Pilih file KTP terlebih dahulu!");
        return;
    }

    const btn = document.getElementById('btnScan');
    const originalText = btn.innerHTML;

    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Mengirim ke Gemini AI...';
    btn.disabled = true;

    const formData = new FormData();
    formData.append('image', file);

    try {
        const response = await fetch('http://localhost:5000/ocr-gemini', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) throw new Error('Gagal menghubungi Server OCR');

        const result = await response.json();

        if (result.success && result.data) {
            const d = result.data;

            if (d.nik) document.getElementById('tenantNik').value = d.nik;
            if (d.nama) document.getElementById('tenantName').value = d.nama;

            let marital = 'Belum Kawin';
            if (d.status_perkawinan) {
                const status = d.status_perkawinan.toUpperCase();
                if (status.includes('KAWIN') && !status.includes('BELUM')) marital = 'Kawin';
            }
            document.getElementById('tenantMarital').value = marital;

            showSuccess("✅ Scan Berhasil! Data KTP telah diekstrak.");
        } else {
            showError("Gagal mengekstrak data. Coba foto yang lebih jelas.");
        }

    } catch (e) {
        console.error(e);
        showError("Server OCR Error: " + e.message);
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

function showWarning(msg) {
    Toast.show(msg, 'warning');
}

// --- Extension Lease Logic ---
function openExtendModal() {
    const tenantId = document.getElementById('detailTenantId').value;
    const tenant = window.activeTenants ? window.activeTenants.find(t => t.id == tenantId) : null;

    if (!tenant) return;

    document.getElementById('extTenantName').textContent = tenant.name;
    document.getElementById('extCurrentRoom').textContent = `Kamar ${tenant.room_number}`;
    document.getElementById('extCurrentDueDate').textContent = tenant.check_out_date;

    document.getElementById('extDays').value = 30;
    document.getElementById('extAmount').value = tenant.rent_amount || '';
    document.getElementById('extProof').value = '';

    const select = document.getElementById('extRoomSelect');
    select.innerHTML = '<option value="">Tetap di Kamar yang Sama</option>';

    const totalRooms = window.currentProjectTotalRooms || 10;
    for (let i = 1; i <= totalRooms; i++) {
        const isOccupied = window.activeTenants.some(t => t.room_number == i);

        if (!isOccupied) {
            const opt = document.createElement('option');
            opt.value = i;
            opt.textContent = `Pindah ke Kamar ${i} (Kosong)`;
            select.appendChild(opt);
        }
    }

    calculateNewDueDate();
    document.getElementById('extendLeaseModal').classList.remove('hidden');
    closeTenantDetailModal();
}

function calculateNewDueDate() {
    const currentDueDateStr = document.getElementById('extCurrentDueDate').textContent;
    const days = parseInt(document.getElementById('extDays').value) || 0;

    if (currentDueDateStr && days > 0) {
        const current = new Date(currentDueDateStr);
        current.setDate(current.getDate() + days);
        document.getElementById('extNewDueDate').textContent = current.toISOString().split('T')[0];
    }
}

async function submitExtension() {
    const tenantId = document.getElementById('detailTenantId').value;
    const days = document.getElementById('extDays').value;
    const amount = document.getElementById('extAmount').value;
    const newRoom = document.getElementById('extRoomSelect').value;
    const proofFile = document.getElementById('extProof').files[0];
    const rawProjectName = sessionStorage.getItem('active_project_name') || '';

    if (!days || !amount) {
        showError("Mohon isi durasi dan nominal pembayaran!");
        return;
    }

    const btn = document.querySelector('button[onclick="submitExtension()"]');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
    btn.disabled = true;

    try {
        let proofUrl = null;
        if (proofFile) {
            const safeName = document.getElementById('extTenantName').textContent.replace(/[^a-zA-Z0-9]/g, '_').toLowerCase();
            proofUrl = await uploadToImageKit(
                proofFile,
                `ext_${safeName}_${Date.now()}.${proofFile.name.split('.').pop()}`,
                `/${rawProjectName.replace(/\s+/g, '_').toLowerCase()}/extensions`
            );
        }

        const newDueDate = document.getElementById('extNewDueDate').textContent;
        const updateData = {
            check_out_date: newDueDate,
            rent_amount: parseInt(amount)
        };

        if (newRoom) {
            updateData.room_number = newRoom;
        }

        if (proofUrl) {
            updateData.payment_proof_url = proofUrl;
        }

        const { error } = await client
            .from('tenants')
            .update(updateData)
            .eq('id', tenantId);

        if (error) throw error;

        const tenantName = document.getElementById('extTenantName').textContent;
        const roomNum = newRoom || document.getElementById('extCurrentRoom').textContent.replace('Kamar ', '');

        await client.from('payment_transactions').insert({
            tenant_id: tenantId,
            project_name: rawProjectName,
            room_number: roomNum,
            tenant_name: tenantName,
            amount: parseInt(amount),
            description: `Perpanjangan Sewa (+${days} Hari)${newRoom ? ' & Pindah Kamar' : ''}`,
            category: 'RENT',
            proof_url: proofUrl
        });

        showSuccess("Perpanjangan Berhasil Disimpan!");
        document.getElementById('extendLeaseModal').classList.add('hidden');

        updateDashboardStats();
        renderCheckoutHistory();

    } catch (e) {
        console.error(e);
        showError("Gagal memperpanjang: " + e.message);
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

// --- Print Receipt ---
async function printReceipt() {
    try {
        if (!window.jspdf) throw new Error("Library jsPDF tidak dimuat. Periksa koneksi internet.");

        const tenantId = document.getElementById('detailTenantId').value;
        const tenant = window.activeTenants ? window.activeTenants.find(t => t.id == tenantId) : null;

        if (!tenant) throw new Error("Data penyewa tidak ditemukan/sinkron.");

        const { jsPDF } = window.jspdf;
        const doc = new jsPDF({
            orientation: 'portrait',
            unit: 'mm',
            format: [80, 150]
        });

        const centerX = 40;
        const leftM = 5;
        const rightM = 75;
        let cursorY = 10;

        function centerText(text, y, size = 10, weight = "normal") {
            doc.setFontSize(size);
            doc.setFont("helvetica", weight);
            doc.text(text, centerX, y, { align: "center" });
        }

        function drawLine(y) {
            doc.setLineWidth(0.2);
            doc.line(leftM, y, rightM, y);
        }

        centerText("SUNRISE KOST", cursorY, 14, "bold");
        cursorY += 5;
        centerText("BANTA-BANTAENG", cursorY, 10, "bold");
        cursorY += 5;
        doc.setFontSize(8);
        doc.setFont("helvetica", "normal");
        doc.text("Jl. Banta-Bantaeng, Makassar", centerX, cursorY, { align: "center" });
        cursorY += 5;
        drawLine(cursorY);
        cursorY += 5;

        // Sequence
        let seqNumber = 'XXXX';
        const projectName = sessionStorage.getItem('active_project_name') || 'project_umum';
        try {
            const { data, error } = await client.rpc('increment_receipt_counter', { project_text: projectName });
            if (!error) seqNumber = data.toString().padStart(4, '0');
        } catch (e) { console.warn("Seq Error", e); }

        const today = new Date();
        const dateStr = today.toLocaleDateString('id-ID');
        const timeStr = today.toLocaleTimeString('id-ID');
        const invNo = `INV/${today.getFullYear()}/${seqNumber}`;

        doc.setFontSize(8);
        doc.text(dateStr + " " + timeStr, leftM, cursorY);
        doc.text(invNo, rightM, cursorY, { align: "right" });
        cursorY += 7;
        drawLine(cursorY);
        cursorY += 5;

        // Content
        doc.setFont("helvetica", "bold");
        doc.text("Penyewa:", leftM, cursorY);
        cursorY += 5;
        doc.setFont("helvetica", "normal");
        doc.text(tenant.name.toUpperCase(), leftM, cursorY);
        cursorY += 7;

        doc.setFont("helvetica", "bold");
        doc.text("Kamar:", leftM, cursorY);
        doc.setFont("helvetica", "normal");
        doc.text(`Kamar ${tenant.room_number}`, rightM, cursorY, { align: "right" });
        cursorY += 7;

        doc.setFont("helvetica", "bold");
        doc.text("Keterangan:", leftM, cursorY);
        cursorY += 5;
        doc.setFont("helvetica", "normal");
        const desc = `Sewa ${tenant.check_in_date} s.d ${tenant.check_out_date}`;
        doc.text(desc, leftM, cursorY, { maxWidth: 70 });
        cursorY += 10;

        drawLine(cursorY);
        cursorY += 6;

        doc.setFontSize(12);
        doc.setFont("helvetica", "bold");
        doc.text("TOTAL", leftM, cursorY);

        const fmt = new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', maximumFractionDigits: 0 });
        doc.text(fmt.format(tenant.rent_amount), rightM, cursorY, { align: "right" });
        cursorY += 10;
        drawLine(cursorY);
        cursorY += 8;

        centerText("TERIMA KASIH", cursorY, 10, "bold");
        cursorY += 5;
        doc.setFontSize(7);
        doc.setFont("helvetica", "italic");
        doc.text("Struk ini adalah bukti pembayaran yang sah.", centerX, cursorY, { align: "center" });

        const safeName = tenant.name.replace(/[^a-zA-Z0-9]/g, '_');
        doc.save(`Struk_${safeName}_${tenant.room_number}.pdf`);

    } catch (err) {
        console.error("Print Error:", err);
        showError("Gagal mencetak struk: " + err.message);
    }
}
