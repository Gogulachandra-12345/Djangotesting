# Status code : 250
SUCCESS = """
connect: ('akshayainc-com01i.mail.protection.outlook.com.', 25)
connect: to ('akshayainc-com01i.mail.protection.outlook.com.', 25) None
reply: b'220 DM6NAM04FT058.mail.protection.outlook.com Microsoft ESMTP MAIL Service ready at Wed, 26 Aug 2020 11:07:46 +0000\r\n'
reply: retcode (220); Msg: b'DM6NAM04FT058.mail.protection.outlook.com Microsoft ESMTP MAIL Service ready at Wed, 26 Aug 2020 11:07:46 +0000'
connect: b'DM6NAM04FT058.mail.protection.outlook.com Microsoft ESMTP MAIL Service ready at Wed, 26 Aug 2020 11:07:46 +0000'
send: 'helo python-email-server\r\n'
reply: b'250 DM6NAM04FT058.mail.protection.outlook.com Hello [206.189.142.106]\r\n'
reply: retcode (250); Msg: b'DM6NAM04FT058.mail.protection.outlook.com Hello [206.189.142.106]'
send: 'mail FROM:<me@domain.com>\r\n'
reply: b'250 2.1.0 Sender OK\r\n'
reply: retcode (250); Msg: b'2.1.0 Sender OK'
send: 'rcpt TO:<swaroopantoo@akshaya-inc.com>\r\n'
reply: b'250 2.1.5 Recipient OK\r\n'
reply: retcode (250); Msg: b'2.1.5 Recipient OK'
send: 'quit\r\n'
reply: b'221 2.0.0 Service closing transmission channel\r\n'
reply: retcode (221); Msg: b'2.0.0 Service closing transmission channel'
"""

# Status Code: 220
FAILURE_1 = """connect: ('shared87.accountservergroup.com.', 25)
connect: to ('shared87.accountservergroup.com.', 25) None
reply: b'220-shared87.accountservergroup.com ESMTP Exim 4.91 #1 Wed, 26 Aug 2020 06:05:14 -0500 \r\n'
reply: b'220-We do not authorize the use of this system to transport unsolicited, \r\n'
reply: b'220 and/or bulk e-mail.\r\n'
reply: retcode (220); Msg: b'shared87.accountservergroup.com ESMTP Exim 4.91 #1 Wed, 26 Aug 2020 06:05:14 -0500\nWe do not authorize the use of this system to transport unsolicited,\nand/or bulk e-mail.'
connect: b'shared87.accountservergroup.com ESMTP Exim 4.91 #1 Wed, 26 Aug 2020 06:05:14 -0500\nWe do not authorize the use of this system to transport unsolicited,\nand/or bulk e-mail.'
send: 'helo python-email-server\r\n'
reply: b'250 shared87.accountservergroup.com Hello python-email-server [206.189.142.106]\r\n'
reply: retcode (250); Msg: b'shared87.accountservergroup.com Hello python-email-server [206.189.142.106]'
send: 'mail FROM:<me@domain.com>\r\n'
reply: b'550 Access denied - Invalid HELO name (See RFC2821 4.1.1.1)\r\n'
reply: retcode (550); Msg: b'Access denied - Invalid HELO name (See RFC2821 4.1.1.1)'
send: 'rcpt TO:<krishna@3ktechnologies.com>\r\n'
"""