document.addEventListener('DOMContentLoaded', () => {
    
    // --- Elementy UI Uploadu ---
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const fileInfo = document.getElementById('file-info');
    const fileNameDisplay = document.getElementById('file-name');
    const processBtn = document.getElementById('process-btn');
    const statusBox = document.getElementById('status-box');
    const loader = document.getElementById('loader');
    const statusMessage = document.getElementById('status-message');
    const chatContext = document.getElementById('chat-context');



    let selectedFile = null;
    let processedFilename = ''; // nazwa pliku po przetworzeniu (_forPowerFI.xlsx)

    // --- Inicjalizacja: pobierz ostatni przetworzony plik z serwera ---
    (async () => {
        try {
            const res = await fetch('/api/current-file');
            const data = await res.json();
            if (data.filename) {
                processedFilename = data.filename;
                // Ustaw etykietę "Aktualny plik" w nagłówku czatu
                const nameWithoutSuffix = data.filename.replace('_forPowerFI.xlsx', '');
                chatContext.textContent = nameWithoutSuffix;
                console.log('[Chat] Przywrócono kontekst pliku:', processedFilename);
            }
        } catch (e) {
            console.warn('[Chat] Nie udało się pobrać aktualnego pliku:', e);
        }
    })();

    // --- Obsługa Drag & Drop ---
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drag-over');
    });

    dropZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
        
        if (e.dataTransfer.files.length) {
            handleFileSelect(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
            handleFileSelect(e.target.files[0]);
        }
    });

    function handleFileSelect(file) {
        const validExtensions = ['.xls', '.xlsx'];
        const fileName = file.name;
        const fileExt = fileName.substring(fileName.lastIndexOf('.')).toLowerCase();

        if (validExtensions.includes(fileExt)) {
            selectedFile = file;
            fileNameDisplay.textContent = fileName;
            fileInfo.classList.remove('hidden');
            processBtn.disabled = false;
            
            // Ukryj ewentualne poprzednie wyniki
            statusBox.classList.add('hidden');
            
            // Zaktualizuj kontekst w czacie
            chatContext.textContent = fileName;
        } else {
            alert('Proszę wybrać plik w formacie .xls lub .xlsx');
            resetFileSelect();
        }
    }

    function resetFileSelect() {
        selectedFile = null;
        fileInput.value = '';
        fileInfo.classList.add('hidden');
        processBtn.disabled = true;
    }

    // --- Wysyłanie pliku do przetworzenia ---
    processBtn.addEventListener('click', async () => {
        if (!selectedFile) return;

        // UI podczas ładowania
        processBtn.disabled = true;
        statusBox.classList.remove('hidden');
        loader.classList.remove('hidden');
        statusMessage.textContent = 'Trwa dodawanie do bazy...';
        statusMessage.style.color = 'var(--text-main)';

        const formData = new FormData();
        formData.append('file', selectedFile);

        try {
            const response = await fetch('/api/process-file', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            loader.classList.add('hidden');

            if (data.success) {
                statusMessage.textContent = data.message;
                statusMessage.style.color = 'var(--ps-green-dark)';
                
                // Zapamiętaj nazwę przetworzonego pliku — serwer zwraca ją bezpośrednio
                processedFilename = data.processed_filename || `${selectedFile.name.substring(0, selectedFile.name.lastIndexOf('.'))}_forPowerFI.xlsx`;
                console.log('[Chat] Kontekst pliku ustawiony:', processedFilename);
            } else {
                statusMessage.textContent = data.error;
                statusMessage.style.color = 'red';
                processBtn.disabled = false;
            }

        } catch (error) {
            loader.classList.add('hidden');
            statusMessage.textContent = 'Błąd połączenia z serwerem.';
            statusMessage.style.color = 'red';
            processBtn.disabled = false;
            console.error(error);
        }
    });

    // --- Elementy UI Chatu ---
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatWindow = document.getElementById('chat-window');

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const message = chatInput.value.trim();
        if (!message) return;

        // Dodaj wiadomość użytkownika
        appendMessage(message, 'user-message');
        chatInput.value = '';

        // Pokaż wskaźnik pisania
        const typingIndicator = showTypingIndicator();
        chatWindow.scrollTop = chatWindow.scrollHeight;

        try {
            const formData = new FormData();
            formData.append('prompt', message);
            if (processedFilename) {
                formData.append('filename', processedFilename);
            }

            const response = await fetch('/api/chat', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            
            // Usuń wskaźnik pisania
            typingIndicator.remove();

            if (data.success) {
                appendMessage(data.response, 'ai-message');
            } else {
                appendMessage('Wystąpił błąd: ' + data.error, 'ai-message');
            }
        } catch (error) {
            typingIndicator.remove();
            appendMessage('Nie udało się połączyć z serwerem czatu.', 'ai-message');
        }
    });

    function appendMessage(text, className) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${className}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.textContent = text;
        
        messageDiv.appendChild(contentDiv);
        chatWindow.appendChild(messageDiv);
        
        // Przewiń na dół
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    function showTypingIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'typing-indicator';
        indicator.innerHTML = `
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        `;
        chatWindow.appendChild(indicator);
        return indicator;
    }
});
