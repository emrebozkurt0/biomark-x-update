const nodemailer = require('nodemailer');

let cachedTransporter = null;

async function createTransporter() {
  if (cachedTransporter) return cachedTransporter;

  const {
    SMTP_HOST,
    SMTP_PORT,
    SMTP_USER,
    SMTP_PASS
  } = process.env;

  if (SMTP_HOST && SMTP_PORT && SMTP_USER && SMTP_PASS) {
    cachedTransporter = nodemailer.createTransport({
      host: SMTP_HOST,
      port: Number(SMTP_PORT),
      secure: Number(SMTP_PORT) === 465,
      auth: { user: SMTP_USER, pass: SMTP_PASS }
    });
    return cachedTransporter;
  }

  // Fallback: Ethereal for dev/testing
  const testAccount = await nodemailer.createTestAccount();
  cachedTransporter = nodemailer.createTransport({
    host: 'smtp.ethereal.email',
    port: 587,
    secure: false,
    auth: {
      user: testAccount.user,
      pass: testAccount.pass
    }
  });
  return cachedTransporter;
}

async function sendMail({ to, subject, html, text }) {
  const transporter = await createTransporter();

  const from = process.env.MAIL_FROM || 'no-reply@example.com';
  const info = await transporter.sendMail({ from, to, subject, html, text });

  // Log preview URL for Ethereal
  try {
    const preview = nodemailer.getTestMessageUrl(info);
    if (preview) console.log('Ethereal preview URL:', preview);
  } catch (e) {}

  return info;
}

module.exports = { sendMail };


