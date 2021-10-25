import paramiko
from datetime import datetime
from datetime import timezone
cmd0 = "/wr/bin/wr_date get"
cmd1 = "date +'%T.%9N'"

ssh=paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('10.0.1.36',username='root',password='')

t_current = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd0)
result0=ssh_stdout.read()
t_host0 = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd1)
result1=ssh_stdout.read()
t_host1 = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    
result0_str=str(result0, encoding = "utf-8")
s=result0_str.split(' ')
d = s[3].split('\n')
wrs_time = d[1] + ' ' +s[4]
sys_time = str(result1, encoding = "utf-8")
sys_time = sys_time.rstrip('\n')
sys_time = d[1] + ' ' + sys_time
print(wrs_time)
print(t_host0,'\n')
print(sys_time)
print(t_host1,'\n')
del(ssh,ssh_stdin, ssh_stdout, ssh_stderr)

