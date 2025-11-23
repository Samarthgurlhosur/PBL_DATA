const chatWindow = document.getElementById("chat-window");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");
const typingIndicator = document.getElementById("typing-indicator");

/* ------------------ ADD MESSAGE TO CHAT WINDOW ------------------ */

function addMessage(text, sender = "bot") {
  const msgDiv = document.createElement("div");
  msgDiv.classList.add("message", sender);

  const avatarDiv = document.createElement("div");
  avatarDiv.classList.add("avatar");

  if (sender === "bot") {
    avatarDiv.classList.add("bot-avatar");
    avatarDiv.textContent = "🤖";
  } else {
    avatarDiv.classList.add("user-avatar");
    avatarDiv.textContent = "👤";
  }

  const bubbleDiv = document.createElement("div");
  bubbleDiv.classList.add("bubble");
  bubbleDiv.textContent = text;

  if (sender === "bot") {
    msgDiv.appendChild(avatarDiv);
    msgDiv.appendChild(bubbleDiv);
  } else {
    msgDiv.appendChild(bubbleDiv);
    msgDiv.appendChild(avatarDiv);
  }

  chatWindow.appendChild(msgDiv);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

/* ------------------ SEND MESSAGE ------------------ */

async function sendMessage() {
  const text = userInput.value.trim();
  if (!text) return;

  // Add user message
  addMessage(text, "user");

  userInput.value = "";
  userInput.focus();

  // Show typing indicator
  typingIndicator.classList.remove("hidden");

  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message: text }),
    });

    const data = await res.json();
    const botReply = data.reply || "Sorry, I couldn't understand that.";

    // Delay to feel more human-like
    setTimeout(() => {
      addMessage(botReply, "bot");
      typingIndicator.classList.add("hidden");
    }, 500);
  } catch (error) {
    typingIndicator.classList.add("hidden");
    addMessage("I'm having trouble connecting right now. Please try again soon.", "bot");
  }
}

/* ------------------ EVENT LISTENERS ------------------ */

sendBtn.addEventListener("click", sendMessage);

userInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    sendMessage();
  }
});
