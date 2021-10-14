import paramiko

cmd = "/wr/bin/wr_date get"
ssh=paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('10.0.1.36',username='root',password='')
ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd)
result=ssh_stdout.read()
result_str=str(result, encoding = "utf-8")
s=result_str.split(' ')
d = s[3].split('\n')
time = d[1] + ' ' +s[4]
print(time)
ssh.close()
del(ssh,ssh_stdin, ssh_stdout, ssh_stderr)

