document.addEventListener("DOMContentLoaded", function () {
  // Check if there are messages to load
  fetch("/get_messages")
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        const chatContainer = document.querySelector(".messages");
        data.messages.forEach((msg) => {
          const roleDiv = document.createElement("div");
          roleDiv.classList.add("message-role");
          if (msg.role === "user") {
            roleDiv.classList.add("user");
          }
          roleDiv.textContent =
            msg.role.charAt(0).toUpperCase() + msg.role.slice(1);
          chatContainer.appendChild(roleDiv);

          const messageDiv = document.createElement("div");
          messageDiv.classList.add(
            msg.role === "user" ? "user-message" : "assistant-message"
          );
          messageDiv.textContent = msg.content;

          chatContainer.appendChild(messageDiv);
        });
      }
    });

  fetch("/get_ids")
    .then((response) => response.json())
    .then((data) => {
      console.log(
        "Data: ",
        data,
        "Assistant ID: ",
        data.assistant_id,
        "Thread ID: ",
        data.thread_id
      );
    });
});


document
  .querySelector("form")
  .addEventListener("submit", function (event) {
    event.preventDefault();
    const messageInput = document.querySelector(
      'textarea[name="message"]'
    );
    const message = messageInput.value.trim();
    const chatContainer = document.querySelector(".messages");
    // Append the user's message to the chat container
    if (message) {
      const roleDiv = document.createElement("div");
      roleDiv.classList.add("message-role");
      roleDiv.classList.add("user");

      roleDiv.textContent = "User";
      chatContainer.appendChild(roleDiv);

      const userMessageDiv = document.createElement("div");
      userMessageDiv.classList.add("user-message");
      userMessageDiv.textContent = message;
      chatContainer.appendChild(userMessageDiv);
    }
    // Clear the message input
    messageInput.value = "";
    // Send the user's message to the server using AJAX
    fetch("/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message: message }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          const roleDiv = document.createElement("div");
          roleDiv.classList.add("message-role");
          roleDiv.classList.add("assistant");

          roleDiv.textContent = "Assistant";
          chatContainer.appendChild(roleDiv);

          // Remove the typing indicator
          typingIndicator.remove();

          // Append the assistant's message to the chat container
          const assistantMessageDiv = document.createElement("div");
          assistantMessageDiv.classList.add("assistant-message");
          assistantMessageDiv.textContent = data.message;
          chatContainer.appendChild(assistantMessageDiv);
          // Scroll to the bottom of the chat container
          chatContainer.scrollTop = chatContainer.scrollHeight;
        }
      })
      .catch((error) => {
        console.error("Error:", error);
      });

    // Create a typing indicator container
    const typingIndicatorContainer = document.createElement("div");
    typingIndicatorContainer.classList.add("typing-indicator-container");

    // Create a typing indicator
    const typingIndicator = document.createElement("div");
    typingIndicator.classList.add("typing-indicator");
    typingIndicator.textContent = "•••";

    // Append the typing indicator to its container
    typingIndicatorContainer.appendChild(typingIndicator);

    // Append the typing indicator container to the chat container
    chatContainer.appendChild(typingIndicatorContainer);

    // Scroll to the bottom of the chat container
    chatContainer.scrollTop = chatContainer.scrollHeight;
  });