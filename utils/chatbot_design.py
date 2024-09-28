# Custom CSS to make the interface fill the entire screen
css = """
html, body {
    height: 100%;
    margin: 0;
    padding: 0;
    overflow: hidden;
}
.gradio-container {
    height: 100vh;
    width: 100vw;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
}
.gradio-chatbot {
    flex: 1;
    display: flex;
    flex-direction: column;
}
.gradio-chatbot .gradio-chatbot-messages {
    flex: 1;
    overflow-y: auto;
}
.gradio-chatbot .gradio-chatbot-input {
    display: flex;
    margin-top: auto;
}
"""