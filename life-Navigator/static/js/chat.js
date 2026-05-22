(function () {
  const launcher = document.getElementById("assistant-btn");
  const chatbot = document.getElementById("chatbot-container");
  const closeButton = document.querySelector("[data-chat-close]");
  const chatBody = document.getElementById("chat-body");
  const input = document.getElementById("user-message");
  const sendButton = document.getElementById("send-message");
  const suggestionButtons = document.querySelectorAll(".chat-suggestion");

  if (!launcher || !chatbot || !chatBody || !input || !sendButton) {
    return;
  }

  const context = chatbot.dataset || {};

  const setOpenState = (isOpen) => {
    chatbot.classList.toggle("open", isOpen);
    launcher.textContent = isOpen ? "Close hospital assistant" : "Open hospital assistant";
    launcher.setAttribute("aria-expanded", String(isOpen));
    launcher.setAttribute("aria-label", isOpen ? "Close hospital assistant" : "Open hospital assistant");

    if (isOpen) {
      window.setTimeout(() => input.focus(), 60);
    }
  };

  const addMessage = (text, sender) => {
    const message = document.createElement("div");
    message.className = `chat-message ${sender}`;

    if (sender === "bot") {
      const avatar = document.createElement("div");
      avatar.className = "avatar";
      avatar.textContent = "AI";
      message.appendChild(avatar);
    }

    const bubble = document.createElement("div");
    bubble.className = "chat-bubble";
    bubble.textContent = text;

    message.appendChild(bubble);
    chatBody.appendChild(message);
    chatBody.scrollTop = chatBody.scrollHeight;
  };

  const showTyping = () => {
    const typing = document.createElement("div");
    typing.className = "chat-message bot";
    typing.id = "typing-indicator";

    const avatar = document.createElement("div");
    avatar.className = "avatar";
    avatar.textContent = "AI";

    const bubble = document.createElement("div");
    bubble.className = "chat-bubble typing";
    bubble.textContent = "Assistant is preparing an explanation...";

    typing.appendChild(avatar);
    typing.appendChild(bubble);
    chatBody.appendChild(typing);
    chatBody.scrollTop = chatBody.scrollHeight;
  };

  const removeTyping = () => {
    const typing = document.getElementById("typing-indicator");
    if (typing) {
      typing.remove();
    }
  };

  const setBusy = (isBusy) => {
    sendButton.disabled = isBusy;
    input.disabled = isBusy;
    suggestionButtons.forEach((button) => {
      button.disabled = isBusy;
    });
  };

  const buildChatUrl = () => {
    const params = new URLSearchParams({
      hospital: context.hospital || "",
      icu_load: context.icuLoad || "",
      icu_beds: context.icuBeds || "",
      severity: context.severity || "",
      emergency: context.emergency || "",
      hospital_level: context.hospitalLevel || "",
      score: context.score || "",
      city: context.city || "",
      confidence: context.confidence || "",
      reason: context.reason || ""
    });

    return `/chat?${params.toString()}`;
  };

  const sendMessage = async (presetMessage) => {
    const message = (presetMessage || input.value).trim();
    if (!message) {
      return;
    }

    setOpenState(true);
    addMessage(message, "user");
    input.value = "";
    setBusy(true);
    showTyping();

    try {
      const response = await fetch(buildChatUrl(), {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ message })
      });

      const payload = await response.json();
      removeTyping();
      addMessage(payload.reply || "I could not generate a reply right now.", "bot");
    } catch (error) {
      removeTyping();
      addMessage("The assistant is temporarily unavailable. Please try again in a moment.", "bot");
      console.error(error);
    } finally {
      setBusy(false);
      input.focus();
    }
  };

  launcher.addEventListener("click", () => {
    setOpenState(!chatbot.classList.contains("open"));
  });

  if (closeButton) {
    closeButton.addEventListener("click", () => setOpenState(false));
  }

  sendButton.addEventListener("click", () => sendMessage());

  input.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  });

  suggestionButtons.forEach((button) => {
    button.addEventListener("click", () => {
      sendMessage(button.dataset.prompt || button.textContent || "");
    });
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && chatbot.classList.contains("open")) {
      setOpenState(false);
    }
  });

  setOpenState(false);
})();
