#coding:utf-8

import thread
import re, time, os
import commands
import sqlalchemy
import sqlite3
from multiprocessing import Pool
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class CAFE_VM(Base):

    __tablename__ = 'cafe_vm_info'

    id = Column( Integer, primary_key=True)
    hostname = Column( String(15))
    ip_addr =  Column( String(12))
    cafe_ver = Column( String(10))
    barista_ver = Column( String(10))
    ixia_ver = Column( String(10))
    stc_ver = Column( String(10))
    trex_ver = Column( String(10))
    installed_pkgs = Column( String(50))
    owner = Column( String(10))


    def __repr__(self):
        return '%s(%r, %r, %r, %r, %r, %r, %r, %r, %r)' % (self.__class__.__name__, self.hostname, self.ip_addr, self.cafe_ver, self.barista_ver, self.ixia_ver, self.stc_ver, self.trex_ver, self.installed_pkgs, self.owner)

# Base.metadata.create_all(engine)
engine = create_engine('sqlite:///./cafe_vm_info.db', echo=True)
Base.metadata.create_all(engine)

########################################
status_compiled=re.compile("\|(\s\w+\s)\|")
ip_compiled=re.compile("(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})")
# cafe_ver_compiled = re.compile("Release Version - (v\d.\d.\d?)")
cafe_ver_compiled = re.compile("Release Version - (.+)")
barista_ver_compiled = re.compile("Release Version - (\d.\d.\d?)")
stc_ver_compiled = re.compile("SpirentHltApi (\d.\d+)")
installed_pkgs_compiled = re.compile("\*\s\s(\w+)")
hostname_compiled = re.compile(">>\n(\w.+)")
########################################



def ansible_send(host, cmd):
    # t1 = time.time()
    ret = commands.getstatusoutput("ansible %s -a '%s' -i /home/jcao/ansible_/hosts_info" % (host, cmd))
    # t2 = time.time()
    # print('ansible send======>', t2-t1)
    return host_check(ret[1])
    # return ret[1]

def stat_check(outputs):
    return status_compiled.search(outputs, re.M | re.I).groups(1)[0]
    # re.search("\|(\s\w+\s)\|", outputs, re.M | re.I).groups(1)[0]

def host_check(outputs):
    # t1 = time.time()
    r = ip_compiled.search(outputs)
    # r = re.search("(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", outputs, re.M | re.I)
    if r:
        # print r.group(1)
        host = r.group(1)
        # t2 = time.time()
        # print 'host check========>', t2-t1
        if "UNREACHABLE!" in outputs:
            print "%s is unreachable!" % host
            return None
        elif 'FAILED' in outputs:
            print 'FAILED:', outputs
            return None
        else:
            return [host, outputs]
    else:
        return None

def get_cafe_version(host, cmd):

    # t1 = time.time()
    ret = ansible_send(host, cmd)
    if isinstance(ret, list):
        host = ret[0]
        outputs = ret[1]
        cafe_version = cafe_ver_compiled.search(outputs, re.M | re.I).group(1)
        # cafe_version = re.search("Release Version - (v\d.\d.\d?)", outputs, re.M | re.I).group(1)
        print host, "CAFE Version:", cafe_version
        # t2 = time.time()
        # print('get cafe version=======>', t2 - t1)
        if cafe_version:
            return cafe_version
        else:
            return None
    else:
        return None

def get_barista_version(host, cmd):

    # t1 = time.time()
    ret = ansible_send(host, cmd)
    if isinstance(ret, list):
        host = ret[0]
        outputs = ret[1]
        barista_version = barista_ver_compiled.search(outputs,re.M | re.I ).group(1)
        # barista_version = re.search("Release Version - (\d.\d.\d?)", outputs, re.M | re.I).group(1)
        print host, "Barista Version:", barista_version
        # t2 = time.time()
        # delta = abs(t2-t1)
        # print "========>", delta
        if barista_version:
            return barista_version
        else:
            return None
    else:
        return None


def get_stc_version(host, cmd):

    ret = ansible_send(host, cmd)
    if isinstance(ret, list):
        host = ret[0]
        outputs = ret[1]
        stc_ver = stc_ver_compiled.search(outputs,re.M | re.I).group(1)
        # stc_ver = re.search("SpirentHltApi (\d.\d+)", outputs, re.M | re.I).group(1)
        print host, "STC version:", stc_ver
        if stc_ver:
            return stc_ver
        else:
            return None
    else:
        return None

def get_installed_pkgs(host,cmd):

    ret = ansible_send(host, cmd)
    if isinstance(ret, list):
        host = ret[0]
        outputs = ret[1]
        installed_pkgs = installed_pkgs_compiled.findall(outputs, re.M | re.I)
        # installed_pkgs = re.findall("\*\s\s(\w+)", outputs, re.M | re.I)
        print host, "Already installed pkgs:", installed_pkgs
        if installed_pkgs:
            return installed_pkgs
        else:
            return None
    else:
        return None

def get_hostname(host, cmd):

    ret = ansible_send(host, cmd)
    if isinstance(ret, list):
        host = ret[0]
        outputs = ret[1]
        hostname = hostname_compiled.search(outputs, re.M | re.I).group(1)
        # hostname = re.search(">>\n(\w.+)", outputs, re.M | re.I).group(1)
        print host, "hostname:", hostname
        if hostname:
            return hostname
        else:
            return None
    else:
        return None

def get_reponse(host, cmd):

    outputs =ansible_send(host, cmd)
    if isinstance(outputs, list):
        s = stat_check(outputs[1])
        print s
        if s.strip() == 'SUCCESS':
            print host, "Outputs:", outputs
            if outputs:
                return outputs
            else:
                return None
    else:
        return None

def collect_info(host):

    d ={}
    print "parent process is %s" % os.getpid()
    p = Pool(6)
    t1 = time.time()
    cafe_ver_r = p.apply_async(get_cafe_version, args=(host, "barista version cafe"))
    barista_ver_r = p.apply_async(get_barista_version, args=(host, "barista version barista"))
    hostname_r = p.apply_async(get_hostname, args=(host, "hostname"))
    stc_ver_r = p.apply_async(get_stc_version, args=(host, "cat /opt/active_tcl/lib/stc_hltapi/pkgIndex.tcl"))
    installed_pkgs_r = p.apply_async(get_installed_pkgs, args=(host, "barista list"))
    if cafe_ver_r:
        d['cafe_ver'] = cafe_ver_r.get()
    else:
        d['cafe_ver'] = None
    if barista_ver_r:
        d['barista_ver'] = barista_ver_r.get()
    else:
        d['barista_ver'] = None
    if hostname_r:
        d['hostname'] = hostname_r.get()
    else:
        d['hostname'] = None
    if stc_ver_r:
        d['stc_ver'] = stc_ver_r.get()
    else:
        d['stc_ver'] = None
    if installed_pkgs_r:
        d['installed_pkgs'] = installed_pkgs_r.get()
    else:
        d['installed_pkgs'] = None
    print 'Waiting for all subprocesses done...'
    p.close()
    p.join()
    t2 = time.time()
    delta = abs(t1 - t2)
    print "=======================>", delta
    print 'All suppresses done.'
    return d

def is_host_exist(session, table, ip):
    for instance in session.query(table.ip_addr).filter_by(ip_addr=ip):
        if instance:
            return True
        else:
            return False

if __name__ == '__main__':
    tt1 = time.time()
    with open("hosts_info") as f:

        for i in f.readlines():
            #print i
            host = i.strip()

            if re.search("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", host):
                # thread.start_new_thread(get_cafe_version, (host, "barista version cafe"))
                # thread.start_new_thread(get_barista_version, (host, "barista version barista"))
                ###########################################################################################################
                # host = '10.245.243.59'
                info = collect_info(host)
                engine = create_engine('sqlite:///./cafe_vm_info.db', echo=True)
                # metadata = MetaData(engine).create_all()
                Session = sessionmaker(bind=engine)
                # Session.configure(bind=engine)
                session = Session()
                vm1 = CAFE_VM(cafe_ver=info['cafe_ver'],
                              hostname=info['hostname'],
                              barista_ver=info['barista_ver'],
                              stc_ver=info['stc_ver'],
                              installed_pkgs=str(info['installed_pkgs']),
                              ip_addr=host)
                if is_host_exist(session, CAFE_VM, host):
                    obj = session.query(CAFE_VM).filter_by(ip_addr=host).first()
                    obj.stc_ver = info['stc_ver']
                    obj.hostname = info['hostname']
                    # obj.hostname = "JAMES"
                    obj.barista_ver = info['barista_ver']
                    obj.cafe_ver = info['cafe_ver']
                    obj.installed_pkgs = str(info['installed_pkgs'])
                    # obj.owner = None
                    # obj.trex_ver = None
                    # obj.ixia_ver = None
                    # session.flush()
                    session.commit()
                    # session.refresh()
                else:
                    session.add(vm1)
                    session.commit()
                # session.flush(vm1)

            else:
                print "%s is not a valid host!" % host
    tt2 = time.time()
    print '=====>', abs(tt2-tt1)





# from sqlalchemy import *
# from sqlalchemy.orm import *
# engine = create_engine('sqlite:///./cafe_vm_info.db', echo=True)
# metadata = MetaData(engine)
#
# table_cafe_vms = Table('cafe_vm_info', metadata,
#                        Column('id', Integer, primary_key=True),
#                        Column("hostname", String(15)),
#                        Column("ip_add", String(12)),
#                        Column("cafe_ver", String(10)),
#                        Column("barista_ver", String(10)),
#                        Column("ixia_ver", String(10)),
#                        Column("stc_ver", String(10)),
#                        Column("trex_ver", String(10)),
#                        Column("installed_pkgs", list(20)),
#                        Column("owner", String(10)))
#
# table_cafe_vms.create()
# table_cafe_vms = Table('users', metadata, autoload=True)
#
# i = table_cafe_vms.insert()
# i.execute(name='rsj217', email='rsj21@gmail.com')
# i.execute({'name': 'ghost'},{'name': 'test'})
#
# d=table_cafe_vms.delete()
# s=table_cafe_vms.select()
# m=table_cafe_vms.update()
###################create#########################
# from sqlalchemy import *
# from sqlalchemy.orm import *
# from sqlalchemy.ext.declarative import declarative_base
# Base = declarative_base()
#
# class CAFE_VM(Base):
#     __tablename__ = 'cafe_vm_info'
#     id = Column('id', Integer, primary_key=True)
#     hostname = Column("hostname", String(15))
#     ip_addr =  Column("ip_add", String(12))
#     cafe_ver = Column("cafe_ver", String(10))
#     barista_ver = Column("barista_ver", String(10))
#     ixia_ver = Column("ixia_ver", String(10))
#     stc_ver = Column("stc_ver", String(10))
#     trex_ver = Column("trex_ver", String(10))
#     install_pkg = Column("installed_pkgs", list(20))
#     owner = Column("owner", String(10))
#
#     def __repr__(self):
#         return '%s(%r, %r, %r, %r, %r, %r, %r, %r, %r)' % (self.__class__.__name__, self.hostname, self.ip_addr, self.cafe_ver, self.barista_ver, self.ixia_ver, self.stc_ver, self.trex_ver, self.install_pkg, self.owner)
#
#
# # Base.metadata.create_all(engine)
#
# Session = sessionmaker(bind=engine)
# # Session.configure(bind=engine)
# session = Session()
# vm1 = CAFE_VM(ip_addr='1.1.1.1', cafe_ver='v1.22')
# session.add(vm1)
# session.flush(vm1)
# session.commit()

# session.add_all([
#     CAFE_VM(name='wendy', fullname='Wendy Williams', password='foobar'),
#     CAFE_VM(name='mary', fullname='Mary Contrary', password='xxg527'),
#     CAFE_VM(name='fred', fullname='Fred Flinstone', password='blah')])

#
# cafe_vm_info = session.query(CAFE_VM).filter_by(ip_addr='1.1.1.1').first()
# ed_user.password = 'f8s7ccs'
# session.dirty
# session.new
# session.commit()
#
# ###################query#########################
# for instance in session.query(CAFE_VM).order_by(CAFE_VM.id):
#     print(instance.name, instance.fullname)
#
# for name, fullname in session.query(CAFE_VM.ip_addr, CAFE_VM.cafe_ver):
#     print(name, fullname)