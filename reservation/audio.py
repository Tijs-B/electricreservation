import subprocess


def get_current_audio_output():
    output = subprocess.check_output(['amixer', 'cget', 'numid=3'])
    output = output.decode("ascii", errors="ignore")
    last_line = output.splitlines()[-1]
    number = last_line[-1]
    if number == '1':
        return "jack"
    else:
        return "hdmi"


def set_audio_output_jack():
    subprocess.run(['amixer', 'cset', 'numid=3', '1'])


def set_audio_output_hdmi():
    subprocess.run(['amixer', 'cset', 'numid=3', '2'])


