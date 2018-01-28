import yagmail


def send_email(login_user, login_password, receiver_email_address, subject, contents):
    yag = yagmail.SMTP(login_user, login_password)

    try:
        yag.send(receiver_email_address, subject, contents=contents)
        return 1
    except Exception as e:
        print 'Could not send email: {}'.format(e.__str__())
        return 0
