// --- ImageKit Helper ---
async function uploadToImageKit(file, fileName, folder) {
    const publicKey = "public_ZzBxgXWQzaOlUvj+11M6G39Si4s=";
    const privateKey = "private_d1MgRwtWJzF4hasu3e0ZhaC+e3Q=";

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
        console.error("IK Error:", err);
        throw new Error(err.message || JSON.stringify(err));
    }

    const data = await response.json();
    return data.url;
}
