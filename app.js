// Supabase configuration (replace with real project values)
const supabaseUrl = "https://xyzcompany.supabase.co";
const supabaseKey = "eyJxGcio..."; // Use the anon key from Project Settings -> API
const supabase = supabase.createClient(supabaseUrl, supabaseKey);

// Example function to fetch all rows from 'barang'
async function ambilDataBarang() {
  const { data, error } = await supabase.from("barang").select("*");

  if (error) {
    console.error("Ada error:", error);
  } else {
    console.log("Data berhasil diambil:", data);
    // renderTable(data);
  }
}

document.getElementById("btnLogin").addEventListener("click", function () {
  const role = document.getElementById("role").value;

  if (!role) {
    alert("Silakan pilih role terlebih dahulu.");
    return;
  }

  // Redirect ke halaman berbeda sesuai role
  switch (role) {
    case "direktur":
      window.location.href = "dashboard_direktur.html";
      break;
    case "finance":
      window.location.href = "dashboard_finance.html";
      break;
    case "operasional":
      window.location.href = "dashboard_operasional.html";
      break;
    case "marketing":
      window.location.href = "dashboard_marketing.html";
      break;
    default:
      alert("Role tidak dikenali.");
  }
});
