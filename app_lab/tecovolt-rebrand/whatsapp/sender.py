const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const express = require('express');
const app = express();

app.use(express.json());

const client = new Client({
    authStrategy: new LocalAuth(),
    puppeteer: {
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--single-process',
            '--no-zygote'
        ],
    }
});

client.on('qr', (qr) => {
    qrcode.generate(qr, { small: true });
    console.log('Escanea este QR con tu WhatsApp:');
});

client.on('ready', () => {
    console.log('¡WhatsApp conectado y listo!');
});

// Endpoint que recibirá la alerta desde Python
app.post('/alert', async (req, res) => {
    const { message, number } = req.body; 
    // El número debe incluir el código de país sin el '+', ej: 5218112345678@c.us
    try {
        console.log("Sending alert")
        await client.sendMessage(number, message);
        res.status(200).send({ status: 'Enviado' });
    } catch (err) {
        res.status(500).send({ error: err.message });
    }
});

client.initialize();
app.listen(3000, () => console.log('Servidor de alertas en puerto 3000'));