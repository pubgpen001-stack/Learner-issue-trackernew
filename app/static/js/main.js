document.addEventListener('DOMContentLoaded', function() {
    var chatMessages = document.getElementById('chat-messages');
    var messageInput = document.getElementById('message-input');
    var sendBtn = document.getElementById('send-btn');

    if (!chatMessages || !messageInput || !sendBtn) return;

    var pathParts = window.location.pathname.split('/');
    var issueId = pathParts[pathParts.length - 1];

    var socket = io();

    socket.on('connect', function() {
        socket.emit('join_room', { issue_id: issueId });
    });

    socket.on('new_message', function(data) {
        var noMessages = document.getElementById('no-messages');
        if (noMessages) noMessages.remove();

        var msgDiv = document.createElement('div');
        msgDiv.className = 'chat-bubble';
        let contentHtml = '';
        if (data.is_flagged) {
            contentHtml = '<p class="mb-0 mt-1"><span class="flagged-content" style="filter: blur(5px); transition: filter 0.3s; cursor: pointer;" onclick="this.style.filter=\\\'none\\\'; this.nextElementSibling.style.display=\\\'none\\\'">' + data.content + '</span><span class="badge bg-danger ms-2" style="font-size: 0.7rem;">Hidden: Flagged Review</span></p>';
        } else {
            contentHtml = '<p class="mb-0 mt-1">' + data.content + '</p>';
        }

        msgDiv.innerHTML = '<strong>' + data.username + '</strong>' +
            '<small class="text-muted ms-2">' + data.sent_at + '</small>' +
            contentHtml;
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    });

    sendBtn.addEventListener('click', function() {
        var content = messageInput.value.trim();
        if (content) {
            socket.emit('send_message', { issue_id: issueId, content: content });
            messageInput.value = '';
        }
    });

    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendBtn.click();
        }
    });

    if (chatMessages) {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
});

document.addEventListener('DOMContentLoaded', function() {
    var toastElList = [].slice.call(document.querySelectorAll('.toast'));
    var toastList = toastElList.map(function(toastEl) {
        var toast = new bootstrap.Toast(toastEl, { autohide: true, delay: 5000 });
        toast.show();
        return toast;
    });
});

/* ── Theme Toggle ── */
document.addEventListener('DOMContentLoaded', function() {
    var toggle = document.getElementById('theme-toggle');
    var iconLight = document.getElementById('theme-icon-light');
    var iconDark = document.getElementById('theme-icon-dark');

    if (!toggle) return;

    function updateIcons() {
        var current = document.body.getAttribute('data-bs-theme');
        if (current === 'dark') {
            iconLight.style.display = 'none';
            iconDark.style.display = 'inline';
        } else {
            iconLight.style.display = 'inline';
            iconDark.style.display = 'none';
        }
    }

    updateIcons();

    toggle.addEventListener('click', function() {
        var current = document.body.getAttribute('data-bs-theme');
        var next = current === 'dark' ? 'light' : 'dark';
        document.body.setAttribute('data-bs-theme', next);
        localStorage.setItem('theme', next);
        updateIcons();
    });
});