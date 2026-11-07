# Security and privacy notes

## Gemini web prototype

The Gemini prototype asks the user to enter an API key and stores it in browser `sessionStorage`. JavaScript sends the key to Google's API from the browser. This means the key is available to client-side code and browser tooling.

- Never commit a real API key, screenshot containing a key, or populated `.env` file.
- For public hosting, move Gemini calls to a server-side backend and read the key from a protected environment variable.
- Configure usage limits and monitor API usage in the provider console.
- Tell users clearly when images are sent to a third-party AI provider.

## Flask prototype

The demo saves uploaded images in its `uploads/` directory and prediction history in a local JSON file.

- Do not deploy the development server as-is to the public internet.
- Add authentication, authorization, rate limiting, secure file handling, retention controls and HTTPS before any real deployment.
- Validate file content rather than trusting only filename extensions.
- Restrict access to uploaded images and avoid logging sensitive data.
- Set a retention/deletion policy for uploaded images and history.
- Review dependency versions and run security checks before deployment.

## Medical privacy

Skin images can be sensitive personal information. Obtain informed permission, minimize collection, limit retention, and use only data you are authorized to process.
