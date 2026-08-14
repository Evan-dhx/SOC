import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check if GTHR_ACTIVE_PROXY is defined
print("=== Checking GTHR_ACTIVE_PROXY ===")
cmd = r"""cd /root/SOC/ly_server_src/server && g++ -E gen_event.cpp -I/usr/include/mysql -I/usr/include/cppdb -I/usr/include/cgicc -I. -I../common 2>&1 | grep 'GTHR_ACTIVE_PROXY' | head -10"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=60)
print(stdout.read().decode())
print(stderr.read().decode())

# Check what __depend actually is
print("\n=== Checking __depend in preprocessor output ===")
cmd2 = r"""cd /root/SOC/ly_server_src/server && g++ -E gen_event.cpp -I/usr/include/mysql -I/usr/include/cppdb -I/usr/include/cgicc -I. -I../common 2>&1 | grep -B2 -A2 '__depend' | head -30"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=60)
print(stdout.read().decode())
print(stderr.read().decode())

# Try compiling with -UGTHR_ACTIVE_PROXY to undefine it
print("\n=== Trying with -UGTHR_ACTIVE_PROXY ===")
cmd3 = r"""cd /root/SOC/ly_server_src/server && g++ gen_event.cpp dbc.o syslog_sender.o -Wall -g -std=c++11 -lpthread -UGTHR_ACTIVE_PROXY -I/usr/include/mysql -I/usr/include/cppdb -I/usr/include/cgicc -I. -L/usr/lib64 -L/usr/lib -L/usr/local/lib -L/usr/lib64/mysql -L/usr/lib/mysql -L/usr/local/mysql/lib -L../common -lcommon -lcppdb -lcgicc -lcurl -lprotobuf -lmysqlclient -lpthread -ljson-c -lboost_regex -o /tmp/gen_event_test 2>&1 | tail -20"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=60)
print(stdout.read().decode())
print(stderr.read().decode())

client.close()
