var childProcess = require("child_process");
var oldSpawn = childProcess.spawn;
function mySpawn() {
    console.log('spawn called');
    console.log(arguments);
    var result = oldSpawn.apply(this, arguments);
    return result;
}
childProcess.spawn = mySpawn;
const thriftServerExePath = "C:\Users\majdoub\botdev\dofusBotDev\pyd2bot\pyd2bot\thriftServer\pyd2botServer.py"
const ps = childProcess.spawn("./" + thriftServerExePath, {shell: true});

ps.stdout.on('data', (data) => {
  console.log(`stdout: ${data}`);
});

ps.stderr.on('data', (data) => {
  console.error(`stderr: ${data}`);
});

ps.on('close', (code) => {
  console.log(`child process exited with code ${code}`);
});