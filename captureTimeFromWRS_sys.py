import paramiko

cmd = "date +'%T.%3N'"
ssh=paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.254',username='root',password='')
ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd)
result=ssh_stdout.read()
result_str=str(result, encoding = "utf-8")
print(result_str)
ssh.close()
del(ssh,ssh_stdin, ssh_stdout, ssh_stderr)

