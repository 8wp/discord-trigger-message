<h2>How it works</h2>

<p>This tool is a locally hosted Python script that uses on-device OCR (Optical Character Recognition) alongside the Discord gateway 
to enable one-time, trigger-based messaging. You define trigger-response pairs in the config file — for example, if the script 
detects a specific piece of text on your screen, it will immediately send the corresponding predefined response to the selected 
Discord channel. The script authenticates with your bot/user token and establishes a WebSocket connection to deliver 
the message instantly. All setup — including trigger text, response messages, and channel selection — is handled entirely 
through the config, making it a straightforward, end-to-end solution for automated OCR-driven responses without external 
hosting or services.</p>

<h2>How to use</h2>

<ol>
  <li>Download the <code>discord-trigger-message.py</code> file.</li>
  <li>Open the file using Python.</li>
  <li>Open Discord and send your target message in any text channel.</li>
  <li>Click <code>2</code> on the startup menu, and follow the prompt to callibrate message area.</li>
  <li>Click <code>3</code> on the startup menu, and follow the prompt to callibrate username area.</li>
  <li>Click <code>4</code> on the startup menu, and input the following data required:</li>
    <ul>
      <li><code>Keywords</code> - The keyword that will trigger your response message, e.g <code>Hello</code>, any messages sent with this keyword will return a response message being sent.</li>
      <li><code>Response Message</code> - This is the message you wish to send in your chosen channel within Discord, e.g <code>Hello World</code>.</li>
       <li><code>Scan Interval</code> - How often you wish for your message to be sent.</li>
      <li> <code>Token</code> - You can find your bot token on the <a href="https://discord.com/developers/applications" target="_blank" rel="noopener noreferrer">Discord Developer Portal</a> under the <code>Bot</code> tab of your chosen application. Alternatively, you can use your user token which you can find on the <a href="https://discord.com/channels/@me" target="_blank" rel="noopener noreferrer">Web App</a> through using <code>Ctrl + Shift + I</code> and under the <code>Storage</code> header, opening the dropdown on <code>Local Storage</code> and clicking on <code>https://discord.com</code>. Then filter your search to sort for the <code>token</code> key. If it does not show up, use <code>Ctrl + Shift + M</code> two times, to refresh for the <code>token</code> key. Through clicking on it, a window will be visible that you can copy and paste your token from. You must remove the quotation marks before pasting the token, or else it will not approve. Do not share your user token with anyone, as it allows for gateway access to your account if used maliciously, it is recommended to reset your password if you believe to have accidentally shared it with anyone, as this will reset your user token.</li>
      <li><code>Channel ID</code> - Enable <code>Developer Mode</code> in Discord settings, this can be found under the <code>Advanced</code> tab. Then <code>Right Click</code> the channel you wish to send the messages to, and <code>Copy Channel ID</code>.</li>
    </ul>
  <li>On the startup menu click <code>1</code> to start the tool.</li>
  <li>When you wish to turn off the tool, click <code>Esc</code>.</li>
</ol>

<h2>Disclaimer</h2>
  <p>Using your user token violates <a href="https://discord.com/terms/guidelines-march-2023" target="_blank" rel="noopener noreferrer">Discord Community Guidelines</a>, and as such is for educational purposes only.</p>
