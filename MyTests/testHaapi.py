accounts = {
    "slicer-the-dicer": {
        "login": "shooter.jhon92@gmail.com",
        "password": "p33_6_.XkgzNfYv",
        "certId": 125970667,
        "certHash": "72ffd7b745613fe745eae5005820921d98756ba7cc5472a3e9bfea318ba8497d"
    },
    "twistedFater": {
        "login": "aloone95",
        "password": "rmrtxha4",
        "certId": 126305096,
        "certHash": "793ef80060b0ee9c82fccbade4860ef8231984eb5dc48e8cf2dcef2e624ffe6d"
    },
    "Money": {
        "login": "tarik-maj@hotmail.fr",
        "password": "rmrtxha1",
        "certId": 126304780,
        "certHash": "f2a5726c0581d18c92b4a2278ff4c457240e62e8a64265cef8793781c641ba8c"
    },
    "Exodios-panda": {
        "login": "aloone-102",
        "password": "rmrtxha1",
        "certId": 126304696,
        "certHash": "d9b9b949ba7b5fad686a52a284605936f4077256cf4f78cb63358ec83163bf50"
    },
    "Exodios-cra": {
        "login": "aloone-100",
        "password": "rmrtxha1",
        "certId": 126200687,
        "certHash": "7f5bc8707c07b2d86303c608c6b80c5abd7c64df2f26e11569c51b9bc9094f45"
    },
    "TheGrinder": {
        "login": "alone-95",
        "password": "Rmrtxha2",
        "certId": 126194254,
        "certHash": "9546d87143160da0c1a9115fff4e1c08b70207e385867374ffdcb43964f863c5"
    },
    "Exodios-arc": {
        "login": "aloone-101",
        "password": "rmrtxha1",
        "certId": 126304681,
        "certHash": "5338d3bca4366251c237295c6c011b78dca61ded2792bb288109ff9439decfd2"
    },
    "melanco-lalco": {
        "login": "maniac.depressif@gmail.com",
        "password": "5hgCd.JMUVwxK-s",
        "certId": 126142784,
        "certHash": "aed578dee4dbb4aec9ddab79dedb14b91ed5c40313e846e1fb80616051f39aa5"
    }
}

from multiprocessing import Process

from pydofus2.com.ankamagames.haapi.Haapi import Haapi

def f(idx):
    key = list(accounts.keys())[idx]
    res = Haapi().getLoginToken(**accounts[key])
    print(f"Key for account melanco-lalco : " + res)
    return res

f(5)
# p2 = Process(target=f, args=(5, ))
# p2.start()
# p2.join()

# for key, account in accounts.items():
#     try:
#         res = Haapi().getLoginToken(**account)
#         print(f"Key for account {key} : " + res)
#     except Exception as e:
#         pass
#     print("sleeping for 10 s")
#     sleep(10)
#     print("ended sleeping")
    