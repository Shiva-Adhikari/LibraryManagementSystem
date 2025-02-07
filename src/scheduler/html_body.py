def mail_box(user_username, subject_filled, body_filled):
    subject = f'{subject_filled}'
    body = f"""
    <html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: 'Arial', sans-serif; line-height: 1.6; background-color: #f4f4f4; margin: 0; padding: 20px;">
    <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); overflow: hidden;">
        <div style="background-color: #2c3e50; color: white; padding: 20px; text-align: center;">
            <h1>Library Reminder</h1>
        </div>
        <div style="padding: 30px;">
            <div style="background-color: #e74c3c; color: white; padding: 10px; border-radius: 5px; margin-bottom: 20px; text-align: center;">
                <strong>{subject_filled}</strong>
            </div>
            <h2>Dear {user_username}</h2>
            <p>{body_filled}</p>
            <strong>Thank You</strong><br>
            <strong>LIBRARY</strong>
        </div>
    </div>
</body>
</html>
    """
    return subject, body
