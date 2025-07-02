function getBotResponse(event) {
    event.preventDefault();
    const userInputField = document.getElementById("user-input");
    const userMessage = userInputField.value;

    if (userMessage.trim() === "") return;

    appendMessage("user", userMessage);
    userInputField.value = ""; // Clear input after sending

    fetch("/get_response", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_input: userMessage }),
    })
      .then((response) => response.json())
      .then((data) => {
        try {
          const botResponse = JSON.parse(data.response);
          if (botResponse.type === 'question_multiple_choice') {
            displayMultipleChoiceQuestion(botResponse);
          } else if (botResponse.type === 'question_slider') {
            displaySliderQuestion(botResponse);
          } else if (botResponse.type === 'question_open_ended') {
            displayOpenEndedQuestion(botResponse);
          } else if (botResponse.type === 'recommendations_list') {
            displayRecommendations(botResponse);
          } else {
            appendMessage("bot", data.response);
          }
        } catch (e) {
          // If not JSON, treat as plain text
          appendMessage("bot", data.response);
        }
      }).catch((error) => {
        console.error("Error:", error);
        appendMessage("bot", "Sorry, something went wrong.");
      });
  }

  function appendMessage(sender, text) {
    const chatMessages = document.getElementById("chat-messages");
    const messageElement = document.createElement("div");
    messageElement.classList.add("chat-message", `${sender}-message`);
    messageElement.innerHTML = `<p>${text}</p>`;
    chatMessages.appendChild(messageElement);
    chatMessages.scrollTop = chatMessages.scrollHeight; // Scroll to the bottom
  }

  // Functions to display specific message types

  function displayMultipleChoiceQuestion(questionData) {
    const chatMessages = document.getElementById("chat-messages");
    const messageElement = document.createElement("div");
    messageElement.classList.add("chat-message", "bot-message");
    let htmlContent = `<p><strong>Question:</strong> ${questionData.question}</p>`;
    htmlContent += `<p><strong>Reasoning:</strong> ${questionData.reasoning}</p>`;
    if (questionData.options && questionData.options.length > 0) {
      htmlContent += `<p><strong>Options:</strong></p><ul>`;
      questionData.options.forEach(option => {
        // htmlContent += `<li>${option}</li>`;
        htmlContent += `<input type="radio" name="answer" value="${option}"> <label>${option}</label><br>
        <label for="answer">${option}</label><br>`
      });
      htmlContent += `</ul>`;
    }
    messageElement.innerHTML = htmlContent;
    chatMessages.appendChild(messageElement);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function displaySliderQuestion(questionData) {
    const chatMessages = document.getElementById("chat-messages");
    const messageElement = document.createElement("div");
    messageElement.classList.add("chat-message", "bot-message");
    let htmlContent = `<p><strong>Question:</strong> ${questionData.question}</p>`;
    htmlContent += `<p><strong>Reasoning:</strong> ${questionData.reasoning}</p>`;
    if (questionData.slider_range) {
      htmlContent += `<p><strong>Slider Range:</strong> ${questionData.slider_range}</p>`;
      // You might want to create a slider input element here
    }
    messageElement.innerHTML = htmlContent;
    chatMessages.appendChild(messageElement);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function displayOpenEndedQuestion(questionData) {
    const chatMessages = document.getElementById("chat-messages");
    const messageElement = document.createElement("div");
    messageElement.classList.add("chat-message", "bot-message");
    let htmlContent = `<p><strong>Question:</strong> ${questionData.question}</p>`;
    htmlContent += `<p><strong>Reasoning:</strong> ${questionData.reasoning}</p>`;
    messageElement.innerHTML = htmlContent;
    chatMessages.appendChild(messageElement);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function displayRecommendations(recommendationsData) {
    const chatMessages = document.getElementById("chat-messages");
    const messageElement = document.createElement("div");
    messageElement.classList.add("chat-message", "bot-message");
    let htmlContent = "<p><strong>Here are some recommendations:</strong></p>";
    if (recommendationsData.recommendations && recommendationsData.recommendations.length > 0) {
      recommendationsData.recommendations.forEach((rec, index) => {
        htmlContent += `<div class="recommendation-item">`;
        htmlContent += `<p><strong>Recommendation ${index + 1}:</strong> ${rec.text}</p>`;
        if (rec.specs) htmlContent += `<p><strong>Specs:</strong> ${rec.specs}</p>`;
        if (rec.price) htmlContent += `<p><strong>Price:</strong> ${rec.price.replace('Price: ', '')}</p>`;
        if (rec.ratings) htmlContent += `<p><strong>Ratings:</strong> ${rec.ratings.replace('Ratings: ', '')}</p>`;
        htmlContent += `</div>`;
      });
    } else {
      htmlContent += "<p>No recommendations found.</p>";
    }
    messageElement.innerHTML = htmlContent;
    chatMessages.appendChild(messageElement);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }