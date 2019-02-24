from .models import User, Notice, u2g, Gnotice, Group
import datetime
from .email import send_maila
from app import db


def task():
    time = datetime.datetime.now()
    notices = Notice.query.all()
    for notice in notices:
        if notice.ntime1 is not None:
            if notice.if1 == 0:

                if (notice.ntime1 - time).seconds < 300:
                    if notice.usr.isemail == 1 and notice.usr.isopen == 1:
                        if send_maila(notice.usr.email, notice.nname, '/email/email', title=notice.nname,
                                     data=notice.dec, link='http://ddl.ywxisky.cn'):
                            notice.if1 = 1
                            db.session.add(notice)
                            db.session.commit()
        if notice.ntime2 is not None:
            if notice.if2 == 0:
                if (notice.ntime2 - time).seconds < 300:
                    if notice.usr.isemail == 1 and notice.usr.isopen == 1:
                        if send_maila(notice.usr.email, notice.nname, '/email/email', title=notice.nname,
                                     data=notice.dec, link='http://ddl.ywxisky.cn'):
                            notice.if2 = 1
                            db.session.add(notice)
                            db.session.commit()
    gnotices = Gnotice.query.all()
    for gnotice in gnotices:
        if gnotice.gtime1 is not None:
            if gnotice.if1 == 0:
                if (gnotice.gtime1 - time).seconds < 300:
                    for usr in gnotices.gp.users:
                        if usr.isemail == 1 and usr.isopen==1:
                            send_maila(usr.email, gnotice.gname, '/email/email', title=gnotice.gname,
                                  data=gnotice.dec, link='http://ddl.ywxisky.cn')
                    gnotice.if1 = 1
                    db.session.add(gnotice)
                    db.session.commit()
        if gnotice.gtime2 is not None:
            if gnotice.if2 == 0:
                if (gnotice.gtime2 - time).seconds < 300:
                    for usr in gnotices.gp.users:
                        if usr.isemail == 1 and usr.isopen==1:
                            send_maila(usr.email, gnotice.gname, '/email/email', title=gnotice.gname,
                                  data=gnotice.dec, link='http://ddl.ywxisky.cn')
                    gnotice.if2 = 2
                    db.session.add(gnotice)
                    db.session.commit()

    return 0
