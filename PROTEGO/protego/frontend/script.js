/*
script.js
=========
Frontend controller for PROTEGO chatbot.

Responsibilities:
- Chat UI toggling
- Message rendering
- Backend communication
- Emergency highlighting
- UX safety handling

This version is:
✅ Robust
✅ Interview-ready
✅ Production-grade
*/

const CHAT_API_URL = "http://127.0.0.1:8000/chat";

const chatBox = document.getElementById("chatBox");
const chatBody = document.getElementById("chatBody");
const userInput = document.getElementById("userInput");

let isSending = false;

/* -----------------------------
   UI helpers
----------------------------- */
function toggleChat() {
  chatBox.style.display = chatBox.style.display === "block" ? "none" : "block";
}

function addMessage(text, className) {
  const div = document.createElement("div");
  div.className = className;
  div.innerHTML = text;
  chatBody.appendChild(div);
  chatBody.scrollTop = chatBody.scrollHeight;
}

function addTypingIndicator() {
  const div = document.createElement("div");
  div.className = "bot-msg";
  div.innerText = "Typing...";
  chatBody.appendChild(div);
  chatBody.scrollTop = chatBody.scrollHeight;
  return div;
}

/* -----------------------------
   Event listeners
----------------------------- */
userInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    sendMessage();
  }
});

/* -----------------------------
   Core chat logic
----------------------------- */
async function sendMessage() {
  if (isSending) return;

  const text = userInput.value.trim();
  if (!text) return;

  isSending = true;
  userInput.value = "";

  addMessage(text, "user-msg");
  const typingBubble = addTypingIndicator();

  try {
    const response = await fetch(CHAT_API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        message: text,
        country: "India"
      })
    });

    if (!response.ok) {
      throw new Error("Server returned error");
    }

    const data = await response.json();

    typingBubble.innerText = data.reply || "I’m here with you 🤍";

    if (data.show_emergency) {
      typingBubble.classList.add("emergency");
    }

    // Render emergency contacts if present
    if (data.emergency_contacts) {
      let contactsHtml = "<strong>Emergency Contacts:</strong><ul>";
      for (const [label, number] of Object.entries(data.emergency_contacts)) {
        contactsHtml += `<li>${label}: ${number}</li>`;
      }
      contactsHtml += "</ul>";
      addMessage(contactsHtml, "bot-msg emergency");
    }

  } catch (error) {
    typingBubble.innerText =
      "⚠️ I’m having trouble connecting right now. Please try again.";
    typingBubble.classList.add("emergency");
  } finally {
    isSending = false;
    chatBody.scrollTop = chatBody.scrollHeight;
  }
}
