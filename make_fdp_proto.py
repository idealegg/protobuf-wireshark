#! /usr/bin/python

import os
import re
import sys
import shutil


conf = {'proto_path': 'messages',
        'orig_proto_path': '/usr/system/workspace/TowerMSG/messages',
        'protoc': '/usr/system/workspace/TowerCOMM/ext/protoc-i386',
        'wireshark_src_dir': '/usr/share/wireshark/wireshark-1.8.10',
        'wireshark_install_dir': '/usr/share/wireshark-1.8.10',
        'wireshark_version': '1.8.10',
}

port_map = {
        #"AodbJmsTopic": "",
        "AwosAtisProto": "9322",
        #"bcl": "",
        "BusinessObjectsMessage": "9323",
        #"DclMessage": "",
        #"DummyTopic": "",
        "FlightPlanTopic": "9997",
        #"FpmFlightPlanTopic": "",
        "FrequencySectorTopic": "9324",
        "GcfTopic": "9123",
        "GServer_CwpMsg": "28000",  # trs 
        #"IntegerTopic": "",
        "ResectorizationTopic": "9100",
        "SIDcfgMessage": "9200",
        "SRSSCalendar": "9321",
        }

#port_map = {"AwosAtisProto": "9322",}

make_conf_template='''name                  : %s
package               : %s
proto_file            : %s
wireshark_src_dir     : %s
wireshark_install_dir : %s
wireshark_version     : %s
port_num              : %s'''

def findstr(str1,str2):
  count = 0
  length = len(str1)
  for sublen in range(length,0,-1):
    for start in range(0,length - sublen + 1):
      count += 1
      substr = str1[start:start+sublen]
      if substr and str2.find(substr) > -1:
        print('count=%s,  subStringLen:%s'  % (count,sublen))
        return substr
  else:
    return ""

def read_f(f_path):
  f=open(f_path)
  text = f.read()
  f.close()
  return text

def write_f(f_path, text):
  f=open(f_path, 'w')
  f.write(text)
  f.close()

def process_import(text):
  p=re.compile(r'\bimport\s+"([^\s"]+)"s*;')
  r=p.findall(text)
  if r:
    text=p.sub("", text);
    for im in set(r):
      if not os.path.isfile(os.path.join(conf['proto_path'], im)):
        shutil.copy(os.path.join(conf['orig_proto_path'], im), conf['proto_path'])
      f2 = open(os.path.join(conf['proto_path'], im))
      text2 = f2.read()
      f2.close()
      r2 = re.compile(r'\b(message|enum)\s+[\w_]+\s*\{').search(text2)
      if r2:
        text += "\n"+text2[r2.start():]
        r3 = re.compile(r'\bpackage\s+([\w_]+)\s*;').search(text2)
        if r3:
          text = re.compile(r'\b'+r3.group(1)+r'.').sub('', text)
  return text

def replace_str_in_file(text, s_targets, s_replaces, f_path):
  modifiedText = text
  for i, s_target in enumerate(s_targets):
    p=re.compile(s_target);
    s_replace = s_replaces[i]
    if p.search(text):
      print "replace "+s_target+" to "+s_replace+ " in file " + f_path
      text=p.sub(s_replace, text)
    else:
      print "str "+s_target+" not in file " + f_path
  return text

def get_new_f_proto(text, f_proto_path):
  p=re.compile(r'\bmessage\s+([\w_]+)\s*{')
  r=p.findall(text)
  keys = filter(lambda x: len(re.compile(r'\b'+x+r'\b').findall(text)) == 1, set(r))
  if len(keys) > 1:
    print("too much message:")
    print(r)
    print(map(lambda x: "%s: %s" % (x, len(re.compile(r'\b'+x+r'\b').findall(text))), set(r)))
    f_proto_path_base = os.path.splitext(f_proto_path)[0]
    keys.sort(key=lambda x: len(findstr(x.lower(), f_proto_path_base.lower())), reverse=True)
    print(keys)
    return "%s.proto" % keys[0]
  elif len(keys) == 0:
    print("no message found")
    return f_proto_path
  else:
    print(keys[0])
    return "%s.proto" % keys[0]


def generate_cpp(f_proto_path):
  cur_dir = os.getcwd()
  os.chdir(conf['proto_path'])
  cmd = '%s --cpp_out=. %s' % (conf['protoc'], f_proto_path)
  ret = os.system(cmd)
  print("cur_dir[%s], proto_path[%s]", cur_dir, conf['proto_path'])
  print("generate_cpp, protoc, cmd[%s], ret[%s]", cmd, ret)
  os.chdir(cur_dir)


def prepare_make_conf(f_proto_path, old_f_proto_path):
    plugin = os.path.splitext(f_proto_path)[0]
    text = make_conf_template % (plugin, 
                                 conf['package_name'],
                                 os.path.join(conf['proto_path'], f_proto_path),
                                 conf['wireshark_src_dir'],
                                 conf['wireshark_install_dir'],
                                 conf['wireshark_version'],
                                 port_map[os.path.splitext(old_f_proto_path)[0]])
    f = open('%s.conf' % plugin, 'w')
    f.write(text)
    f.close()


if __name__ == "__main__":
  if not os.path.isabs(conf['proto_path']):
    conf['proto_path'] = os.path.join(os.getcwd(), conf['proto_path'])
  if not os.path.isdir(conf['proto_path']):
    os.mkdir(conf['proto_path'])
  package_names = set()
  for f_proto in os.listdir(conf['orig_proto_path']):
    f_proto_base = os.path.splitext(f_proto)[0]
    if f_proto.endswith('.proto') and f_proto_base in port_map:
      shutil.copy(os.path.join(conf['orig_proto_path'], f_proto), conf['proto_path'])
      while f_proto_base in package_names:
        f_proto_base = "%s_" % f_proto_base
      package_names.add(f_proto_base)
      conf['package_name'] = f_proto_base
      f_proto_path = os.path.join(conf['proto_path'], f_proto)
      text = read_f(f_proto_path)
      text = process_import(text)
      t_strs = [r"package [\w.]+;"]
      r_strs = ["package %s;" % conf['package_name']]
      '''if f_proto.startswith('ResectorizationTopic.'):
        t_strs.extend([r'\bSectorType\b', r'\bSector\b', r'\bSNAPSHOT\b'])
        r_strs.extend(['SectorType2', 'Sector2', 'SNAPSHOT2'])
      elif f_proto.startswith('GcfTopic.'):
        t_strs.extend([r'\bUpdateKind\b'])
        r_strs.extend(['UpdateKind2'])'''
      text = replace_str_in_file(text, 
                          t_strs,
                          r_strs,
                          f_proto_path)
      write_f(f_proto_path, text)
      new_f_proto = get_new_f_proto(text, f_proto)
      if new_f_proto != f_proto:
        os.rename(f_proto_path, os.path.join(conf['proto_path'], new_f_proto))
      generate_cpp(new_f_proto)
      prepare_make_conf(new_f_proto, f_proto)
      os.system('./make_wireshark_plugin.py %s.conf' % os.path.splitext(new_f_proto)[0])

