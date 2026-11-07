# Gemini web prototype

Static HTML/CSS/JavaScript interface that sends an uploaded image to the Google Gemini 2.5 Flash Vision API.

## Run
Open `index.html` in a modern browser, enter your Gemini API key in the UI, and upload an image.

## Important
This is a Gemini vision API integration, not a local EfficientNet/ResNet model. The API key is stored in browser `sessionStorage` and requests are made directly from the browser. Do not deploy publicly in this form. See `../../docs/SECURITY.md`.
