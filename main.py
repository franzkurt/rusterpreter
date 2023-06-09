"""
Copyright (C) 2023 Free Software Foundation, Inc.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.  

Written by Franz Gastring.  

Color support from rich package and rust compiler by rust foundation, 
see <https://foundation.rust-lang.org/>.  

"""

import time
import random
import readline  # ler caracteres especiais
from subprocess import Popen, PIPE
import tempfile

from rich import print
from rich.console import Console
from string import ascii_letters, digits

import logging

log = logging.getLogger("rich")

def print_banner(name, version, author):
    def _shuffle(line, nlen):
        for x in range(0, random.randint(1, 4)):
            print("\t{}".format(char(nlen)), end="\r")
            time.sleep(0.1)
        print("\t" + line)

    char = lambda i: " ".join(random.sample(ascii_letters + digits, k=i)).upper()

    nlen = len(name) + 4
    name = " ".join(name.upper())
    name = f"{char(2)} [bright_red]{name}[/bright_red] {char(2)}"

    lines = [char(nlen), name, char(nlen)]
    print("")
    [_shuffle(line, nlen) for line in lines]
    print(f"\n\tAuthor: {author}")
    print(f"\tVersion: {version}\n")


# Rust REPL
class RustInterpreter:

    def __init__(self):

        stdout, stderr = Popen(
            ["which", "rustc"], stdout=PIPE, shell=False
        ).communicate()

        if not stdout:
            raise Exception("Error: Rust compiler ('rustc') not found on system.")
        self.history = []

    def run(self):

        T_INICIO = """\n//--- BEGIN ---\nfn main() {\n\tlet _rust_result = {\n\t\t"""
        T_FIM = """\n\t};\n\tprintln!("{:?}", _rust_result);\n}\n//---- END ----"""

        while True:

            user_input = Console().input("rust> ").strip()
            start_time = time.time()

            if user_input == "exit":
                break

            if user_input == "clear":
                self.history.clear()
                continue

            # generate the file (rust source code)
            if user_input:
                self.history.append(user_input)

            # print(self.history)
            if not self.history:
                continue
            his = [(h if ";" in h else h + ";") for h in self.history[:-1]]
            his.append(self.history[-1])
            rcode = "\n\t\t".join(his)
            rust_code = T_INICIO + rcode + T_FIM
            print(rust_code)

            # to avoid temfile name prediction 
            # https://security.openstack.org/guidelines/dg_using-temporary-files-securely.html

            compiled = tempfile.NamedTemporaryFile(delete=False)

            with tempfile.NamedTemporaryFile(mode='w+', delete=True) as temp_file:
                temp_file.write(rust_code)
                temp_file.seek(0)

                # set file permissions to only allow owner access
                # os.chmod(temp_file.name, 0o600)
                
                # temporary compiled file 
                # print(compiled.name)

                # compile rust code (rustc build tool)
                _p = Popen(
                    ["rustc", temp_file.name, "-o", compiled.name],
                    stdout=PIPE,
                    stderr=PIPE,
                    shell=False
                )
                # _p.wait()
                stdout, stderr = _p.communicate()

                if stdout:
                    print(stderr.decode().strip())

                if stderr:
                    # errors from compiler
                    print(stderr.decode().strip())
                    if "error" in stderr.decode().strip():
                        self.history.pop()

            compiled.close()

            # execute rust (compiled file)
            process = Popen(
                compiled.name, stdout=PIPE, stderr=PIPE, shell=False
            )
            stdout, stderr = process.communicate()

            if stdout:
                # expected output from build
                print(stdout.decode().strip())
            if stderr:
                print(stderr.decode().strip())

            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"Elapsed time: {elapsed_time:.2} seconds.")

if __name__ == "__main__":
    print_banner("Rusterpreter", "0.2.4", "Franz Kurt")
    print(">> Rust REPL (works in Python 3.x--) <<")
    RustInterpreter().run()
