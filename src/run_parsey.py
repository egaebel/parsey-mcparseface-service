from multiprocessing import Pool
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

def test_with_multiple_processes():
    pool = Pool()
    test_sentences = ["This has been a test of the emergency parsey mcparseface parser." for x in range(0, 128)]
    results = pool.map(run_parsey, test_sentences)
    for i in range(len(results)):
        print("\n\nResult %d:" % i)
        print(results[i])
    pool.close()

if __name__ == '__main__':
    sentence = "What a nice sentence this is."
    print("Testing run_parsey with sentence: %s" % sentence)
    print("run_parsey output: %s " % run_parsey(sentence))

    test_with_multiple_processes()