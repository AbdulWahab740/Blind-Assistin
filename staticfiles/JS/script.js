// import Webcam from 'webcam-easy';
// ------------------ Loader Js ------------------

console.log("Hello ")
setTimeout(() => {
    document.getElementById("loader-container").style.display = "none"
    document.getElementById("main").style.display = "block"
}, 2000)


// ------------------ audio ------------------


window.addEventListener('load', () => {
    const audio = document.getElementById('myAudio');

    audio.play()
        .then(() => {
            audio.muted = false;
        }).catch((error) => {
            console.log(error)
        });
})


// ------------------ Voice input ------------------


setTimeout(() => {
    if ('webkitSpeechRecognition' in window) {
        const recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;

        recognition.start();
        console.log("Listening...")

        recognition.onresult = (event) => {
            var transcript = event.results[0][0].transcript;
            if (transcript.includes("capture") || transcript.includes("image") || transcript.includes("pic") || transcript.includes("picture")) {
                handleCapture()
            }
            console.log(transcript)
        };

        recognition.onerror = (event) => {
            console.error('Error occurred in recognition:', event.error);
        };

        recognition.onend = () => {
            console.log("Listening completed")
            recognition.start();
        };
    } else {
        console.error("Speech Recognition not supported in this browser.");
    }
}, 10000)




