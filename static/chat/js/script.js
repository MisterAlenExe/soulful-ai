function createNewChat() {}

function createAIBubble(id) {
  $(".chat-messages").append(
    `<div class="message ai-message"> <span class="message-text" data-id="${id}"></span> </div>`
  );
}

function addAIMessage(id, message) {
  $(`.message-text[data-id="${id}"]`).html(message);
}

function addUserMessage(message) {
  $(".chat-messages").append(
    `<div class="message user-message"> <span class="message-text">${message}</span> </div>`
  );
}

$(document).ready(async function () {
  const chatRoomId = $("#chat-room.active").data("id");

  $("#chat-form").on("submit", async function (e) {
    e.preventDefault();
    const prompt = $("#prompt").val();

    addUserMessage(prompt);
    createAIBubble(prompt);

    $("#prompt").val("");

    const csrfToken = $("input[name=csrfmiddlewaretoken]").val();

    try {
      const response = await fetch("/chat/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({
          prompt: prompt,
          chat_room_id: chatRoomId,
        }),
      });

      if (response.ok) {
        const reader = response.body.getReader();

        let responseText = "";

        while (true) {
          const { done, value } = await reader.read();

          if (done) {
            break;
          }

          responseText += new TextDecoder("utf-8").decode(value);

          addAIMessage(prompt, responseText);
        }
      }
    } catch (error) {
      console.log(error);
    }
  });

  $("#new-chat-form").on("submit", async function (e) {
    e.preventDefault();
    const name = $("#chat").val();

    $("#chat").val("");

    const csrfToken = $("input[name=csrfmiddlewaretoken]").val();

    await fetch("/chat/new/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
      body: JSON.stringify({ name: name }),
    })
      .then((response) => {
        if (response.ok) {
          return response.json();
        } else {
          throw new Error("Something went wrong");
        }
      })
      .then((data) => {
        const uuid = data["uuid"];
        window.location.href = `/chat/${uuid}/`;
      })
      .catch((error) => {
        console.log(error);
      });
  });
});
