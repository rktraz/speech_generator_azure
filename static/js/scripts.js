function handleFileSelect(event) {
  const file = event.target.files[0];
  const reader = new FileReader();

  reader.onload = function (e) {
    const contents = e.target.result;

    if (file.name.endsWith(".txt")) {
      document.getElementById("text-input").value = contents;
    } else if (file.name.endsWith(".doc") || file.name.endsWith(".docx")) {
      const formData = new FormData();
      formData.append("file", file);

      fetch("/extract_text", {
        method: "POST",
        body: formData,
      })
        .then((response) => response.text())
        .then((text) => {
          document.getElementById("text-input").value = text;
        })
        .catch((error) => console.error(error));
    }
  };

  if (file) {
    reader.readAsText(file);
  }
}

function downloadText(event) {
  const text = document.getElementById("translated-text").value;
  const language = document.getElementById("target-lang-select").value;

  const currentDate = new Date();
  const formattedDate = currentDate.toISOString().split("T")[0];
  const formattedTime = currentDate
    .toLocaleTimeString("en-US", { hour12: false })
    .replace(/:/g, "-");

  const fileName = `translated_to_${language}_${formattedDate}_${formattedTime}.txt`;

  const blob = new Blob([text], { type: "text/plain" });
  event.preventDefault();
  // Check if the browser supports the 'download' attribute
  if (navigator.msSaveBlob) {
    // For Internet Explorer and Microsoft Edge
    navigator.msSaveBlob(blob, fileName);
  } else {
    // For other browsers
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = fileName;
    link.style.display = "none";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }
}

function copyText(textAreaId) {
  const textArea = document.getElementById(textAreaId);
  textArea.select();
  textArea.setSelectionRange(0, 99999);
  document.execCommand("copy");
}

document.addEventListener("generateSpeechBtn", function () {
  var loadingMessage = document.querySelector(".loading-message");
  loadingMessage.style.display = "block";

  var audioPlayer = document.querySelector(".audio-player");
  audioPlayer.style.display = "none";
});

document
  .getElementById("translate-button")
  .addEventListener("click", function () {
    var textInput = document.getElementById("text-input").value;
    var targetLang = document.getElementById("target-lang-select").value;

    fetch("/translate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        original_text: textInput,
        target_lang: targetLang,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        document.getElementById("translated-text").value = data.translated_text;

        // Update voice dropdown menu
        var voiceSelect = document.getElementById("voice-actor-input");
        voiceSelect.innerHTML = "";

        data.voices_list.forEach(function (voice) {
          var option = document.createElement("option");
          option.value = voice;
          option.text = voice;
          voiceSelect.add(option);
        });
      })
      .catch((error) => console.error(error));
  });
