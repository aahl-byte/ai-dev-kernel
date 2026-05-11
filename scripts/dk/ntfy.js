#!/usr/bin/env node
'use strict';

/**
 * Send a push notification via ntfy.sh.
 * Usage: node scripts/dk/ntfy.js "your message here"
 *    or: bun ntfy -- "your message here"
 *
 * Set the NTFY_TOPIC environment variable to your ntfy.sh topic.
 * Default topic: dk-notifications (override this!)
 */

const https = require('https');

const message = process.argv.slice(2).join(' ');
if (!message) {
  console.error('Usage: bun ntfy -- "message"');
  process.exit(1);
}

const topic = process.env.NTFY_TOPIC || 'dk-notifications';
const url = `https://ntfy.sh/${topic}`;

const req = https.request(url, {
  method: 'POST',
  headers: { 'Content-Type': 'text/plain' }
}, (res) => {
  res.resume();
  if (res.statusCode >= 200 && res.statusCode < 300) {
    console.log(`Notification sent: "${message}"`);
  } else {
    console.error(`Notification failed (HTTP ${res.statusCode})`);
  }
});

req.on('error', (err) => {
  console.error(`Notification failed: ${err.message}`);
});

req.end(message);
