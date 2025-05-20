// Client-side RSA encryption for AuthVault
async function getPublicKey() {
    try {
        const response = await fetch('/get_public_key');
        return (await response.json()).public_key;
    } catch (error) {
        console.error('Error:', error);
        return null;
    }
}

// Parse PEM format to get the key
function parsePublicKey(pemKey) {
    return pemKey
        .replace('-----BEGIN PUBLIC KEY-----', '')
        .replace('-----END PUBLIC KEY-----', '')
        .replace(/[\n\r\s]/g, '');
}

// RSA encrypt the password
async function encryptPassword(password, publicKeyPem) {
    try {
        const cleanKey = publicKeyPem.replace(/-----(BEGIN|END) PUBLIC KEY-----|\n|\r|\s/g, '');
        const binaryDer = Uint8Array.from(atob(cleanKey), c => c.charCodeAt(0));
        
        const cryptoKey = await window.crypto.subtle.importKey(
            'spki',
            binaryDer,
            {name: 'RSA-OAEP', hash: 'SHA-256'},
            false,
            ['encrypt']
        );

        const encrypted = await window.crypto.subtle.encrypt(
            {name: 'RSA-OAEP'},
            cryptoKey,
            new TextEncoder().encode(password)
        );

        return btoa(String.fromCharCode(...new Uint8Array(encrypted)));
    } catch (error) {
        throw new Error('Encryption failed');
    }
}

// Handle form submissions
document.addEventListener('DOMContentLoaded', () => {
    ['login-form', 'register-form'].forEach(formId => {
        const form = document.getElementById(formId);
        if (form) {
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                try {
                    const formData = new FormData();
                    formData.append('username', document.getElementById('username').value);
                    formData.append('password', await encryptPassword(
                        document.getElementById('password').value,
                        await getPublicKey()
                    ));

                    const response = await fetch(formId === 'login-form' ? '/login' : '/create_account', {
                        method: 'POST',
                        body: formData
                    });

                    if (response.redirected) {
                        window.location.href = response.url;
                    } else if (!response.ok) {
                        throw new Error(await response.text());
                    }
                } catch (error) {
                    const errorDiv = document.getElementById('error-message') || document.createElement('div');
                    errorDiv.className = 'error';
                    errorDiv.textContent = error.message;
                    errorDiv.style.display = 'block';
                    if (!document.getElementById('error-message')) {
                        form.appendChild(errorDiv);
                    }
                }
            });
        }
    });
});