let countdownInterval;

async function generateId() {
    const pid = document.getElementById('pidInput').value.trim();
    if (!pid) return;

    const btn = document.getElementById('generateBtn');
    btn.disabled = true;
    btn.innerText = 'Generating...';
    
    hideMessages();

    try {
        const response = await fetch('/api/generate_id', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ pid })
        });

        const data = await response.json();

        if (!response.ok) {
            showMessage(data.error || 'An error occurred', 'error');
            
            // If it's an existing valid ID, show the remaining time and the image
            if (response.status === 403 && data.remaining_seconds) {
                startTimer(data.remaining_seconds);
                showResult(data.image_url);
            }
        } else {
            showMessage(data.message, 'success');
            showResult(data.image_url);
            // New ID generated, valid for 8 hours
            startTimer(8 * 3600);
        }
    } catch (error) {
        showMessage('Network error, please try again later.', 'error');
    } finally {
        btn.disabled = false;
        btn.innerText = 'Generate Digital ID';
    }
}

function showMessage(msg, type) {
    const box = document.getElementById('messageBox');
    box.textContent = msg;
    box.className = type;
}

function hideMessages() {
    const box = document.getElementById('messageBox');
    box.className = 'hidden';
    document.getElementById('resultContent').classList.add('hidden');
    document.getElementById('emptyState').classList.remove('hidden');
    clearInterval(countdownInterval);
}

function showResult(url) {
    const preview = document.getElementById('idPreview');
    const download = document.getElementById('downloadBtn');
    
    preview.src = url;
    download.href = url;
    
    document.getElementById('emptyState').classList.add('hidden');
    document.getElementById('resultContent').classList.remove('hidden');
}

function startTimer(seconds) {
    clearInterval(countdownInterval);
    const timerDisplay = document.getElementById('timerDisplay');
    
    let remaining = seconds;
    
    function updateDisplay() {
        if (remaining <= 0) {
            clearInterval(countdownInterval);
            timerDisplay.innerText = "Expired";
            document.querySelector('.status-indicator').style.backgroundColor = '#ef4444';
            document.querySelector('.status-indicator').style.boxShadow = '0 0 0 2px rgba(239, 68, 68, 0.2)';
            showMessage("ID expired. You can generate a new one now.", "success");
            return;
        }
        
        const h = Math.floor(remaining / 3600);
        const m = Math.floor((remaining % 3600) / 60);
        const s = Math.floor(remaining % 60);
        
        timerDisplay.innerText = 
            "Valid for: " + 
            String(h).padStart(2, '0') + ':' + 
            String(m).padStart(2, '0') + ':' + 
            String(s).padStart(2, '0');
            
        remaining--;
    }
    
    // Reset indicator to green
    document.querySelector('.status-indicator').style.backgroundColor = '#22c55e';
    document.querySelector('.status-indicator').style.boxShadow = '0 0 0 2px rgba(34, 197, 94, 0.2)';
    
    updateDisplay();
    countdownInterval = setInterval(updateDisplay, 1000);
}
