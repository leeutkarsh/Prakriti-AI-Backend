Backend API is ready through ngrok.

Base URL: `https://<your-ngrok-url>.ngrok-free.app`

Use `POST /analyze` as `multipart/form-data` with:

* `file` → image
* `disease_or_pest`
* `address`
* `soil_type`
* `disease_category` (optional)

Response gives:

* `data` → prediction/results
* `annotated_image_url` → use `BASE_URL + annotated_image_url` to display the annotated image

Annotated image endpoint:
`GET /annotated-images/{image_id}`

Also make sure frontend requests are configured for CORS; backend already has CORS enabled.

So basically: frontend sends the image + fields to `/analyze`, gets JSON back, displays `data`, and loads the annotated image using the returned `annotated_image_url`.
