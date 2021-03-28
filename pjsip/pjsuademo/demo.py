import pjsua2 as pj
import time

ep = None

class Call(pj.Call):
    def __init__(self, acc, call_id = pj.PJSUA_INVALID_ID):
        pj.Call.__init__(self, acc, call_id)
        self.acc = acc
        self.pcm_capture = None
        self.pcm_stream = None

    def onCallMediaState(self, prm):
        ci = self.getInfo()
        aud_med = self.getAudioMedia(-1)
        if not self.pcm_capture:
            self.pcm_capture = pj.AudioMediaCapture()
            self.pcm_capture.createMediaCapture(ci.id)
            aud_med.startTransmit(self.pcm_capture)
        if not self.pcm_stream:
            self.pcm_stream = pj.AudioMediaStream()
            self.pcm_stream.createMediaStream(ci.id)
            self.pcm_stream.startTransmit(aud_med)


    def getFrames(self):
        if self.pcm_capture:
            s = self.pcm_capture.getFrames()
            print(type(s))
            print('====== fetch:', len(s))
            return s
        #     return self.pcm_capture.getFrames().encode('utf-8', errors='surrogateescape')
        return b''

    def putFrame(self, chunk):
        if self.pcm_stream:
            self.pcm_stream.putFrame(chunk)
        else:
            print('WTF')

def pjsua2_test():
    global ep
    # Create and initialize the library
    ep_cfg = pj.EpConfig()
    ep_cfg.logConfig.level = 5;
    ep = pj.Endpoint()
    ep.libCreate()
    ep.libInit(ep_cfg)
    ep.audDevManager().setNullDev()

    for codec in ep.codecEnum2():
        priority = 0
        if 'PCMA/8000' in codec.codecId:
            priority = 255
        ep.codecSetPriority(codec.codecId, priority)

    # Create SIP transport. Error handling sample is shown
    sipTpConfig = pj.TransportConfig();
    sipTpConfig.port = 15060;
    ep.transportCreate(pj.PJSIP_TRANSPORT_UDP, sipTpConfig);
    # Start the library
    ep.libStart();

    acfg = pj.AccountConfig();
    acfg.idUri = "sip:1002@asterisk";
    acfg.regConfig.registrarUri = "sip:asterisk";
    cred = pj.AuthCredInfo("digest", "*", "1002", 0, "12345");
    acfg.sipConfig.authCreds.append( cred )
    # Create the account
    acc = pj.Account()
    acc.create(acfg)
    # Here we don't have anything else to do..
    while not acc.getInfo().regIsActive:
        print('========== registering')
        time.sleep(0.1)

    if acc.getInfo().regStatus != 200:
        print('++++++++++++++++++')
        print('no registration')
        return

    call = Call(acc)
    prm = pj.CallOpParam(True)
    prm.opt.audioCount = 1
    prm.opt.videoCount = 0

    call.makeCall("sip:8080@asterisk", prm)

    while call.getInfo().state != pj.PJSIP_INV_STATE_CONFIRMED:
        print(call.getInfo().stateText)
        time.sleep(0.1)

    f = open('output.lpcm', 'wb')
    f2 = open('hw.raw', 'rb')
    hwraw = f2.read()
    n = 320
    [call.putFrame(hwraw[i:i+320]) for i in range(0, len(hwraw), n)]

    for i in range(10):
        time.sleep(1)
        data = call.getFrames()
        if data:
            f.write(data)
    f.close()

    prm = pj.CallOpParam()
    call.hangup(prm)

    # Destroy the library
    ep.hangupAllCalls()
    print('unregistering')
    acc.delete()

#
# main()
#
if __name__ == "__main__":
    pjsua2_test()
    print('===========')
    time.sleep(3)
    ep.libDestroy()
