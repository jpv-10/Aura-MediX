// ===== VOICE ASSISTANT - PREMIUM UI INTERACTIONS =====
// Original functionality 100% preserved.
// Visual enhancement additions are clearly marked with  ⟨VISUAL+⟩

class VoiceAssistant {
    constructor() {
        this.isRecording = false;
        this.recognition = this.initializeSpeechRecognition();
        this.micButton = document.getElementById('micButton');
        this.statusText = document.getElementById('statusText');
        this.transcriptText = document.getElementById('transcriptText');
        this.waveformContainer = document.getElementById('waveformContainer');
        this.aiResponseContainer = document.getElementById('aiResponseContainer');
        this.aiResponseText = document.getElementById('aiResponseText');
        this.clearBtn = document.getElementById('clearBtn');
        this.resetBtn = document.getElementById('resetBtn');
        this.micIcon = document.getElementById('micIcon');

        // ⟨VISUAL+⟩ References for visual enhancement elements
        this.statusBadge       = document.getElementById('statusBadge');
        this.thinkingIndicator = document.getElementById('thinkingIndicator');
        this.micTapHint        = document.querySelector('.mic-tap-hint');

        this.initializeParticles();
        this.setupEventListeners();

        // ⟨VISUAL+⟩ Apply initial visual state
        this.setStatusState('ready');

        this.simulateResponses = [
            "Your blood pressure looks stable. Keep maintaining hydration.",
            "Based on your symptoms, I recommend scheduling a consultation.",
            "Your fitness metrics are improving. Continue the current routine.",
            "Rest and hydration are recommended for your condition.",
            "Your BMI is within healthy range. Great work!"
        ];
    }

    initializeSpeechRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            console.log('Speech Recognition API not available - using simulation');
            return null;
        }
        const recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = 'en-US';
        return recognition;
    }

    setupEventListeners() {
        this.micButton.addEventListener('click', () => this.toggleRecording());
        this.clearBtn.addEventListener('click', () => this.clearTranscript());
        this.resetBtn.addEventListener('click', () => this.resetAssistant());

        if (this.recognition) {
            this.recognition.addEventListener('start', () => this.onRecordingStart());
            this.recognition.addEventListener('end', () => this.onRecordingEnd());
            this.recognition.addEventListener('result', (e) => this.onSpeechResult(e));
            this.recognition.addEventListener('error', (e) => this.onSpeechError(e));
        }
    }

    toggleRecording() {
        if (!this.recognition) {
            // Fallback: simulate recording
            this.simulateRecording();
            return;
        }

        if (this.isRecording) {
            this.stopRecording();
        } else {
            this.startRecording();
        }
    }

    startRecording() {
        this.isRecording = true;
        this.micButton.classList.add('recording');
        this.waveformContainer.classList.remove('hidden');
        this.statusText.textContent = 'Listening...';
        this.micIcon.textContent = '⏹️';
        this.transcriptText.textContent = 'Listening...';
        this.aiResponseContainer.style.display = 'none';

        // ⟨VISUAL+⟩ Update state-driven visual cues
        this.setStatusState('listening');
        this.hideThinking();
        if (this.micTapHint) this.micTapHint.textContent = 'Tap to stop';

        if (this.recognition) {
            this.recognition.start();
        }
    }

    stopRecording() {
        this.isRecording = false;
        this.micButton.classList.remove('recording');
        this.waveformContainer.classList.add('hidden');
        this.statusText.textContent = 'Processing...';
        this.micIcon.textContent = '🎙️';

        // ⟨VISUAL+⟩ Show processing state
        this.setStatusState('processing');
        this.showThinking();
        if (this.micTapHint) this.micTapHint.textContent = 'Tap to speak';

        if (this.recognition) {
            this.recognition.stop();
        } else {
            this.simulateProcessing();
        }
    }

    onRecordingStart() {
        console.log('Recording started');
    }

    onRecordingEnd() {
        this.isRecording = false;
        this.micButton.classList.remove('recording');
        this.waveformContainer.classList.add('hidden');
        // ⟨VISUAL+⟩
        if (this.micTapHint) this.micTapHint.textContent = 'Tap to speak';
    }

    onSpeechResult(event) {
        let interim_transcript = '';
        let final_transcript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;

            if (event.results[i].isFinal) {
                final_transcript += transcript + ' ';
            } else {
                interim_transcript += transcript;
            }
        }

        const displayTranscript = final_transcript || interim_transcript;
        this.updateTranscript(displayTranscript);

        if (final_transcript) {
            this.statusText.textContent = 'Processing...';
            // ⟨VISUAL+⟩
            this.setStatusState('processing');
            this.showThinking();
            setTimeout(() => this.generateAIResponse(), 1500);
        }
    }

    onSpeechError(event) {
        console.error('Speech recognition error:', event.error);
        this.statusText.textContent = 'Error: ' + event.error;
        this.isRecording = false;
        this.micButton.classList.remove('recording');
        // ⟨VISUAL+⟩
        this.setStatusState('error');
        this.hideThinking();
        if (this.micTapHint) this.micTapHint.textContent = 'Tap to speak';
    }

    simulateRecording() {
        this.startRecording();

        const sampleInputs = [
            'I have a headache and fever',
            'What should I eat for better health',
            'How many steps did I take today',
            'Check my blood pressure status',
            'What exercises should I do'
        ];

        const randomInput = sampleInputs[Math.floor(Math.random() * sampleInputs.length)];

        let charIndex = 0;
        const typeCharacter = () => {
            if (charIndex < randomInput.length) {
                this.transcriptText.textContent = randomInput.substring(0, charIndex + 1);
                this.transcriptText.classList.add('typing');
                charIndex++;
                setTimeout(typeCharacter, 40);
            } else {
                this.transcriptText.classList.remove('typing');
                setTimeout(() => {
                    this.stopRecording();
                }, 500);
            }
        };

        typeCharacter();
    }

    simulateProcessing() {
        this.statusText.textContent = 'Processing...';

        setTimeout(() => {
            this.statusText.textContent = 'Ready to listen';
            // ⟨VISUAL+⟩
            this.hideThinking();
            this.generateAIResponse();
        }, 2000);
    }

    updateTranscript(text) {
        this.transcriptText.textContent = text || 'Listening...';
    }

    generateAIResponse() {
        // ⟨VISUAL+⟩ Dismiss thinking indicator before showing response
        this.hideThinking();

        const randomResponse = this.simulateResponses[
            Math.floor(Math.random() * this.simulateResponses.length)
        ];

        this.aiResponseContainer.style.display = 'block';
        this.aiResponseText.textContent = '';

        let charIndex = 0;
        const typeResponse = () => {
            if (charIndex < randomResponse.length) {
                this.aiResponseText.textContent += randomResponse[charIndex];
                charIndex++;
                setTimeout(typeResponse, 15);
            } else {
                // ⟨VISUAL+⟩ Restore ready state once typing is complete
                this.setStatusState('ready');
                this.statusText.textContent = 'Ready to listen';
            }
        };

        typeResponse();
    }

    clearTranscript() {
        this.transcriptText.textContent = 'Waiting for input...';
        this.aiResponseContainer.style.display = 'none';
        this.aiResponseText.textContent = '';
        // ⟨VISUAL+⟩
        this.hideThinking();
        this.setStatusState('ready');
    }

    resetAssistant() {
        if (this.isRecording) {
            this.stopRecording();
        }
        this.isRecording = false;
        this.micButton.classList.remove('recording');
        this.waveformContainer.classList.add('hidden');
        this.statusText.textContent = 'Ready to listen';
        this.micIcon.textContent = '🎙️';
        this.transcriptText.textContent = 'Waiting for input...';
        this.aiResponseContainer.style.display = 'none';
        this.aiResponseText.textContent = '';
        // ⟨VISUAL+⟩
        this.hideThinking();
        this.setStatusState('ready');
        if (this.micTapHint) this.micTapHint.textContent = 'Tap to speak';
    }

    initializeParticles() {
        const container = document.getElementById('particleContainer');
        const particleCount = window.innerWidth > 768 ? 30 : 15;

        for (let i = 0; i < particleCount; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            particle.style.left = Math.random() * 100 + '%';
            particle.style.top = 100 + '%';
            particle.style.animation = `particleFloat ${10 + Math.random() * 10}s linear infinite`;
            particle.style.animationDelay = Math.random() * 5 + 's';
            container.appendChild(particle);
        }
    }

    // ─────────────────────────────────────────────────────────
    // ⟨VISUAL+⟩  Visual Enhancement Methods
    // These are purely cosmetic. Removing them does not
    // affect any transcription, speech, or AI response logic.
    // ─────────────────────────────────────────────────────────

    /**
     * Set a data-state attribute on the status badge so CSS can
     * apply state-specific colours without touching JS logic.
     * States: 'ready' | 'listening' | 'processing' | 'error'
     */
    setStatusState(state) {
        if (this.statusBadge) {
            this.statusBadge.dataset.state = state;
        }
    }

    /**
     * Reveal the "AI is analysing…" thinking indicator.
     */
    showThinking() {
        if (this.thinkingIndicator) {
            this.thinkingIndicator.style.display = 'flex';
        }
    }

    /**
     * Hide the thinking indicator.
     */
    hideThinking() {
        if (this.thinkingIndicator) {
            this.thinkingIndicator.style.display = 'none';
        }
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    new VoiceAssistant();
});