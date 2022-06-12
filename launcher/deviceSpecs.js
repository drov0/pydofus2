import os from 'os';

export class DeviceSpecs {

    static get instance() {
        return DeviceSpecs._instance || (DeviceSpecs._instance = new DeviceSpecs), DeviceSpecs._instance
    }

    constructor() {
    }

    getComputerRam() {
        return Math.pow(2, Math.round(Math.log(os.totalmem() / 1024 / 1024) / Math.log(2)))
    }

    getOsVersion() {
        var t, n;
        [t, n] = os.release().split(".");
        return parseFloat(`${t}.${n}`)
    }
}
