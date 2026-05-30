/* ═══════════════════════════════════════════════════════════════════════
   AURA MEDIX — AI Doctor Chat JS
   Fully working fetch-based chat with typing indicator
   ═══════════════════════════════════════════════════════════════════════ */

const ChatApp = {
  history: [],
  isTyping: false,

  init() {
    this.messagesEl = document.getElementById('chatMessages');
    this.inputEl    = document.getElementById('chatInput');
    this.sendBtn    = document.getElementById('sendBtn');
    this.clearBtn   = document.getElementById('clearChatBtn');
    this.newBtn     = document.getElementById('newChatBtn');

    if (!this.messagesEl || !this.inputEl) {
      console.error('[ChatApp] Required DOM elements not found');
      return;
    }

    // Send on button click
    this.sendBtn?.addEventListener('click', () => this.sendMessage());

    // Send on Enter (not Shift+Enter)
    this.inputEl.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        this.sendMessage();
      }
    });

    // Auto-resize textarea
    this.inputEl.addEventListener('input', () => {
      this.inputEl.style.height = 'auto';
      this.inputEl.style.height = Math.min(this.inputEl.scrollHeight, 120) + 'px';
    });

    // Clear chat
    this.clearBtn?.addEventListener('click', () => {
      this.messagesEl.innerHTML = '';
      this.history = [];
      this.addMessage('assistant', 'Chat cleared. How can I help you today?');
    });

    // New chat
    this.newBtn?.addEventListener('click', () => {
      this.messagesEl.innerHTML = '';
      this.history = [];
      this.addMessage('assistant', "Hello! I'm AURA, your AI health assistant. How can I help you today?");
    });

    // Quick prompt chips
    document.querySelectorAll('.qp-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const prompt = btn.dataset.prompt;
        if (prompt) {
          this.inputEl.value = prompt;
          this.sendMessage();
        }
      });
    });
  },

  async sendMessage() {
    const text = this.inputEl.value.trim();
    if (!text || this.isTyping) return;

    this.addMessage('user', text);
    this.inputEl.value = '';
    this.inputEl.style.height = 'auto';
    this.history.push({ role: 'user', content: text });
    this.setTyping(true);

    try {
      const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content || '';
      const response = await fetch('/ai/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
          message: text,
          history: this.history.slice(-10)
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      this.setTyping(false);

      if (data.success) {
        this.addMessage('assistant', data.response);
        this.history.push({ role: 'assistant', content: data.response });

        // Show follow-up if present
        if (data.follow_up) {
          setTimeout(() => this.addMessage('assistant', data.follow_up), 800);
        }
      } else {
        throw new Error(data.error || 'Unknown server error');
      }

    } catch (err) {
      console.error('[ChatApp] Fetch error:', err);
      this.setTyping(false);
      this.addMessage('error', `Connection error: ${err.message}. Please check your server and try again.`);
    }
  },

  addMessage(role, text) {
    const wrap = document.createElement('div');
    wrap.className = `msg ${role === 'user' ? 'user' : 'assistant'}`;

    const av = document.createElement('div');
    av.className = `msg-av ${role === 'user' ? 'user-av' : 'ai'}`;
    av.textContent = role === 'user' ? (window._userInitial || 'U') : '🤖';

    const bubble = document.createElement('div');
    bubble.className = 'msg-bubble';

    const content = document.createElement('div');
    content.className = 'msg-content';

    // Convert markdown-style bold and newlines
    const formatted = text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\n/g, '<br>');
    content.innerHTML = formatted;

    const time = document.createElement('span');
    time.className = 'msg-time';
    time.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    bubble.appendChild(content);
    bubble.appendChild(time);
    wrap.appendChild(av);
    wrap.appendChild(bubble);

    this.messagesEl.appendChild(wrap);
    this.messagesEl.scrollTop = this.messagesEl.scrollHeight;

    // Entrance animation
    wrap.style.opacity = '0';
    wrap.style.transform = 'translateY(8px)';
    requestAnimationFrame(() => {
      wrap.style.transition = 'opacity 0.25s ease, transform 0.25s ease';
      wrap.style.opacity = '1';
      wrap.style.transform = 'translateY(0)';
    });
  },

  setTyping(state) {
    this.isTyping = state;
    if (this.sendBtn) this.sendBtn.disabled = state;

    const existing = document.getElementById('typing-indicator');
    if (existing) existing.remove();

    if (state) {
      const typing = document.createElement('div');
      typing.id = 'typing-indicator';
      typing.className = 'msg assistant';
      typing.innerHTML = `
        <div class="msg-av ai">🤖</div>
        <div class="msg-bubble">
          <div class="typing-bubble">
            <span></span><span></span><span></span>
          </div>
        </div>`;
      this.messagesEl.appendChild(typing);
      this.messagesEl.scrollTop = this.messagesEl.scrollHeight;
    }
  }
};

document.addEventListener('DOMContentLoaded', () => ChatApp.init());
