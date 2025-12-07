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
