import subprocess
import os

# spokenTxt="Hello"
# process = subprocess.Popen(['festival', '--tts'],
#                            stdin=subprocess.PIPE,
#                            stdout=subprocess.PIPE,
#                            stderr=subprocess.STDOUT)
# stdout_value, stderr_value = process.communicate(spokenTxt)
# process.wait()

def run(*popenargs, **kwargs):
    input = kwargs.pop("input", None)
    check = kwargs.pop("handle", False)

    if input is not None:
        if 'stdin' in kwargs:
            raise ValueError('stdin and input arguments may not both be used.')
        kwargs['stdin'] = subprocess.PIPE

    process = subprocess.Popen(*popenargs, **kwargs)
    try:
        stdout, stderr = process.communicate(input)
    except:
        process.kill()
        process.wait()
        raise
    retcode = process.poll()
    if check and retcode:
        raise subprocess.CalledProcessError(
            retcode, process.args, output=stdout, stderr=stderr)
    return retcode, stdout, stderr

if __name__=='__main__':
    # subprocess.call("source activate kfpy3 && python test.py && source deactivate", shell=True)
    try:
        os.mkdir("test")
    except OSError:
        print("error caught")
