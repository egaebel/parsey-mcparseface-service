from subprocess import PIPE
from subprocess import Popen
from subprocess import STDOUT

def run_parsey(sentence):
    parsey_path = "../../parsey-mcparseface-service/src/parsey.sh"
    parsey_proc = Popen(["/bin/bash", parsey_path, sentence], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    parsey_output, parsey_error = parsey_proc.communicate(input="\n")
    # Trim logging, start output at line starting with "Input:""
    parsey_output_list = parsey_output.split("\n")
    start_index = 0
    for line in parsey_output_list:
        if line.find("Input:") == 0:
            break
        start_index += 1
    return '\n'.join(parsey_output_list[start_index:])
