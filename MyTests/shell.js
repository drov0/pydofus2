const child_process = require('child_process')
const path = require('path')
var pyd2botExePath = path.join(process.env.AppData, 'pyd2bot', 'pyd2bot.exe');
var instance = child_process.spawn(pyd2botExePath + " --host 0.0.0.0 --port 9999", {"shell": true});

instance.stdout.on('data', (data) => {
    console.log(`stdout: ${data}`);
});

instance.stderr.on('data', (data) => {
    console.log(`error in process : ${data}`);
});

instance.on('close', (code) => {
    console.log(`child process exited with code ${code}`);
});

