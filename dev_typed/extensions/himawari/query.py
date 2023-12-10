

import aioftp

from datetime import datetime, timezone, timedelta


FTP_HOST = 'ftp.ptree.jaxa.jp'
FTP_USER = 'capino627_163.com'
FTP_PWD = 'SP+wari8'
TIMEOUT = 5


async def query(t, delta):
    d = 600
    t = t.astimezone(timezone.utc)
    t0 = datetime.fromtimestamp(round(t.timestamp() / d) * d, tz=timezone.utc)
    t1 = t0
    diff = (t0 - t).total_seconds()
    i = 1 if diff < 0 else -1
    k = 2
    async with aioftp.Client.context(FTP_HOST, user=FTP_USER, password=FTP_PWD, socket_timeout=TIMEOUT) as ftp:
        while abs((t0 - t).total_seconds()) <= delta:
            for idx in [8, 9]:
                path = t0.strftime(f'/jma/netcdf/%Y%m/%d/NC_H{idx:02d}_%Y%m%d_%H%M_R21_FLDK.06001_06001.nc')
                if await ftp.exists(path):
                    return True, path
            t0 = t1 + timedelta(seconds=d * (k // 2) * i)
            i = -i
            k += 1
    return False, None
