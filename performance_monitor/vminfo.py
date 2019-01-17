#coding:utf-8

# import thread
import re, time, os
import subprocess
# import sqlalchemy
# import sqlite3
from multiprocessing import Pool
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Performance_data(Base):

    __tablename__ = 'Performance_data'

    id = Column( Integer, primary_key=True)
    hostname = Column( String(15))
    ip_addr =  Column( String(12))

    def __repr__(self):
        return '%s(%r, %r )' % (self.__class__.__name__, self.hostname, self.ip_addr)
        # return '%s(%r, %r, %r, %r, %r, %r, %r, %r, %r)' % (self.__class__.__name__, self.hostname, self.ip_addr, self.cafe_ver, self.barista_ver, self.ixia_ver, self.stc_ver, self.trex_ver, self.installed_pkgs, self.owner)

# Base.metadata.create_all(engine)
engine = create_engine('sqlite:///./performance_data.db', echo=True)
Base.metadata.create_all(engine)

########################################
status_compiled=re.compile("\|(\s\w+\s)\|")
ip_compiled=re.compile("(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})")
hostname_compiled = re.compile(">>\n(\w.+)")
########################################

def send(host, cmd):
    import paramiko
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, port=22, username="jcao", password="WD87diannao")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    result = stdout.read().decode()
    ssh.close()
    return result

def CPU_collect(res):
  for l in [line for line in res.split('\n')]:
      print(l.split(":")[0] + '=' +l.split(':')[1].strip('kB'))
      print(int(l.split(':')[1].strip('kB')))


def MEM_collect():
    pass

def collect_info(host):

    d ={}
    # print("parent process is %s" % os.getpid())
    p = Pool(6)
    t1 = time.time()
    hostname_r = p.apply_async(CPU_collect, args=(host, "whoami"))

    if hostname_r:
        d['hostname'] = hostname_r.get()
    else:
        d['hostname'] = None

    # print('Waiting for all subprocesses done...')
    p.close()
    p.join()
    t2 = time.time()
    delta = abs(t1 - t2)
    # print("=======================>", delta)
    # print('All suppresses done.')
    return d

def is_host_exist(session, table, ip):
    for instance in session.query(table.ip_addr).filter_by(ip_addr=ip):
        if instance:
            return True
        else:
            return False

if __name__ == '__main__':
    ret = send("192.168.0.116","cat /proc/meminfo")
    print(CPU_collect(ret))
    # tt1 = time.time()
    # with open("hosts") as f:
    #
    #     for i in f.readlines():
    #
    #         host = i.strip()
    #         if re.search("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", host):
    #
    #             info = collect_info(host)
    #             engine = create_engine('sqlite:///./performance_data.db', echo=True)
    #             # metadata = MetaData(engine).create_all()
    #             Session = sessionmaker(bind=engine)
    #             # Session.configure(bind=engine)
    #             session = Session()
    #             vm1 = Performance_data(hostname=info['hostname'],)
    #             if is_host_exist(session, Performance_data, host):
    #                 obj = session.query(Performance_data).filter_by(ip_addr=host).first()
    #                 obj.hostname = info['hostname']
    #                 # session.flush()
    #                 session.commit()
    #                 # session.refresh()
    #             else:
    #                 session.add(vm1)
    #                 session.commit()
    #             # session.flush(vm1)
    #
    #         else:
    #             print("%s is not a valid host!" % host)
    # tt2 = time.time()
    # print('=====>', abs(tt2-tt1))

